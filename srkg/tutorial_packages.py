"""Install a reviewed tutorial export as ordinary authored YAML."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from tempfile import NamedTemporaryFile
from zipfile import ZIP_STORED, BadZipFile, ZipFile

import yaml

from srkg.kb import load_knowledge_base
from srkg.tutorials import AUDIO_ID, AUDIO_TYPE, TutorialLoadError, load_tutorials, validate_audio_reference

MAX_TEXT_BYTES = 10 * 1024 * 1024
MAX_CLIP_BYTES = 50 * 1024 * 1024
MAX_PACKAGE_BYTES = 200 * 1024 * 1024


def read_tutorial_package(path: Path) -> dict:
    return _read_package(path)[0]


def _read_package(path: Path) -> tuple[dict, dict]:
    if path.stat().st_size > MAX_PACKAGE_BYTES:
        raise TutorialLoadError("Tutorial package exceeds 200 MB")
    try:
        manifest = None
        assets = {}
        if path.suffix.lower() == ".zip":
            with ZipFile(path) as archive:
                infos = archive.infolist()
                names = {entry.filename for entry in infos}
                if len(names) != len(infos) or len(infos) > 1000 or sum(i.file_size for i in infos) > MAX_PACKAGE_BYTES:
                    raise TutorialLoadError("Invalid or oversized tutorial archive")
                if not {"manifest.json", "tutorial.json"} <= names:
                    raise TutorialLoadError("Tutorial package needs manifest.json and tutorial.json")
                for key in ("manifest.json", "tutorial.json"):
                    if archive.getinfo(key).file_size > MAX_TEXT_BYTES:
                        raise TutorialLoadError("Tutorial document exceeds 10 MB")
                manifest = json.loads(archive.read("manifest.json"))
                document = json.loads(archive.read("tutorial.json"))
                version = manifest.get("schema_version")
                inventory = manifest.get("assets")
                _check_header(manifest, version)
                if not isinstance(inventory, list) or (version == 1 and (inventory or len(names) != 2)):
                    raise TutorialLoadError("Invalid tutorial audio inventory")
                if version == 2:
                    for entry in inventory:
                        identifier = entry["id"]
                        mime, length = entry["mimeType"], entry["byteLength"]
                        if (set(entry) != {"id", "mimeType", "byteLength"} or
                            not AUDIO_ID.fullmatch(identifier) or identifier in assets or
                            not AUDIO_TYPE.fullmatch(mime) or len(mime) > 128 or
                            type(length) is not int or not 0 < length <= MAX_CLIP_BYTES):
                            raise TutorialLoadError("Invalid tutorial audio asset")
                        item = archive.getinfo(f"audio/{identifier}")
                        if item.file_size != length or item.compress_type != ZIP_STORED:
                            raise TutorialLoadError("Invalid tutorial audio size or ZIP encoding")
                        content = archive.read(item)
                        if hashlib.sha256(content).hexdigest() != identifier:
                            raise TutorialLoadError("Tutorial audio checksum mismatch")
                        assets[identifier] = (mime, content)
                    if names != {"manifest.json", "tutorial.json"} | {f"audio/{key}" for key in assets}:
                        raise TutorialLoadError("Unexpected file in voiced tutorial archive")
        else:
            if path.stat().st_size > MAX_TEXT_BYTES:
                raise TutorialLoadError("Tutorial document exceeds 10 MB")
            version = 1
            document = json.loads(path.read_text(encoding="utf-8-sig"))
        _check_header(document, version)
        route = document["tutorial"]["route"]
        if not isinstance(route, dict):
            raise TutorialLoadError("Tutorial route must be an object")
        references = set()
        for step in route.get("steps", []):
            if "audio" not in step:
                continue
            audio = validate_audio_reference(step["audio"], step.get("title", "Card"))
            references.add(audio["assetId"])
            if audio["assetId"] not in assets:
                raise TutorialLoadError("A voiced card is missing its audio asset")
            audio["mimeType"] = assets[audio["assetId"]][0]
            step["audio"] = audio
        if references != assets.keys():
            raise TutorialLoadError("Tutorial audio inventory does not match its cards")
        return route, assets
    except (BadZipFile, json.JSONDecodeError, UnicodeError, KeyError, AttributeError, TypeError, RuntimeError) as exc:
        raise TutorialLoadError(f"Invalid tutorial package: {exc}") from exc


def _check_header(value, version):
    if type(version) is not int or version not in (1, 2) or (
        value.get("format"), value.get("schema_version"), value.get("route_schema_version")
    ) != ("physicskg-tutorial", version, version):
        raise TutorialLoadError("Unsupported tutorial package version")


def install_tutorial(package: Path, data_root: Path, tutorial_id: str, *, replace: bool = False,
                     domains: list[str] | None = None, dry_run: bool = False, report=None) -> Path:
    """Validate against the target KB, then atomically install a new/revised built-in."""
    if not tutorial_id or tutorial_id.startswith("personal:") or any(char.isspace() for char in tutorial_id):
        raise TutorialLoadError("Choose a non-personal built-in tutorial ID")
    kb = load_knowledge_base(data_root, include_graphics=False)
    existing = next((item for item in kb.tutorials if item.tutorial_id == tutorial_id), None)
    target = (existing.source if existing else None) or kb.paths.tutorials or data_root / "tutorials.yaml"
    document = yaml.safe_load(target.read_text()) if target.exists() else {"schema_version": 1, "tutorials": []}
    if not isinstance(document, dict) or document.get("schema_version") != 1 or not isinstance(document.get("tutorials"), list):
        raise TutorialLoadError("Invalid target tutorial catalogue")
    rows = document["tutorials"]
    if any(row["tutorial_id"] == tutorial_id for row in rows) and not replace:
        raise TutorialLoadError("This built-in ID already exists; use --replace explicitly")
    route, assets = _read_package(package)
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
    if not dry_run:
        target.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with NamedTemporaryFile(mode="w", suffix=".yaml", dir=None if dry_run else target.parent, delete=False) as file:
            temporary = Path(file.name)
            yaml.safe_dump(document, file, sort_keys=False, allow_unicode=True)
        load_tutorials(temporary, concept_ids=(concept.id for concept in kb.concepts),
                       module_ids=(module.module_id for module in kb.modules),
                       block_ids=(block.block_id for owner in (*kb.concepts, *kb.modules) for block in owner.content_blocks),
                       domain_ids={concept.domain for concept in kb.concepts})
        if report is not None:
            report(f"{'Replace' if existing else 'Install'} {tutorial_id} in {target}")
            for index, step in enumerate(route["steps"], start=1):
                report(f"  {index}. {step['title']} ({step['step_id']})" +
                       (" — voice" if step.get("audio") else ""))
        if not dry_run:
            for identifier, (_, content) in assets.items():
                path = target.parent / "tutorial-audio" / identifier
                path.parent.mkdir(exist_ok=True)
                if path.exists():
                    if path.read_bytes() != content:
                        raise TutorialLoadError(f"Existing asset has different bytes: {identifier}")
                else:
                    with NamedTemporaryFile(dir=path.parent, delete=False) as audio_file:
                        staging = Path(audio_file.name)
                        try:
                            audio_file.write(content)
                            audio_file.close()
                            staging.replace(path)
                        finally:
                            staging.unlink(missing_ok=True)
            temporary.replace(target)
        return target
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
