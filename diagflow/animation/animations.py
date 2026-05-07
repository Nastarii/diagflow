from dataclasses import dataclass, field
from typing import List, Any


@dataclass
class FadeIn:
    target: str
    at: float = 0.0

    def to_dict(self) -> dict:
        return {"type": "fade_in", "target": self.target, "at": self.at}


@dataclass
class FadeOut:
    target: str
    at: float = 0.0

    def to_dict(self) -> dict:
        return {"type": "fade_out", "target": self.target, "at": self.at}


@dataclass
class ScaleIn:
    target: str
    at: float = 0.0
    from_scale: float = 0.5

    def to_dict(self) -> dict:
        return {
            "type": "scale_in",
            "target": self.target,
            "at": self.at,
            "from_scale": self.from_scale,
        }


@dataclass
class Pulse:
    target: str
    at: float = 0.0
    scale: float = 1.15
    duration: float = 0.6

    def to_dict(self) -> dict:
        return {
            "type": "pulse",
            "target": self.target,
            "at": self.at,
            "scale": self.scale,
            "duration": self.duration,
        }


@dataclass
class Highlight:
    target: str
    color: str = "#fbbf24"
    at: float = 0.0
    duration: float = 1.0

    def to_dict(self) -> dict:
        return {
            "type": "highlight",
            "target": self.target,
            "color": self.color,
            "at": self.at,
            "duration": self.duration,
        }


@dataclass
class SendMessage:
    from_id: str
    to_id: str
    label: str = ""
    at: float = 0.0

    def to_dict(self) -> dict:
        return {
            "type": "send_message",
            "from": self.from_id,
            "to": self.to_id,
            "label": self.label,
            "at": self.at,
        }


@dataclass
class Step:
    title: str
    animations: List[Any] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "animations": [a.to_dict() for a in self.animations if a is not None],
        }
