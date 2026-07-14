import csv

import pytest


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

    stored = page.evaluate(
        """() => JSON.parse(localStorage.getItem("srkg.userNotes.v1")).notes"""
    )
    assert len(stored) == 1
    assert stored[0]["conceptId"] == "2.1"
    assert stored[0]["title"] == "Check this derivation"
    assert stored[0]["body"] == "This should become an optional detail later."

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
