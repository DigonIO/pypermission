import networkx as nx
import plotly.graph_objects as go
from sqlalchemy.sql import select
from sqlalchemy.orm import Session

from pypermission.models import HierarchyORM, MemberORM, PolicyORM, RoleORM, SubjectORM
from pypermission.exc import PyPermissionError


def dag_factory(*, db: Session) -> nx.DiGraph:

    role_orms = db.scalars(select(RoleORM)).all()
    roles = set(role_orm.id for role_orm in role_orms)

    hierarchy_orms = db.scalars(select(HierarchyORM)).all()
    role_hierarchy = set(
        (hierarchy_orm.child_role_id, hierarchy_orm.parent_role_id)
            for hierarchy_orm in hierarchy_orms
    )

    subject_orms = db.scalars(select(SubjectORM)).all()
    subjects = set(subject_orm.id for subject_orm in subject_orms)

    member_orms = db.scalars(select(MemberORM)).all()
    members = set(
        (member_orm.subject_id, member_orm.role_id) for member_orm in member_orms
    )

    policy_orms = db.scalars(select(PolicyORM)).all()
    permissions = set(
        _permission_to_str(
            policy_orm.resource_type, policy_orm.resource_id, policy_orm.action
        )
        for policy_orm in policy_orms
    )
    policies = set(
        (
            policy_orm.role_id,
            _permission_to_str(
                policy_orm.resource_type, policy_orm.resource_id, policy_orm.action
            ),
        )
        for policy_orm in policy_orms
    )

    dag = nx.DiGraph()
    dag.add_nodes_from(roles, type="role")
    dag.add_edges_from(role_hierarchy)
    dag.add_nodes_from(subjects, type="subject")
    dag.add_edges_from(members)
    dag.add_nodes_from(permissions, type="permission")
    dag.add_edges_from(policies)

    return dag


def plot_factory(*, dag: nx.DiGraph) -> None:

    if not len(dag):
        raise PyPermissionError("The RBAC system is empty. Nothing to plot!")

    fig = _build_plotly_figure(dag=dag)
    fig.write_html("dag.html", auto_open=True)


################################################################################
#### Util
################################################################################

COLOR_MAP = {
    "role": "lightgreen",
    "subject": "lightblue",
    "permission": "lightcoral",
}

NodePositions = dict[str, tuple[float, int]]


def _build_plotly_figure(*, dag: nx.DiGraph) -> go.Figure:
    node_positions = _calc_node_positions(dag=dag)
    node_colors = tuple(COLOR_MAP[dag.nodes[n]["type"]] for n in dag.nodes())

    nodes = _build_nodes(
        dag=dag, node_positions=node_positions, node_colors=node_colors
    )
    edges = _build_edges(dag=dag, node_positions=node_positions)

    fig = go.Figure(data=[nodes, edges])
    fig.update_layout(
        showlegend=False,
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    )

    return fig


def _build_edges(*, dag: nx.DiGraph, node_positions: NodePositions) -> go.Scatter:
    edge_x, edge_y = [], []

    for u, v in dag.edges():
        x0, y0 = node_positions[u]
        x1, y1 = node_positions[v]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    return go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=1, color="black"),
        hoverinfo="none",
        mode="lines",
    )


def _build_nodes(
    *, dag: nx.DiGraph, node_positions: NodePositions, node_colors: tuple[str, ...]
) -> go.Scatter:
    return go.Scatter(
        x=[node_positions[n][0] for n in dag.nodes()],
        y=[node_positions[n][1] for n in dag.nodes()],
        mode="markers+text",
        text=[str(n) for n in dag.nodes()],
        textposition="top center",
        marker=dict(size=20, color=node_colors, line=dict(width=2, color="black")),
    )


def _calc_node_positions(*, dag: nx.DiGraph) -> dict[str, tuple[float, int]]:
    layers = {}
    for node in nx.topological_sort(dag):
        node_type = dag.nodes[node]["type"]
        if node_type == "subject":
            layers[node] = 1
        else:
            layers[node] = 1 + max(layers[p] for p in dag.predecessors(node))

    max_layer = max(layers.values())
    for node in dag.nodes():
        if dag.nodes[node]["type"] == "permission":
            layers[node] = max_layer

    layer_nodes: dict[int, list[str]] = {}
    for node, layer in layers.items():
        layer_nodes.setdefault(layer, []).append(node)

    node_positions = {}
    for layer, nodes_in_layer in layer_nodes.items():
        n_nodes = len(nodes_in_layer)
        xs: tuple[float, ...]
        if n_nodes == 1:
            xs = (0.0,)
        else:
            xs = tuple(2 * x / (n_nodes - 1) - 1 for x in range(n_nodes))
        y = -layer
        for x, node in zip(xs, nodes_in_layer):
            node_positions[node] = (x, y)
    return node_positions


def _permission_to_str(resource_type: str, resource_id: str, action: str) -> str:
    if not resource_id:
        return f"{resource_type}:{action}"
    return f"{resource_type}[{resource_id}]:{action}"
