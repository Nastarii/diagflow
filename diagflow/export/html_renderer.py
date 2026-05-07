import json
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from diagflow.core.diagram import Diagram

from diagflow.core.node import NODE_W, NODE_H

PADDING = 60
CP = 50  # bezier control-point offset

_TPL = Path(__file__).parent / "templates" / "diagram.html.j2"


def render_html(diagram: "Diagram") -> str:
    from jinja2 import Template

    nodes = list(diagram.nodes.values())
    edges = diagram.edges

    max_x = max((n.x for n in nodes), default=0) + NODE_W + PADDING
    max_y = max((n.y + n.height for n in nodes), default=0) + PADDING

    node_map = {n.id: n for n in nodes}
    edge_data = []
    for e in edges:
        src = node_map.get(e.source.id)
        tgt = node_map.get(e.target.id)
        if src and tgt:
            path_d, x1, y1, x2, y2 = _bezier(src, tgt)
            edge_data.append({
                "id": e.id,
                "path_d": path_d,
                "label": e.label,
                "mid_x": (x1 + x2) / 2,
                "mid_y": (y1 + y2) / 2 - 14,
                "style": e.style,
                "x1": x1, "y1": y1,
                "x2": x2, "y2": y2,
            })

    diagram_data = {
        "title": diagram.title,
        "nodes": [n.to_dict() for n in nodes],
        "edges": [e.to_dict() for e in edges],
        "steps": [s.to_dict() for s in diagram.steps],
        "node_w": NODE_W,
        "node_h": NODE_H,
    }

    tpl = Template(_TPL.read_text(encoding="utf-8"))
    return tpl.render(
        title=diagram.title or "Diagflow",
        width=int(max_x),
        height=int(max_y),
        nodes=nodes,
        edges=edge_data,
        steps=diagram.steps,
        NODE_W=NODE_W,
        NODE_H=NODE_H,
        diagram_json=json.dumps(diagram_data),
    )


def _bezier(src, tgt) -> tuple[str, float, float, float, float]:
    """Return (svg path_d, x1, y1, x2, y2) for a bezier edge."""
    src_h = getattr(src, 'height', NODE_H)
    tgt_h = getattr(tgt, 'height', NODE_H)

    dx = tgt.x - src.x
    dy = tgt.y - src.y

    if abs(dx) >= abs(dy):
        if dx >= 0:
            x1, y1 = src.x + NODE_W, src.y + src_h / 2
            x2, y2 = tgt.x, tgt.y + tgt_h / 2
            cx1, cy1 = x1 + CP, y1
            cx2, cy2 = x2 - CP, y2
        else:
            x1, y1 = src.x, src.y + src_h / 2
            x2, y2 = tgt.x + NODE_W, tgt.y + tgt_h / 2
            cx1, cy1 = x1 - CP, y1
            cx2, cy2 = x2 + CP, y2
    else:
        if dy >= 0:
            x1, y1 = src.x + NODE_W / 2, src.y + src_h
            x2, y2 = tgt.x + NODE_W / 2, tgt.y
            cx1, cy1 = x1, y1 + CP
            cx2, cy2 = x2, y2 - CP
        else:
            x1, y1 = src.x + NODE_W / 2, src.y
            x2, y2 = tgt.x + NODE_W / 2, tgt.y + tgt_h
            cx1, cy1 = x1, y1 - CP
            cx2, cy2 = x2, y2 + CP

    d = f"M {x1:.1f} {y1:.1f} C {cx1:.1f} {cy1:.1f} {cx2:.1f} {cy2:.1f} {x2:.1f} {y2:.1f}"
    return d, x1, y1, x2, y2
