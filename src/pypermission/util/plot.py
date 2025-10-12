import networkx as nx
import plotly.graph_objects as go

from pypermission.exc import PyPermissionError


def plot_factory(
    *, dag: nx.DiGraph, auto_open: bool = False, file_path: str = "dag.html"
) -> None:
    """
    Generate an interactive HTML visualization of an RBAC DAG and save it to `file_path`.

    Parameters
    ----------
    dag : nx.DiGraph
        The RBAC system DAG.
    auto_open : bool
        Automatically opens the plot in the browser.
    file_path: str
        Path and filename for the generated HTML as string.

    Raises
    ------
    PyPermissionError
        Raised when the input DAG is empty, indicating that there is no data to plot.
    """

    if not len(dag):
        raise PyPermissionError("RBAC system is empty. Nothing to plot!")

    fig = _build_plotly_figure(dag=dag)
    fig.write_html(file_path, auto_open=auto_open)


################################################################################
#### Util
################################################################################

COLOR_MAP = {
    "subject_node": "darkturquoise",
    "member_edge": "darkturquoise",
    "role_node": "coral",
    "hierarchy_edge": "coral",
    "permission_node": "forestgreen",
    "policy_edge": "forestgreen",
}

NodePositions = dict[str, tuple[float, float]]


def _build_plotly_figure(*, dag: nx.DiGraph) -> go.Figure:
    node_positions = _calc_node_positions(dag=dag)
    nodes = _build_nodes(dag=dag, node_positions=node_positions)

    edge_colors = tuple(COLOR_MAP[dag.edges[n]["type"]] for n in dag.edges())
    edges = _build_edges(
        dag=dag, node_positions=node_positions, edge_colors=edge_colors
    )

    fig = go.Figure(data=[edges[0], edges[1], edges[2], nodes[0], nodes[1], nodes[2]])
    fig.update_layout(
        showlegend=True,
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    )

    return fig


def _build_nodes(
    *, dag: nx.DiGraph, node_positions: NodePositions
) -> tuple[go.Scatter, go.Scatter, go.Scatter]:
    node_subjects = tuple(
        node for node, data in dag.nodes.data() if data["type"] == "subject_node"
    )
    node_roles = tuple(
        node for node, data in dag.nodes.data() if data["type"] == "role_node"
    )
    node_permissions = tuple(
        node for node, data in dag.nodes.data() if data["type"] == "permission_node"
    )

    return (
        go.Scatter(
            x=tuple(node_positions[node][0] for node in node_subjects),
            y=tuple(node_positions[node][1] for node in node_subjects),
            mode="markers+text",
            text=tuple(str(n) for n in node_subjects),
            textposition="top center",
            textfont=dict(size=20, color="black"),
            marker=dict(size=20, color=COLOR_MAP["subject_node"]),
            name="Subjects",
        ),
        go.Scatter(
            x=tuple(node_positions[node][0] for node in node_roles),
            y=tuple(node_positions[node][1] for node in node_roles),
            mode="markers+text",
            text=[str(n) for n in node_roles],
            textposition="top center",
            textfont=dict(size=20, color="black"),
            marker=dict(size=20, color=COLOR_MAP["role_node"]),
            name="Roles",
        ),
        go.Scatter(
            x=tuple(node_positions[node][0] for node in node_permissions),
            y=tuple(node_positions[node][1] for node in node_permissions),
            mode="markers+text",
            text=tuple(str(node) for node in node_permissions),
            textposition="top center",
            textfont=dict(size=20, color="black"),
            marker=dict(size=20, color=COLOR_MAP["permission_node"]),
            name="Permissions",
        ),
    )


def _build_edges(
    *, dag: nx.DiGraph, node_positions: NodePositions, edge_colors: tuple[str, ...]
) -> tuple[go.Scatter, go.Scatter, go.Scatter]:
    edge_x_member, edge_y_member = [], []
    edge_x_hierarchy, edge_y_hierarchy = [], []
    edge_x_policy, edge_y_policy = [], []

    for n_0, n_1, data in dag.edges.data():
        x_0, y_0 = node_positions[n_0]
        x_1, y_1 = node_positions[n_1]

        match data["type"]:
            case "member_edge":
                edge_x_member.extend([x_0, x_1, None])
                edge_y_member.extend([y_0, y_1, None])
            case "hierarchy_edge":
                edge_x_hierarchy.extend([x_0, x_1, None])
                edge_y_hierarchy.extend([y_0, y_1, None])
            case "policy_edge":
                edge_x_policy.extend([x_0, x_1, None])
                edge_y_policy.extend([y_0, y_1, None])

    return (
        go.Scatter(
            x=edge_x_member,
            y=edge_y_member,
            line=dict(width=2, color=COLOR_MAP["member_edge"]),
            hoverinfo="none",
            mode="lines",
            name="Role assignment",
        ),
        go.Scatter(
            x=edge_x_hierarchy,
            y=edge_y_hierarchy,
            line=dict(width=2, color=COLOR_MAP["hierarchy_edge"]),
            hoverinfo="none",
            mode="lines",
            name="Role hierarchy",
        ),
        go.Scatter(
            x=edge_x_policy,
            y=edge_y_policy,
            line=dict(width=2, color=COLOR_MAP["policy_edge"]),
            hoverinfo="none",
            mode="lines",
            name="Permission assignment",
        ),
    )


def _calc_node_positions(*, dag: nx.DiGraph) -> dict[str, tuple[float, float]]:

    role_nodes = [n for n, d in dag.nodes(data=True) if d.get("type") == "role_node"]
    hierarchy_edges = [
        (u, v) for u, v, d in dag.edges(data=True) if d.get("type") == "hierarchy_edge"
    ]

    role_sdag = nx.DiGraph()
    role_sdag.add_nodes_from(role_nodes)
    role_sdag.add_edges_from(hierarchy_edges)

    unsorted_role_sdags = [
        dag.subgraph(c).copy() for c in nx.weakly_connected_components(role_sdag)
    ]
    role_sdags = sorted(
        unsorted_role_sdags, key=lambda g: g.number_of_nodes(), reverse=False
    )

    role_layers: dict[str, int] = {}
    for sdag in role_sdags:
        for node in nx.topological_sort(sdag):
            predecessors = tuple(dag.predecessors(node))
            role_layers[node] = (
                1
                + max(
                    tuple(
                        role_layers[p]
                        for p in predecessors
                        if dag.nodes[p]["type"] == "role_node"
                    )
                    + (0,)
                )
                if predecessors
                else 1
            )

    permission_layer = 0
    subject_layer = max(role_layers.values()) + 1

    layer_x_nodes: dict[int, list[str]] = {
        layer: [] for layer in range(permission_layer, subject_layer + 1)
    }
    for node in nx.topological_sort(dag):
        match dag.nodes[node]["type"]:
            case "subject_node":
                layer_x_nodes[subject_layer].append(node)
            case "permission_node":
                layer_x_nodes[permission_layer].append(node)

    for sdag in role_sdags:
        for node in nx.topological_sort(sdag):
            layer_x_nodes[role_layers[node]].append(node)

    node_positions = {}
    for layer, nodes_in_layer in layer_x_nodes.items():
        n_nodes = len(nodes_in_layer)
        ys: tuple[float, ...]
        if n_nodes == 1:
            ys = (1,)
        else:
            ys = tuple(1 * x / (n_nodes - 1) for x in range(n_nodes))
        x = -layer
        for y, node in zip(ys, nodes_in_layer):
            node_positions[node] = (float(x), y)
    return node_positions
