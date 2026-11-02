"""Shared landscape framing, independent of any subject registry."""
import re


def landscape_svg(module_id: str, module_title: str, source: str, variant: str) -> str:
    """Present the square source motif in a module-specific landscape card."""
    start = source.index(">") + 1
    end = source.rfind("</svg>")
    inner = source[start:end]
    if variant == "detail":
        # Keep one landscape frame rather than the source motif's old square
        # review-card frame nested inside it.
        inner = re.sub(
            r'\s*<rect x="(?:20|26)" y="(?:20|26)"[^>]*stroke="#dbe3f3"[^>]*/>',
            "",
            inner,
            count=1,
        )
    safe_id = module_id.replace(".", "-")
    title = f"{module_title} {variant} graphic"
    frame = (
        '<rect x="2" y="2" width="764" height="476" rx="54" '
        'fill="#fbfcff" stroke="#dbe3f3" stroke-width="4"/>'
        if variant == "detail"
        else '<rect width="768" height="480" fill="#fbfcff"/>'
    )
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="768" height="480" '
        'viewBox="0 0 768 480" role="img" '
        f'aria-labelledby="title-{safe_id}-{variant}">\n'
        f'<title id="title-{safe_id}-{variant}">{title}</title>\n'
        f'{frame}\n'
        '<svg x="144" y="-16" width="480" height="480" viewBox="0 0 512 512" '
        'preserveAspectRatio="xMidYMid meet">\n'
        f'{inner}\n</svg>\n</svg>'
    )
