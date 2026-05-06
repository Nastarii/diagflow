from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING
import uuid

if TYPE_CHECKING:
    from diagflow.core.node import Node


def _eid() -> str:
    return f"e_{uuid.uuid4().hex[:8]}"


@dataclass
class Edge:
    source: "Node"
    target: "Node"
    label: Optional[str] = None
    id: str = field(default_factory=_eid)
    style: str = "solid"  # solid | dashed

    def fade_in(self, at: float = 0.0):
        from diagflow.animation.animations import FadeIn
        return FadeIn(target=self.id, at=at)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "source": self.source.id,
            "target": self.target.id,
            "label": self.label,
            "style": self.style,
        }
