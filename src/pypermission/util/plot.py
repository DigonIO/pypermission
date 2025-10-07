import networkx as nx
import plotly.graph_objects as go

from pypermission.exc import PyPermissionError


def plot_factory(*, dag: nx.DiGraph) -> None:

    if not len(dag):
        raise PyPermissionError("The RBAC system is empty. Nothing to plot!")

    fig = _build_plotly_figure(dag=dag)
    fig.write_html("dag.html", auto_open=True)


################################################################################
#### Util
################################################################################

COLOR_MAP = {
    "role_node": "lightgreen",
    "subject_node": "lightblue",
    "permission_node": "lightcoral",
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
    role_layers: dict[str, int] = {}
    for node in nx.topological_sort(dag):
        if dag.nodes[node]["type"] == "role_node":
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

    subject_layer = 0
    permission_layer = max(role_layers.values()) + 1

    layer_x_nodes: dict[int, list[str]] = {
        layer: [] for layer in range(subject_layer, permission_layer + 1)
    }
    for node in nx.topological_sort(dag):
        match dag.nodes[node]["type"]:
            case "role_node":
                layer_x_nodes[role_layers[node]].append(node)
            case "subject_node":
                layer_x_nodes[subject_layer].append(node)
            case "permission_node":
                layer_x_nodes[permission_layer].append(node)

    node_positions = {}
    for layer, nodes_in_layer in layer_x_nodes.items():
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
