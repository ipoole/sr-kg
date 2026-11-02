"""Load explicit domain-local graphics providers without a central subject list."""
from dataclasses import dataclass
from functools import lru_cache
import hashlib
import importlib
from pathlib import Path
import re
import sys
from types import ModuleType

from srkg.schema import KnowledgeBaseLoadError


@dataclass(frozen=True)
class GraphicsRegistry:
    concepts: dict
    modules: dict

    def concept(self, concept_id, variant="icon"):
        creator = self.concepts.get(str(concept_id).strip())
        return creator(variant) if creator else None

    def module(self, module_id, variant="icon"):
        creator = self.modules.get(str(module_id).strip())
        return creator(variant) if creator else None


def collect_graphics(packages) -> GraphicsRegistry:
    concepts, modules = {}, {}
    for package in packages:
        if not package.graphics:
            continue
        if not re.fullmatch(r"[a-zA-Z_]\w*(?:\.[a-zA-Z_]\w*)*", package.graphics):
            raise KnowledgeBaseLoadError(f"{package.root}/domain.yaml: invalid graphics module")
        # Isolated namespace per directory supports relative provider imports,
        # including temporary/external packages, without modifying sys.path.
        namespace = "_kg_domain_" + hashlib.sha256(str(package.root.resolve()).encode()).hexdigest()[:20]
        if namespace not in sys.modules:
            module = ModuleType(namespace)
            module.__path__ = [str(package.root.resolve())]
            sys.modules[namespace] = module
        try:
            provider = importlib.import_module(namespace + "." + package.graphics)
        except Exception as exc:
            raise KnowledgeBaseLoadError(f"{package.root}: could not load graphics provider: {exc}") from exc
        for attribute, registry in (("CONCEPT_CREATORS", concepts), ("MODULE_CREATORS", modules)):
            creators = getattr(provider, attribute, {})
            if not isinstance(creators, dict) or any(not isinstance(key, str) or not callable(value) for key, value in creators.items()):
                raise KnowledgeBaseLoadError(f"{package.root}: invalid {attribute} registry")
            duplicate = registry.keys() & creators.keys()
            if duplicate:
                raise KnowledgeBaseLoadError(f"{package.root}: duplicate graphic IDs: {', '.join(sorted(duplicate))}")
            registry.update(creators)
    return GraphicsRegistry(concepts, modules)


@lru_cache(maxsize=1)
def default_graphics() -> GraphicsRegistry:
    """Public compatibility APIs use the repository's discovered collection."""
    from srkg.kb import resolve_knowledge_base_paths
    from srkg.domain_sources import discover_domains
    paths = resolve_knowledge_base_paths(Path(__file__).resolve().parents[1] / "data")
    return collect_graphics(discover_domains(paths))
