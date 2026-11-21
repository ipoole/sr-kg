# Personal tutorial authoring and voice narration

Status: design accepted; stages 1–6 and voiced playback from stage 7 implemented.
Text export/import, backup integration and tutorial sync are available for text-only
libraries. Local voice recording/import and optional playback are available; compact
cards and audio delivery remain planned. See the local voice authoring section below for current limits.
Agreed direction: write and refine the whole tutorial first, then optionally
record its written narration card by card. Ian's recordings should be exportable
and installable as built-in tutorials, adding a personal human voice.

This extends [Tutorial playback](tutorial_playback.md), using its existing
player, semantic commands, pointer targets and presentation restoration.
“Card” is the user-facing term; the existing route format calls it a step.

Stage 2 review: Tools → Tutorials → New tutorial opens the same editor used for
personal copies. Edit tutorial/card titles, summary and written narration; select
any existing card. Metadata and ordering are under Advanced. Continue tutorial resumes at the selected card; playback Exit leaves the editor closed. Playable personal introductions offer Start, with
Edit card during playback; unplayable routes instead retain Edit draft.
Stage 3 adds card management, explicit action editing and selected-card rehearsal;
action capture follows in stage 4.
Stage 5 adds text export/import, full backup inclusion and optional Google sync.
Storage failures retain the open draft and offer Retry or text export.

During personal tutorial playback, **Edit card** opens the editor on the current
card, whether playback began in the library or the editor. **Continue tutorial**
replays the revised card and then continues normally. The handoff restores the
pre-playback presentation, so the edit/replay cycle retains the original return
view. Built-in playback has no editing button: first make an editable copy in
Tools → Tutorials. Card identity, rather than its position/title, locates the
current card if the stored route has changed; missing/deleted cards report an
error without ending playback or silently selecting a different card.

## 1. Ownership and library

Tools → Tutorials offers Built-in tutorials and My tutorials. Opening the library
does not change the viewer. Personal tutorials need no account or setup.

- New creates and saves a personal draft with one placeholder card, then opens
  the ordinary editor. There is no creation wizard or separate creation model.
- Edit on a built-in means Make an editable copy. The original remains available.
- Personal tutorials support Start, Duplicate, Export and Delete. Use Edit card
  during playback, or Edit draft directly when validation prevents Start.
- A copy gets a new tutorial ID and retains source ID/version and author credit.
  Existing card IDs may remain: they are unique within their tutorial.
- Deleting the final card leaves an empty draft with Add card available.
  Drafts can be saved/exported, but incomplete routes cannot be played or installed
  as built-in tutorials. Deletion requires confirmation; reordering does not.

The new draft has title “New tutorial”, an empty summary and one card titled
“New card”, with empty written narration. Placeholder prompts are editor UI,
not narration that could accidentally reach learners. This title-only card can
play immediately; tutorial and card titles remain required. Its action is the existing
zero-duration wait and its pointer target is narration; `demonstrate: true`
starts new cards with their actions shown. These are hidden as
“No viewer action”: a commentary-only card needs no invented user interaction.

## 2. Editor workflow

The editor contains tutorial title/summary/optional author credit, an ordered
Card dropdown and the selected card. Keep Add, Duplicate and Delete beside the
dropdown. Move up/down remains under Advanced; there is no separate Arrange list
or drag-reordering interface. Reordering may require revising downstream cards.

Each card exposes:

| Field | Behaviour |
| --- | --- |
| Title | Short label; required for playback. |
| Action visibility | Per-card Show/Hide menu, editable after recording. Show (default) demonstrates actions; Hide sets the scene without pointer demonstrations or automatic inter-action delays. Both show narration and honour explicit pauses. |
| Written narration | Optional commentary. Blank cards show their title and playback controls. Reuse existing safe text, maths and concept-link conventions and editing helpers. |
| Legacy preparation | Optional saved setup commands remain supported by playback and export/import, but have no editing panel. Use JSON for deliberate changes. |
| Actions | Ordered friendly entries such as “Select Lorentz transformations”, with editable parameters, optional pointer and pause. |
| Voice | Optional recording/file, duration, Listen, Replace and Remove; audio can be added after the text route is complete. |

Autosave valid draft structure locally, including temporarily blank fields.
Show Saving/Saved or a visible failure; never silently discard work on quota or
storage errors. Completing an edit and starting playback flush pending saves.
Track substantive edits, not editor focus, folding or rehearsal, as modifications.
Playback/rehearsal uses a frozen route snapshot: library edits or background sync
must not change its cards midway through playback. Sync must also preserve an open
editor and its current draft, rather than rebuilding the pane or moving the viewer.

Continue tutorial reconstructs the preceding route from its known baseline, then
plays the current card and permits normal progression. It does not assume the
viewer happens to be in the right state. Select the first card to review from the start.
There is no single-card playback mode: use Edit card when another revision is
needed, or continue with Next. Exit restores the pre-playback presentation and
leaves the editor closed. Review the entire route after changing earlier cards.

Desktop authoring uses the available editor/viewer space. On phones the editor
and action-capture view are switched explicitly rather than squeezing an editor,
graph and details into the screen together. Recording is supported on phones,
not restricted to desktop: show the normal viewer with a compact current-card,
action-count, Undo, Redo, Pause +1s, Finish recording and Cancel strip. Desktop is
the initial implementation/test target; phone capture belongs in the stage 4
review gate. Playback remains fully supported on phones and the old iPad;
comfortable complex editing is desktop-first. Microphone recording is a separate
per-device capability, particularly on the old iPad.

## 3. Recording viewer actions

Workflow: Add/select This Card → write narration → Record card actions → operate
PhysicsKG → Finish recording → Continue tutorial. A fixed footer keeps Record card
actions, Continue tutorial and Done editing visible while the editor body scrolls. Record card actions is prominent
with a red record dot; Continue tutorial has a play triangle. Advanced is smaller
and last, with metadata, ordering, manual actions and Export ZIP/JSON. Done editing
saves and closes without starting playback, including incomplete drafts; a save
failure retains the editor for Retry or export. Summary and written narration are
optional and hidden when blank. Select the first card to play from the start;
Exit during playback leaves the editor closed. Desktop Escape also closes safely.

Advanced is the last section after narration, closed by default. It contains
Required domains, Author credit, Move up/down, manual Viewer actions. These remain available without cluttering the usual writing/recording
workflow. The Card dropdown supplies navigation through the route.

Record begins before this card's actions, after replaying earlier cards and its
silent setup. Its current actions start in the redo queue. Redo executes the next
queued action against the current view, then remembers a session checkpoint;
Undo returns it to the queue. A new recorded action discards the unplayed tail.
The strip describes the next queued action. Appending is therefore Redo to the
end, then record more. Invalid old actions do not prevent starting a replacement;
Redo reports the invalid action without consuming it.

Pause +1s records an explicit one-second wait. Repeated presses add independent
waits immediately, with a combined trailing-duration message. Undo removes one
wait at a time before affecting the preceding graph action. Recording/Redo does
not wait out a pause; playback does. Pauses keep the pointer and view stationary,
including trailing pauses. New recorded actions add no implicit pause; existing
per-action pause metadata remains supported in Advanced and survives Redo.

Queued timing refinement: make a pause a minimum interval measured from applying
the preceding action, counting processing/rendering time and waiting only for the
remainder. Exclude pointer travel before the action, accumulate consecutive pauses
against one clock, and always await completion of the preceding operation. The
current explicit-wait implementation still adds the full duration; the editor UI
refinement does not change that timing yet.

Action visibility can be changed during later review, independently of recording.
The title and any supplied narration remain visible in either mode, and explicit pauses work
in both. New cards default to Show; omitted flags on older cards also mean Show,
preserving older imports. Existing `prepare` setup remains quiet and preserved
without an editing panel. Built-in routes have been explicitly audited and migrated
to whole-card visibility without adding cards.

Jumping to a later card or reconstructing a previous view skips earlier main-action
waits, since they do not change the view. Forward playback still honours each
explicit pause. Existing silent preparation commands retain their behaviour.

Keep captured actions/checkpoints in memory; the old saved sequence stays untouched
until Finish. Finish keeps the applied sequence, dropping any remaining redo tail,
including allowing an empty narration-only card. Cancel discards the recording.
Both restore the pre-recording presentation and reopen the editor/card. A failed
save retains the draft for Retry or export. Closing the page during capture warns
about the unfinished recording.

Capture only supported user intentions, using semantic IDs. Several actions
belong to one card; clicks never automatically create cards. Suggest a pointer
from the recorded action, allow its replacement/removal, and support narration-only
cards. Distinguish recorded playback actions from silent preparation explicitly.

Audit the current UI-to-command coverage: some handlers still bypass the shared
dispatcher. Include selection, context/depth, pane and graph modes, module folding,
search, details blocks, relationship controls, reading trees, Fit and Fit++.
Report unsupported operations rather than guessing a command or recording pixels.
Do not capture automatic consequences as additional actions.

Do not record notes, question answers, read marks, personal-layout writes,
authentication, playback/rehearsal, or learners' Explore actions. Do not record
continuous pointer motion, arbitrary scroll offsets or raw pinch/pan events.
Manual graph pan/zoom remain available for inspection, but are not recorded or
reproduced in playback. Authors should prefer Fit/Fit++ for framing, because those
commands adapt to the playback device. Details scrolling and text zoom also remain
available without recording their raw gestures.
Prefer semantic block targets and responsive Fit commands. Exact manual camera framing remains unrecorded.

After Fit++, each completed context-node drag records one `place-context-node`
action; pointer motion and unchanged drops do not add actions. Concepts and folded
modules use stable IDs. The destination is a finite graph-coordinate offset from
the recorded Fit++ anchor, not a screen pixel position. Playback places the node
directly; no drag-path animation is stored. Undo/Redo, Back, starting from a later
card and Explore/Resume use the same temporary checkpoints and commands. Moving
the anchor itself records an offset from its preceding position. No movement
writes a Personal layout; navigation and Exit retain normal restoration rules.
A subsequent Fit context can frame the tidied arrangement for the playback device.

While recording, Undo last action removes the last captured action and restores
its preceding viewer presentation, including selection, context, folding and
camera consequences. Redo restores that action/result until a new recorded action
discards the redo branch. These are temporary authoring checkpoints, not permanent
snapshots embedded in exported tutorials. Undo covers supported actions applied
within this recording session, not arbitrary personal-data changes. Test the finished sequence
with Continue tutorial; there is no separate replay control in the recording strip.
Manual action edits and pause adjustments remain available under Advanced.
Recording assigns pointers automatically. Manual pointer overrides remain, but
there is no separate Use suggested pointer button.
Report failed reconstruction rather than leaving an unexplained partial state.

Retain the existing baseline/replay model and explicit preparation commands.
Do not serialize an entire personal presentation checkpoint into every card.
The baseline, selection defaults and initial Fit must be explicit enough for a
route to start consistently on another device; they must not depend on the
author's last selection or screen dimensions.

## 4. Route and record contract

Use one normalized route contract for built-in YAML, exported JSON and player
input. Extend the existing contract compatibly; existing built-ins remain valid
without conversion. Schema versions are independent of product versions.

| Record | Minimum contract |
| --- | --- |
| Personal tutorial | Stable tutorial ID, route, UTC created/updated times, deletion tombstone, revision ID and optional source provenance. |
| Route | Existing tutorial ID, title, category, sequence, required domains and ordered steps. Optional summary and author credit. |
| Card/step | Stable step ID, title, commentary, preparation, one action or an ordered action sequence, semantic pointers/pauses, optional `demonstrate` boolean; optional audio reference. |
| Audio reference | Asset ID, recorded commentary hash and duration. A changed commentary hash means “Voice needs review”, not removal of the recording. |
| Audio asset | SHA-256 content ID, MIME type, byte length and immutable bytes; local/cloud/hosted location belongs to the asset resolver, not a player command. |

Use namespaced generated IDs for personal tutorials and generated stable card
IDs. Reordering and editing do not change them. Duplication creates independent
editable records, while immutable audio bytes may be shared by content ID.
Changing written narration flags the recording for review. Changes to actions
also prompt a narration review, without claiming the voice is automatically wrong.

The importer and generator must agree on accepted commands, target grammar and
normalization. Share their declarative contract and parity fixtures; do not grow
independent permissive JavaScript and strict Python dialects. Persist draft
records separately from the validated route passed to the existing player.

## 5. Validation and editing dependencies

Save incomplete drafts; explain why Play is unavailable. Validate before rehearsal,
export for publication and repository installation. Identify errors by card and
action, not only by a schema path.

Deleting or changing an earlier action can break a later card. Check syntax and
references immediately, and perform an explicit route rehearsal for state-dependent
availability. Do not silently invent preparation, delete cards or skip broken
targets. A missing concept/block/domain makes a retained tutorial unavailable or
needing repair; a different PhysicsKG version alone does not.

Imported data never executes scripts or arbitrary selectors. Use the existing
safe commentary renderer and command allow-list. Validate ZIP paths, declared
files, checksums and reasonable resource limits before changing local data.
Malformed import changes nothing; unresolved KB references can be retained for
repair when the package itself is structurally valid.

## 6. Voice authoring and playback

Voice is an optional final authoring pass, essentially reading the written
narration. Provide Record, Stop, Listen, Replace, Remove and audio-file import.
Request microphone access only on Record. Show recording state/duration; release
the microphone when tutorial authoring ends; mute it between takes and cards. Keep an old recording
until its replacement is successfully saved. Moving cards does not detach audio.

Detect supported recording/playback formats rather than assuming one codec works
everywhere. Preserve imported originals and report unsupported formats clearly.
The old iPad must retain text playback even if recording is unavailable. Built-in
installation must validate or prepare a delivery format tested on all target
devices; a successfully recorded clip is not proof of cross-device playability.

Agreed playback sequence:

1. Establish the card and run any preparation.
2. When voice is enabled, start narration alongside the card actions. Keep written commentary available.
3. Wait for the learner's Next; audio completion never advances automatically.

Cards with a recording show a Voice checkbox. Turn Voice off to stop the clip,
then on to start it from the beginning without repeating viewer actions. Back,
Next, Explore and Exit stop the current clip and cancel pending audio requests.
After Explore, the clip stays stopped until Voice is turned off and on. Cards
without a recording hide the checkbox and preserve the listener's preference.

The introduction offers ordinary Start and, when available, Start with voice.
Conservative initial default: text remains usable without choosing audio. Remember
the listener's voice preference locally; it is not tutorial content. Defer word-level
action/audio timing, continuous recordings and automatic transcription.

## 7. Full and compact narration cards

Voice and card size are independent listener choices. Full mode retains the
written narration. Compact mode removes that text and introductory guidance,
retaining card title/progress, voice controls, Back, Next, Explore and Exit, plus
Show text. Show text expands persistently until the learner chooses Hide text.

Example compact phone layout (controls may wrap, never disappear):

    Card title · 4 / 12                         [Show text]
    [Back] [Play/Pause] [Explore] [Next] [Exit]

Do not make compact mode a prerequisite for narration or silently collapse text
when audio starts. If a card has no usable audio, reveal its written narration;
keep the compact preference for subsequent voiced cards. Recalculate the actual
dialogue/dock footprint before Fit or positioning a pointer. Check Both, Graph
and Details views on phones. Controls remain keyboard/screen-reader accessible.

## 8. Local storage, backup and Google sync

Expose personal tutorials as a collection through the same Personal data facade.
Use a versioned IndexedDB store for tutorial metadata and a separate asset table
for binary audio, not Base64 inside localStorage or every tutorial record. Casual users retain current behaviour without setup.
Only load the current clip; release media resources after use. Report persistence
failure and offer export; browser storage is not a guaranteed backup.

Compatibility constraint: the published viewer's profile normalizer and CSV sync
archive do not preserve unknown collections. Adding tutorials to that old archive
would let an old tab overwrite them. Keep tutorial metadata outside the legacy
local-storage profile too; the shared facade owns both stores. Keep the existing
four-collection cloud file unchanged and introduce a versioned companion “PhysicsKG tutorials.zip” behind the
same Connect/Sync controls. Old viewers cannot overwrite a file they do not use.
Synchronize immutable audio as separate attachments, transferring missing/changed
assets rather than the entire recording library after every reading tick.

Tutorial text/actions sync at whole-tutorial granularity. Keep a last-successful-sync
baseline/revision so independent edits can be detected. If both copies changed,
preserve a clearly labelled conflict copy rather than merging card order or losing
one edit. Deletions use tombstones; preserve an independently edited copy when it
conflicts with deletion. Record the conflict resolution so repeated sync does not
create duplicate conflict copies.

Extend full Personal data export/import to include tutorials and audio, while
retaining import of older backups. Standalone tutorial export remains available.
The facade coordinates backup/merge across metadata and binary storage; imports
validate/stage all assets before committing references. Report partial cloud
completion honestly. Do not delete audio still referenced by a tutorial, pending
conflict, in-progress transfer or active recording.

## 9. Portable packages and built-in installation

A standalone package has one transparent definition, with optional recordings:

    tutorial.zip
      manifest.json       package schema, tutorial/route schema, asset inventory
      tutorial.json       route plus authoring metadata/provenance
      audio/<asset-id>.*   original audio files named in the inventory

Accept a plain JSON definition for text-only exchange too. Exported definitions
contain no browser-specific media URLs, private notes, study records or entire
personal layouts. Packages identify whether they are unfinished drafts. When an
ID already exists, Import as another copy is the safe default; Replace is explicit
and preserves a recoverable previous copy. KB-unavailable imports remain listed.

Copying a built-in voiced tutorial must retain independent access to its audio:
copy its immutable assets into personal storage, with visible progress/errors,
rather than depending on a mutable built-in URL surviving future releases.
Sharing a package does not publish it. A personal tutorial URL works only where
that tutorial has already been installed or synchronized.

Provide a repository installation tool for an exported package. It validates the
complete route and assets, previews proposed changes, and deliberately creates or
replaces a chosen built-in ID. Preserve card IDs and source attribution where
appropriate; normalise to the existing YAML source contract. The browser cannot
write into the repository or silently replace a built-in. Built-in audio is hosted
as separate immutable assets and packaged/deployed with the website, not embedded
into every viewer. The HTML remains text-capable without bundled audio. Fully
offline use also needs the existing viewer dependencies and any audio assets;
this work does not implicitly include the separate installable/offline-app issue.

## Implemented through stage 5

The editor supports independent cards with stable IDs; add, duplicate, delete,
Move up/down under Advanced; Card selection, Add, Duplicate and Delete remain
readily available. Manual viewer actions use a command form driven by the build validator's shared
command contract. Legacy silent setup remains supported in the data, without an editor.
Each visible action can choose a semantic pointer and a 0–5 second pause before
the next action. Empty or invalid drafts still save; validation identifies the
card/action that prevents playback.

Continue tutorial reconstructs preceding cards without pointer animation, runs the
selected card, then permits normal progression. It validates the entire route.
Exit restores the original view and leaves the editor closed.
Earlier action edits can break later steps: report rehearsal failures, retain the
draft and offer Exit rather than silently repairing the sequence.

Record card actions switches to the normal viewer with a compact strip on both desktop
and phone. Existing actions begin in Redo; session Undo/Redo walks the applied
sequence, Pause +1s adds waits, Finish saves and Cancel keeps the old sequence. Silent setup is retained. The first
card receives a silent `home` preparation command when a recording is accepted,
not on cancellation. Recording reconstructs earlier cards and only the selected
card's setup before accepting input. This avoids device-specific stored snapshots.
Checkpoint snapshots exist only in memory for the active recording, at most 20
captured actions. New recordings cannot overlap playback or another editor.

Capture covers selection, named context/depth, pane/graph modes, module folding,
Search (including clearing the query, debounce and Enter), Fit/Fit++, native
Details block opening/folding, relationship controls and reading-tree
opening/folding/depth/synchronisation. Older local controls are translated before
their native handlers; automatic effects are not captured twice. During replay,
Undo/Redo and restoration the dispatcher bypasses capture.

Personal notes, answers, reading marks and layout/data/account changes are not
recorded or rolled back. Camera gestures and scrolling are not serialized.
Unsupported local clarifications, full-width reading focus, bulk content folding,
custom-context rules and ambiguous repeated reading-concept occurrences are
reported rather than guessed. Hover demonstrations remain available through the
explicit action editor; incidental mouse motion is not recorded. Portable text
export/import and sync are implemented in stage 5; local voice authoring is described below.

Local clarification folds, full-width reading controls and ambiguous repeated
occurrences of a concept in one reading tree remain unsupported capture targets;
the strip reports these rather than guessing which occurrence to reproduce.

### Text portability and sync

Tools → Tutorials → Import accepts the versioned text-only ZIP or JSON exported
by this viewer. The review dialog defaults to an independent copy. Replacement
is offered only for a matching personal ID and preserves a separate previous
copy; a changed local revision stops replacement until reviewed again. Built-ins
are never overwritten by browser import. Missing KB targets/domains remain
editable drafts; repair Required domains and the highlighted actions before
playing. Unsupported commands, unsafe target syntax and damaged archives are
rejected before saving. Export from the editor also recovers its current text if
a local save has failed. ZIP entries are stored UTF-8; JSON is the simpler option
when manually editing a text definition.

Personal data backup includes the entire library, including deletion tombstones.
Old backups retain existing tutorials. Optional Google sync uses the separate
**PhysicsKG tutorials.zip** companion file and whole-route conflict copies; see
[Personal data](personal_data.md). It preserves an open editor and a running
playback snapshot. Exporting a tutorial does not expose notes, answers or layouts.
Packages currently reject audio assets; portable audio delivery remains stage 8.

To install an exported text tutorial into the repository:

```bash
conda run -n sr-kg python tools/install_tutorial.py my-tutorial.zip --tutorial-id my-tutorial --dry-run
conda run -n sr-kg python tools/install_tutorial.py my-tutorial.zip --tutorial-id my-tutorial
```

Use `--replace` explicitly for an existing built-in ID, and `--data-root` for a
separate KB. Required domains are inferred from references and combined with the
exported list; `--domains` overrides that list. Full target/schema validation runs
before an atomic YAML update. Card IDs and author credit survive. Review the Git
diff, build/test normally, then publish through the artifact workflow. The command
does not publish or alter the browser's personal library.

## 10. Delivery stages and review gates

Complete and review each stage before dependent work; commit coherent increments.
Build a reviewable viewer before lengthy browser checks. Publish only when asked,
using the normal artifact workflow and preview version increments.

| Stage | Deliverable and review gate |
| --- | --- |
| 1 — design | This contract, New-as-draft workflow and compact playback sketch. Review the storage compatibility approach and playback defaults before implementation. |
| 2 — library/storage | New and independent built-in copies, minimal editing, persistence and playback through the existing engine. Review copy/edit/reload/play without changing the original. |
| 3 — card editor | Add/delete/duplicate/reorder/edit cards and actions, autosave/status and rehearsal. Review a substantial rewrite with inserted/deleted cards. |
| 4 — action capture | Explicit replacement Record/Finish/Cancel, session Undo/Redo, semantic targets, multiple actions and unsupported-action feedback. Review a tutorial created from scratch and played on desktop/phone. |
| 5 — text portability/sync | Validation/repair, JSON/ZIP round trip, conflict-safe companion sync archive, full backup integration and text-only built-in installation. Review fresh-browser import, two-device sync/conflict and a built-in test build. Useful text-only release boundary. |
| 6 — voice authoring | Per-card recording/import/replacement and durable attachments with stale-narration indicators. Ian voices a finished text route; review reload/listening on laptop, phone and old iPad. |
| 7 — voiced/compact player | Concurrent narration, manual Next, independent full/compact modes and text fallback. Review screen space, scrolling, stopping audio, Explore/Resume and mixed voiced/unvoiced cards. |
| 8 — audio delivery | Complete export/import, attachment sync, repository installation and lazy hosted audio. Review Ian's exported voiced route installed as built-in in a preview, cross-device sync and local/offline behaviour. |

Stage 9 completes the restrained code cleanup, user/authoring guides and Quick
Start, keyboard/screen-reader checks and old-iPad profiling. Final review is the
end-to-end create → voice → export → install workflow before release.

Tests must cover draft/reload safety, built-in independence, editing/reordering,
recording boundaries, presentation restoration, invalid/missing targets, import
rollback, repeated sync/conflicts/deletions, missing audio, format/permission/storage
failures and old/new-viewer coexistence. Retain existing unit and fast/full browser
lanes; avoid multiplying combinations unrelated to a specific behaviour.

### Built-in route visibility audit

The built-in routes use explicit whole-card visibility, with no separate `prepare`
sequences. Using PhysicsKG demonstrates controls with Show cards; its opening map
and reading-tree scene use Hide. The physics routes use Hide throughout: each
card prepares its graph or reading scene quietly, then invites the learner to
read. Card identifiers and teaching order are preserved. Legacy imported
`prepare` sequences remain supported.

## Local voice authoring (issue #6, stages 1–2)

The card editor provides **Record voice narration** below action recording, plus
**Remove voice** beside it and **Import audio file** under Advanced. The voice dialogue displays the card's
formatted written narration without operating the graph. Record/Re-record → Stop
→ Play/Pause → Finish recording accepts a take. Cancel (including Escape) keeps
the previously saved recording. Recording requests microphone permission only on
Record and reuses the stream throughout the tutorial authoring session. Stop,
Finish recording and Cancel mute its tracks; rehearsal and Edit card retain access
within the same tutorial. Done editing, Exit tutorial, switching tutorials,
page exit and recorder errors release them. An ended/revoked stream is reacquired
on the next Record. No audio is recorded between takes. A late permission
On iPhone and iPad, the stream is released after each take so the browser
can return to playback audio routing. Re-recording can prompt for access again.
response after cancellation releases its stream without starting a recording.

Recordings and imported originals are limited to 50 MB per clip. Imports must have
an audio MIME type and a finite duration readable on the current device. Recording
selects a supported MediaRecorder format, falling back to the browser default.
Support on the authoring device does not establish cross-device compatibility.
The dialogue offers Download audio for a separate copy, including after a failed
save; microphone recording is not required for file import or listening.

The local database is version 3, with a separate `audio` object store containing
SHA-256 content IDs, immutable Blob bytes, MIME type and byte length. A card's
optional `audio` reference contains `assetId`, `duration` (seconds),
`commentaryHash` and `actionsHash` (SHA-256 of the portable stable JSON encoding).
The action hash includes preparation, actions, pointers and demonstration mode;
card identity/order and title are excluded. Changed hashes show **Voice needs
review**, retaining the recording. Restoring the original content clears that
indicator. Duplicate cards and personal tutorials share immutable assets.

Saving a take writes its asset and updated tutorial in one IndexedDB transaction,
using the existing revision check. Failure keeps the previous reference and bytes;
the unsaved take remains in the dialogue for retry/download. Removal detaches only
that card's reference. Assets are retained conservatively; garbage collection is
deferred until backup/conflict/transfer lifetimes are implemented.

Delivery remains staged: the player resolves audio from this browser. Version-1 packages,
backups and tutorial sync remain text-only, and explicitly reject records containing
audio references before export or cloud access. No silently incomplete voiced
package is produced. A library containing recordings cannot currently use full
personal-data backup or tutorial sync; download the clips separately for now.
Version-2 clients cannot reopen the upgraded local database and overwrite voice
references. Existing text-only package formats are unchanged.

Before audio delivery ships, introduce package/route schema version 2 with an
asset inventory and validated `audio/<content-id>.<extension>` entries. Use a
separate versioned cloud companion for voiced metadata/attachments; do not place
voice references in the version-1 companion read by older viewers. That migration,
asset transfer, cross-device encoding and compact cards remain
later stages of the issue implementation plan (design delivery stages 7–8).


## Voice playback (issue #6, implementation stage 3)

Tutorial introductions offer **Start** for text and **Start with voice** when at
least one card has an audio reference. The player shows a Voice checkbox on cards with a recording and keeps written narration visible. The listener's
choice is remembered locally, including for Continue tutorial from the editor.
Starting a text-only route does not change that preference.

After card preparation, the clip loads on demand while the card actions run.
The actions and narration proceed independently, without timing cues. Playback and asset loading never block Next, Back,
Explore, Edit card or Exit. Ending audio does not advance the card. Turning Voice off and on restarts the clip without repeating actions.
Returning with Back starts the previous card's clip from the beginning. Explore
stops and releases audio; Continue with tutorial restores the scene with voice
stopped until the listener turns Voice off and on. Navigation invalidates pending
asset loads and play promises so late completion cannot voice an old card or
interrupt the new one.

Missing clips, unsupported audio and browser autoplay rejection keep written
narration and navigation available with a retry message. Unvoiced cards hide
the Voice checkbox and preserve the preference for subsequent cards.
Only the current clip is retained, and its object URL is revoked on navigation.
The controls take part in the existing phone dock sizing and pointer positioning.
Compact mode, audio-bearing packages, hosted audio and attachment sync are still
out of scope for this increment.
