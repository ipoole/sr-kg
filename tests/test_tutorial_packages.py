import json
from pathlib import Path
import shutil
from zipfile import ZIP_STORED, ZipFile

import pytest
import yaml

from srkg.kb import load_knowledge_base
from srkg.pipeline import generate_viewer_from_root
from srkg.tutorial_packages import install_tutorial
from srkg.tutorials import TutorialLoadError

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def installation(tmp_path):
    data = tmp_path / "data"
    shutil.copytree(ROOT / "data", data)
    manifest = yaml.safe_load((data / "manifest.yaml").read_text())
    manifest["domains_root"] = str(ROOT / "domains")
    (data / "manifest.yaml").write_text(yaml.safe_dump(manifest))
    route = load_knowledge_base(data, include_graphics=False).tutorials[0].to_viewer_data()
    route["author"] = "A physics teacher"
    route["steps"][0]["demonstrate"] = False
    package = tmp_path / "tutorial.json"
    document = {"format":"physicskg-tutorial", "schema_version":1, "route_schema_version":1,
                "tutorial":{"route":route}}
    package.write_text(json.dumps(document))
    return data, package, document


def test_install_exported_tutorial_and_generate_with_credit(installation, tmp_path):
    data, package, _ = installation
    target = install_tutorial(package, data, "teacher-tour")
    kb = load_knowledge_base(data, include_graphics=False)
    installed = next(item for item in kb.tutorials if item.tutorial_id == "teacher-tour")
    assert installed.author == "A physics teacher"
    assert installed.steps[0].demonstrate is False
    assert installed.to_viewer_data()["author"] == installed.author
    output = tmp_path / "viewer.html"
    generate_viewer_from_root(data_root=str(data), out_path=str(output), height="100vh", width="100vw", title="Test")
    assert '"tutorial_id": "teacher-tour"' in output.read_text()
    assert target == data / "tutorials.yaml"


def test_install_dry_run_and_replace_are_explicit(installation):
    data, package, document = installation
    target = data / "tutorials.yaml"
    before = target.read_bytes()
    original_id = document["tutorial"]["route"]["tutorial_id"]
    with pytest.raises(TutorialLoadError):
        install_tutorial(package, data, original_id)
    install_tutorial(package, data, original_id, replace=True, dry_run=True)
    assert target.read_bytes() == before
    install_tutorial(package, data, original_id, replace=True)
    assert next(item for item in load_knowledge_base(data, include_graphics=False).tutorials if item.tutorial_id == original_id).author


def test_bad_package_and_incomplete_draft_never_change_authored_file(installation):
    data, package, document = installation
    target = data / "tutorials.yaml"
    before = target.read_bytes()
    document["tutorial"]["route"]["steps"][0]["commentary"] = ""
    package.write_text(json.dumps(document))
    with pytest.raises(TutorialLoadError):
        install_tutorial(package, data, "incomplete")
    assert target.read_bytes() == before
    package.write_text("{broken")
    with pytest.raises(TutorialLoadError):
        install_tutorial(package, data, "broken")
    assert target.read_bytes() == before


def test_stored_zip_install_and_missing_domains_are_inferred(installation):
    data, package, document = installation
    route = document["tutorial"]["route"]
    route["domains"] = []
    route["steps"] = [{"step_id":"edge", "title":"A dependency", "commentary":"Inspect the connection.",
                       "action":{"command":"show-graph-edge-hover", "target":"edge:sr.mass_energy_equivalence|REQUIRES|math.manifold"}}]
    # Use known IDs without requiring this illustrative edge to exist.
    archive = package.with_suffix('.zip')
    with ZipFile(archive,'w',compression=ZIP_STORED) as zip_file:
        zip_file.writestr('manifest.json',json.dumps({"format":"physicskg-tutorial","schema_version":1,"route_schema_version":1,"assets":[]}))
        zip_file.writestr('tutorial.json',json.dumps(document))
    install_tutorial(archive,data,"edge-tour")
    installed = next(item for item in load_knowledge_base(data,include_graphics=False).tutorials if item.tutorial_id=='edge-tour')
    assert set(installed.domains) == {'math','sr'}
