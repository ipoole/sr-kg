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


@pytest.mark.browser
def test_user_notes_are_toggleable_persistent_and_read_only_when_editing_off(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("2.1")
    assert page.locator("#info_panel .kg-add-note").first.is_visible() is False

    page.locator("#kg_notes_section summary").click()
    page.locator("#kg_notes_edit_toggle").check()
    assert page.locator("#info_panel .kg-add-note").count() > 0
    assert page.locator("#info_panel .kg-add-note").first.is_visible()

    page.locator("#info_panel .kg-add-note").first.click()
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
    assert page.locator("#kg_notes_list .kg-note-list-item").count() == 1
    list_item = page.locator("#kg_notes_list .kg-note-list-item")
    assert list_item.get_attribute("data-target-type") == "concept"
    assert list_item.get_attribute("data-target-id") == "2.1"
    assert "Check this derivation" in list_item.inner_text()

    note.locator(".user-note-close").click()
    note = page.locator("#info_panel details.user-note").first
    assert note.get_attribute("open") is None
    assert note.locator("summary").inner_text() == "Check this derivation"

    page.locator("#kg_notes_edit_toggle").uncheck()
    assert page.locator("#info_panel .kg-add-note").first.is_visible() is False
    assert page.locator("#info_panel .user-note-title-input").count() == 0
    assert page.locator("#info_panel .user-note-body-input").count() == 0
    assert page.locator("#info_panel details.user-note summary").inner_text() == (
        "Check this derivation"
    )
    page.locator("#info_panel details.user-note summary").click()
    assert "This should become an optional detail later." in page.locator(
        "#info_panel details.user-note"
    ).inner_text()

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
    page.locator("#kg_notes_section summary").click()
    page.locator("#kg_notes_edit_toggle").check()
    page.locator("#info_panel .kg-add-note").first.click()

    assert page.locator("#info_panel details.user-note").count() == 1
    page.locator("#info_panel .user-note-close").click()

    assert page.locator("#info_panel details.user-note").count() == 0
    assert page.locator("#info_panel .kg-add-note").first.is_visible()
    assert page.locator("#kg_notes_list .kg-note-list-item").count() == 0
    assert page.locator("#kg_notes_list .kg-note-list-empty").count() == 1
    assert page.evaluate(
        """() => JSON.parse(localStorage.getItem("srkg.userNotes.v1")).notes.length"""
    ) == 0


@pytest.mark.browser
def test_notes_panel_list_navigates_to_note_concept(browser_graph):
    page = browser_graph.page

    browser_graph.click_concept("2.1")
    page.locator("#kg_notes_section summary").click()
    page.locator("#kg_notes_edit_toggle").check()
    page.locator("#info_panel .kg-add-note").first.click()
    page.locator("#info_panel .user-note-title-input").fill("Beta note")
    page.locator("#info_panel .user-note-body-input").fill("Remember beta.")
    page.locator("#info_panel .user-note-close").click()

    browser_graph.click_concept("1.1")
    page.locator("#info_panel .kg-add-note").first.click()
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
    page.locator("#kg_notes_edit_toggle").check()
    page.locator("#info_panel .kg-add-note").first.click()
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
    page.locator("#kg_notes_edit_toggle").check()

    browser_graph.click_concept("2.2")
    graphic = page.locator("#info_panel .concept-figure")
    assert graphic.locator(".kg-add-note").count() == 1
    graphic.locator(".kg-add-note").click()
    graphic.locator(".user-note-title-input").fill("Review graphic")
    graphic.locator(".user-note-body-input").fill("Check the arrows.")
    graphic.locator(".user-note-close").click()

    browser_graph.open_control_section("kg_modules_section")
    page.locator('.kg-module-item[data-module-id="test.m01_foundations"]').click()
    overview = page.locator("#info_panel .module-content-block").first
    assert overview.locator(".kg-add-note").count() > 0
    if not overview.evaluate("el => el.open"):
        overview.locator(":scope > summary").click()
    overview.locator(".kg-add-note").first.click()
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
def test_study_questions_share_one_stable_note_anchor(browser_graph):
    page = browser_graph.page
    browser_graph.click_concept("2.1")
    page.locator("#kg_notes_section summary").click()
    page.locator("#kg_notes_edit_toggle").check()

    study = page.locator("#info_panel details.study-questions")
    assert study.locator(".kg-add-note").count() == 1
    if not study.evaluate("element => element.open"):
        study.locator(":scope > summary").click()
    study.locator(".kg-add-note").click()
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
    page.locator("#kg_notes_edit_toggle").check()

    section = page.locator('#info_panel .concept-section[data-section="Explanation"]')
    assert section.locator(".optional-detail").count() == 1
    page.wait_for_selector(
        '#info_panel .concept-section[data-section="Explanation"] mjx-container[display="true"]'
    )

    assert section.locator(".kg-add-note:visible").count() >= 4
    assert section.evaluate(
        """section => {
          const optional = section.querySelector(".optional-detail");
          const line = optional && optional.closest(".concept-line");
          const next = line && line.nextElementSibling;
          return Boolean(next && next.querySelector(".kg-add-note"));
        }"""
    )
    assert section.evaluate(
        """section => {
          const equation = section.querySelector('mjx-container[display="true"]');
          const line = equation && equation.closest(".concept-line");
          const next = line && line.nextElementSibling;
          return Boolean(next && next.querySelector(".kg-add-note"));
        }"""
    )


@pytest.mark.browser
def test_note_uses_stable_block_id_across_section_rename(browser_graph):
    page = browser_graph.page
    browser_graph.click_concept("2.1")
    page.locator("#kg_notes_section summary").click()
    page.locator("#kg_notes_edit_toggle").check()

    definition = page.locator('#info_panel .concept-section[data-section="Definition"]')
    definition.locator(".kg-add-note").first.click()
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
    page.locator("#kg_notes_edit_toggle").check()

    explanation = page.locator('#info_panel .concept-section[data-section="Explanation"]')
    anchor = explanation.locator(".kg-add-note").last
    anchor.click()
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
    page.locator("#kg_notes_edit_toggle").check()

    explanation = page.locator('#info_panel .concept-section[data-section="Explanation"]')
    explanation.locator(".kg-add-note").last.click()
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
