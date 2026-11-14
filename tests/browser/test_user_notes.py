import csv

import pytest


def _reveal_note_parents(page):
    """Inspect saved notes explicitly inside their now-folded authored blocks."""
    page.locator('#info_panel .user-note').evaluate_all("""notes=>notes.forEach(note=>{
        let parent=note.parentElement;
        while(parent){if(parent.tagName==='DETAILS')parent.open=true;parent=parent.parentElement;}
    })""")


def _hover_beta_node(page):
    point = page.evaluate(
        """() => {
          const position = network.getPositions(["2.1"])["2.1"];
          const dom = network.canvasToDOM(position);
          const rect = network.canvas.frame.canvas.getBoundingClientRect();
          return {x: rect.left + dom.x, y: rect.top + dom.y};
        }"""
    )
    page.mouse.move(point["x"], point["y"])
    page.wait_for_selector("#kg_node_tooltip", state="visible")


def _place_note_at_anchor(anchor):
    block = anchor.locator("xpath=ancestor::*[@data-note-block][1]")
    atomic = block.evaluate(
        "element => element.matches('.concept-figure, .study-questions')"
    )
    block.locator(
        ":scope > summary .kg-note-block-action, "
        ":scope > .kg-noteable-heading .kg-note-block-action"
    ).click()
    if not atomic and block.locator(".concept-line").count() > 0:
        anchor.evaluate("element => element.click()")


@pytest.mark.browser
def test_note_bubbles_replace_permanent_paragraph_controls(repo_browser_graph):
    page = repo_browser_graph.page
    repo_browser_graph.open_control_section("kg_modules_section")
    page.locator(
        '.kg-module-item[data-module-id="math.m01_manifolds_and_coordinates"]'
    ).click()

    overview = page.locator(
        '#info_panel [data-content-block-id='
        '"math.m01_manifolds_and_coordinates.overview"]'
    )
    bubble = overview.locator(":scope > summary .kg-note-block-action")
    assert bubble.count() == 1
    assert bubble.get_attribute("data-note-state") == "empty"
    title = overview.locator(":scope > summary .content-block-title-text").inner_text()
    assert bubble.get_attribute("aria-label") == f"Add a note to {title}"
    assert overview.locator(":scope > summary .kg-note-bubble-glyph").inner_text() == "+"
    assert page.locator("#info_panel .kg-add-note-row:visible").count() == 0

    repo_browser_graph.click_concept("math.manifold")
    graphic = page.locator('#info_panel > [data-content-block-id="math.manifold.graphic"]')
    assert graphic.locator(":scope > summary .kg-note-block-action").count() == 1
    study = page.locator("#info_panel details.study-questions")
    assert study.locator(":scope > summary .kg-note-block-action").count() == 1
    assert page.locator("#kg_notes_edit_toggle").count() == 0


@pytest.mark.browser
def test_note_bubble_places_note_after_chosen_paragraph(repo_browser_graph):
    page = repo_browser_graph.page
    repo_browser_graph.open_control_section("kg_modules_section")
    page.locator(
        '.kg-module-item[data-module-id="math.m01_manifolds_and_coordinates"]'
    ).click()

    explanation = page.locator(
        '#info_panel [data-content-block-id='
        '"math.m01_manifolds_and_coordinates.terrain_setup"]'
    )
    if not explanation.evaluate("element => element.open"):
        explanation.locator(":scope > summary").click()
    bubble = explanation.locator(":scope > summary .kg-note-block-action")
    bubble.click()

    assert explanation.get_attribute("data-note-placement") == "active"
    instruction = explanation.locator(
        ":scope > summary .kg-note-placement-instruction"
    )
    assert instruction.is_visible()
    assert "Choose paragraph ↓" in instruction.inner_text()
    assert explanation.locator(".kg-add-note-row:visible").count() == 0
    assert page.locator(
        '#info_panel [data-content-block-id='
        '"math.m01_manifolds_and_coordinates.overview"]'
    ).get_attribute("data-note-placement") is None

    explanation.locator(".concept-line").last.click()

    explanation = page.locator(
        '#info_panel [data-content-block-id='
        '"math.m01_manifolds_and_coordinates.terrain_setup"]'
    )
    assert explanation.get_attribute("data-note-placement") is None
    assert explanation.locator("details.user-note").count() == 1
    bubble = explanation.locator(":scope > summary .kg-note-block-action")
    assert bubble.get_attribute("data-note-state") == "present"
    assert bubble.get_attribute("aria-label") == (
        "Notes present in The kame-and-kettle survey; add another note"
    )
    assert bubble.locator(".kg-note-bubble-glyph").inner_text() == "+"
    assert bubble.locator(".kg-note-bubble-glyph").evaluate(
        "element => getComputedStyle(element).backgroundColor"
    ) == "rgb(138, 100, 0)"
    assert page.locator("#info_panel .kg-unmatched-notes").count() == 0


@pytest.mark.browser
def test_note_placement_can_be_cancelled(repo_browser_graph):
    page = repo_browser_graph.page
    repo_browser_graph.open_control_section("kg_modules_section")
    page.locator(
        '.kg-module-item[data-module-id="math.m01_manifolds_and_coordinates"]'
    ).click()
    overview = page.locator(
        '#info_panel [data-content-block-id='
        '"math.m01_manifolds_and_coordinates.overview"]'
    )

    overview.locator(":scope > summary .kg-note-block-action").click()
    overview.locator(":scope > summary .kg-note-placement-cancel").click()

    assert overview.get_attribute("data-note-placement") is None
    assert page.locator("#info_panel details.user-note").count() == 0
    assert page.locator("#info_panel .kg-add-note-row:visible").count() == 0
    assert overview.locator(":scope > summary .kg-note-block-action").evaluate(
        "element => document.activeElement === element"
    )


@pytest.mark.browser
def test_note_placement_supports_keyboard_and_multiple_notes(repo_browser_graph):
    page = repo_browser_graph.page
    repo_browser_graph.open_control_section("kg_modules_section")
    page.locator(
        '.kg-module-item[data-module-id="math.m01_manifolds_and_coordinates"]'
    ).click()
    overview = page.locator(
        '#info_panel [data-content-block-id='
        '"math.m01_manifolds_and_coordinates.overview"]'
    )
    bubble = overview.locator(":scope > summary .kg-note-block-action")

    bubble.click()
    first_paragraph = overview.locator(":scope > .content-block-body .concept-line").first
    assert first_paragraph.get_attribute("tabindex") == "0"
    assert first_paragraph.get_attribute("aria-label") == (
        "Place note after this paragraph"
    )
    page.keyboard.press("Enter")
    first_title = overview.locator(".user-note-title-input").first
    assert first_title.evaluate("element => document.activeElement === element")
    first_title.fill("First note")
    overview.locator(".user-note-body-input").first.fill("First body")
    overview.locator(".user-note-close").first.click()

    bubble = overview.locator(":scope > summary .kg-note-block-action")
    assert bubble.get_attribute("data-note-state") == "present"
    bubble.click()
    assert overview.get_attribute("data-note-placement") == "active"
    overview.locator(".kg-add-note").last.evaluate("element => element.click()")
    overview.locator(".user-note-title-input").last.fill("Second note")
    overview.locator(".user-note-body-input").last.fill("Second body")

    assert overview.locator("details.user-note").count() == 2
    title = overview.locator(":scope > summary .content-block-title-text").inner_text()
    assert bubble.get_attribute("aria-label") == (
        f"Notes present in {title}; add another note"
    )


@pytest.mark.browser
def test_atomic_note_blocks_create_their_single_note_directly(repo_browser_graph):
    page = repo_browser_graph.page
    # Canonical Graphic blocks are caption-only atomic targets, as are
    # study-question sections. Keep their notes attached to the block identity.
    repo_browser_graph.click_concept("gr.metric_tensor")

    graphic = page.locator('#info_panel [data-content-block-id="gr.metric_tensor.graphic"]')
    graphic.locator(":scope > summary .kg-note-block-action").click()
    assert graphic.get_attribute("data-note-placement") is None
    assert graphic.locator("details.user-note").count() == 1
    graphic_title = graphic.locator(".user-note-title-input")
    assert graphic_title.evaluate("element => document.activeElement === element")
    graphic_title.fill("Graphic note")
    graphic.locator(".user-note-body-input").fill("Review the manifold graphic.")
    graphic.locator(".user-note-close").click()
    repo_browser_graph.click_concept("gr.line_element")
    repo_browser_graph.click_concept("gr.metric_tensor")
    graphic = page.locator('#info_panel [data-content-block-id="gr.metric_tensor.graphic"]')
    assert graphic.locator("details.user-note > summary").inner_text() == "Graphic note"
    assert page.locator("#info_panel .kg-unmatched-notes").count() == 0

    study = page.locator("#info_panel details.study-questions")
    study.locator(":scope > summary .kg-note-block-action").click()
    assert study.get_attribute("data-note-placement") is None
    assert study.locator("details.user-note").count() == 1
    assert study.locator(".user-note-title-input").evaluate(
        "element => document.activeElement === element"
    )


@pytest.mark.browser
def test_touch_scroll_does_not_place_note(repo_browser_graph):
    page = repo_browser_graph.page
    repo_browser_graph.open_control_section("kg_modules_section")
    page.locator(
        '.kg-module-item[data-module-id="math.m01_manifolds_and_coordinates"]'
    ).click()
    overview = page.locator(
        '#info_panel [data-content-block-id='
        '"math.m01_manifolds_and_coordinates.overview"]'
    )
    overview.locator(":scope > summary .kg-note-block-action").click()
    first_paragraph = overview.locator(":scope > .content-block-body .concept-line").first
    first_paragraph.evaluate(
        """element => {
          element.dispatchEvent(new PointerEvent('pointerdown', {
            bubbles: true, clientX: 10, clientY: 10
          }));
          element.dispatchEvent(new PointerEvent('pointermove', {
            bubbles: true, clientX: 10, clientY: 35
          }));
          element.dispatchEvent(new PointerEvent('pointerup', {
            bubbles: true, clientX: 10, clientY: 35
          }));
          element.click();
        }"""
    )

    assert overview.locator("details.user-note").count() == 0
    assert overview.get_attribute("data-note-placement") == "active"


@pytest.mark.browser
def test_user_notes_default_to_reading_and_remain_editable(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("2.1")
    assert page.locator("#info_panel .kg-add-note").first.is_visible() is False

    assert page.locator("#info_panel .kg-add-note").count() > 0
    assert page.locator("#info_panel .kg-add-note").first.is_visible() is False

    _place_note_at_anchor(page.locator("#info_panel .kg-add-note").first)
    note = page.locator("#info_panel details.user-note").first
    assert note.is_visible()
    assert note.get_attribute("open") is not None

    note.locator(".user-note-title-input").fill("Check this derivation")
    note.locator(".user-note-body-input").fill("This should become an optional detail later.")
    assert note.locator(".user-note-body-input").evaluate(
        "el => getComputedStyle(el).fontWeight"
    ) in {"400", "normal"}

    stored = page.evaluate(
        """() => JSON.parse(localStorage.getItem("srkg.userNotes.v1")).notes"""
    )
    assert len(stored) == 1
    assert stored[0]["targetType"] == "concept"
    assert stored[0]["targetId"] == "2.1"
    assert stored[0]["conceptId"] == "2.1"
    assert stored[0]["title"] == "Check this derivation"
    assert stored[0]["body"] == "This should become an optional detail later."
    _hover_beta_node(page)
    tooltip_text = page.locator("#kg_node_tooltip").inner_text()
    assert "Check this derivation" in tooltip_text
    assert "This should become an optional detail later." not in tooltip_text
    page.locator("#kg_notes_section summary").click()
    assert page.locator("#kg_notes_list .kg-note-list-item").count() == 1
    list_item = page.locator("#kg_notes_list .kg-note-list-item")
    assert list_item.get_attribute("data-target-type") == "concept"
    assert list_item.get_attribute("data-target-id") == "2.1"
    _reveal_note_parents(page)
    assert "Check this derivation" in list_item.inner_text()

    note.locator(".user-note-close").click()
    note = page.locator("#info_panel details.user-note").first
    assert note.get_attribute("open") is not None
    _reveal_note_parents(page)
    assert note.locator(".user-note-reading").inner_text() == "This should become an optional detail later."
    _reveal_note_parents(page)
    assert note.locator("summary").inner_text() == "Check this derivation"

    assert page.locator("#info_panel .kg-add-note").first.is_visible() is False
    assert page.locator("#info_panel .user-note-title-input").count() == 0
    assert page.locator("#info_panel .user-note-body-input").count() == 0
    _reveal_note_parents(page)
    assert page.locator("#info_panel details.user-note summary").inner_text() == (
        "Check this derivation"
    )
    page.locator("#info_panel details.user-note summary").click()
    page.locator("#info_panel details.user-note summary").click()
    assert page.locator("#info_panel .user-note-body-input").count() == 0
    page.locator("#info_panel .user-note-edit").click()
    _reveal_note_parents(page)
    assert page.locator("#info_panel .user-note-body-input").input_value() == (
        "This should become an optional detail later."
    )

    page.reload(wait_until="domcontentloaded")
    page.wait_for_selector("#kg_controls", state="attached")
    page.wait_for_function(
        """() =>
          typeof network !== "undefined" &&
          typeof nodes !== "undefined" &&
          typeof edges !== "undefined"
        """
    )
    browser_graph.click_concept("2.1")
    _reveal_note_parents(page)
    assert page.locator("#info_panel details.user-note summary").inner_text() == (
        "Check this derivation"
    )


@pytest.mark.browser
def test_closing_default_empty_note_deletes_it_and_restores_anchor(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("2.1")
    _place_note_at_anchor(page.locator("#info_panel .kg-add-note").first)

    assert page.locator("#info_panel details.user-note").count() == 1
    page.locator("#info_panel .user-note-close").click()

    assert page.locator("#info_panel details.user-note").count() == 0
    assert page.locator("#info_panel .kg-add-note").first.is_visible() is False
    assert page.locator("#kg_notes_list .kg-note-list-item").count() == 0
    assert page.locator("#kg_notes_list .kg-note-list-empty").count() == 1
    assert page.evaluate(
        """() => JSON.parse(localStorage.getItem("srkg.userNotes.v1")).notes.length"""
    ) == 0


@pytest.mark.browser
def test_notes_panel_list_navigates_to_note_concept(browser_graph):
    page = browser_graph.page

    page.locator("#kg_notes_section summary").click()
    browser_graph.click_concept("2.1")
    _place_note_at_anchor(page.locator("#info_panel .kg-add-note").first)
    page.locator("#info_panel .user-note-title-input").fill("Beta note")
    page.locator("#info_panel .user-note-body-input").fill("Remember beta.")
    page.locator("#info_panel .user-note-close").click()

    browser_graph.click_concept("1.1")
    _place_note_at_anchor(page.locator("#info_panel .kg-add-note").first)
    page.locator("#info_panel .user-note-title-input").fill("Alpha note")
    page.locator("#info_panel .user-note-body-input").fill("Remember alpha.")
    page.locator("#info_panel .user-note-close").click()

    list_items = page.locator("#kg_notes_list .kg-note-list-item")
    assert list_items.count() == 2
    assert list_items.nth(0).get_attribute("data-target-type") == "concept"
    assert list_items.nth(0).get_attribute("data-target-id") == "1.1"
    assert "Alpha note" in list_items.nth(0).inner_text()
    assert list_items.nth(1).get_attribute("data-target-type") == "concept"
    assert list_items.nth(1).get_attribute("data-target-id") == "2.1"
    assert "Beta note" in list_items.nth(1).inner_text()

    list_items.nth(1).click()

    assert page.locator("#info_panel").get_attribute("data-concept-id") == "2.1"
    assert page.evaluate("() => window.location.hash") == "#concept-2.1"
    assert page.locator("#info_panel details.user-note summary").inner_text() == "Beta note"


@pytest.mark.browser
def test_user_notes_export_and_import_csv(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("2.1")
    page.locator("#kg_notes_section summary").click()
    _place_note_at_anchor(page.locator("#info_panel .kg-add-note").first)
    page.locator("#info_panel .user-note-title-input").fill("Exported title")
    page.locator("#info_panel .user-note-body-input").fill("Exported body")

    with page.expect_download() as download_info:
        page.locator("#kg_notes_export").click()
    download = download_info.value
    csv_text = download.path().read_text(encoding="utf-8")
    rows = list(csv.DictReader(csv_text.splitlines()))
    assert rows[0]["concept_id"] == "2.1"
    assert rows[0]["concept_label"] == "Beta"
    assert rows[0]["target_type"] == "concept"
    assert rows[0]["target_id"] == "2.1"
    assert rows[0]["title"] == "Exported title"
    assert rows[0]["body"] == "Exported body"
    assert rows[0]["anchor_block_id"] == "2.1.definition"
    assert rows[0]["anchor_section_key"] == ""
    assert "anchor_context_before" in rows[0]
    assert "anchor_context_after" in rows[0]

    page.evaluate("""() => {
      localStorage.removeItem("srkg.userNotes.v1");
      localStorage.removeItem("srkg.personalData.v1");
    }""")
    page.reload(wait_until="domcontentloaded")
    page.wait_for_selector("#kg_controls", state="attached")
    page.wait_for_function("""() => typeof network !== "undefined" && typeof nodes !== "undefined" """)

    import_path = browser_graph.output_path.parent / "import-notes.csv"
    imported_row = rows[0]
    imported_row["note_id"] = "imported-note-1"
    imported_row["title"] = "Imported title"
    imported_row["body"] = "Imported body"
    with import_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(imported_row))
        writer.writeheader()
        writer.writerow(imported_row)

    page.locator("#kg_notes_import_input").set_input_files(str(import_path))
    browser_graph.click_concept("2.1")
    _reveal_note_parents(page)
    assert page.locator("#info_panel details.user-note summary").inner_text() == (
        "Imported title"
    )
    page.locator("#info_panel details.user-note summary").click()
    assert page.locator("#info_panel .user-note-body-input").count() == 0
    _reveal_note_parents(page)
    assert page.locator("#info_panel .user-note-reading").inner_text() == "Imported body"


@pytest.mark.browser
def test_module_overview_and_concept_graphic_have_note_hooks(browser_graph):
    page = browser_graph.page

    page.locator("#kg_notes_section summary").click()
    browser_graph.click_concept("2.2")
    graphic = page.locator("#info_panel .concept-figure")
    assert graphic.locator(".kg-add-note").count() == 1
    _place_note_at_anchor(graphic.locator(".kg-add-note"))
    graphic.locator(".user-note-title-input").fill("Review graphic")
    graphic.locator(".user-note-body-input").fill("Check the arrows.")
    graphic.locator(".user-note-close").click()

    browser_graph.open_control_section("kg_modules_section")
    page.locator('.kg-module-item[data-module-id="test.m01_foundations"]').click()
    overview = page.locator("#info_panel .module-content-block").first
    assert overview.locator(".kg-add-note").count() > 0
    if not overview.evaluate("el => el.open"):
        overview.locator(":scope > summary").click()
    _place_note_at_anchor(overview.locator(".kg-add-note").first)
    overview.locator(".user-note-title-input").fill("Review module overview")
    overview.locator(".user-note-body-input").fill("Tighten this introduction.")
    overview.locator(".user-note-close").click()

    stored = page.evaluate(
        "() => JSON.parse(localStorage.getItem('srkg.userNotes.v1')).notes"
    )
    assert [(note["targetType"], note["targetId"]) for note in stored] == [
        ("concept", "2.2"),
        ("module", "test.m01_foundations"),
    ]
    module_item = page.locator("#kg_notes_list .kg-note-list-item").filter(
        has_text="Review module overview"
    )
    assert module_item.get_attribute("data-target-type") == "module"
    assert module_item.get_attribute("data-target-id") == "test.m01_foundations"

    browser_graph.click_concept("1.1")
    module_item.click()
    assert page.locator("#info_panel").get_attribute("data-module-id") == "test.m01_foundations"
    assert page.locator("#info_panel details.user-note summary").inner_text() == (
        "Review module overview"
    )


@pytest.mark.browser
def test_module_example_note_stays_at_its_anchor(repo_browser_graph):
    page = repo_browser_graph.page

    page.locator("#kg_notes_section summary").click()
    repo_browser_graph.open_control_section("kg_modules_section")
    page.locator(
        '.kg-module-item[data-module-id="math.m01_manifolds_and_coordinates"]'
    ).click()

    example = page.locator(
        '#info_panel .module-content-block[data-content-block-id='
        '"math.m01_manifolds_and_coordinates.terrain_setup"]'
    )
    if not example.evaluate("element => element.open"):
        example.locator(":scope > summary").click()
    add_note = example.locator(".kg-add-note").last
    add_note.evaluate(
        "element => element.setAttribute('data-anchor-context-before', 'corrupted')"
    )
    _place_note_at_anchor(add_note)

    assert example.locator("details.user-note").count() == 1
    assert page.locator("#info_panel .kg-unmatched-notes").count() == 0


@pytest.mark.browser
def test_legacy_module_note_with_corrupted_context_recovers_by_paragraph(repo_browser_graph):
    page = repo_browser_graph.page
    repo_browser_graph.open_control_section("kg_modules_section")
    module_selector = (
        '.kg-module-item[data-module-id="math.m01_manifolds_and_coordinates"]'
    )
    page.locator(module_selector).click()

    example_selector = (
        '#info_panel .module-content-block[data-content-block-id='
        '"math.m01_manifolds_and_coordinates.terrain_setup"]'
    )
    example = page.locator(example_selector)
    if not example.evaluate("element => element.open"):
        example.locator(":scope > summary").click()
    _place_note_at_anchor(example.locator(".kg-add-note").last)
    example.locator(".user-note-title-input").fill("Recovered field note")
    example.locator(".user-note-body-input").fill("Keep this beside the survey setup.")
    example.locator(".user-note-close").click()

    page.evaluate("""() => {
      const legacy = JSON.parse(localStorage.getItem('srkg.userNotes.v1'));
      const profile = JSON.parse(localStorage.getItem('srkg.personalData.v1'));
      [legacy.notes[0], profile.notes.find(note => !note.deletedAt)].forEach(note => {
        note.anchor.contextBefore = 'corrupted legacy context';
        note.anchor.contextAfter = 'corrupted legacy context';
      });
      localStorage.setItem('srkg.userNotes.v1', JSON.stringify(legacy));
      localStorage.setItem('srkg.personalData.v1', JSON.stringify(profile));
    }""")
    page.reload(wait_until="domcontentloaded")
    page.wait_for_function(
        "() => typeof network !== 'undefined' && typeof nodes !== 'undefined'"
    )
    repo_browser_graph.open_control_section("kg_modules_section")
    page.locator(module_selector).click()

    example = page.locator(example_selector)
    _reveal_note_parents(page)
    assert example.locator("details.user-note summary").inner_text() == (
        "Recovered field note"
    )
    assert page.locator("#info_panel .kg-unmatched-notes").count() == 0


@pytest.mark.browser
def test_study_questions_share_one_stable_note_anchor(browser_graph):
    page = browser_graph.page
    browser_graph.click_concept("2.1")
    page.locator("#kg_notes_section summary").click()
    study = page.locator("#info_panel details.study-questions")
    assert study.locator(".kg-add-note").count() == 1
    if not study.evaluate("element => element.open"):
        study.locator(":scope > summary").click()
    _place_note_at_anchor(study.locator(".kg-add-note"))
    study.locator(".user-note-title-input").fill("Review the question set")
    study.locator(".user-note-body-input").fill("Return to these questions later.")
    study.locator(".user-note-close").click()

    stored = page.evaluate(
        "() => JSON.parse(localStorage.getItem('srkg.userNotes.v1')).notes[0]"
    )
    assert stored["anchor"]["sectionKey"] == "study-questions"
    assert stored["section"] == "Study Questions"

    browser_graph.click_concept("1.1")
    browser_graph.click_concept("2.1")
    study = page.locator("#info_panel details.study-questions")
    if not study.evaluate("element => element.open"):
        study.locator(":scope > summary").click()
    assert study.locator("details.user-note summary").inner_text() == (
        "Review the question set"
    )
    assert page.locator("#info_panel .kg-unmatched-notes").count() == 0


@pytest.mark.browser
def test_legacy_concept_note_csv_still_imports(browser_graph):
    page = browser_graph.page
    import_path = browser_graph.output_path.parent / "legacy-notes.csv"
    fieldnames = [
        "note_id", "concept_id", "concept_label", "section", "anchor_index",
        "anchor_after", "title", "body", "created_at", "updated_at",
    ]
    with import_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow({
            "note_id": "legacy-note",
            "concept_id": "2.1",
            "concept_label": "Beta",
            "section": "Definition",
            "anchor_index": "0",
            "anchor_after": "",
            "title": "Legacy note",
            "body": "Still readable.",
            "created_at": "2026-01-01T00:00:00Z",
            "updated_at": "2026-01-01T00:00:00Z",
        })

    page.locator("#kg_notes_import_input").set_input_files(str(import_path))
    browser_graph.click_concept("2.1")

    _reveal_note_parents(page)
    assert page.locator("#info_panel details.user-note summary").inner_text() == "Legacy note"
    stored = page.evaluate(
        "() => JSON.parse(localStorage.getItem('srkg.userNotes.v1')).notes[0]"
    )
    assert stored["targetType"] == "concept"
    assert stored["targetId"] == "2.1"


@pytest.mark.browser
def test_legacy_local_storage_note_is_loaded_and_migrated(browser_graph):
    page = browser_graph.page
    page.evaluate("""() => {
      localStorage.removeItem('srkg.personalData.v1');
      localStorage.setItem('srkg.userNotes.v1', JSON.stringify({
      version: 1,
      notes: [{
        id: 'stored-v1-note',
        conceptId: '2.1',
        section: 'Definition',
        anchor: {blockIndex: 0, afterText: ''},
        title: 'Stored legacy note',
        body: 'Preserve this browser-local note.',
        createdAt: '2026-01-01T00:00:00Z',
        updatedAt: '2026-01-01T00:00:00Z'
      }]
      }));
    }""")
    page.reload(wait_until="domcontentloaded")
    page.wait_for_function("() => typeof network !== 'undefined'")
    browser_graph.click_concept("2.1")

    _reveal_note_parents(page)
    assert page.locator("#info_panel details.user-note summary").inner_text() == (
        "Stored legacy note"
    )
    stored = page.evaluate(
        "() => JSON.parse(localStorage.getItem('srkg.userNotes.v1'))"
    )
    assert stored["version"] == 2
    assert stored["notes"][0]["anchor"]["blockId"] == "2.1.definition"


@pytest.mark.browser
def test_note_hooks_follow_optional_details_and_display_equations(mathjax_browser_graph):
    page = mathjax_browser_graph.page

    mathjax_browser_graph.click_concept("2.1")
    page.locator("#info_panel > details.content-block").evaluate_all("es=>es.forEach(e=>e.open=true)")
    page.locator("#kg_notes_section summary").click()
    section = page.locator('#info_panel [data-content-block-id="2.1.explanation"]')
    assert section.locator(".optional-detail").count() == 1
    page.wait_for_selector(
        '#info_panel [data-content-block-id="2.1.explanation"] mjx-container[display="true"]'
    )

    section.locator(":scope > summary .kg-note-block-action").click()
    assert section.locator('.concept-line[tabindex="0"]').count() >= 4
    assert section.evaluate(
        """section => {
          const optional = section.querySelector(".optional-detail");
          const line = optional && optional.closest(".concept-line");
          return Boolean(line && line.getAttribute("aria-label") ===
            "Place note after this paragraph");
        }"""
    )
    assert section.evaluate(
        """section => {
          const equation = section.querySelector('mjx-container[display="true"]');
          const line = equation && equation.closest(".concept-line");
          return Boolean(line && line.getAttribute("aria-label") ===
            "Place note after this paragraph");
        }"""
    )


@pytest.mark.browser
def test_note_uses_stable_block_id_across_section_rename(browser_graph):
    page = browser_graph.page
    browser_graph.click_concept("2.1")
    page.locator("#kg_notes_section summary").click()
    definition = page.locator('#info_panel [data-content-block-id="2.1.definition"]')
    _place_note_at_anchor(definition.locator(".kg-add-note").first)
    definition.locator(".user-note-title-input").fill("Stable definition note")
    definition.locator(".user-note-body-input").fill("Keep this with the definition.")
    definition.locator(".user-note-close").click()

    stored = page.evaluate(
        "() => JSON.parse(localStorage.getItem('srkg.userNotes.v1')).notes[0]"
    )
    assert stored["anchor"]["blockId"] == "2.1.definition"

    page.evaluate("""() => {
      conceptData['2.1'].content_blocks.find(block => block.kind === 'definition').title =
        'Renamed definition';
    }""")
    browser_graph.click_concept("1.1")
    browser_graph.click_concept("2.1")

    renamed = page.locator('#info_panel [data-content-block-id="2.1.definition"]')
    assert renamed.locator(":scope > summary .content-block-title-text").filter(has_text="Renamed definition").count() == 1
    _reveal_note_parents(page)
    assert renamed.locator("details.user-note summary").inner_text() == "Stable definition note"
    assert page.locator("#info_panel .kg-unmatched-notes").count() == 0


@pytest.mark.browser
def test_note_context_survives_paragraph_insertion_and_splitting(browser_graph):
    page = browser_graph.page
    browser_graph.click_concept("2.1")
    page.locator("#kg_notes_section summary").click()
    explanation = page.locator('#info_panel [data-content-block-id="2.1.explanation"]')
    anchor = explanation.locator(".kg-add-note").last
    _place_note_at_anchor(anchor)
    explanation.locator(".user-note-title-input").fill("Context note")
    explanation.locator(".user-note-body-input").fill("Remain after the final passage.")
    explanation.locator(".user-note-close").click()

    page.evaluate("""() => {
      const section = conceptData['2.1'].content_blocks.find(item => item.kind === 'explanation');
      section.body = 'An inserted opening paragraph.\\n' +
        section.body.replace('After the display equation.', 'After the display\\n equation.');
    }""")
    browser_graph.click_concept("1.1")
    browser_graph.click_concept("2.1")

    explanation = page.locator('#info_panel [data-content-block-id="2.1.explanation"]')
    note = explanation.locator("details.user-note")
    _reveal_note_parents(page)
    assert note.locator("summary").inner_text() == "Context note"
    assert page.locator("#info_panel .kg-unmatched-notes").count() == 0


@pytest.mark.browser
def test_unmatched_note_is_preserved_and_visibly_flagged(browser_graph):
    page = browser_graph.page
    browser_graph.click_concept("2.1")
    page.locator("#kg_notes_section summary").click()
    explanation = page.locator('#info_panel [data-content-block-id="2.1.explanation"]')
    _place_note_at_anchor(explanation.locator(".kg-add-note").last)
    explanation.locator(".user-note-title-input").fill("Orphaned passage note")
    explanation.locator(".user-note-body-input").fill("Do not lose this note.")
    explanation.locator(".user-note-close").click()

    page.evaluate("""() => {
      conceptData['2.1'].content_blocks.find(
        item => item.kind === 'explanation'
      ).body = 'Completely replacement prose with no original anchor context.';
    }""")
    browser_graph.click_concept("1.1")
    browser_graph.click_concept("2.1")

    unmatched = page.locator("#info_panel .kg-unmatched-notes")
    assert unmatched.count() == 1
    assert "Orphaned passage note" in unmatched.inner_text()
    assert "Explanation" in unmatched.inner_text()
    assert page.locator("#kg_notes_list .kg-note-list-warning").inner_text() == "Needs placement"
    stored = page.evaluate(
        "() => JSON.parse(localStorage.getItem('srkg.userNotes.v1')).notes[0]"
    )
    assert stored["title"] == "Orphaned passage note"


@pytest.mark.parametrize("width", [390, 1280])
@pytest.mark.parametrize("saved_count", [0, 12])
def test_tutorial_hover_keeps_notes_compact_and_ignores_empty_drafts(browser_graph, width, saved_count):
    page = browser_graph.page
    page.set_viewport_size({"width": width, "height": 844})
    page.evaluate("""count => {
      const notes = Array.from({length:count + 4}, (_, i) => ({
        id:'hover-note-' + i, targetType:'concept', targetId:'2.1',
        conceptId:'2.1', section:'Definition', anchor:{blockIndex:0},
        title:'Note', body:i < count ? 'Saved reminder ' + i : '',
        createdAt:'2026-01-01T00:00:00Z', updatedAt:'2026-01-01T00:00:00Z'
      }));
      kgPersonalData.replaceNotes(notes);
    }""", saved_count)
    page.reload(wait_until="domcontentloaded")
    page.wait_for_function("typeof kgExecuteViewerCommand === 'function'")
    before = page.evaluate("kgPersonalData.getSnapshot()")
    page.evaluate("kgExecuteViewerCommand({command:'show-graph-concept-hover',target:'concept:2.1'}, {origin:'tutorial'})")
    tooltip = page.locator("#kg_node_tooltip")
    assert tooltip.is_visible()
    if saved_count:
        assert tooltip.locator("ul").last.locator("li").count() == 3
        assert f"{saved_count - 3} more notes" in tooltip.inner_text()
    else:
        assert "Notes" not in tooltip.inner_text()
    assert page.evaluate("kgPersonalData.getSnapshot()") == before


@pytest.mark.browser
def test_legacy_section_note_migrates_to_the_canonical_block(browser_graph):
    page = browser_graph.page
    page.evaluate("""() => {
      const profile = kgPersonalData.getSnapshot();
      profile.notes.push({id:'legacy-section-key',targetType:'concept',targetId:'2.1',
        conceptId:'2.1',section:'Definition',title:'A legacy section note',body:'Keep this note.',
        anchor:{blockId:'',sectionKey:'legacy:definition',blockIndex:0,afterText:'',
          contextBefore:'',contextAfter:''},
        createdAt:'2026-10-01T12:00:00Z',updatedAt:'2026-10-01T12:00:00Z',deletedAt:''});
      kgPersonalData.replaceSnapshot(profile);
    }""")
    page.reload(wait_until='domcontentloaded')
    page.wait_for_function("() => typeof kgViewerStateSnapshot === 'function'")
    browser_graph.click_concept('2.1')
    _reveal_note_parents(page)
    assert page.locator('#info_panel details.user-note summary').inner_text() == 'A legacy section note'
    anchor = page.evaluate("kgPersonalData.getSnapshot().notes.find(n => n.id === 'legacy-section-key').anchor")
    assert anchor['blockId'] == '2.1.definition'
    assert anchor['sectionKey'] == ''
    assert page.locator('#info_panel .kg-unmatched-notes').count() == 0


@pytest.mark.browser
def test_note_reading_is_safe_and_done_does_not_fold_parent(browser_graph):
    page = browser_graph.page
    browser_graph.click_concept('2.1')
    _place_note_at_anchor(page.locator('#info_panel .kg-add-note').first)
    note = page.locator('#info_panel details.user-note').first
    parent = note.locator('xpath=ancestor::details[1]')
    note.locator('.user-note-title-input').fill('Personal explanation')
    note.locator('.user-note-body-input').fill('<img src=x onerror="window.noteInjected=true">\n\nSecond paragraph')
    note.locator('.user-note-close').click()
    assert parent.evaluate('el => el.open')
    assert note.evaluate('el => el.open')
    assert note.locator('.user-note-reading .concept-line').last.inner_text() == 'Second paragraph'
    assert note.locator('img').count() == 0
    assert not page.evaluate('Boolean(window.noteInjected)')
    assert note.get_attribute('data-content-origin') == 'personal'
    assert parent.get_attribute('data-content-origin') == 'authored'
    assert note.locator('input, textarea, .user-note-delete, .content-read-toggle').count() == 0
    note.locator(':scope > summary').click()
    note.locator(':scope > summary').click()
    assert note.locator('textarea').count() == 0
    note.locator('.user-note-edit').click()
    assert note.locator('.user-note-body-input').input_value().endswith('Second paragraph')



@pytest.mark.browser
def test_insert_maths_replaces_selection_and_persists(browser_graph):
    page = browser_graph.page
    browser_graph.click_concept('2.1')
    _place_note_at_anchor(page.locator('#info_panel .kg-add-note').first)
    body = page.locator('#info_panel .user-note-body-input')
    body.fill('Before replace after')
    body.evaluate('el => { el.focus(); el.setSelectionRange(7, 14); }')
    page.get_by_role('button', name='Insert maths', exact=True).click()
    sample = r'\(\gamma = 1/\sqrt{1-v^2/c^2}\)'
    _reveal_note_parents(page)
    assert body.input_value() == 'Before ' + sample + ' after'
    assert body.evaluate('el => [el.selectionStart, el.selectionEnd]') == [7 + len(sample)] * 2
    stored = page.evaluate('kgPersonalData.getSnapshot().notes[0].body')
    _reveal_note_parents(page)
    assert stored == body.input_value()
    browser_graph.click_concept('1.1')
    browser_graph.click_concept('2.1')
    _reveal_note_parents(page)
    assert page.locator('#info_panel .user-note-body-input').input_value() == stored
    page.locator('#info_panel .user-note-close').click()
    profile = page.evaluate('''() => kgPersonalDataArchive.importBytes(
        kgPersonalDataArchive.exportBytes(kgPersonalData.getSnapshot()))''')
    assert profile['notes'][0]['body'] == stored


@pytest.mark.browser
def test_note_inline_and_display_maths_render(mathjax_browser_graph):
    graph = mathjax_browser_graph
    page = graph.page
    graph.click_concept('2.1')
    _place_note_at_anchor(page.locator('#info_panel .kg-add-note').first)
    page.locator('#info_panel .user-note-body-input').fill(
        r'Inline \(\gamma\).' + '\n\n' + r'\[E=mc^2\]')
    page.locator('#info_panel .user-note-close').click()
    reading = page.locator('#info_panel .user-note-reading')
    reading.locator('mjx-container').first.wait_for()
    assert reading.locator('mjx-container').count() == 2
    assert reading.locator('mjx-container[display="true"]').count() == 1
    assert reading.locator('mjx-merror, [data-mjx-error]').count() == 0


@pytest.mark.browser
@pytest.mark.parametrize('owner', ['concept', 'module'])
def test_owner_note_placement_navigation_and_round_trip(browser_graph, owner):
    page = browser_graph.page
    browser_graph.click_concept('2.1')
    owner_id = '2.1'
    if owner == 'module':
        browser_graph.open_control_section('kg_modules_section')
        owner_id = 'test.m01_foundations'
        page.locator(f'.kg-module-item[data-module-id="{owner_id}"]').click()
    page.locator('#info_panel .kg-note-owner-action').click()
    note = page.locator('#info_panel .kg-owner-notes details.user-note')
    note.locator('.user-note-title-input').fill('My extra explanation')
    note.locator('.user-note-body-input').fill('Independent of any paragraph.')
    note.locator('.user-note-close').click()
    assert note.locator('textarea').count() == 0
    stored = page.evaluate('kgPersonalData.getSnapshot().notes[0]')
    assert (stored['placement'], stored['targetType'], stored['targetId']) == ('owner', owner, owner_id)
    assert stored['anchor']['blockId'] == ''
    browser_graph.click_concept('1.1')
    browser_graph.open_control_section('kg_notes_section')
    page.locator('#kg_notes_list .kg-note-list-item').click()
    assert note.is_visible()
    assert note.evaluate('el => el.open')
    assert note.locator('.user-note-reading').inner_text() == 'Independent of any paragraph.'
    assert page.locator('#info_panel .kg-unmatched-notes').count() == 0
    with page.expect_download() as download:
        page.locator('#kg_notes_export').click()
    rows = list(csv.DictReader(download.value.path().read_text().splitlines()))
    assert rows[0]['placement'] == 'owner'
    page.evaluate('kgPersonalData.replaceNotes([])')
    page.reload(wait_until='domcontentloaded')
    page.wait_for_function('Boolean(window.kgPersonalData)')
    page.locator('#kg_notes_import_input').set_input_files(str(download.value.path()))
    browser_graph.open_control_section('kg_notes_section')
    page.locator('#kg_notes_list .kg-note-list-item').click()
    assert page.locator('#info_panel .kg-owner-notes .user-note-reading').inner_text() == 'Independent of any paragraph.'


@pytest.mark.browser
def test_authored_derivation_clarifications_render_with_shared_disclosures(mathjax_browser_graph):
    from pathlib import Path
    root = Path(__file__).resolve().parents[2]
    with (root / 'domains/sr/data/content_blocks.csv').open() as source:
        block = next(row for row in csv.DictReader(source)
                     if row['block_id'] == 'sr.momentum_four_vector.work_energy')
    page = mathjax_browser_graph.page
    page.evaluate('''async body => {
      const markup = kgCreateContentMarkup({concept: () => null, hash: id => '#' + id});
      const container = document.createElement('section');
      container.id = 'derivation-clarification-test';
      container.innerHTML = markup.renderBodyLines(body);
      document.getElementById('info_panel').appendChild(container);
      await MathJax.typesetPromise([container]);
    }''', block['body'])
    details = page.locator('#derivation-clarification-test .optional-detail')
    assert details.count() == 2
    for disclosure in details.all():
        assert not disclosure.evaluate('el => el.open')
        assert disclosure.get_attribute('data-content-origin') == 'authored'
        assert 'kg-content-unit' in disclosure.get_attribute('class')
        disclosure.locator(':scope > summary').click()
        assert disclosure.locator('mjx-container').count() > 0
    assert page.locator('#derivation-clarification-test [data-mjx-error]').count() == 0


@pytest.mark.browser
def test_folding_an_editor_returns_to_reading_without_losing_draft(browser_graph):
    page = browser_graph.page
    browser_graph.click_concept('2.1')
    _place_note_at_anchor(page.locator('#info_panel .kg-add-note').first)
    note = page.locator('#info_panel details.user-note')
    note.locator('.user-note-title-input').fill('Draft retained')
    note.locator('.user-note-body-input').fill('Keep my words.')
    note.locator(':scope > summary').click()
    page.wait_for_function("!document.querySelector('#info_panel .user-note-body-input')")
    before = page.evaluate('kgPersonalData.getSnapshot().notes[0].updatedAt')
    note.locator(':scope > summary').focus()
    page.keyboard.press('Enter')
    assert note.locator('.user-note-reading').inner_text() == 'Keep my words.'
    note.locator(':scope > summary').click()
    note.locator(':scope > summary').click()
    assert page.evaluate('kgPersonalData.getSnapshot().notes[0].updatedAt') == before
    note.locator('.user-note-edit').focus()
    page.keyboard.press('Enter')
    assert note.locator('.user-note-body-input').input_value() == 'Keep my words.'
    note.locator('.user-note-close').click()
    assert page.evaluate('kgPersonalData.getSnapshot().notes[0].updatedAt') == before


@pytest.mark.browser
def test_personal_notes_do_not_change_read_completion(browser_graph):
    graph = browser_graph
    page = graph.page
    graph.click_concept('2.2')
    page.locator('#info_panel details.content-block').evaluate_all('es=>es.forEach(e=>e.open=true)')
    for checkbox in page.locator('#info_panel details.content-block > summary .content-block-read-toggle').all():
        checkbox.check()
    indicator = page.locator('#info_panel .concept-sticky-header .content-read-complete-indicator')
    assert indicator.is_visible()
    before = page.evaluate('kgPersonalData.getSnapshot().readingProgress')
    page.locator('#info_panel .kg-note-owner-action').click()
    note = page.locator('#info_panel .kg-owner-notes .user-note')
    note.locator('.user-note-body-input').fill('Unfinished personal work.')
    note.locator('.user-note-close').click()
    assert indicator.is_visible()
    assert page.evaluate('kgPersonalData.getSnapshot().readingProgress') == before
    assert note.locator('.content-block-read-toggle').count() == 0


@pytest.mark.browser
def test_mobile_owner_note_math_editing(mobile_repo_browser_graph):
    graph = mobile_repo_browser_graph
    page = graph.page
    graph.click_concept('sr.momentum_four_vector')
    page.locator('#info_panel .kg-note-owner-action').tap()
    note = page.locator('#info_panel .kg-owner-notes .user-note')
    note.locator('.user-note-title-input').fill('My calculation')
    note.locator('.user-note-body-input').fill('Check: ')
    note.get_by_role('button', name='Insert maths').tap()
    note.get_by_role('button', name='Done', exact=True).tap()
    note.locator('.user-note-reading mjx-container').wait_for()
    assert note.locator('textarea').count() == 0
    assert page.locator('#info_panel').evaluate('el => el.scrollWidth <= el.clientWidth + 1')
    note.locator('.user-note-edit').tap()
    assert r'\gamma' in note.locator('textarea').input_value()


@pytest.mark.browser
def test_done_and_notes_list_reveal_note_below_sticky_contents(repo_browser_graph):
    graph = repo_browser_graph
    page = graph.page
    graph.click_concept('sr.momentum_four_vector')
    page.locator('#info_panel .kg-note-owner-action').click()
    note = page.locator('#info_panel .kg-owner-notes .user-note')
    note.locator('.user-note-title-input').fill('Read this addition')
    note.locator('textarea').fill('A short reading note after a large contents list.')
    note.locator('.user-note-close').click()
    page.wait_for_function('''() => {
      const note = document.querySelector('#info_panel .kg-owner-notes .user-note');
      const header = document.querySelector('#info_panel .concept-sticky-header');
      return note.getBoundingClientRect().top >= header.getBoundingClientRect().bottom;
    }''')


@pytest.mark.browser
def test_note_placement_does_not_offer_personal_paragraphs_as_targets(browser_graph):
    graph = browser_graph
    page = graph.page
    graph.click_concept('2.1')
    _place_note_at_anchor(page.locator('#info_panel .kg-add-note').first)
    note = page.locator('#info_panel .user-note')
    note.locator('textarea').fill('My personal explanation.')
    note.locator('.user-note-close').click()
    block = note.locator('xpath=ancestor::*[@data-note-block][1]')
    block.locator(':scope > summary .kg-note-block-action').click()
    assert note.locator('.concept-line').get_attribute('tabindex') is None
    assert block.locator('.concept-line[tabindex="0"]').count() > 0
    note.locator('.concept-line').click()
    assert page.locator('#info_panel .user-note').count() == 1


@pytest.mark.browser
def test_content_units_nest_without_inheriting_origin_or_capabilities(browser_graph):
    page = browser_graph.page
    result = page.evaluate(r'''() => {
      const markup = kgCreateContentMarkup({concept: () => null, hash: id => '#' + id});
      const host = document.createElement('div');
      host.innerHTML = markup.renderContentUnit({
        level:'block', origin:'authored', title:'Parent', open:true,
        capabilities:{annotate:true, trackRead:true},
        actions:[{capability:'edit', html:'<button data-unit-action>Edit</button>'}],
        body:'A built-in paragraph.', children:[{
          origin:'personal', title:'Personal child', open:true,
          capabilities:{edit:true},
          actions:[{capability:'edit', html:'<button data-unit-action>Edit</button>'}],
          body:'<script>unsafe</script> \\optional_details{Maths}{\\(x^2\\)}',
          children:[{origin:'authored', title:'Grandchild',
                     body:'\\optional_details{Further explanation}{Nested body}'}]
        }]
      });
      return Array.from(host.querySelectorAll('.kg-content-framed')).map(el => ({
        origin:el.dataset.contentOrigin,
        block:el.classList.contains('kg-content-block'),
        edit:el.classList.contains('kg-content-editable'),
        track:el.classList.contains('kg-content-trackable'),
        annotate:el.dataset.noteBlock === 'true',
        actions:el.querySelectorAll(':scope > .kg-content-body > [data-unit-action]').length,
        parent:el.parentElement.closest('.kg-content-framed')?.dataset.contentOrigin || null,
        unsafe:el.querySelector('script') !== null
      }));
    }''')
    assert result == [
        dict(origin='authored', block=True, edit=False, track=True, annotate=True, actions=0, parent=None, unsafe=False),
        dict(origin='personal', block=False, edit=True, track=False, annotate=False, actions=1, parent='authored', unsafe=False),
        dict(origin='personal', block=False, edit=False, track=False, annotate=False, actions=0, parent='personal', unsafe=False),
        dict(origin='authored', block=False, edit=False, track=False, annotate=False, actions=0, parent='personal', unsafe=False),
        dict(origin='authored', block=False, edit=False, track=False, annotate=False, actions=0, parent='authored', unsafe=False),
    ]


@pytest.mark.browser
def test_personal_and_authored_content_share_geometry_at_each_level(browser_graph):
    graph = browser_graph
    page = graph.page
    graph.click_concept('2.1')
    _place_note_at_anchor(page.locator('#info_panel .kg-add-note').first)
    inline = page.locator('#info_panel [data-content-block-id="2.1.definition"] .user-note')
    inline.locator('textarea').fill('An inline personal explanation.')
    inline.locator('.user-note-close').click()
    page.locator('#info_panel .kg-note-owner-action').click()
    owner = page.locator('#info_panel .kg-owner-notes .user-note')
    owner.locator('textarea').fill('A top-level personal explanation.')
    owner.locator('.user-note-close').click()
    authored = page.locator('#info_panel [data-content-block-id="2.1.explanation"]')
    optional = authored.locator('.optional-detail[data-content-origin="authored"]')
    authored.evaluate("e=>e.open=true")
    optional.locator(':scope > summary').click()
    geometry = '''el => {
      const s = getComputedStyle(el);
      return ['paddingLeft','paddingRight','marginLeft','marginRight','borderLeftWidth',
              'borderRightWidth','borderTopWidth','borderBottomWidth','borderRadius']
        .map(key => s[key]);
    }'''
    assert owner.evaluate(geometry) == authored.evaluate(geometry)
    assert inline.evaluate(geometry) == optional.evaluate(geometry)
    for explanation in [inline, optional]:
        assert explanation.evaluate('el => getComputedStyle(el).backgroundColor') == 'rgba(0, 0, 0, 0)'
        assert explanation.evaluate('''el => {
          const enclosing = getComputedStyle(el.parentElement).color;
          return [getComputedStyle(el).color, getComputedStyle(el.querySelector('summary')).color,
                  getComputedStyle(el.querySelector('.kg-content-body')).color]
            .every(color => color === enclosing);
        }''')
    # Origin/kind share geometry. Only folded explanations lose their frame.
    for unit in [owner, inline, authored, optional]:
        summary = unit.locator(':scope > summary')
        title = summary.locator('.content-block-title-line')
        assert summary.bounding_box()['height'] <= title.bounding_box()['height'] + 2
        assert unit.evaluate("el => getComputedStyle(el).borderLeftWidth") == ('1px' if unit in [inline, optional] else '5px')
        assert unit.evaluate("el => getComputedStyle(el).borderTopWidth") == '1px'
        assert unit.evaluate("el => getComputedStyle(el).borderTopStyle") == 'solid'
        assert unit.evaluate("el => getComputedStyle(el).borderTopColor") != 'rgba(0, 0, 0, 0)'
        expanded_geometry = unit.evaluate(geometry)
        unit.locator(':scope > summary').click()
        if unit in [inline, optional]:
            personal_colour = owner.locator(':scope > summary').evaluate('el => getComputedStyle(el).color')
            if unit == inline:
                assert summary.evaluate('el => getComputedStyle(el).color') == personal_colour
            else:
                assert summary.evaluate('el => getComputedStyle(el).color') != personal_colour
            assert unit.evaluate('''el => {
              const s = getComputedStyle(el);
              return [s.borderLeftWidth, s.borderTopWidth, s.paddingTop,
                      s.paddingBottom, s.backgroundColor];
            }''') == ['0px', '0px', '0px', '0px', 'rgba(0, 0, 0, 0)']
            assert unit.bounding_box()['height'] == pytest.approx(summary.bounding_box()['height'], abs=1)
        else:
            assert unit.evaluate(geometry) == expanded_geometry
        unit.locator(':scope > summary').click()
        assert unit.evaluate(geometry) == expanded_geometry
    original_geometry = authored.evaluate(geometry)
    for kind in ['intuition', 'result', 'derivation', 'worked_example', 'convention']:
        authored.evaluate("(el, kind) => el.className = 'kg-content-unit kg-content-framed kg-content-block content-block content-block-' + kind", kind)
        assert authored.evaluate(geometry) == original_geometry
    for note in [owner, inline]:
        assert note.locator(':scope > .user-note-content').evaluate(
            "el => [getComputedStyle(el).borderLeftWidth, getComputedStyle(el).paddingLeft]"
        ) == ['0px', '0px']
        note.locator('.user-note-edit').click()
        assert note.locator('.user-note-editor').evaluate(
            "el => [getComputedStyle(el).borderLeftWidth, getComputedStyle(el).paddingLeft]"
        ) == ['0px', '0px']
        note.locator('.user-note-close').click()
    assert optional.locator(':scope > .optional-detail-body').evaluate(
        "el => [getComputedStyle(el).borderLeftWidth, getComputedStyle(el).paddingLeft]"
    ) == ['0px', '0px']


@pytest.mark.browser
def test_delete_all_notes_confirms_and_syncs_deletions_only(browser_graph):
    graph = browser_graph
    page = graph.page
    page.evaluate('''() => {
      const store = kgPersonalData, now = '2026-10-01T12:00:00Z';
      const snapshot = store.getSnapshot();
      snapshot.notes = [
        {id:'owner-note', targetType:'concept', targetId:'2.1', placement:'owner', section:'Personal notes', anchor:{}},
        {id:'module-note', targetType:'module', targetId:'test.m01_foundations', placement:'owner', section:'Personal notes', anchor:{}},
        {id:'unloaded-note', targetType:'concept', targetId:'other.absent', placement:'owner', section:'Personal notes', anchor:{}},
        {id:'unmatched-note', targetType:'concept', targetId:'2.1', placement:'anchor', section:'Former paragraph', anchor:{blockId:'2.1.removed'}}
      ].map(note => Object.assign(note, {title:note.id, body:'Keep until confirmed', createdAt:now, updatedAt:now}));
      store.mergeSnapshot(snapshot);
      store.addStudyAttempt('2.1.q1', 'correct', now);
      store.setRead('2.1.definition', true);
      store.replaceLayout({published_revision:'unpublished', concepts:{'2.1':{x:25,y:30}}, modules:{}});
    }''')
    page.reload(wait_until='domcontentloaded')
    page.wait_for_function('Boolean(window.kgPersonalData)')
    graph.click_concept('2.1')
    note = page.locator('#info_panel .kg-owner-notes .user-note')
    note.locator(':scope > summary').click()
    note.locator('.user-note-edit').click()
    editor = note.locator('textarea')
    editor.fill('A draft to preserve on cancellation')
    original_editor = editor.element_handle()
    before = page.evaluate('window.__notesBeforeDelete = kgPersonalData.getSnapshot()')
    graph.open_control_section('kg_notes_section')
    assert page.locator('#kg_notes_list .kg-note-list-warning').count() == 2
    button = page.get_by_role('button', name='Delete all notes', exact=True)
    page.once('dialog', lambda dialog: dialog.dismiss())
    button.click()
    assert page.evaluate('kgPersonalData.getSnapshot()') == before
    assert editor.evaluate('(el, original) => el === original', original_editor)
    assert editor.input_value() == 'A draft to preserve on cancellation'
    page.once('dialog', lambda dialog: dialog.accept())
    button.click()
    after = page.evaluate('kgPersonalData.getSnapshot()')
    assert len(after['notes']) == 4
    assert all(note['deletedAt'] for note in after['notes'])
    for key in ['layout', 'studyResults', 'studyResets', 'readingProgress']:
        assert after[key] == before[key]
    assert page.locator('#info_panel .user-note').count() == 0
    assert page.locator('#kg_notes_list .kg-note-list-item').count() == 0
    assert button.is_disabled()
    # An older browser/cloud snapshot must not resurrect any deleted note.
    assert page.evaluate('kgPersonalData.mergeSnapshot(window.__notesBeforeDelete)')
    assert page.evaluate('kgPersonalData.getNotes()') == []
    page.reload(wait_until='domcontentloaded')
    page.wait_for_function('Boolean(window.kgPersonalData)')
    assert page.evaluate('kgPersonalData.getNotes()') == []
