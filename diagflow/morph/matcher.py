"""
Bipartite matching between nodes/edges of two diagram states.

Priority order:
  1. Exact ID match           → score 1.0
  2. Label similarity (SequenceMatcher) → score * 0.85  (cap below exact ID)
  3. Structural similarity bonus on top of label score
"""
from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from diagflow.core.node import Node
    from diagflow.core.edge import Edge


@dataclass
class NodeMatch:
    d1: "Node"
    d2: "Node"
    score: float
    method: str  # "id" | "label" | "structural"


# ── scoring ───────────────────────────────────────────────────────────────────

def _label_sim(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower().strip(), b.lower().strip()).ratio()


def _structural_bonus(
    n1: "Node",
    n2: "Node",
    edges1: list["Edge"],
    edges2: list["Edge"],
    label_map1: dict[str, str],
    label_map2: dict[str, str],
) -> float:
    """
    Jaccard similarity between the sets of neighbor *labels* in each diagram.
    Using labels avoids the ID-mismatch problem across independent diagrams.
    """
    def neighbor_labels(node_id: str, edges: list["Edge"], label_map: dict[str, str]) -> set[str]:
        out = set()
        for e in edges:
            if e.source.id == node_id:
                out.add(label_map.get(e.target.id, ""))
            elif e.target.id == node_id:
                out.add(label_map.get(e.source.id, ""))
        return out - {""}

    nb1 = neighbor_labels(n1.id, edges1, label_map1)
    nb2 = neighbor_labels(n2.id, edges2, label_map2)

    if not nb1 and not nb2:
        return 0.1  # both isolated — small bonus
    if not nb1 or not nb2:
        return 0.0
    return len(nb1 & nb2) / len(nb1 | nb2)


def _node_score(
    n1: "Node",
    n2: "Node",
    edges1: list["Edge"],
    edges2: list["Edge"],
    label_map1: dict[str, str],
    label_map2: dict[str, str],
) -> tuple[float, str]:
    if n1.id == n2.id:
        return 1.0, "id"

    ls = _label_sim(n1.label, n2.label)
    sb = _structural_bonus(n1, n2, edges1, edges2, label_map1, label_map2)

    # Weighted combination; cap at 0.85 so ID match always wins
    score = min(0.85, ls * 0.70 + sb * 0.15)
    method = "label" if ls >= sb else "structural"
    return score, method


# ── public API ────────────────────────────────────────────────────────────────

def match_nodes(
    nodes1: list["Node"],
    nodes2: list["Node"],
    edges1: list["Edge"],
    edges2: list["Edge"],
    threshold: float = 0.30,
) -> tuple[list[NodeMatch], set[str], set[str]]:
    """
    Greedy bipartite matching (highest-score-first).

    Returns:
        matches        – list of NodeMatch pairs
        matched1_ids   – D1 node IDs that were matched
        matched2_ids   – D2 node IDs that were matched
    """
    label_map1 = {n.id: n.label for n in nodes1}
    label_map2 = {n.id: n.label for n in nodes2}

    candidates: list[NodeMatch] = []
    for n1 in nodes1:
        for n2 in nodes2:
            score, method = _node_score(n1, n2, edges1, edges2, label_map1, label_map2)
            if score >= threshold:
                candidates.append(NodeMatch(d1=n1, d2=n2, score=score, method=method))

    candidates.sort(key=lambda c: c.score, reverse=True)

    matched1: set[str] = set()
    matched2: set[str] = set()
    matches:  list[NodeMatch] = []

    for c in candidates:
        if c.d1.id not in matched1 and c.d2.id not in matched2:
            matches.append(c)
            matched1.add(c.d1.id)
            matched2.add(c.d2.id)

    return matches, matched1, matched2


def match_edges(
    edges1: list["Edge"],
    edges2: list["Edge"],
    id_map: dict[str, str],  # d1_node_id → d2_node_id
) -> tuple[list[tuple["Edge", "Edge"]], set[str], set[str]]:
    """
    Match edges based on their (matched) endpoint pairs.
    An edge pair is "persistent" when both src and tgt were matched between D1/D2.

    Returns:
        persist_pairs  – [(d1_edge, d2_edge), ...]
        matched_e1_ids – D1 edge IDs that were matched
        matched_e2_ids – D2 edge IDs that were matched
    """
    persist: list[tuple["Edge", "Edge"]] = []
    matched_e1: set[str] = set()
    matched_e2: set[str] = set()

    # Build a lookup: (d2_src_id, d2_tgt_id) → d2_edge
    d2_lookup: dict[tuple[str, str], "Edge"] = {}
    for e2 in edges2:
        d2_lookup[(e2.source.id, e2.target.id)] = e2

    for e1 in edges1:
        src_d2 = id_map.get(e1.source.id)
        tgt_d2 = id_map.get(e1.target.id)
        if src_d2 is None or tgt_d2 is None:
            continue
        e2 = d2_lookup.get((src_d2, tgt_d2))
        if e2 is not None and e2.id not in matched_e2:
            persist.append((e1, e2))
            matched_e1.add(e1.id)
            matched_e2.add(e2.id)

    return persist, matched_e1, matched_e2
