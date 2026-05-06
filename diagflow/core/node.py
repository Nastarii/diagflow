from dataclasses import dataclass, field
from typing import Optional
import uuid


def _nid() -> str:
    return f"n_{uuid.uuid4().hex[:8]}"


PALETTE = [
    "#4299e1", "#48bb78", "#ed8936", "#9f7aea",
    "#f56565", "#38b2ac", "#ed64a6", "#ecc94b",
]


@dataclass
class Node:
    label: str
    id: str = field(default_factory=_nid)
    color: Optional[str] = None
    shape: str = "rect"
    x: float = 0.0
    y: float = 0.0

    def fade_in(self, at: float = 0.0):
        from diagflow.animation.animations import FadeIn
        return FadeIn(target=self.id, at=at)

    def appear(self, at: float = 0.0):
        return self.fade_in(at=at)

    def highlight(self, color: str = "#fbbf24", at: float = 0.0, duration: float = 1.0):
        from diagflow.animation.animations import Highlight
        return Highlight(target=self.id, color=color, at=at, duration=duration)

    def send(self, message: str, to: "Node", at: float = 0.0):
        from diagflow.animation.animations import SendMessage
        return SendMessage(from_id=self.id, to_id=to.id, label=message, at=at)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "label": self.label,
            "x": self.x,
            "y": self.y,
            "color": self.color or "#4299e1",
            "shape": self.shape,
        }
