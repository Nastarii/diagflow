"""
Morph: smooth animated transition between two diagram states.

SVG strategy
------------
The rendered SVG is a "merged canvas" containing ALL elements from D1 ∪ D2:

  • Persistent nodes   – one <g> element, starts at D1 pos, animated to D2 pos
  • Removed nodes      – one <g> element at D1 pos, faded out
  • Added nodes        – one <g> element at D2 pos, starts hidden, fades in
  • D1 edges           – rendered at D1 geometry, faded out during transition
  • D2 edges           – rendered at D2 geometry, start hidden, faded in after move

Because GSAP applies a CSS translate on the <g> element (not changing child
x/y attributes), D2 edge paths — pre-computed with D2 absolute coordinates —
always connect correctly after nodes finish moving.

Timeline phases (fraction of total duration)
----------------------------------------------
  [0.00 → 0.30]  Phase 1: fade-out removed nodes + all D1 edges
  [0.20 → 0.75]  Phase 2: move persistent nodes, optional color/label morph
  [0.65 → 0.90]  Phase 3: fade-in added nodes
  [0.72 → 1.00]  Phase 4: fade-in D2 edges
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from diagflow.core.diagram import Diagram
    from diagflow.morph.diff import GraphDiff

# Phase boundaries as fractions of total duration
_PH = {
    "remove": (0.00, 0.30),
    "move":   (0.20, 0.75),
    "add":    (0.65, 0.90),
    "edges":  (0.72, 1.00),
}


@dataclass
class MorphConfig:
    duration: float = 1.5
    stagger:  float = 0.08
    easing:   str   = "power2.inOut"
    match_by: str   = "auto"
    threshold: float = 0.30


class Morph:
    """Generate a smooth animated HTML morph between two Diagram states."""

    def __init__(
        self,
        d1: "Diagram",
        d2: "Diagram",
        duration:  float = 1.5,
        stagger:   float = 0.08,
        easing:    str   = "power2.inOut",
        match_by:  str   = "auto",
        threshold: float = 0.30,
    ):
        self.d1 = d1
        self.d2 = d2
        self.cfg = MorphConfig(
            duration=duration,
            stagger=stagger,
            easing=easing,
            match_by=match_by,
            threshold=threshold,
        )

    # ── public ────────────────────────────────────────────────────────────────

    def compute(self) -> dict:
        """Build the full data package consumed by the JS morph engine."""
        from diagflow.layout.auto_layout import apply_layout, NODE_W, NODE_H, PADDING
        from diagflow.morph.diff import compute_diff
        from diagflow.export.html_renderer import _bezier

        apply_layout(self.d1)
        apply_layout(self.d2)

        diff = compute_diff(self.d1, self.d2, self.cfg.match_by, self.cfg.threshold)

        merged_nodes = self._build_merged_nodes(diff)
        merged_edges = self._build_merged_edges(diff, _bezier)
        animations   = self._gen_animations(diff, merged_nodes, merged_edges)

        # SVG bounds: encompass all D1 and D2 positions
        all_x = [n["x"] for n in merged_nodes.values()] + \
                [n.get("to_x", n["x"]) for n in merged_nodes.values()]
        all_y = [n["y"] for n in merged_nodes.values()] + \
                [n.get("to_y", n["y"]) for n in merged_nodes.values()]

        svg_w = int(max(all_x, default=400) + NODE_W + PADDING)
        svg_h = int(max(all_y, default=300) + NODE_H + PADDING)

        return {
            "d1_title": self.d1.title,
            "d2_title": self.d2.title,
            "config": {
                "duration": self.cfg.duration,
                "stagger":  self.cfg.stagger,
                "easing":   self.cfg.easing,
            },
            "nodes":      list(merged_nodes.values()),
            "edges":      list(merged_edges.values()),
            "animations": animations,
            "node_w": NODE_W,
            "node_h": NODE_H,
            "svg_w":  svg_w,
            "svg_h":  svg_h,
            "diff_summary": diff.summary(),
        }

    def export(self, path: str = "morph_output.html") -> str:
        from pathlib import Path
        from jinja2 import Template

        data = self.compute()
        tpl_path = Path(__file__).parent.parent / "export" / "templates" / "morph.html.j2"
        tpl  = Template(tpl_path.read_text(encoding="utf-8"))
        html = tpl.render(
            title=f"{self.d1.title} → {self.d2.title}",
            morph_json=json.dumps(data),
            **data,
        )
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)

        print(f"Exported morph: {path}")
        print(f"  {data['diff_summary']}")
        return path

    # ── builders ──────────────────────────────────────────────────────────────

    def _build_merged_nodes(self, diff: "GraphDiff") -> dict[str, dict]:
        nodes: dict[str, dict] = {}

        for nc in diff.persisted_nodes:
            nodes[nc.d1.id] = {
                "id":       nc.d1.id,
                "label":    nc.d1.label,
                "x":        nc.d1.x,
                "y":        nc.d1.y,
                "color":    nc.d1.color,
                "role":     "persist",
                "to_x":     nc.d2.x,
                "to_y":     nc.d2.y,
                "to_label": nc.d2.label,
                "to_color": nc.d2.color,
            }

        for nc in diff.removed_nodes:
            nodes[nc.d1.id] = {
                "id":    nc.d1.id,
                "label": nc.d1.label,
                "x":     nc.d1.x,
                "y":     nc.d1.y,
                "color": nc.d1.color,
                "role":  "remove",
            }

        for nc in diff.added_nodes:
            nodes[nc.d2.id] = {
                "id":    nc.d2.id,
                "label": nc.d2.label,
                "x":     nc.d2.x,
                "y":     nc.d2.y,
                "color": nc.d2.color,
                "role":  "add",
            }

        return nodes

    def _build_merged_edges(self, diff: "GraphDiff", bezier_fn) -> dict[str, dict]:
        """
        All D1 edges get role "d1_edge" (start visible, fade out).
        All D2 edges get role "d2_edge" (start hidden, fade in).
        Paths use absolute D1/D2 coordinates, so they connect correctly.
        """
        edges: dict[str, dict] = {}

        # D1 edges (all of them: removed + persist source side)
        for ec in diff.edge_changes:
            if ec.d1 is not None:
                src = self.d1.nodes.get(ec.d1.source.id)
                tgt = self.d1.nodes.get(ec.d1.target.id)
                if src and tgt:
                    path_d, x1, y1, x2, y2 = bezier_fn(src, tgt)
                    eid = f"d1_{ec.d1.id}"
                    edges[eid] = {
                        "id":     eid,
                        "path_d": path_d,
                        "label":  ec.d1.label,
                        "style":  ec.d1.style,
                        "role":   "d1_edge",
                    }

        # D2 edges — path computed at D2 node positions
        for ec in diff.edge_changes:
            if ec.d2 is not None:
                src = self.d2.nodes.get(ec.d2.source.id)
                tgt = self.d2.nodes.get(ec.d2.target.id)
                if src and tgt:
                    path_d, x1, y1, x2, y2 = bezier_fn(src, tgt)
                    eid = f"d2_{ec.d2.id}"
                    edges[eid] = {
                        "id":     eid,
                        "path_d": path_d,
                        "label":  ec.d2.label,
                        "style":  ec.d2.style,
                        "role":   "d2_edge",
                    }

        return edges

    def _gen_animations(
        self,
        diff: "GraphDiff",
        merged_nodes: dict[str, dict],
        merged_edges: dict[str, dict],
    ) -> list[dict]:
        D  = self.cfg.duration
        S  = self.cfg.stagger
        ea = self.cfg.easing
        anims: list[dict] = []

        def phase(key: str) -> tuple[float, float]:
            lo, hi = _PH[key]
            return lo * D, hi * D

        # ── Phase 1: remove nodes + all D1 edges ──────────────────────────────
        t0, t1 = phase("remove")
        dur = (t1 - t0) * 0.60

        for i, nc in enumerate(diff.removed_nodes):
            anims.append({
                "type": "fade_node",
                "id":   nc.d1.id,
                "to_opacity": 0,
                "scale": 0.75,
                "at":   round(t0 + i * S, 3),
                "dur":  round(dur, 3),
                "ease": "power2.in",
            })

        edge_fade_dur = 0.22
        t0e, _ = phase("move")
        for i, e in enumerate(merged_edges.values()):
            if e["role"] == "d1_edge":
                anims.append({
                    "type": "fade_edge",
                    "id":   e["id"],
                    "to_opacity": 0,
                    "at":  round(t0 + i * S * 0.3, 3),
                    "dur": edge_fade_dur,
                })

        # ── Phase 2: move persistent nodes ────────────────────────────────────
        t0, t1 = phase("move")
        move_dur = (t1 - t0) * 0.75

        for i, nc in enumerate(diff.persisted_nodes):
            n = merged_nodes[nc.d1.id]
            dx = round(n["to_x"] - n["x"], 2)
            dy = round(n["to_y"] - n["y"], 2)
            label_changed = n["to_label"] != n["label"]
            color_changed = n["to_color"] != n["color"]

            # Skip entirely if there is truly nothing to animate
            if dx == 0 and dy == 0 and not label_changed and not color_changed:
                continue

            anim: dict = {
                "type": "move_node",
                "id":   nc.d1.id,
                "dx":   dx,
                "dy":   dy,
                "at":   round(t0 + i * S * 0.35, 3),
                "dur":  round(move_dur, 3),
                "ease": ea,
            }
            if label_changed:
                anim["to_label"] = n["to_label"]
            if color_changed:
                anim["to_color"] = n["to_color"]
            anims.append(anim)

        # ── Phase 3: add new nodes ─────────────────────────────────────────────
        t0, t1 = phase("add")
        add_dur = (t1 - t0) * 0.65

        for i, nc in enumerate(diff.added_nodes):
            anims.append({
                "type": "add_node",
                "id":   nc.d2.id,
                "at":   round(t0 + i * S, 3),
                "dur":  round(add_dur, 3),
            })

        # ── Phase 4: D2 edges ──────────────────────────────────────────────────
        t0, _ = phase("edges")

        for i, e in enumerate(merged_edges.values()):
            if e["role"] == "d2_edge":
                anims.append({
                    "type": "fade_edge",
                    "id":   e["id"],
                    "to_opacity": 1,
                    "at":  round(t0 + i * S * 0.4, 3),
                    "dur": 0.30,
                })

        # Sort by start time for clarity
        anims.sort(key=lambda a: a["at"])
        return anims
