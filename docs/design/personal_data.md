# Personal data

## Purpose

Personal data is the learner's work, distinct from authored knowledge-base
content and transient viewer state. It currently comprises:

- notes;
- personal concept positions and module anchors;
- latest study-question results;
- content-block read marks.

Selection, context, camera, folded modules, open details, temporary Fit++ adjustments
and control preferences are not personal data. They are not exported or merged.

The viewer remains local-first. Without setup, personal data is stored only in
the current browser. Export and import provide optional portability. The
optional Google Drive provider uses the same snapshot and merge operations to
synchronise explicitly across browsers and devices.

## Runtime model

Viewer features access personal data through one store rather than reading
individual browser-storage keys. The store owns a versioned profile and a
separate per-browser device ID. A profile has a stable `profile_id`, creation
and modification times, and the four collections above.

All timestamps are UTC ISO 8601 values. Record IDs and authored semantic IDs
are stable. Invalid or unknown authored IDs are preserved during import where
that is safe, so content removed from one build is not silently destroyed.

Local migration is automatic and one-way: the first load imports the existing
notes, layout, study-progress and read-progress keys into the personal profile.
The legacy keys may remain as compatibility fallbacks for one release, but the
personal profile becomes authoritative.

## Records and merge rules

### Notes

A note retains its stable note ID, target and anchor data, text, `created_at`,
`updated_at` and optional `deleted_at`. The newest modification or deletion for
an ID wins. Deleted records remain as tombstones so another browser cannot
resurrect a deleted note.

The viewer adds notes through the speech-bubble control in a content-block
heading and a temporary paragraph-placement mode. A selected paragraph places
the note below it; atomic blocks such as graphics and Study Questions use one
block-level anchor. Authored block IDs and nearby text make anchors resilient to
editorial changes. Legacy module notes with a valid stable block and
unambiguous recorded paragraph are repaired during local migration; genuinely
ambiguous notes remain visible as needing placement.

Notes use the shared authored-content disclosure and text renderer. Existing notes
open for reading; Edit exposes the editor, Done returns to reading, and folding an
editor retains its draft and returns to reading on reopening. Inline and display
MathJax are supported; Insert maths inserts an editable example, leaving it
unselected with the caret at its end. Raw HTML is escaped. New notes open for editing. Neither folding nor reading a note changes
its synchronised content timestamp.

An optional `placement` is `anchor` (also the default for older records) or `owner`.
Owner notes attach directly to a concept/module ID and appear after authored
exposition, before relationships/study (and module member listings). They have no
paragraph dependency and never enter anchor recovery. Both placements preserve
stable IDs, timestamps and tombstones through merge and CSV/ZIP exchange; the
optional CSV column keeps older exports readable. Presentation state is local;
notes do not contribute to reading/question completion. See
[Notes and authored content](notes_content_unification.md).

Tools → Notes → Delete all notes requires confirmation and deletes every personal
note, including missing targets, unresolved placements and unloaded domains.
Existing deletion tombstones are retained and new ones synchronise, so merging an
older snapshot cannot resurrect the notes. Other personal-data collections are
untouched; Cancel leaves both saved notes and open editors unchanged.

### Layout

Each concept position and module anchor is an independent record containing
coordinates, `updated_at` and optional `deleted_at`. Resetting a personal
position creates a tombstone. Records merge independently, so moving one node
does not overwrite unrelated moves from another browser. The profile also
records the published layout revision from which the overrides were made.

### Question results

Each question has one result: question ID, latest outcome (`correct`, `incorrect`
or `unknown`), update time and originating device. A new answer replaces that
question’s result; no attempt history, counts or typed responses are retained.
Local writes advance beyond the observed question result/reset when timestamps
would tie, so a fresh answer or reset is never lost. The newest timestamp wins on merge; equal timestamps use device ID then outcome
as a deterministic tie-break. Unloaded-domain results remain untouched.

Question and global reset events suppress earlier results, preventing stale
cloud data or old archives from resurrecting cleared progress. The internal
schema-2 model stores latest-result records. Loading schema-1 browser data or
archives retains each question’s latest surviving result and discards counts
and history. Other personal data is unchanged.

The shared browser key and exported/cloud ZIP deliberately keep their
schema-1 envelope readable by the published viewer. Each question is represented
by one legacy-shaped row with `attempt_count=1`; that constant denotes the single
retained result, not a cumulative count. `studyResultsVersion=2` identifies the
browser projection, and `study_model=latest-result` identifies an export. This
allows preview and public viewers to share personal data safely. Import also
accepts the format-2 `study_results.csv` archives produced by development builds.

### Reading progress

Each content block has an explicit checked or unchecked record with
`updated_at` and device ID. The newest record wins. Keeping unchecked records
is necessary for an untick to propagate during a future merge.

When timestamps are equal, record ID or device ID provides a deterministic
tie-break rather than depending on import order.

## Portable archive

**Export personal data** downloads one `srkg-personal-data.zip`. It is a
standard, unencrypted ZIP containing UTF-8 CSV files:

| File | Purpose |
| --- | --- |
| `manifest.csv` | schema version, profile ID and export metadata |
| `notes.csv` | notes and deletion tombstones |
| `layout.csv` | personal concept positions and module anchors |
| `study_attempts.csv` | one latest result per question; legacy-compatible column names |
| `study_resets.csv` | per-question and global reset events |
| `reading_progress.csv` | checked and unchecked read records |

CSV uses RFC 4180-style quoting and a header row. Empty collections still have
a file containing their header. The manifest identifies archive schema version
`1`; import rejects unsupported versions rather than guessing.

Import first validates the complete archive and reports counts. The user then
chooses:

- **Merge** (default): combine records using the rules above;
- **Replace**: replace the current profile after explicit confirmation.

Import is atomic: malformed input changes nothing. The old notes-only CSV
import remains available for compatibility.

## Synchronisation architecture

Implementation ownership: `personal_data.js` owns the local profile/merge model;
archive, sync and Drive modules provide separate codecs/protocol adapters.
`personal_data_controller.js` owns connection UI and sync scheduling. Its explicit
merge callback reloads the layout, notes and study controllers and updates
summaries without replacing the active Details pane. This preserves open blocks,
note editors and question drafts. See [Architecture](architecture.md) for the
complete controller map.

The provider-neutral sync engine downloads the portable archive, validates and
merges it through the personal-data store, then uploads the merged archive. A
provider supplies only revision-aware `read` and `write` operations. If a write
reports a concurrent change, the engine reads, merges and retries up to a
bounded limit.

Local storage remains the working copy, so viewing and editing continue
offline. Authentication, cloud file discovery and transport belong to provider
adapters; they do not change the personal-data model or archive format.

### Google Drive provider

The first provider uses the narrow `drive.file` OAuth scope and creates the
visible file `PhysicsKG personal data.zip` in the user's Drive. Each browser
finds that app-created file by name. Connecting performs an immediate merge and
sync. While connected, local changes schedule a short-delay sync; a visible page
also checks every five minutes and when it becomes active after being away.
**Sync now** remains available, and the status reports the last successful sync
time. Disconnecting removes authorization from the current page but does not
delete either copy of the data.

The standalone viewer uses Google Identity Services' browser token flow. The
repository's public OAuth web-client ID is the normal build default and
authorises `https://physicskg.org`. Other deployments can override it with
`--google-drive-client-id` or `PHYSICSKG_GOOGLE_DRIVE_CLIENT_ID`; their hosting
origin must be registered for that client. The ID is public configuration, not
a secret. Access tokens are kept only in memory and may expire, requiring the
user to connect again; regular syncing does not extend the token lifetime.
Fully unattended token refresh would require a backend and is deliberately
outside this implementation.

An authorization failure never discards the local working copy. The viewer
stops automatic sync and shows a persistent **Sync paused** action. This opens
Personal data without requesting sign-in, offering **Reconnect** and **Disconnect**.
Disconnect works offline, dismisses the notice and stops automatic attempts
without deleting either copy. Reconnection performs the normal merge before
writing either copy.

The published [privacy policy](https://physicskg.org/privacy.html) is
linked from the viewer's Personal data controls. It explains the browser-local
record, portable archive, optional Drive transfer and deletion choices in
user-facing language. Public OAuth configuration and release checks are recorded
in [Google OAuth publication](google_oauth_publication.md).

### Notes on shared explanations

Reading-tree occurrences reuse the source owner's existing note record and
paragraph anchors. A named local explanation uses its enclosing block ID and
`sectionKey = explanation:<JSON slot array>`; this is a scoped anchor, not a
new global content identity. The existing CSV/archive representation preserves
both fields unchanged. Reading-occurrence paths and the active editor location
are transient and never synchronised. Renamed/missing scopes retain notes for
placement rather than attaching them to another paragraph.
