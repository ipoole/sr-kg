import csv

import pytest


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
    assert bubble.get_attribute("aria-label") == "Add a note to Module overview"
    assert overview.locator(":scope > summary .kg-note-bubble-glyph").inner_text() == "+"
    assert page.locator("#info_panel .kg-add-note-row:visible").count() == 0

    repo_browser_graph.click_concept("math.manifold")
    graphic = page.locator("#info_panel details.concept-figure")
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
    first_paragraph = overview.locator(".concept-line").first
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
    assert bubble.get_attribute("aria-label") == (
        "Notes present in Module overview; add another note"
    )


@pytest.mark.browser
def test_atomic_note_blocks_create_their_single_note_directly(repo_browser_graph):
    page = repo_browser_graph.page
    repo_browser_graph.click_concept("math.manifold")

    graphic = page.locator("#info_panel details.concept-figure")
    graphic.locator(":scope > summary .kg-note-block-action").click()
    assert graphic.get_attribute("data-note-placement") is None
    assert graphic.locator("details.user-note").count() == 1
    graphic_title = graphic.locator(".user-note-title-input")
    assert graphic_title.evaluate("element => document.activeElement === element")
    graphic_title.fill("Graphic note")
    graphic.locator(".user-note-body-input").fill("Review the manifold graphic.")
    graphic.locator(".user-note-close").click()

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
    first_paragraph = overview.locator(".concept-line").first
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
def test_user_notes_are_persistent_and_always_editable(browser_graph):
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
    assert "Check this derivation" in list_item.inner_text()

    note.locator(".user-note-close").click()
    note = page.locator("#info_panel details.user-note").first
    assert note.get_attribute("open") is None
    assert note.locator("summary").inner_text() == "Check this derivation"

    assert page.locator("#info_panel .kg-add-note").first.is_visible() is False
    assert page.locator("#info_panel .user-note-title-input").count() == 1
    assert page.locator("#info_panel .user-note-body-input").count() == 1
    assert page.locator("#info_panel details.user-note summary").inner_text() == (
        "Check this derivation"
    )
    page.locator("#info_panel details.user-note summary").click()
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
    assert rows[0]["anchor_section_key"] == "legacy:definition"
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
    assert page.locator("#info_panel details.user-note summary").inner_text() == (
        "Imported title"
    )
    page.locator("#info_panel details.user-note summary").click()
    assert page.locator("#info_panel .user-note-body-input").input_value() == "Imported body"


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

    assert page.locator("#info_panel details.user-note summary").inner_text() == (
        "Stored legacy note"
    )
    stored = page.evaluate(
        "() => JSON.parse(localStorage.getItem('srkg.userNotes.v1'))"
    )
    assert stored["version"] == 2
    assert stored["notes"][0]["anchor"]["blockId"] == "2.1.definition"


@pytest.mark.browser
def test_note_hooks_follow_optional_details_and_display_equations(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("2.1")
    page.locator("#kg_notes_section summary").click()
    section = page.locator('#info_panel .concept-section[data-section="Explanation"]')
    assert section.locator(".optional-detail").count() == 1
    page.wait_for_selector(
        '#info_panel .concept-section[data-section="Explanation"] mjx-container[display="true"]'
    )

    section.locator(
        "xpath=ancestor::*[@data-note-block][1]"
    ).locator(":scope > .kg-noteable-heading .kg-note-block-action").click()
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
    definition = page.locator('#info_panel .concept-section[data-section="Definition"]')
    _place_note_at_anchor(definition.locator(".kg-add-note").first)
    definition.locator(".user-note-title-input").fill("Stable definition note")
    definition.locator(".user-note-body-input").fill("Keep this with the definition.")
    definition.locator(".user-note-close").click()

    stored = page.evaluate(
        "() => JSON.parse(localStorage.getItem('srkg.userNotes.v1')).notes[0]"
    )
    assert stored["anchor"]["blockId"] == "2.1.definition"

    page.evaluate("""() => {
      conceptData['2.1'].sections.find(section => section.key === 'definition').title =
        'Renamed definition';
    }""")
    browser_graph.click_concept("1.1")
    browser_graph.click_concept("2.1")

    renamed = page.locator('#info_panel .concept-section[data-section="Renamed definition"]')
    assert page.locator("#info_panel h3").filter(has_text="Renamed definition").count() == 1
    assert renamed.locator("details.user-note summary").inner_text() == "Stable definition note"
    assert page.locator("#info_panel .kg-unmatched-notes").count() == 0


@pytest.mark.browser
def test_note_context_survives_paragraph_insertion_and_splitting(browser_graph):
    page = browser_graph.page
    browser_graph.click_concept("2.1")
    page.locator("#kg_notes_section summary").click()
    explanation = page.locator('#info_panel .concept-section[data-section="Explanation"]')
    anchor = explanation.locator(".kg-add-note").last
    _place_note_at_anchor(anchor)
    explanation.locator(".user-note-title-input").fill("Context note")
    explanation.locator(".user-note-body-input").fill("Remain after the final passage.")
    explanation.locator(".user-note-close").click()

    page.evaluate("""() => {
      const section = conceptData['2.1'].sections.find(item => item.key === 'explanation');
      section.text = 'An inserted opening paragraph.\\n' +
        section.text.replace('After the display equation.', 'After the display\\n equation.');
    }""")
    browser_graph.click_concept("1.1")
    browser_graph.click_concept("2.1")

    explanation = page.locator('#info_panel .concept-section[data-section="Explanation"]')
    note = explanation.locator("details.user-note")
    assert note.locator("summary").inner_text() == "Context note"
    assert page.locator("#info_panel .kg-unmatched-notes").count() == 0


@pytest.mark.browser
def test_unmatched_note_is_preserved_and_visibly_flagged(browser_graph):
    page = browser_graph.page
    browser_graph.click_concept("2.1")
    page.locator("#kg_notes_section summary").click()
    explanation = page.locator('#info_panel .concept-section[data-section="Explanation"]')
    _place_note_at_anchor(explanation.locator(".kg-add-note").last)
    explanation.locator(".user-note-title-input").fill("Orphaned passage note")
    explanation.locator(".user-note-body-input").fill("Do not lose this note.")
    explanation.locator(".user-note-close").click()

    page.evaluate("""() => {
      conceptData['2.1'].sections.find(
        item => item.key === 'explanation'
      ).text = 'Completely replacement prose with no original anchor context.';
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
