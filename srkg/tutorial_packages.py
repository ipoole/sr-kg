"""Install a reviewed text-only tutorial export as ordinary authored YAML."""
from __future__ import annotations

import json
from pathlib import Path
from tempfile import NamedTemporaryFile
from zipfile import BadZipFile, ZipFile

import yaml

from srkg.kb import load_knowledge_base
from srkg.tutorials import TutorialLoadError, load_tutorials

MAX_PACKAGE_BYTES = 10 * 1024 * 1024


def read_tutorial_package(path: Path) -> dict:
    if path.stat().st_size > MAX_PACKAGE_BYTES:
        raise TutorialLoadError("Tutorial package exceeds 10 MB")
    try:
        if path.suffix.lower() == ".zip":
            with ZipFile(path) as archive:
                names = archive.namelist()
                if sorted(names) != ["manifest.json", "tutorial.json"] or sum(info.file_size for info in archive.infolist()) > MAX_PACKAGE_BYTES:
                    raise TutorialLoadError("Expected a text-only tutorial package")
                manifest = json.loads(archive.read("manifest.json"))
                if manifest.get("format") != "physicskg-tutorial" or manifest.get("schema_version") != 1 or manifest.get("route_schema_version") != 1 or manifest.get("assets") != []:
                    raise TutorialLoadError("Unsupported tutorial manifest or audio assets")
                document = json.loads(archive.read("tutorial.json"))
        else:
            document = json.loads(path.read_text(encoding="utf-8-sig"))
        if document.get("format") != "physicskg-tutorial" or document.get("schema_version") != 1 or document.get("route_schema_version") != 1:
            raise TutorialLoadError("Unsupported tutorial definition")
        route = document["tutorial"]["route"]
        if not isinstance(route, dict):
            raise TutorialLoadError("Tutorial route must be an object")
        return route
    except (BadZipFile, json.JSONDecodeError, UnicodeError, KeyError, AttributeError, TypeError, RuntimeError) as exc:
        raise TutorialLoadError(f"Invalid tutorial package: {exc}") from exc


def install_tutorial(package: Path, data_root: Path, tutorial_id: str, *, replace: bool = False,
                     domains: list[str] | None = None, dry_run: bool = False) -> Path:
    """Validate against the target KB, then atomically install a new/revised built-in."""
    if not tutorial_id or tutorial_id.startswith("personal:") or any(char.isspace() for char in tutorial_id):
        raise TutorialLoadError("Choose a non-personal built-in tutorial ID")
    kb = load_knowledge_base(data_root, include_graphics=False)
    target = kb.paths.tutorials or data_root / "tutorials.yaml"
    document = yaml.safe_load(target.read_text()) if target.exists() else {"schema_version": 1, "tutorials": []}
    if not isinstance(document, dict) or document.get("schema_version") != 1 or not isinstance(document.get("tutorials"), list):
        raise TutorialLoadError("Invalid target tutorial catalogue")
    rows = document["tutorials"]
    if any(row["tutorial_id"] == tutorial_id for row in rows) and not replace:
        raise TutorialLoadError("This built-in ID already exists; use --replace explicitly")
    route = read_tutorial_package(package)
    route["tutorial_id"] = tutorial_id
    owners = {concept.id: concept.domain for concept in kb.concepts}
    owners.update({module.module_id: module.domain for module in kb.modules})
    for owner in (*kb.concepts, *kb.modules):
        owners.update({block.block_id: owner.domain for block in owner.content_blocks})
    inferred = set()

    def references(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if key in {"target", "block"} and isinstance(item, str):
                    for identifier, domain in owners.items():
                        if item.endswith(":" + identifier) or identifier in [part.rsplit(":", 1)[-1] for part in item.split("|")]:
                            inferred.add(domain)
                references(item)
        elif isinstance(value, list):
            for item in value:
                references(item)

    references(route.get("steps"))
    route["domains"] = sorted(set(domains if domains is not None else route.get("domains", [])) | inferred)
    if not route["domains"]:
        route["domains"] = sorted({concept.domain for concept in kb.concepts if concept.domain})
    document["tutorials"] = [row for row in rows if row["tutorial_id"] != tutorial_id] + [route]
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with NamedTemporaryFile(mode="w", suffix=".yaml", dir=target.parent, delete=False) as file:
            temporary = Path(file.name)
            yaml.safe_dump(document, file, sort_keys=False, allow_unicode=True)
        load_tutorials(temporary, concept_ids=(concept.id for concept in kb.concepts),
                       module_ids=(module.module_id for module in kb.modules),
                       block_ids=(block.block_id for owner in (*kb.concepts, *kb.modules) for block in owner.content_blocks),
                       domain_ids={concept.domain for concept in kb.concepts})
        if not dry_run:
            temporary.replace(target)
        return target
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
