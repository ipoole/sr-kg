import csv
import io
from pathlib import Path
import zipfile

import pytest


@pytest.mark.browser
def test_personal_data_archive_round_trips_all_collections(browser_graph):
    page = browser_graph.page
    page.evaluate(
        """() => {
          const snapshot = window.kgPersonalData.getSnapshot();
          const now = "2026-10-05T12:00:00.000Z";
          snapshot.notes.push({
            id: "note-portable", targetType: "concept", targetId: "2.1",
            conceptId: "2.1", section: "Definition",
            anchor: {blockIndex: 0, afterText: "", blockId: "2.1.definition",
              sectionKey: "", contextBefore: "", contextAfter: ""},
            title: "Portable note", body: "Move between browsers.",
            createdAt: now, updatedAt: now, deletedAt: ""
          });
          snapshot.layout.publishedRevision = "unpublished";
          snapshot.layout.records["concept:2.1"] = {
            objectType: "concept", objectId: "2.1", x: 12, y: 34,
            updatedAt: now, deletedAt: "", deviceId: window.kgPersonalData.deviceId
          };
          window.kgPersonalData.replaceSnapshot(snapshot);
          window.kgPersonalData.addStudyAttempt("2.1.q1", "correct", now);
          window.kgPersonalData.setRead("2.1.definition", true);
        }"""
    )

    browser_graph.open_control_section("kg_personal_data_section")
    with page.expect_download() as download_info:
        page.locator("#kg_personal_data_export").click()
    archive_path = Path(download_info.value.path())

    with zipfile.ZipFile(archive_path) as archive:
        assert set(archive.namelist()) == {
            "manifest.csv",
            "notes.csv",
            "layout.csv",
            "study_attempts.csv",
            "study_resets.csv",
            "reading_progress.csv",
        }
        notes = list(csv.DictReader(io.TextIOWrapper(archive.open("notes.csv"))))
        layout = list(csv.DictReader(io.TextIOWrapper(archive.open("layout.csv"))))
        attempts = list(
            csv.DictReader(io.TextIOWrapper(archive.open("study_attempts.csv")))
        )
        reading = list(
            csv.DictReader(io.TextIOWrapper(archive.open("reading_progress.csv")))
        )
    assert notes[0]["title"] == "Portable note"
    assert layout[0]["object_id"] == "2.1"
    assert attempts[0]["question_id"] == "2.1.q1"
    assert reading[0]["block_id"] == "2.1.definition"

    page.evaluate("() => localStorage.removeItem('srkg.personalData.v1')")
    page.reload(wait_until="domcontentloaded")
    page.wait_for_function("() => Boolean(window.kgPersonalData)")
    browser_graph.open_control_section("kg_personal_data_section")
    page.locator("#kg_personal_data_import_input").set_input_files(str(archive_path))
    page.locator("#kg_personal_data_import_dialog[open]").wait_for()
    assert "1 note" in page.locator("#kg_personal_data_import_summary").inner_text()
    assert "1 study attempt record" in page.locator(
        "#kg_personal_data_import_summary"
    ).inner_text()
    page.locator("#kg_personal_data_import_apply").click()
    page.wait_for_function(
        """() => window.kgPersonalData &&
          window.kgPersonalData.getSnapshot().notes.some(note => note.id === "note-portable")"""
    )
    restored = page.evaluate("() => window.kgPersonalData.getSnapshot()")
    assert restored["layout"]["records"]["concept:2.1"]["x"] == 12
    assert restored["studyAttempts"][0]["outcome"] == "correct"
    assert restored["readingProgress"]["2.1.definition"]["isRead"] is True


@pytest.mark.browser
def test_malformed_personal_data_archive_changes_nothing(browser_graph, tmp_path):
    page = browser_graph.page
    before = page.evaluate("() => window.kgPersonalData.getSnapshot().profileId")
    invalid = tmp_path / "invalid.zip"
    invalid.write_bytes(b"not a zip")

    browser_graph.open_control_section("kg_personal_data_section")
    page.locator("#kg_personal_data_import_input").set_input_files(str(invalid))
    page.wait_for_function(
        "() => document.getElementById('kg_personal_data_status').textContent.includes('Could not import')"
    )

    assert page.evaluate("() => window.kgPersonalData.getSnapshot().profileId") == before
    assert page.locator("#kg_personal_data_import_dialog").get_attribute("open") is None
