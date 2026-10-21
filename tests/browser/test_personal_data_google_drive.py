import pytest


@pytest.mark.browser
def test_google_drive_sync_is_optional_in_an_unconfigured_viewer(browser_graph):
    page = browser_graph.page
    browser_graph.open_control_section("kg_personal_data_section")

    assert page.locator("#kg_cloud_sync_connect").is_disabled()
    assert "Not configured" in page.locator("#kg_cloud_sync_status").inner_text()
    assert page.locator("#kg_personal_data_export").is_enabled()
    assert page.locator("#kg_personal_data_import_button").is_enabled()


@pytest.mark.browser
def test_connect_syncs_immediately_and_local_changes_schedule_another_sync(browser_graph):
    page = browser_graph.page
    browser_graph.open_control_section("kg_personal_data_section")
    page.evaluate(
        """() => {
          window.__syncCalls = 0;
          kgCloudSyncConfig.googleDriveClientId = 'test-client';
          window.kgCreateGoogleDriveAuthorizer = () => ({
            connect: () => Promise.resolve(),
            token: () => 'test-token',
            disconnect: () => {}
          });
          window.kgCreateGoogleDrivePersonalDataProvider = () => ({
            fileName: 'PhysicsKG personal data.zip'
          });
          window.kgCreatePersonalDataSyncEngine = options => ({
            synchronize: () => {
              window.__syncCalls += 1;
              options.onStatus({state: 'synced', detail: 'Personal data synced.'});
              return Promise.resolve({});
            },
            isSynchronizing: () => false
          });
          kgInitialiseGoogleDriveSync();
        }"""
    )

    page.locator("#kg_cloud_sync_connect").click()
    page.wait_for_function("() => window.__syncCalls === 1")
    assert "Last synced" in page.locator("#kg_cloud_sync_status").inner_text()

    page.evaluate("() => kgSchedulePersonalDataAutoSync(0)")
    page.wait_for_function("() => window.__syncCalls === 2")


@pytest.mark.browser
def test_completed_sync_does_not_rebuild_an_active_details_editor(browser_graph):
    page = browser_graph.page
    browser_graph.open_control_section("kg_personal_data_section")
    page.evaluate(
        """() => {
          kgCloudSyncConfig.googleDriveClientId = 'test-client';
          window.__finishSync = null;
          window.kgCreateGoogleDriveAuthorizer = () => ({
            connect: () => Promise.resolve(),
            token: () => 'test-token',
            disconnect: () => {}
          });
          window.kgCreateGoogleDrivePersonalDataProvider = () => ({});
          window.kgCreatePersonalDataSyncEngine = () => ({
            synchronize: () => new Promise(resolve => { window.__finishSync = resolve; }),
            isSynchronizing: () => false
          });
          kgInitialiseGoogleDriveSync();
        }"""
    )
    page.locator("#kg_cloud_sync_connect").click()
    page.wait_for_function("() => typeof window.__finishSync === 'function'")

    browser_graph.click_concept("2.1")
    questions = page.locator("#info_panel details.study-questions")
    questions.locator(":scope > summary").click()
    response = page.locator(
        '.study-question[data-question-id="2.1.q1"] textarea.study-self-response'
    )
    response.fill("An answer still being written")
    editor_element = response.element_handle()
    question = page.locator('.study-question[data-question-id="2.1.q1"]')
    if question.evaluate("element => element.open"):
        question.locator(":scope > summary").click()
    question_element = question.element_handle()

    page.evaluate("() => window.__finishSync({})")
    page.wait_for_function(
        "() => document.querySelector('#kg_cloud_sync_status').textContent.includes('Last synced')"
    )

    assert response.evaluate(
        "(element, original) => element === original", editor_element
    )
    assert questions.evaluate("element => element.open")
    assert response.input_value() == "An answer still being written"
    assert question.evaluate(
        "(element, original) => element === original", question_element
    )
    assert not question.evaluate("element => element.open")


@pytest.mark.browser
def test_completed_sync_leaves_an_open_note_untouched(browser_graph):
    page = browser_graph.page
    browser_graph.open_control_section("kg_personal_data_section")
    page.evaluate(
        """() => {
          kgCloudSyncConfig.googleDriveClientId = 'test-client';
          window.__finishSync = null;
          window.kgCreateGoogleDriveAuthorizer = () => ({
            connect: () => Promise.resolve(),
            token: () => 'test-token',
            disconnect: () => {}
          });
          window.kgCreateGoogleDrivePersonalDataProvider = () => ({});
          window.kgCreatePersonalDataSyncEngine = () => ({
            synchronize: () => new Promise(resolve => { window.__finishSync = resolve; }),
            isSynchronizing: () => false
          });
          kgInitialiseGoogleDriveSync();
        }"""
    )
    page.locator("#kg_cloud_sync_connect").click()
    page.wait_for_function("() => typeof window.__finishSync === 'function'")

    browser_graph.click_concept("2.1")
    questions = page.locator("#info_panel details.study-questions")
    questions.locator(":scope > summary").click()
    questions.locator(":scope > summary .kg-note-block-action").click()
    note = questions.locator("details.user-note")
    body = note.locator(".user-note-body-input")
    body.fill("A note still being written")
    note_element = note.element_handle()
    body_element = body.element_handle()

    page.evaluate("() => window.__finishSync({})")
    page.wait_for_function(
        "() => document.querySelector('#kg_cloud_sync_status').textContent.includes('Last synced')"
    )

    assert note.evaluate("(element, original) => element === original", note_element)
    assert body.evaluate("(element, original) => element === original", body_element)
    assert note.evaluate("element => element.open")
    assert body.input_value() == "A note still being written"


@pytest.mark.browser
def test_cloud_sync_status_reports_expired_sign_in(browser_graph):
    page = browser_graph.page
    browser_graph.open_control_section("kg_personal_data_section")
    page.evaluate(
        """() => {
          kgCloudSyncConfig.googleDriveClientId = 'test-client';
          window.kgCreateGoogleDriveAuthorizer = () => ({
            connect: () => Promise.resolve(),
            token: () => 'test-token',
            disconnect: () => {}
          });
          window.kgCreateGoogleDrivePersonalDataProvider = () => ({
            fileName: 'PhysicsKG personal data.zip'
          });
          window.kgCreatePersonalDataSyncEngine = () => ({
            synchronize: () => Promise.reject(Object.assign(
              new Error('Google sign-in is required'), {code: 'auth_required'}
            )),
            isSynchronizing: () => false
          });
          kgInitialiseGoogleDriveSync();
        }"""
    )

    page.locator("#kg_cloud_sync_connect").click()
    page.wait_for_function(
        "() => document.querySelector('#kg_cloud_sync_status').textContent.includes('expired')"
    )
    assert page.locator("#kg_cloud_sync_connect").is_visible()
    attention = page.locator("#kg_cloud_sync_attention")
    assert attention.is_visible()
    assert "Sync paused" in attention.inner_text()

    page.evaluate(
        """() => {
          document.querySelector('#kg_controls').classList.add('kg-hidden');
          document.querySelector('#kg_personal_data_section').open = false;
          window.kgCreatePersonalDataSyncEngine = options => ({
            synchronize: () => {
              options.onStatus({state: 'synced', detail: 'Personal data synced.'});
              return Promise.resolve({});
            },
            isSynchronizing: () => false
          });
        }"""
    )
    attention.click()
    page.wait_for_function("() => document.querySelector('#kg_cloud_sync_attention').hidden")
    assert not page.locator("#kg_controls").evaluate("element => element.classList.contains('kg-hidden')")
    assert page.locator("#kg_personal_data_section").evaluate("element => element.open")


@pytest.mark.browser
def test_google_drive_provider_reads_visible_archive_and_updates_with_revision(browser_graph):
    page = browser_graph.page
    result = page.evaluate(
        """async () => {
          const archiveBytes = window.kgPersonalDataArchive.exportBytes(
            window.kgPersonalData.getSnapshot()
          );
          const calls = [];
          const response = (body, options = {}) => ({
            ok: options.ok !== false,
            status: options.status || 200,
            headers: new Headers(options.headers || {}),
            json: async () => body,
            arrayBuffer: async () => archiveBytes.buffer
          });
          const fakeFetch = async (url, options = {}) => {
            calls.push({url, method: options.method || "GET", headers: options.headers || {}});
            if (url.includes("?q=")) {
              return response({files: [{id: "drive-file", name: "PhysicsKG personal data.zip"}]});
            }
            if (url.includes("alt=media")) {
              return response(null, {headers: {etag: '"revision-1"'}});
            }
            return response({id: "drive-file", version: "2"}, {headers: {etag: '"revision-2"'}});
          };
          const provider = window.kgCreateGoogleDrivePersonalDataProvider({
            accessToken: "test-token", fetch: fakeFetch
          });
          const remote = await provider.read();
          const written = await provider.write(archiveBytes, {
            create: false, revision: remote.revision
          });
          return {calls, revision: remote.revision, written};
        }"""
    )

    assert result["revision"] == '"revision-1"'
    assert result["written"]["revision"] == '"revision-2"'
    update = result["calls"][-1]
    assert update["method"] == "PATCH"
    assert update["headers"]["If-Match"] == '"revision-1"'


@pytest.mark.browser
def test_google_drive_provider_creates_named_zip_when_cloud_copy_is_absent(browser_graph):
    page = browser_graph.page
    result = page.evaluate(
        """async () => {
          const calls = [];
          const fakeFetch = async (url, options = {}) => {
            calls.push({url, method: options.method || "GET",
              contentType: (options.headers || {})["Content-Type"] || ""});
            if ((options.method || "GET") === "GET") {
              return {ok: true, status: 200, headers: new Headers(),
                json: async () => ({files: []})};
            }
            return {ok: true, status: 200, headers: new Headers({etag: '"created"'}),
              json: async () => ({id: "new-file", version: "1"})};
          };
          const provider = window.kgCreateGoogleDrivePersonalDataProvider({
            accessToken: "test-token", fetch: fakeFetch
          });
          const remote = await provider.read();
          const written = await provider.write(new Uint8Array([1, 2, 3]), {create: true});
          return {remote, written, calls};
        }"""
    )

    assert result["remote"] is None
    create = result["calls"][-1]
    assert create["method"] == "POST"
    assert "uploadType=multipart" in create["url"]
    assert create["contentType"].startswith("multipart/related; boundary=")
