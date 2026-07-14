from dataclasses import dataclass
from pathlib import Path
import re
import shutil

import pandas as pd
import pytest

from srkg.pipeline import generate_viewer


REPO_ROOT = Path(__file__).resolve().parents[2]
BROWSER_TEST_ROOT = Path(__file__).resolve().parent


def pytest_collection_modifyitems(config, items):
    """Keep browser tests opt-in for whole-suite unit test runs."""
    explicit_browser_run = any(
        (Path(arg).resolve() == BROWSER_TEST_ROOT or BROWSER_TEST_ROOT in Path(arg).resolve().parents)
        for arg in config.args
        if not arg.startswith("-")
    )
    if explicit_browser_run:
        return

    skip_browser = pytest.mark.skip(
        reason="browser tests run only when tests/browser is selected explicitly",
    )
    for item in items:
        if "browser" in item.keywords:
            item.add_marker(skip_browser)


@dataclass(frozen=True)
class BrowserGraph:
    page: object
    output_path: Path
    page_errors: list[str]
    console_errors: list[str]


def _write_browser_fixture(tmp_path: Path) -> tuple[Path, Path, Path]:
    nodes_path = tmp_path / "nodes.csv"
    edges_path = tmp_path / "edges.csv"
    edge_key_path = tmp_path / "edges_key.csv"
    pd.DataFrame([
        {
            "id": "1.1",
            "label": "Alpha",
            "layer": "1",
            "layer_title": "Foundations",
            "definition_new": "Alpha definition",
            "derivation_new": "",
            "explanation_new": "",
        },
        {
            "id": "2.1",
            "label": "Beta",
            "layer": "2",
            "layer_title": "Applications",
            "definition_new": "Beta definition",
            "derivation_new": "",
            "explanation_new": (
                "Beta explains alpha. "
                "\\optional_details{Why this matters}{The optional body can include "
                "\\(x^{2}+y^{2}\\) and a \\cref{link to Alpha}{1.1}.} "
                "\\[x^{2}+y^{2}=z^{2}\\] "
                "After the display equation."
            ),
        },
        {
            "id": "2.2",
            "label": "Gamma",
            "layer": "2",
            "layer_title": "Applications",
            "definition_new": "Gamma definition",
            "derivation_new": "",
            "explanation_new": "",
        },
        {
            "id": "3.1",
            "label": "Delta",
            "layer": "3",
            "layer_title": "Synthesis",
            "definition_new": "Delta definition",
            "derivation_new": "",
            "explanation_new": "",
        },
    ]).to_csv(nodes_path, index=False)
    pd.DataFrame([
        {
            "source": "3.1",
            "target": "2.1",
            "relation": "DEPENDS_ON",
            "note": "Delta depends on beta",
        },
        {
            "source": "2.1",
            "target": "1.1",
            "relation": "DEPENDS_ON",
            "note": "Beta depends on alpha",
        },
        {
            "source": "1.1",
            "target": "2.1",
            "relation": "RELATED",
            "note": "Bidirectional teaching relation",
        },
        {
            "source": "3.1",
            "target": "2.2",
            "relation": "DEPENDS_ON",
            "note": "Delta depends on gamma",
        },
    ]).to_csv(edges_path, index=False)
    pd.DataFrame([
        {
            "relation": "DEPENDS_ON",
            "directed": "true",
            "category": "dependency",
            "meaning": "source depends on target",
            "example": "Beta depends on Alpha",
        },
        {
            "relation": "RELATED",
            "directed": "false",
            "category": "association",
            "meaning": "source is related to target",
            "example": "Alpha is related to Beta",
        },
    ]).to_csv(edge_key_path, index=False)
    return nodes_path, edges_path, edge_key_path


def _copy_local_browser_assets(output_dir: Path) -> None:
    for relative_path in [
        Path("bindings") / "utils.js",
        Path("vis-9.1.2") / "vis-network.css",
        Path("vis-9.1.2") / "vis-network.min.js",
    ]:
        source = REPO_ROOT / "lib" / relative_path
        target = output_dir / "lib" / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def _use_local_vis_assets(html_text: str) -> str:
    html_text = re.sub(
        r'<link rel="stylesheet" href="https://cdnjs\.cloudflare\.com/ajax/libs/vis-network/9\.1\.2/dist/dist/vis-network\.min\.css"[^>]*>',
        '<link rel="stylesheet" href="lib/vis-9.1.2/vis-network.css" />',
        html_text,
    )
    return re.sub(
        r'<script src="https://cdnjs\.cloudflare\.com/ajax/libs/vis-network/9\.1\.2/dist/vis-network\.min\.js"[^>]*></script>',
        '<script src="lib/vis-9.1.2/vis-network.min.js"></script>',
        html_text,
    )


@pytest.fixture
def browser_graph(tmp_path):
    playwright_api = pytest.importorskip(
        "playwright.sync_api",
        reason="Playwright is not installed in the sr-kg environment",
    )

    nodes_path, edges_path, edge_key_path = _write_browser_fixture(tmp_path)
    output_path = tmp_path / "viewer.html"
    generate_viewer(
        nodes_path=str(nodes_path),
        edges_path=str(edges_path),
        edge_key_path=str(edge_key_path),
        out_path=str(output_path),
        height="100vh",
        width="100vw",
        title="Browser Harness",
    )
    _copy_local_browser_assets(tmp_path)
    output_path.write_text(
        _use_local_vis_assets(output_path.read_text(encoding="utf-8")),
        encoding="utf-8",
    )

    page_errors: list[str] = []
    console_errors: list[str] = []
    with playwright_api.sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch(timeout=5000)
        except playwright_api.Error as exc:
            pytest.skip(f"Playwright Chromium is not available: {exc}")

        page = browser.new_page(viewport={"width": 1280, "height": 800})
        page.set_default_timeout(5000)
        page.on("pageerror", lambda exc: page_errors.append(str(exc)))
        page.on(
            "console",
            lambda message: (
                console_errors.append(message.text)
                if message.type == "error"
                else None
            ),
        )
        page.goto(output_path.as_uri(), wait_until="domcontentloaded")
        page.evaluate(
            """() => {
              localStorage.removeItem("srkg.userNotes.v1");
              localStorage.removeItem("srkg.noteEditing.v1");
            }"""
        )
        page.reload(wait_until="domcontentloaded")
        page.wait_for_selector("#kg_controls", state="attached")
        page.wait_for_selector("#info_panel", state="attached")
        page.wait_for_function(
            """() =>
              typeof network !== "undefined" &&
              typeof nodes !== "undefined" &&
              typeof edges !== "undefined" &&
              document.querySelector("#kg_node_labels")
            """
        )

        try:
            yield BrowserGraph(
                page=page,
                output_path=output_path,
                page_errors=page_errors,
                console_errors=console_errors,
            )
        finally:
            browser.close()
