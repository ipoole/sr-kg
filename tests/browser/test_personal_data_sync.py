import pytest


@pytest.mark.browser
def test_sync_engine_merges_remote_and_uploads_combined_snapshot(browser_graph):
    page = browser_graph.page
    result = page.evaluate(
        """async () => {
          const local = window.kgPersonalData;
          const remoteProfile = local.getSnapshot();
          const now = "2026-10-08T12:00:00.000Z";
          remoteProfile.notes.push({
            id: "remote-note", targetType: "concept", targetId: "sr.1.1",
            conceptId: "sr.1.1", section: "Overview", anchor: {},
            title: "Remote", body: "From another browser", createdAt: now,
            updatedAt: now, deletedAt: ""
          });
          let uploaded = null;
          const provider = {
            read: async () => ({
              bytes: window.kgPersonalDataArchive.exportBytes(remoteProfile),
              revision: "remote-v1"
            }),
            write: async (bytes, options) => {
              uploaded = {profile: window.kgPersonalDataArchive.importBytes(bytes), options};
              return {revision: "remote-v2"};
            }
          };
          const statuses = [];
          const engine = window.kgCreatePersonalDataSyncEngine({
            store: local, archive: window.kgPersonalDataArchive, provider,
            onStatus: status => statuses.push(status.state)
          });
          const syncResult = await engine.synchronize();
          return {uploaded, statuses, syncResult};
        }"""
    )

    assert result["uploaded"]["options"]["revision"] == "remote-v1"
    assert result["uploaded"]["options"]["create"] is False
    assert any(note["id"] == "remote-note" for note in result["uploaded"]["profile"]["notes"])
    assert result["statuses"] == ["syncing", "synced"]
    assert result["syncResult"]["revision"] == "remote-v2"


@pytest.mark.browser
def test_sync_engine_re_reads_and_merges_after_provider_conflict(browser_graph):
    page = browser_graph.page
    result = page.evaluate(
        """async () => {
          const store = window.kgPersonalData;
          let reads = 0;
          let writes = 0;
          const remote = store.getSnapshot();
          const provider = {
            read: async () => {
              reads += 1;
              return reads === 1 ? null : {
                bytes: window.kgPersonalDataArchive.exportBytes(remote), revision: "v2"
              };
            },
            write: async () => {
              writes += 1;
              if (writes === 1) {
                throw window.kgPersonalDataSyncConflictError("changed");
              }
              return {revision: "v3"};
            }
          };
          const engine = window.kgCreatePersonalDataSyncEngine({
            store, archive: window.kgPersonalDataArchive, provider
          });
          const value = await engine.synchronize();
          return {reads, writes, revision: value.revision};
        }"""
    )

    assert result == {"reads": 2, "writes": 2, "revision": "v3"}
