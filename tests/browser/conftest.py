from dataclasses import dataclass
from contextlib import contextmanager
from pathlib import Path
import re
import shutil
from unittest.mock import patch

import pandas as pd
import pytest

from srkg.pipeline import generate_viewer_from_root
from srkg.data import createSvgGraphic as create_repo_svg_graphic


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

    def drawn_module_bounds(self, node_id: str) -> dict:
        # vis adds the corner radius to getBoundingBox(), outside the painted box.
        return self.page.evaluate("""id => {
          const s = network.body.nodes[id].shape;
          return {left:s.left, right:s.left+s.width, top:s.top, bottom:s.top+s.height};
        }""", node_id)

    def open_control_section(self, section_id: str) -> None:
        self.page.locator(f"#{section_id}").evaluate("el => { el.open = true; }")

    def open_search(self) -> None:
        if not self.page.locator("#kg_search_section").evaluate("el => el.open"):
            self.page.locator("#kg_search_toggle").click()

    def click_concept(self, concept_id: str) -> None:
        self.open_search()
        self.page.locator(f'.kg-concept-item[data-concept-id="{concept_id}"]').click()
        self.page.locator("#kg_search_close").click()


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
            "  modules: modules.csv",
            "  module_members: module_members.csv",
            "  module_supports: module_supports.csv",
            "  module_content_blocks: module_content_blocks.csv",
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
            "domain": "test",
            "domain_title": "Test Physics",
        },
        {
            "id": "2.1",
            "display_id": "2.1",
            "label": "Beta",
            "domain": "test",
            "domain_title": "Test Physics",
        },
        {
            "id": "2.2",
            "display_id": "2.2",
            "label": "Gamma",
            "domain": "test",
            "domain_title": "Test Physics",
        },
        {
            "id": "3.1",
            "display_id": "3.1",
            "label": "Delta",
            "domain": "test",
            "domain_title": "Test Physics",
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
            "relation": "REQUIRES",
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
            "relation": "REQUIRES",
            "note": "Beta depends on alpha through Noether's theorem \\(E=mc^2\\)",
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
            "relation": "REQUIRES",
            "note": "Delta depends on gamma",
        },
    ]).to_csv(edges_path, index=False)
    pd.DataFrame([
        {
            "relation": "REQUIRES",
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
    pd.DataFrame([
        {
            "module_id": "test.m01_foundations",
            "domain": "test",
            "title": "Foundations",
            "sequence": 10,
            "default_collapsed": "false",
        },
        {
            "module_id": "test.m02_applications",
            "domain": "test",
            "title": "Applications",
            "sequence": 20,
            "default_collapsed": "false",
        },
    ]).to_csv(tmp_path / "modules.csv", index=False)
    pd.DataFrame([
        {
            "module_id": "test.m01_foundations",
            "concept_id": "1.1",
            "sequence": 10,
        },
        {
            "module_id": "test.m02_applications",
            "concept_id": "2.1",
            "sequence": 10,
        },
        {
            "module_id": "test.m02_applications",
            "concept_id": "2.2",
            "sequence": 20,
        },
        {
            "module_id": "test.m02_applications",
            "concept_id": "3.1",
            "sequence": 30,
        },
    ]).to_csv(tmp_path / "module_members.csv", index=False)
    pd.DataFrame([
        {
            "module_id": "test.m02_applications",
            "target_type": "module",
            "target_id": "test.m01_foundations",
            "role": "prerequisite",
            "note": "Applications reuse the foundations module.",
        },
    ]).to_csv(tmp_path / "module_supports.csv", index=False)
    pd.DataFrame([
        {
            "block_id": "test.m01_foundations.overview",
            "module_id": "test.m01_foundations",
            "sequence": 10,
            "kind": "overview",
            "title": "Route",
            "body": "Start with Alpha as the foundation.",
        },
        {
            "block_id": "test.m02_applications.overview",
            "module_id": "test.m02_applications",
            "sequence": 10,
            "kind": "overview",
            "title": "Route",
            "body": "Apply the foundation through Beta, Gamma, and Delta.",
        },
    ]).to_csv(tmp_path / "module_content_blocks.csv", index=False)
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


def _create_fixture_svg_graphic(concept_id: str, variant: str = "icon") -> str | None:
    """Give the synthetic numeric-ID fixture a graphic without registry aliases."""
    if concept_id == "2.2":
        size = 160 if variant == "detail" else 80
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}">'
            f'<circle cx="{size / 2}" cy="{size / 2}" r="{size / 3}" '
            'fill="none" stroke="currentColor"/></svg>'
        )
    return create_repo_svg_graphic(concept_id, variant=variant)


@contextmanager
def _open_browser_graph(playwright_api, browser, output_path: Path):
    page_errors: list[str] = []
    console_errors: list[str] = []
    context = browser.new_context(viewport={"width": 1280, "height": 800})
    try:
        page = context.new_page()
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

        yield BrowserGraph(
            page=page,
            output_path=output_path,
            page_errors=page_errors,
            console_errors=console_errors,
        )
    finally:
        context.close()


@pytest.fixture(scope="session")
def playwright_browser():
    playwright_api = pytest.importorskip(
        "playwright.sync_api",
        reason="Playwright is not installed in the sr-kg environment",
    )

    with playwright_api.sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch(timeout=5000)
        except playwright_api.Error as exc:
            pytest.skip(f"Playwright Chromium is not available: {exc}")

        try:
            yield playwright_api, browser
        finally:
            browser.close()


@pytest.fixture(scope="session")
def browser_fixture_output(tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp("browser-fixture")
    _write_browser_fixture(tmp_path)
    with patch("srkg.data.createSvgGraphic", side_effect=_create_fixture_svg_graphic):
        return _prepare_browser_output(tmp_path, tmp_path, "Browser Harness")


@pytest.fixture(scope="session")
def repo_browser_output(tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp("repo-browser")
    return _prepare_browser_output(
        tmp_path,
        REPO_ROOT / "data",
        "Special Relativity and Classical Fields",
    )


@pytest.fixture
def browser_graph(browser_fixture_output, playwright_browser):
    playwright_api, browser = playwright_browser
    with _open_browser_graph(playwright_api, browser, browser_fixture_output) as graph:
        yield graph


@pytest.fixture(scope="module")
def shared_browser_graph(browser_fixture_output, playwright_browser):
    playwright_api, browser = playwright_browser
    with _open_browser_graph(playwright_api, browser, browser_fixture_output) as graph:
        yield graph


@pytest.fixture
def repo_browser_graph(repo_browser_output, playwright_browser):
    playwright_api, browser = playwright_browser
    with _open_browser_graph(playwright_api, browser, repo_browser_output) as graph:
        yield graph
