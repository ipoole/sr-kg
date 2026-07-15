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

    page.locator('.kg-concept-item[data-concept-id="2.1"]').click()
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
    assert stored[0]["conceptId"] == "2.1"
    assert stored[0]["title"] == "Check this derivation"
    assert stored[0]["body"] == "This should become an optional detail later."
    _hover_beta_node(page)
    tooltip_text = page.locator("#kg_node_tooltip").inner_text()
    assert "Check this derivation" in tooltip_text
    assert "This should become an optional detail later." not in tooltip_text
    assert page.locator("#kg_notes_count").inner_text() == "1 note"
    assert page.locator("#kg_notes_list .kg-note-list-item").count() == 1
    assert "2.1 Beta" in page.locator("#kg_notes_list .kg-note-list-item").inner_text()
    assert "Check this derivation" in page.locator("#kg_notes_list .kg-note-list-item").inner_text()

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
    page.locator('.kg-concept-item[data-concept-id="2.1"]').click()
    assert page.locator("#info_panel details.user-note summary").inner_text() == (
        "Check this derivation"
    )


@pytest.mark.browser
def test_closing_default_empty_note_deletes_it_and_restores_anchor(browser_graph):
    page = browser_graph.page

    page.locator('.kg-concept-item[data-concept-id="2.1"]').click()
    page.locator("#kg_notes_section summary").click()
    page.locator("#kg_notes_edit_toggle").check()
    page.locator("#info_panel .kg-add-note").first.click()

    assert page.locator("#info_panel details.user-note").count() == 1
    page.locator("#info_panel .user-note-close").click()

    assert page.locator("#info_panel details.user-note").count() == 0
    assert page.locator("#info_panel .kg-add-note").first.is_visible()
    assert page.locator("#kg_notes_count").inner_text() == "0 notes"
    assert page.locator("#kg_notes_list .kg-note-list-empty").inner_text() == "No notes yet."
    assert page.evaluate(
        """() => JSON.parse(localStorage.getItem("srkg.userNotes.v1")).notes.length"""
    ) == 0


@pytest.mark.browser
def test_notes_panel_list_navigates_to_note_concept(browser_graph):
    page = browser_graph.page

    page.locator('.kg-concept-item[data-concept-id="2.1"]').click()
    page.locator("#kg_notes_section summary").click()
    page.locator("#kg_notes_edit_toggle").check()
    page.locator("#info_panel .kg-add-note").first.click()
    page.locator("#info_panel .user-note-title-input").fill("Beta note")
    page.locator("#info_panel .user-note-body-input").fill("Remember beta.")
    page.locator("#info_panel .user-note-close").click()

    page.locator('.kg-concept-item[data-concept-id="1.1"]').click()
    page.locator("#info_panel .kg-add-note").first.click()
    page.locator("#info_panel .user-note-title-input").fill("Alpha note")
    page.locator("#info_panel .user-note-body-input").fill("Remember alpha.")
    page.locator("#info_panel .user-note-close").click()

    assert page.locator("#kg_notes_count").inner_text() == "2 notes"
    list_items = page.locator("#kg_notes_list .kg-note-list-item")
    assert list_items.count() == 2
    assert "1.1 Alpha" in list_items.nth(0).inner_text()
    assert "Alpha note" in list_items.nth(0).inner_text()
    assert "2.1 Beta" in list_items.nth(1).inner_text()
    assert "Beta note" in list_items.nth(1).inner_text()

    list_items.nth(1).click()

    assert page.locator("#info_panel h2").inner_text() == "2.1 Beta"
    assert page.evaluate("() => window.location.hash") == "#concept-2.1"
    assert page.locator("#info_panel details.user-note summary").inner_text() == "Beta note"


@pytest.mark.browser
def test_user_notes_export_and_import_csv(browser_graph):
    page = browser_graph.page

    page.locator('.kg-concept-item[data-concept-id="2.1"]').click()
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
    assert rows[0]["title"] == "Exported title"
    assert rows[0]["body"] == "Exported body"

    page.evaluate("""() => localStorage.removeItem("srkg.userNotes.v1")""")
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
    page.locator('.kg-concept-item[data-concept-id="2.1"]').click()
    assert page.locator("#info_panel details.user-note summary").inner_text() == (
        "Imported title"
    )
    page.locator("#info_panel details.user-note summary").click()
    assert page.locator("#info_panel .user-note-body-input").input_value() == "Imported body"


@pytest.mark.browser
def test_note_hooks_follow_optional_details_and_display_equations(browser_graph):
    page = browser_graph.page

    page.locator('.kg-concept-item[data-concept-id="2.1"]').click()
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
