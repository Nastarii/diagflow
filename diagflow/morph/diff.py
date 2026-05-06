"""
GraphDiff: semantic difference between two diagram states.

NodeChange.kind:
  "persist"  – same node (same or very similar), may have moved / changed style
  "modify"   – persistent, but label or color differs
  "add"      – only in D2
  "remove"   – only in D1

EdgeChange.kind:
  "persist"  – same logical connection
  "redirect" – same nodes, different source/target swap (shouldn't happen often)
  "add"      – only in D2
  "remove"   – only in D1
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from diagflow.core.diagram import Diagram
    from diagflow.core.node import Node
    from diagflow.core.edge import Edge


NodeKind = Literal["persist", "modify", "add", "remove"]
EdgeKind = Literal["persist", "redirect", "add", "remove"]


@dataclass
class NodeChange:
    kind: NodeKind
    d1: Optional["Node"] = None
    d2: Optional["Node"] = None
    score: float = 1.0

    @property
    def is_modified(self) -> bool:
        if self.d1 is None or self.d2 is None:
            return False
        return self.d1.label != self.d2.label or self.d1.color != self.d2.color


@dataclass
class EdgeChange:
    kind: EdgeKind
    d1: Optional["Edge"] = None
    d2: Optional["Edge"] = None


@dataclass
class GraphDiff:
    node_changes: list[NodeChange] = field(default_factory=list)
    edge_changes: list[EdgeChange] = field(default_factory=list)
    id_map:  dict[str, str] = field(default_factory=dict)  # d1_id → d2_id
    inv_map: dict[str, str] = field(default_factory=dict)  # d2_id → d1_id

    # ── convenience filters ───────────────────────────────────────────────────

    @property
    def persisted_nodes(self) -> list[NodeChange]:
        return [c for c in self.node_changes if c.kind in ("persist", "modify")]

    @property
    def removed_nodes(self) -> list[NodeChange]:
        return [c for c in self.node_changes if c.kind == "remove"]

    @property
    def added_nodes(self) -> list[NodeChange]:
        return [c for c in self.node_changes if c.kind == "add"]

    @property
    def persisted_edges(self) -> list[EdgeChange]:
        return [c for c in self.edge_changes if c.kind in ("persist", "redirect")]

    @property
    def removed_edges(self) -> list[EdgeChange]:
        return [c for c in self.edge_changes if c.kind == "remove"]

    @property
    def added_edges(self) -> list[EdgeChange]:
        return [c for c in self.edge_changes if c.kind == "add"]

    def summary(self) -> str:
        return (
            f"nodes  persist:{len(self.persisted_nodes)}  "
            f"add:{len(self.added_nodes)}  remove:{len(self.removed_nodes)}\n"
            f"edges  persist:{len(self.persisted_edges)}  "
            f"add:{len(self.added_edges)}  remove:{len(self.removed_edges)}"
        )


# ── factory ───────────────────────────────────────────────────────────────────

def compute_diff(
    d1: "Diagram",
    d2: "Diagram",
    match_by: str = "auto",
    threshold: float = 0.30,
) -> GraphDiff:
    """Compute a semantic GraphDiff between two laid-out diagrams."""
    from diagflow.morph.matcher import match_nodes, match_edges

    nodes1 = list(d1.nodes.values())
    nodes2 = list(d2.nodes.values())

    matches, matched1_ids, matched2_ids = match_nodes(
        nodes1, nodes2, d1.edges, d2.edges, threshold=threshold
    )

    id_map  = {m.d1.id: m.d2.id for m in matches}
    inv_map = {m.d2.id: m.d1.id for m in matches}

    node_changes: list[NodeChange] = []

    for m in matches:
        changed = (m.d1.label != m.d2.label) or (m.d1.color != m.d2.color)
        kind: NodeKind = "modify" if changed else "persist"
        node_changes.append(NodeChange(kind=kind, d1=m.d1, d2=m.d2, score=m.score))

    for n in nodes1:
        if n.id not in matched1_ids:
            node_changes.append(NodeChange(kind="remove", d1=n))

    for n in nodes2:
        if n.id not in matched2_ids:
            node_changes.append(NodeChange(kind="add", d2=n))

    # ── edges ─────────────────────────────────────────────────────────────────
    persist_pairs, matched_e1, matched_e2 = match_edges(d1.edges, d2.edges, id_map)

    edge_changes: list[EdgeChange] = []

    for e1, e2 in persist_pairs:
        edge_changes.append(EdgeChange(kind="persist", d1=e1, d2=e2))

    for e in d1.edges:
        if e.id not in matched_e1:
            edge_changes.append(EdgeChange(kind="remove", d1=e))

    for e in d2.edges:
        if e.id not in matched_e2:
            edge_changes.append(EdgeChange(kind="add", d2=e))

    return GraphDiff(
        node_changes=node_changes,
        edge_changes=edge_changes,
        id_map=id_map,
        inv_map=inv_map,
    )
