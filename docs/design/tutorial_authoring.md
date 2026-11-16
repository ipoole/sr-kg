# Personal tutorial authoring and voice narration

Status: design accepted; stages 1–3 implemented. Action recording,
export/import, tutorial sync and voice remain planned.
Agreed direction: write and refine the whole tutorial first, then optionally
record its written narration card by card. Ian's recordings should be exportable
and installable as built-in tutorials, adding a personal human voice.

This extends [Tutorial playback](tutorial_playback.md), using its existing
player, semantic commands, pointer targets and presentation restoration.
“Card” is the user-facing term; the existing route format calls it a step.

Stage 2 review: Tools → Tutorials → New tutorial opens the same editor used for
personal copies. Edit tutorial/card titles, summary, author credit and written
narration; select any existing card. Play tutorial returns to the editor on Exit.
Stage 3 adds card management, explicit action editing and selected-card rehearsal;
action capture follows in stage 4.
Personal tutorial text is local-only at this stage; existing backups and Google
sync do not include it. Storage failures retain the open draft and offer Retry.

## 1. Ownership and library

Tools → Tutorials offers Built-in tutorials and My tutorials. Opening the library
does not change the viewer. Personal tutorials need no account or setup.

- New creates and saves a personal draft with one placeholder card, then opens
  the ordinary editor. There is no creation wizard or separate creation model.
- Edit on a built-in means Make an editable copy. The original remains available.
- Personal tutorials support Edit, Duplicate, Play, Export and Delete.
- A copy gets a new tutorial ID and retains source ID/version and author credit.
  Existing card IDs may remain: they are unique within their tutorial.
- Deleting the final card leaves an empty draft with Add card available.
  Drafts can be saved/exported, but incomplete routes cannot be played or installed
  as built-in tutorials. Deletion requires confirmation; reordering does not.

The new draft has title “New tutorial”, an empty summary and one card titled
“New card”, with empty written narration. Placeholder prompts are editor UI,
not narration that could accidentally reach learners. Its action is the existing
zero-duration wait and its pointer target is narration. These are hidden as
“No viewer action”: a commentary-only card needs no invented user interaction.

## 2. Editor workflow

The editor contains tutorial title/summary/optional author credit, an ordered
card list, and the selected card. Support Add, Duplicate, Delete, Move up/down
and drag reordering; the buttons provide keyboard and touch alternatives.

Each card exposes:

| Field | Behaviour |
| --- | --- |
| Title | Short label; required for playback. |
| Written narration | Primary commentary; required for playback. Reuse existing safe text, maths and concept-link conventions and editing helpers. |
| Preparation | Optional supported actions to establish the card's starting view, shown in a collapsible Setup area. |
| Actions | Ordered friendly entries such as “Select Lorentz transformations”, with editable parameters, optional pointer and pause. |
| Voice | Optional recording/file, duration, Listen, Replace and Remove; audio can be added after the text route is complete. |

Autosave valid draft structure locally, including temporarily blank fields.
Show Saving/Saved or a visible failure; never silently discard work on quota or
storage errors. Completing an edit and starting playback flush pending saves.
Track substantive edits, not editor focus, folding or rehearsal, as modifications.
Playback/rehearsal uses a frozen route snapshot: library edits or background sync
must not change its cards midway through playback. Sync must also preserve an open
editor and its current draft, rather than rebuilding the pane or moving the viewer.

Preview card and Play from here reconstruct the preceding route from its known
baseline; they do not assume the current viewer happens to be in the right state.
Play from beginning uses the same player. Exit returns to the editor and its
pre-preview presentation. Review the entire route after changing earlier cards.

Desktop authoring uses the available editor/viewer space. On phones the editor
and action-capture view are switched explicitly rather than squeezing an editor,
graph and details into the screen together. Recording is supported on phones,
not restricted to desktop: show the normal viewer with a compact current-card,
action-count, Undo and Stop strip, then return to the editor on Stop. Desktop is
the initial implementation/test target; phone capture belongs in the stage 4
review gate. Playback remains fully supported on phones and the old iPad;
comfortable complex editing is desktop-first. Microphone recording is a separate
per-device capability, particularly on the old iPad.

## 3. Recording viewer actions

Workflow: Add/select card → Record actions → operate PhysicsKG → Stop recording
→ tidy actions and add written narration → Preview.

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
Prefer semantic block targets and responsive Fit commands. Exact manual framing
and temporary node arrangements are a later extension, not part of this recorder.

While recording, Undo last action removes the last captured action and restores
its preceding viewer presentation, including selection, context, folding and
camera consequences. Redo restores that action/result until a new recorded action
discards the redo branch. These are temporary authoring checkpoints, not permanent
snapshots embedded in exported tutorials. Undo covers supported actions recorded
into this card, not arbitrary personal-data changes. Replay card rehearses the
current sequence without recording the replay. After Stop, edit/delete/reorder
actions in the editor and reconstruct from the card's known start to rehearse.
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
| Route | Existing tutorial ID, title, summary, category, sequence, required domains and ordered steps. Optional author credit. |
| Card/step | Stable step ID, title, commentary, preparation, one action or an ordered action sequence, semantic pointers/pauses; optional audio reference. |
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
the microphone on Stop, cancellation or leaving recording. Keep an old recording
until its replacement is successfully saved. Moving cards does not detach audio.

Detect supported recording/playback formats rather than assuming one codec works
everywhere. Preserve imported originals and report unsupported formats clearly.
The old iPad must retain text playback even if recording is unavailable. Built-in
installation must validate or prepare a delivery format tested on all target
devices; a successfully recorded clip is not proof of cross-device playability.

Agreed playback sequence:

1. Establish the card and finish its viewer actions/pauses and pointer demonstration.
2. Play its narration when voice is enabled. Keep written commentary available.
3. Wait for the learner's Next; audio completion never advances automatically.

Provide Play/Pause and Replay voice. Back, Next, Explore and Exit stop the current
clip; returning to a card starts from its beginning. Pause within a card resumes
from the paused position. Audio replay does not repeat viewer actions. On resuming
from Explore, restore the card and leave its voice stopped, ready for Replay.
Cancel pending media loads/play requests on navigation so a late result cannot
speak an old card. Browser audio restrictions or missing files reveal text and a
clear Play/retry choice; they never strand the learner.

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

## Implemented through stage 3

The editor supports independent cards with stable IDs; add, duplicate, delete,
Move up/down and drag reordering. Visible actions and optional silent setup use
the same command form, driven by the build validator's shared command contract.
Each visible action can choose a semantic pointer and a 0–5 second pause before
the next action. Empty or invalid drafts still save; validation identifies the
card/action that prevents playback.

Preview card reconstructs the preceding cards without pointer animation, then
runs only the selected card. Its Back/Next are disabled. Incomplete later cards
do not prevent this preview. Play from here rebuilds the same prefix and then
permits normal progression; Play tutorial starts at the beginning. Exit restores
the original viewer presentation and reopens the editor at the same card. Earlier
action edits can break later steps: report rehearsal failures, retain the draft
and offer Exit rather than silently repairing the sequence.

Recording remains stage 4; these controls currently edit actions explicitly.

## 10. Delivery stages and review gates

Complete and review each stage before dependent work; commit coherent increments.
Build a reviewable viewer before lengthy browser checks. Publish only when asked,
using the normal artifact workflow and preview version increments.

| Stage | Deliverable and review gate |
| --- | --- |
| 1 — design | This contract, New-as-draft workflow and compact playback sketch. Review the storage compatibility approach and playback defaults before implementation. |
| 2 — library/storage | New and independent built-in copies, minimal editing, persistence and playback through the existing engine. Review copy/edit/reload/play without changing the original. |
| 3 — card editor | Add/delete/duplicate/reorder/edit cards and actions, autosave/status and rehearsal. Review a substantial rewrite with inserted/deleted cards. |
| 4 — action capture | Explicit Record/Stop, Undo/Redo and Replay for one card, semantic targets, multiple actions and unsupported-action feedback. Review a tutorial created from scratch and played on desktop/phone. |
| 5 — text portability/sync | Validation/repair, JSON/ZIP round trip, conflict-safe companion sync archive, full backup integration and text-only built-in installation. Review fresh-browser import, two-device sync/conflict and a built-in test build. Useful text-only release boundary. |
| 6 — voice authoring | Per-card recording/import/replacement and durable attachments with stale-narration indicators. Ian voices a finished text route; review reload/listening on laptop, phone and old iPad. |
| 7 — voiced/compact player | Agreed after-actions narration, manual Next, independent full/compact modes and text fallback. Review screen space, scrolling, stopping audio, Explore/Resume and mixed voiced/unvoiced cards. |
| 8 — audio delivery | Complete export/import, attachment sync, repository installation and lazy hosted audio. Review Ian's exported voiced route installed as built-in in a preview, cross-device sync and local/offline behaviour. |

Stage 9 completes the restrained code cleanup, user/authoring guides and Quick
Start, keyboard/screen-reader checks and old-iPad profiling. Final review is the
end-to-end create → voice → export → install workflow before release.

Tests must cover draft/reload safety, built-in independence, editing/reordering,
recording boundaries, presentation restoration, invalid/missing targets, import
rollback, repeated sync/conflicts/deletions, missing audio, format/permission/storage
failures and old/new-viewer coexistence. Retain existing unit and fast/full browser
lanes; avoid multiplying combinations unrelated to a specific behaviour.
