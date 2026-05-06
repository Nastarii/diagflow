import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from diagflow.core.diagram import Diagram

NODE_W = 140
NODE_H = 56
H_GAP = 120
V_GAP = 80
PADDING = 60


def apply_layout(diagram: "Diagram") -> None:
    nodes = list(diagram.nodes.values())
    if not nodes:
        return

    try:
        import networkx as nx
        _nx_layout(diagram, nodes)
    except ImportError:
        _grid_layout(nodes)


def _nx_layout(diagram, nodes) -> None:
    import networkx as nx

    G = nx.DiGraph()
    for n in nodes:
        G.add_node(n.id)
    for e in diagram.edges:
        G.add_edge(e.source.id, e.target.id)

    node_map = {n.id: n for n in nodes}

    try:
        generations = list(nx.topological_generations(G))
        for col, gen in enumerate(generations):
            x = PADDING + col * (NODE_W + H_GAP)
            for row, nid in enumerate(sorted(gen)):
                node_map[nid].x = float(x)
                node_map[nid].y = float(PADDING + row * (NODE_H + V_GAP))
    except nx.NetworkXUnfeasible:
        _spring_layout(G, nodes, node_map)


def _spring_layout(G, nodes, node_map) -> None:
    import networkx as nx

    pos = nx.spring_layout(G, seed=42, k=2.5)
    if not pos:
        return

    xs = [p[0] for p in pos.values()]
    ys = [p[1] for p in pos.values()]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    rng_x = max(max_x - min_x, 0.1)
    rng_y = max(max_y - min_y, 0.1)

    target_w = len(nodes) * (NODE_W + H_GAP) * 0.6
    target_h = max(300.0, target_w * 0.55)

    for nid, (px, py) in pos.items():
        node = node_map.get(nid)
        if node:
            node.x = float(PADDING + (px - min_x) / rng_x * target_w)
            node.y = float(PADDING + (py - min_y) / rng_y * target_h)


def _grid_layout(nodes) -> None:
    cols = max(1, math.ceil(math.sqrt(len(nodes))))
    for i, node in enumerate(nodes):
        node.x = float(PADDING + (i % cols) * (NODE_W + H_GAP))
        node.y = float(PADDING + (i // cols) * (NODE_H + V_GAP))
