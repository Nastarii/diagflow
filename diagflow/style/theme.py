from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Theme:
    primary: str = "#4299e1"
    background: str = "#161b22"
    node_radius: int = 10
    font_size: int = 13
    edge_color: str = "#30363d"
    extra: dict = field(default_factory=dict)

    @classmethod
    def dark(cls) -> "Theme":
        return cls()

    @classmethod
    def light(cls) -> "Theme":
        return cls(background="#ffffff", edge_color="#cbd5e0")
