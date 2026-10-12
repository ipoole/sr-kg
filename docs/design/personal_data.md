# Personal data

## Purpose

Personal data is the learner's work, distinct from authored knowledge-base
content and transient viewer state. It currently comprises:

- notes;
- personal concept positions and module anchors;
- study-question attempts;
- content-block read marks.

Selection, context, camera, folded modules, open details, temporary layout edits
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

### Layout

Each concept position and module anchor is an independent record containing
coordinates, `updated_at` and optional `deleted_at`. Resetting a personal
position creates a tombstone. Records merge independently, so moving one node
does not overwrite unrelated moves from another browser. The profile also
records the published layout revision from which the overrides were made.

### Study attempts

Attempts are append-only events with a stable attempt ID, question ID, outcome,
time, originating device ID and a positive `attempt_count`. New attempts have a
count of one. Migration may create one event whose count represents several
historical attempts because the old store retained only a total and latest
outcome.

Question and global reset events suppress earlier attempts. Attempts and reset
events merge by stable ID; displayed totals and latest outcomes are derived.
Typed free-text answers are not stored.

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
| `study_attempts.csv` | attempt events |
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
finds that app-created file by name. A user explicitly connects and presses
**Sync now**; disconnecting removes authorization from the current page but
does not delete either copy of the data.

The standalone viewer uses Google Identity Services' browser token flow. The
repository's public OAuth web-client ID is the normal build default and
authorises `https://ipoole.github.io`. Other deployments can override it with
`--google-drive-client-id` or `PHYSICSKG_GOOGLE_DRIVE_CLIENT_ID`; their hosting
origin must be registered for that client. The ID is public configuration, not
a secret. Access tokens are kept only in memory and may expire, requiring the
user to connect again. Fully unattended token refresh would require a backend
and is deliberately outside the first implementation.
