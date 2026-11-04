# Published viewer inventory

[published_viewers.csv](published_viewers.csv) contains 133 publication/snapshot
records, oldest first, from 24 June to 4 November 2026. It is an inventory for
issue 6.3, not an archive: no historical HTML or release packages were downloaded
or extracted while preparing it. Existing local Git objects were inspected in
memory to identify viewers and read embedded versions.

## Scope and columns

- **88 Mainline records:** each changed generated viewer on main's first-parent
  history, including the initial June 2026 viewer. Early mainline snapshots are
  candidates for the historical archive; Git alone does not establish that every
  intermediate commit was actually served publicly.
- **42 Preview records:** changed viewers in `origin/phone-preview`'s first-parent
  history, excluding commits already on main. This includes the GR-only edition
  and published mobile diagnostics/A/B builds. Unpublished development branches
  and experimental layouts are excluded.
- **3 artefact records:** the initial live Actions deployment, first hosted preview
  and subsequent release update, confirmed in the deployment records. The earlier
  validation-only package was never deployed and is excluded. These records retain
  repeated v4.5.0 payloads because the publication routes/events differ.

`date` is the Git committer's calendar date for Git snapshots, or the known
publication day for artefacts. It is not an independently verified historical
hosting timestamp. `file_name` is the original repository path or deployed package
member, not a proposed archive filename. `version` is the embedded application
version, or literal `none` when absent. Artefact versions are corroborated by
source branding and the deployment verification records. `git_commit_id` is the
full commit containing the Git file, or the artefact's recorded source commit.
`summary` identifies Mainline, Preview or artefact records and briefly describes
the change using commit history and the authored release history.

Keep same-day records and repeated version numbers: they can represent different
HTML builds. Some mobile A/B previews intentionally repeat earlier HTML. The old
`output/interactive_graph.html` viewer is included; its later tiny compatibility
page is not a viewer and is excluded.

## Sources and saved sample

For Git records, the full commit ID plus `file_name` identifies the exact blob.
For the three artefact records, the summary supplies the `site-*` release tag;
retrieve `site.tar.gz` from that Release and use `file_name` as its member path.
The source commit alone does not contain generated HTML after untracking.

The agreed sample has now been saved in Git-ignored `historic_builds/`:
33 PhysicsKG builds (positions 1, 3, 5, ...) and 14 interactive_graph builds
(positions 1, 6, 11, ...), taking each filename family oldest-first. The differently
named GR-only edition was not part of the requested sample.

Archive filenames include a short commit ID and end with the embedded version
when available, otherwise the date. For example:
`PhysicsKG_620a0262_v4.5.0.html` and
`interactive_graph_ec4f1fd1_2026-06-24.html`. The ignored directory's `manifest.csv`
records full source mappings, sampling positions, sizes and SHA-256 checksums.
The 47 HTML files total 95.2 MiB; all hashes and Git-backed byte comparisons passed.

Shared local libraries, verified unchanged since the initial commit, are included
under `historic_builds/lib/`. External CDNs may still be needed; historical browser
compatibility has not been checked for every build. HTML and asset references are
unmodified. No Git history rewriting has been performed. Preserve the ignored
archive and its manifest separately when preparing the eventual history cleanup.
