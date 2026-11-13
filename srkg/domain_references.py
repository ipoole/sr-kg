"""Semantic namespaces and diagnostics for selected-domain references."""
import re
from dataclasses import dataclass

from srkg.schema import KnowledgeBaseLoadError


def domain_namespace(semantic_id: str, location: str = "") -> str:
    """The first dotted component is the owning domain, independently of loading."""
    value = str(semantic_id).strip()
    namespace, separator, local_id = value.partition(".")
    if not separator or not local_id or not re.fullmatch(r"[a-z][a-z0-9_]*", namespace) or any(char.isspace() for char in value):
        raise KnowledgeBaseLoadError(f"{location}: invalid namespaced semantic ID {value!r}")
    return namespace


@dataclass(frozen=True)
class BuildWarning:
    kind: str
    domain: str
    target: str
    location: str
    source: str = ""


class ReferenceResolver:
    """Resolve only loaded namespaces; never inspect other source packages."""
    def __init__(self, domains, concepts, modules, blocks=()):
        self.domains = set(domains)
        self.known = {"concept": set(concepts), "module": set(modules)}
        self.known["prose"] = self.known["concept"] | set(blocks)
        self.warnings: list[BuildWarning] = []

    def available(self, target, *, target_type="concept", kind, location, source=""):
        target = str(target).strip()
        namespace = domain_namespace(target, location)
        if namespace not in self.domains:
            self.warnings.append(BuildWarning(kind, namespace, target, location, source))
            return False
        if target not in self.known[target_type]:
            raise KnowledgeBaseLoadError(f"{location}: {target} is unresolved within loaded domain {namespace}")
        return True


def format_build_warnings(warnings, *, example_limit=2) -> str:
    """Summarise external namespaces without flooding generator output."""
    warnings = tuple(warnings)
    if not warnings:
        return ""
    domains = sorted({warning.domain for warning in warnings})
    lines = ["Warning: missing domains referenced by selected content: " + ", ".join(domains)]
    descriptions = {"edge": ("omitted edge", "omitted edges"),
                    "module-support": ("omitted support link", "omitted support links"),
                    "prose-reference": ("unlinked prose reference", "unlinked prose references"),
                    "content-reference": ("unavailable shared explanation", "unavailable shared explanations"),
                    "tutorial": ("omitted tutorial", "omitted tutorials")}
    for domain in domains:
        entries = [warning for warning in warnings if warning.domain == domain]
        counts = {}
        for warning in entries:
            key = (warning.source or warning.location) if warning.kind == "tutorial" else None
            counts.setdefault(warning.kind, []).append(key)
        summary = []
        for kind, values in counts.items():
            count = len(set(values)) if kind == "tutorial" else len(values)
            description = descriptions.get(kind, (kind, kind))[0 if count == 1 else 1]
            summary.append(f"{count} {description}")
        lines.append(f"  {domain}: " + "; ".join(summary))
        examples = list(dict.fromkeys((warning.target, warning.location) for warning in entries))
        for target, location in examples[:example_limit]:
            lines.append(f"    {location}: {target}")
        if len(examples) > example_limit:
            lines.append(f"    ... {len(examples) - example_limit} further locations/targets")
    return "\n".join(lines)
