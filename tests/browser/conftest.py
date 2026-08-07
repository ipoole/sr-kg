from dataclasses import dataclass
from contextlib import contextmanager
from pathlib import Path
import re
import shutil

import pandas as pd
import pytest

from srkg.pipeline import generate_viewer_from_root


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

    def open_control_section(self, section_id: str) -> None:
        self.page.locator(f"#{section_id}").evaluate("el => { el.open = true; }")

    def open_search(self) -> None:
        self.open_control_section("kg_search_section")

    def click_concept(self, concept_id: str) -> None:
        self.open_search()
        self.page.locator(f'.kg-concept-item[data-concept-id="{concept_id}"]').click()


def _write_browser_fixture(tmp_path: Path) -> tuple[Path, Path, Path]:
    (tmp_path / "manifest.yaml").write_text(
        "\n".join([
            "name: browser-test-kb",
            "files:",
            "  nodes: nodes.csv",
            "  edges: edges.csv",
            "  edge_key: edges_key.csv",
            "  content_blocks: content_blocks.csv",
            "  study_questions: study_questions.csv",
            "  references: references.csv",
            "  reference_links: reference_links.csv",
            "",
        ]),
        encoding="utf-8",
    )
    nodes_path = tmp_path / "nodes.csv"
    edges_path = tmp_path / "edges.csv"
    edge_key_path = tmp_path / "edges_key.csv"
    content_blocks_path = tmp_path / "content_blocks.csv"
    study_questions_path = tmp_path / "study_questions.csv"
    pd.DataFrame([
        {
            "id": "1.1",
            "display_id": "1.1",
            "label": "Alpha",
            "layer": "1",
            "layer_title": "Foundations",
        },
        {
            "id": "2.1",
            "display_id": "2.1",
            "label": "Beta",
            "layer": "2",
            "layer_title": "Applications",
        },
        {
            "id": "2.2",
            "display_id": "2.2",
            "label": "Gamma",
            "layer": "2",
            "layer_title": "Applications",
        },
        {
            "id": "3.1",
            "display_id": "3.1",
            "label": "Delta",
            "layer": "3",
            "layer_title": "Synthesis",
        },
    ]).to_csv(nodes_path, index=False)
    pd.DataFrame([
        {
            "block_id": "1.1.definition",
            "concept_id": "1.1",
            "sequence": 10,
            "kind": "definition",
            "title": "Definition",
            "body": "Alpha definition",
        },
        {
            "block_id": "2.1.definition",
            "concept_id": "2.1",
            "sequence": 10,
            "kind": "definition",
            "title": "Definition",
            "body": "Beta definition \\(E=mc^2\\)",
        },
        {
            "block_id": "2.1.explanation",
            "concept_id": "2.1",
            "sequence": 30,
            "kind": "explanation",
            "title": "Explanation",
            "body": (
                "Beta explains alpha. "
                "\\optional_details{Why this matters}{The optional body can include "
                "\\(x^{2}+y^{2}\\) and a \\cref{link to Alpha}{1.1}.} "
                "\\[x^{2}+y^{2}=z^{2}\\] "
                "After the display equation."
            ),
        },
        {
            "block_id": "2.2.definition",
            "concept_id": "2.2",
            "sequence": 10,
            "kind": "definition",
            "title": "Definition",
            "body": "Gamma definition",
        },
        {
            "block_id": "2.2.intuition",
            "concept_id": "2.2",
            "sequence": 20,
            "kind": "intuition",
            "title": "Gamma intuition",
            "body": "Gamma intuition body",
        },
        {
            "block_id": "2.2.warning",
            "concept_id": "2.2",
            "sequence": 30,
            "kind": "warning",
            "title": "Gamma warning",
            "body": "Gamma warning body",
        },
        {
            "block_id": "2.2.derivation_step",
            "concept_id": "2.2",
            "sequence": 35,
            "kind": "derivation_step",
            "title": "Gamma algebra step",
            "body": "Gamma derivation-step body",
        },
        {
            "block_id": "2.2.historical_note",
            "concept_id": "2.2",
            "sequence": 40,
            "kind": "historical_note",
            "title": "Gamma history",
            "body": "Gamma history body",
        },
        {
            "block_id": "3.1.definition",
            "concept_id": "3.1",
            "sequence": 10,
            "kind": "definition",
            "title": "Definition",
            "body": "Delta definition",
        },
    ]).to_csv(content_blocks_path, index=False)
    pd.DataFrame([
        {
            "source": "3.1",
            "target": "2.1",
            "relation": "DEPENDS_ON",
            "note": "Delta depends on beta",
        },
        {
            "source": "3.1",
            "target": "2.2",
            "relation": "DERIVES_FROM",
            "note": "Delta derives from gamma",
        },
        {
            "source": "2.2",
            "target": "1.1",
            "relation": "DERIVES_FROM",
            "note": "Gamma derives from alpha",
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
        {
            "relation": "DERIVES_FROM",
            "directed": "true",
            "category": "knowledge",
            "meaning": "source can be mathematically derived from target",
            "example": "Delta derives from Gamma",
        },
    ]).to_csv(edge_key_path, index=False)
    pd.DataFrame([
        {
            "question_id": "2.1.q1",
            "concept_id": "2.1",
            "sequence": 10,
            "question_type": "short_answer",
            "prompt": "Beta question?\\n\\nA. First option\\nB. Second option",
            "answer": "Beta answer.",
        },
        {
            "question_id": "2.2.q1",
            "concept_id": "2.2",
            "sequence": 10,
            "question_type": "short_answer",
            "prompt": "Gamma short-answer question?",
            "answer": "Gamma short-answer answer.",
        },
        {
            "question_id": "2.2.q2",
            "concept_id": "2.2",
            "sequence": 20,
            "question_type": "calculation",
            "prompt": "Gamma calculation question?",
            "answer": "Gamma calculation answer.",
        },
        {
            "question_id": "2.2.q3",
            "concept_id": "2.2",
            "sequence": 30,
            "question_type": "multiple_choice",
            "prompt": "Gamma multiple-choice question?",
            "answer": "Gamma multiple-choice answer.",
        },
    ]).to_csv(study_questions_path, index=False)
    pd.DataFrame(columns=[
        "reference_id",
        "reference_type",
        "citation",
        "authors",
        "title",
        "year",
        "url",
        "note",
    ]).to_csv(tmp_path / "references.csv", index=False)
    pd.DataFrame(columns=[
        "source_type",
        "source_id",
        "reference_id",
        "locator",
        "note",
    ]).to_csv(tmp_path / "reference_links.csv", index=False)
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


def _prepare_browser_output(tmp_path: Path, data_root: Path, title: str) -> Path:
    output_path = tmp_path / "viewer.html"
    generate_viewer_from_root(
        data_root=str(data_root),
        out_path=str(output_path),
        height="100vh",
        width="100vw",
        title=title,
    )
    _copy_local_browser_assets(tmp_path)
    output_path.write_text(
        _use_local_vis_assets(output_path.read_text(encoding="utf-8")),
        encoding="utf-8",
    )
    return output_path


@contextmanager
def _open_browser_graph(playwright_api, output_path: Path):
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
              localStorage.removeItem("srkg.splash.dismissed.v1");
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
            page.locator("#kg_splash_dialog[open]").wait_for(timeout=1000)
            page.locator("#kg_splash_dismiss").click()
        except playwright_api.TimeoutError:
            pass

        try:
            yield BrowserGraph(
                page=page,
                output_path=output_path,
                page_errors=page_errors,
                console_errors=console_errors,
            )
        finally:
            browser.close()


@pytest.fixture
def browser_graph(tmp_path):
    playwright_api = pytest.importorskip(
        "playwright.sync_api",
        reason="Playwright is not installed in the sr-kg environment",
    )

    _write_browser_fixture(tmp_path)
    output_path = _prepare_browser_output(tmp_path, tmp_path, "Browser Harness")
    with _open_browser_graph(playwright_api, output_path) as graph:
        yield graph


@pytest.fixture
def repo_browser_graph(tmp_path):
    playwright_api = pytest.importorskip(
        "playwright.sync_api",
        reason="Playwright is not installed in the sr-kg environment",
    )

    output_path = _prepare_browser_output(
        tmp_path,
        REPO_ROOT / "data",
        "Special Relativity and Classical Fields",
    )
    with _open_browser_graph(playwright_api, output_path) as graph:
        yield graph
