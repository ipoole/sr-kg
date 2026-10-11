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
