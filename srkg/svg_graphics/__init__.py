"""Shared SVG machinery; domain creators load only through their providers."""

__all__ = ["IMPLEMENTED_NODE_IDS", "create_svg_graphic", "save_svg_graphics"]


def __getattr__(name):
    if name in __all__:
        from srkg.svg_graphics import registry
        return getattr(registry, name)
    raise AttributeError(name)
