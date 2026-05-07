from dataclasses import dataclass


@dataclass
class NodeLayout:
    """Visual layout preset for nodes."""
    name: str = "default"
    fill_is_white: bool = False
    fill_opacity: float = 0.18
    stroke_opacity: float = 0.7
    stroke_width: float = 1.5
    rx: int = 10
    has_inner_highlight: bool = True
    use_gradient: bool = False
    hover_scale: float = 1.04
    hover_glow: bool = False


_PRESETS: dict[str, NodeLayout] = {
    "default": NodeLayout(),

    "glass": NodeLayout(
        name="glass",
        fill_is_white=True,
        fill_opacity=0.08,
        stroke_opacity=0.35,
        stroke_width=1.0,
        rx=14,
        has_inner_highlight=True,
        hover_scale=1.06,
        hover_glow=True,
    ),

    "minimal": NodeLayout(
        name="minimal",
        fill_opacity=1.0,
        stroke_opacity=0.0,
        stroke_width=0.0,
        rx=6,
        has_inner_highlight=False,
        hover_scale=1.03,
        hover_glow=False,
    ),

    "material": NodeLayout(
        name="material",
        fill_opacity=0.92,
        stroke_opacity=0.0,
        stroke_width=0.0,
        rx=8,
        has_inner_highlight=False,
        hover_scale=1.03,
        hover_glow=False,
    ),

    "gradient": NodeLayout(
        name="gradient",
        fill_opacity=1.0,
        stroke_opacity=0.3,
        stroke_width=1.0,
        rx=12,
        has_inner_highlight=True,
        use_gradient=True,
        hover_scale=1.04,
        hover_glow=True,
    ),
}


def get_layout(name: str) -> NodeLayout:
    return _PRESETS.get(name, _PRESETS["default"])


def glass() -> NodeLayout:
    return _PRESETS["glass"]


def minimal() -> NodeLayout:
    return _PRESETS["minimal"]


def material() -> NodeLayout:
    return _PRESETS["material"]


def gradient_layout() -> NodeLayout:
    return _PRESETS["gradient"]
