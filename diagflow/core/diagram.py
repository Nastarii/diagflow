from typing import List, Optional, Union
from diagflow.core.node import Node, PALETTE
from diagflow.core.edge import Edge
from diagflow.animation.animations import Step, FadeIn


class _StepCtx:
    def __init__(self, step: Step, diagram: "Diagram"):
        self._step = step
        self._diagram = diagram

    def __enter__(self) -> Step:
        self._diagram._current_step = self._step
        return self._step

    def __exit__(self, *_):
        self._diagram._current_step = None


class Diagram:
    def __init__(self, title: str = ""):
        self.title = title
        self.nodes: dict[str, Node] = {}
        self.edges: List[Edge] = []
        self.steps: List[Step] = []
        self._current_step: Optional[Step] = None
        self._color_idx = 0

    def __enter__(self):
        return self

    def __exit__(self, *_):
        pass

    # ── internals ─────────────────────────────────────────────────────────────

    def _next_color(self) -> str:
        color = PALETTE[self._color_idx % len(PALETTE)]
        self._color_idx += 1
        return color

    def _register_node(self, node: Node) -> Node:
        if node.color is None:
            node.color = self._next_color()
        self.nodes.setdefault(node.id, node)
        return node

    def _active_step(self) -> Step:
        if self._current_step:
            return self._current_step
        if not self.steps:
            self.steps.append(Step(""))
        return self.steps[-1]

    # ── public API ─────────────────────────────────────────────────────────────

    def add(self, *elements) -> "Diagram":
        """Add nodes/edges. Inside a step(), auto-registers FadeIn."""
        for el in elements:
            if isinstance(el, Node):
                self._register_node(el)
                if self._current_step is not None:
                    self._current_step.animations.append(FadeIn(target=el.id))
            elif isinstance(el, Edge):
                self._register_node(el.source)
                self._register_node(el.target)
                self.edges.append(el)
                if self._current_step is not None:
                    self._current_step.animations.append(FadeIn(target=el.id))
        return self

    def connect(
        self,
        source: Node,
        target: Node,
        label: Optional[str] = None,
        style: str = "solid",
    ) -> Edge:
        """Create an edge between two nodes."""
        self._register_node(source)
        self._register_node(target)
        edge = Edge(source=source, target=target, label=label, style=style)
        self.edges.append(edge)
        if self._current_step is not None:
            self._current_step.animations.append(FadeIn(target=edge.id))
        return edge

    def step(self, title: str = "") -> _StepCtx:
        """Context manager for a presentation step/slide."""
        s = Step(title)
        self.steps.append(s)
        return _StepCtx(s, self)

    def animate(self, *animations) -> "Diagram":
        """Append animations to the active step (or auto-creates one)."""
        active = self._active_step()
        for a in animations:
            if a is not None:
                active.animations.append(a)
        return self

    def show(self, *elements, at: float = 0.0) -> "Diagram":
        """Convenience: fade-in a list of nodes/edges."""
        active = self._active_step()
        for el in elements:
            active.animations.append(FadeIn(target=el.id, at=at))
        return self

    def theme(self, config: dict) -> "Diagram":
        self._theme = config
        return self

    def export(self, path: str = "output.html") -> str:
        from diagflow.layout.auto_layout import apply_layout
        from diagflow.export.html_renderer import render_html

        # Auto-generate a single step if none defined
        if not self.steps:
            s = Step("Overview")
            for i, node in enumerate(self.nodes.values()):
                s.animations.append(FadeIn(target=node.id, at=round(i * 0.2, 2)))
            for i, edge in enumerate(self.edges):
                s.animations.append(
                    FadeIn(target=edge.id, at=round(len(self.nodes) * 0.2 + i * 0.15, 2))
                )
            self.steps.append(s)

        apply_layout(self)
        html = render_html(self)

        with open(path, "w", encoding="utf-8") as f:
            f.write(html)

        print(f"Exported: {path}")
        return path

    def transition_to(
        self,
        other: "Diagram",
        duration:  float = 1.5,
        stagger:   float = 0.08,
        easing:    str   = "power2.inOut",
        match_by:  str   = "auto",
        threshold: float = 0.30,
    ) -> "Morph":  # noqa: F821
        """Return a Morph object that animates self → other."""
        from diagflow.morph.morph_engine import Morph
        return Morph(
            self, other,
            duration=duration,
            stagger=stagger,
            easing=easing,
            match_by=match_by,
            threshold=threshold,
        )
