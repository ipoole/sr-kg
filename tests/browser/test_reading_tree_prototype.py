"""Fast behavioural checks for the standalone design prototype, without a build."""

from pathlib import Path

import pytest

from conftest import _use_stub_mathjax


REPO_ROOT = Path(__file__).resolve().parents[2]
PROTOTYPE = REPO_ROOT / "domains/math/docs/graph_aligned_reading_mockup.html"


@pytest.fixture(scope="session")
def reading_prototype_output(tmp_path_factory):
    output = tmp_path_factory.mktemp("reading-prototype") / "prototype.html"
    output.write_text(_use_stub_mathjax(PROTOTYPE.read_text(encoding="utf-8")),
                      encoding="utf-8")
    return output


def _toggle_concept(disclosure):
    return disclosure.locator("xpath=..").locator(
        ":scope > .concept-title > .concept-toggle")


def _expand_dependencies(page, tree_id):
    """Wait for native toggle events, not arbitrary sleeps or eager recursion."""
    selector = f"#tree-{tree_id} .dependency"
    for _ in range(12):
        closed = page.locator(selector + ":not([open])")
        if not closed.count():
            return
        closed.evaluate_all("items => items.forEach(item => { item.open = true; })")
        page.wait_for_function(
            """selector => [...document.querySelectorAll(selector)]
                .filter(item => item.open)
                .every(item => item.querySelector(':scope > .body')
                    .dataset.loaded === 'true')""",
            arg=selector,
        )
    pytest.fail("Dependency expansion did not terminate")


@pytest.mark.browser
@pytest.mark.parametrize("width", [390, 1280])
def test_reading_prototype_routes_and_independent_disclosures(
        reading_prototype_output, playwright_browser, width):
    _, browser = playwright_browser
    context = browser.new_context(viewport={"width": width, "height": 1050})
    errors = []
    try:
        page = context.new_page()
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(reading_prototype_output.as_uri(), wait_until="domcontentloaded")
        page.wait_for_function("window.paper")
        page.add_script_tag(path=str(REPO_ROOT / "srkg/viewer_assets/graph_model.js"))
        assert page.locator("#reading details[open]").count() == 0

        # Both recipes must project to the real Context algorithm at every depth.
        for recipe, preset in [("derivation", "derivation"),
                               ("teaching", "foundations")]:
            tree = page.locator(f"#tree-{recipe}")
            tree.locator(":scope > summary").click()
            page.wait_for_function(
                "id => paper.trees[id].loaded", arg=recipe)
            assert tree.locator(".owned-block[open]").count() == 0
            first = tree.locator(".tree-content > .concept-group > .block").first
            assert first.get_attribute("data-kind") == "definition"
            for depth, canonical in [("1", "one-hop"), ("2", "two-hops"),
                                     ("3", "three-hops"), ("all", "transitive")]:
                tree.locator("[data-depth-tree]").select_option(depth)
                comparison = page.evaluate("""args => {
                    const edges = paper.data.edges.map(edge => ({
                        ...edge, from: edge.source, to: edge.target,
                        id: [edge.source, edge.relation, edge.target].join('|')
                    }));
                    const definitions = {
                        DERIVES_FROM: {directed: true},
                        CONSTRUCTED_FROM: {directed: true},
                        REQUIRES: {directed: true}, RELATED: {directed: false}
                    };
                    const valid = Object.fromEntries(
                        Object.keys(paper.nodes).map(id => [id, true]));
                    const expected = kgGraphModel.computeContextSubgraph(
                        [paper.data.root], {preset: args[1], depth: args[2]},
                        edges, definitions, valid);
                    const plan = paper.trees[args[0]].plan;
                    return {
                        expectedNodes: expected.nodeIds,
                        actualNodes: Object.keys(plan.dist),
                        expectedEdges: expected.edgeIds,
                        actualEdges: plan.edges.map(edge =>
                            [edge.source, edge.relation, edge.target].join('|'))
                    };
                }""", [recipe, preset, canonical])
                assert set(comparison["actualNodes"]) == set(comparison["expectedNodes"])
                assert set(comparison["actualEdges"]) == set(comparison["expectedEdges"])

        derivation = page.locator("#tree-derivation")
        teaching = page.locator("#tree-teaching")
        first = derivation.locator(".dependency").first
        control = _toggle_concept(first)
        why = first.locator("xpath=..").locator(":scope > .justification")
        assert why.is_visible()
        assert first.locator("xpath=..").locator(":scope > .statement").count() == 0
        control.focus()
        page.keyboard.press("Enter")
        page.wait_for_function(
            "id => document.getElementById(id).getAttribute('aria-expanded') === 'true'",
            arg=control.get_attribute("id"))
        assert why.is_visible()

        # Editing one recipe's depth must not rebuild the other recipe or local prose.
        local = page.locator("#owned-blocks .owned-block").first
        local.locator(":scope > summary").click()
        teaching.locator("[data-depth-tree]").select_option("2")
        assert first.evaluate("element => element.open")
        assert local.evaluate("element => element.open")
        teaching.locator("[data-depth-tree]").select_option("all")
        _expand_dependencies(page, "teaching")
        actual_edges = teaching.locator("[data-edge]").evaluate_all(
            "items => [...new Set(items.map(item => item.dataset.edge))]")
        expected_edges = page.evaluate("""paper.trees.teaching.plan.edges.map(
            edge => [edge.source, edge.relation, edge.target].join('|'))""")
        assert set(actual_edges) == set(expected_edges)

        # Repeated sources retain independent occurrences and focus/Return keeps DOM.
        repeated = teaching.locator('.dependency[data-owner="math.tangent_space"]')
        assert repeated.count() > 1
        _toggle_concept(repeated.first).click()
        assert repeated.nth(1).evaluate("element => element.open")
        assert teaching.locator(
            '.dependency[data-depth="1"] > .body > .focus-button').count() == 0
        page.select_option("#layout", "focus")
        branch = teaching.locator(
            '.dependency[data-depth="2"][data-owner="math.tensor_field"]').first
        branch.locator(":scope > .body > .focus-button").click()
        assert page.evaluate("paper.focusDepth") == 1
        child = page.locator(
            '#focus-host .dependency[data-owner="math.cotangent_space"]').first
        child_id = child.get_attribute("id")
        child.locator(":scope > .body > .focus-button").click()
        assert page.evaluate("paper.focusDepth") == 2
        page.click("#return")
        page.click("#return")
        assert page.locator("#" + child_id).evaluate("element => element.open")
        assert branch.evaluate("element => element.open")

        # A deliberately introduced ancestor cycle must remain a finite projection.
        page.evaluate("""paper.data.edges.push({
            source: 'math.manifold', target: paper.data.root,
            relation: 'CONSTRUCTED_FROM', note: 'Synthetic cycle'
        })""")
        teaching.locator("[data-depth-tree]").select_option("1")
        teaching.locator("[data-depth-tree]").select_option("all")
        _expand_dependencies(page, "teaching")
        assert teaching.locator(".concept-branch > .boundary").count() > 0
        teaching.locator("[data-fold-tree]").click()
        assert teaching.locator(".nest[open]").count() == 0
        assert first.evaluate("element => element.open")
        assert local.evaluate("element => element.open")
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        assert not errors
    finally:
        context.close()
