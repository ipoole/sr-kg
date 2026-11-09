/* Notes list/editor ownership, placement recovery, rendering and CSV exchange. */
function kgCreateNotesController(options) {
  "use strict";
  var escapeHtml = options.markup.escapeHtml;
  var renderConceptText = options.markup.renderConceptText;
  var splitConceptBlocks = options.markup.splitConceptBlocks;
  var getConcept = options.content.getConcept;
  var getModule = options.content.getModule;
  var conceptDisplayId = options.content.conceptDisplayId;
  var conceptGraphicSvg = options.content.conceptGraphicSvg;
  var conceptContentBlocks = options.content.conceptContentBlocks;
  var moduleContentBlocks = options.content.moduleContentBlocks;
  var contentBlockKindLabel = options.content.contentBlockKindLabel;
  var compareConceptIds = options.content.compareConceptIds;
  var compareModules = options.content.compareModules;
  var searchDisplayText = options.content.searchDisplayText;
  var personalDataStore = options.store, userNotesStorageKey = options.storageKey;
  var safeLocalStorageSet = options.writeStorage;
  var schedulePersonalDataAutoSync = options.onSave;
  var refreshActiveConcept = options.onContentChange, refreshNodeTooltips = options.onSummariesChange;
  var userNotesState = loadUserNotes(), editingNoteId = null, editingOccurrence = "";
  var openNotes = new Set();
  function reload() { userNotesState = loadUserNotes(); }
  function openNote(id) { openNotes.add(id); }
  function noteOccurrence(id, context) { return "note:" + id + ":" + (context || ""); }
  function noteContext(element, id) {
    return (element.getAttribute("data-content-occurrence") || "").slice(noteOccurrence(id, "").length);
  }
  function openEditor(id, context) {
    editingNoteId = id; editingOccurrence = noteOccurrence(id, context); openNote(id);
  }
  function noteToggled(element) {
    if (!element.isConnected) { return; }
    var id = element.getAttribute("data-note-id");
    if (element.open) { openNotes.add(id); }
    else {
      openNotes.delete(id);
      if (editingNoteId === id && element.getAttribute("data-content-occurrence") === editingOccurrence) {
        syncUserNoteFromEditor(id);
        editingNoteId = null;
        replaceNoteElement(id);
      }
    }
  }

  function replaceNoteElement(noteId, focusSelector, skipEditor) {
    var note = findUserNote(noteId), focus = null;
    document.querySelectorAll("#info_panel details.user-note").forEach(function(element) {
      if (element.getAttribute("data-note-id") !== noteId) { return; }
      var key = element.getAttribute("data-content-occurrence");
      if (skipEditor && key === editingOccurrence) { return; }
      if (window.MathJax && MathJax.typesetClear) { MathJax.typesetClear([element]); }
      var holder = document.createElement("div");
      holder.innerHTML = note ? renderUserNote(note, noteContext(element, noteId)) : "";
      var replacement = holder.firstElementChild;
      if (!replacement) { element.remove(); return; }
      replacement.open = element.open || (key === editingOccurrence && editingNoteId === noteId);
      element.replaceWith(replacement);
      options.typeset(replacement);
      if (!skipEditor && key === editingOccurrence) {
        focus = replacement.querySelector(focusSelector || ":scope > summary");
      }
    });
    if (focus) {
      focus.focus({preventScroll: true});
      if (focusSelector === ".user-note-edit") { options.onReveal(focus.closest("details.user-note")); }
    }
  }

  function editNote(id, element) {
    if (!findUserNote(id)) { return; }
    if (editingNoteId) {
      var previous = editingNoteId;
      syncUserNoteFromEditor(previous);
      editingNoteId = null;
      replaceNoteElement(previous);
    }
    openEditor(id, element ? noteContext(element, id) : "");
    replaceNoteElement(id, ".user-note-body-input");
  }

  function loadUserNotes() {
    return {
      version: 2,
      notes: personalDataStore.getNotes().map(normalizeUserNote).filter(Boolean)
    };
  }

  function saveUserNotes() {
    var saved = personalDataStore.replaceNotes(userNotesState.notes);
    safeLocalStorageSet(userNotesStorageKey, JSON.stringify(userNotesState));
    schedulePersonalDataAutoSync();
    setNotesStatus(saved ? "Notes saved locally." : "Could not save notes locally.");
    refreshNodeTooltips();
    renderNotesOverview();
    return saved;
  }

  function setNotesStatus(message) {
    var el = document.getElementById("kg_notes_status");
    if (el) { el.innerText = message || ""; }
  }

  function noteIsDefaultEmpty(note) {
    return note &&
      String(note.title || "").trim() === "Note" &&
      String(note.body || "").trim() === "";
  }

  function normalizeUserNote(note) {
    if (!note || !note.section) { return null; }
    var targetType = String(note.targetType || (note.moduleId ? "module" : "concept"));
    var targetId = String(note.targetId || note.moduleId || note.conceptId || "");
    if ((targetType !== "concept" && targetType !== "module") || !targetId) {
      return null;
    }
    var anchor = note.anchor || {};
    var blockIndex = Number(anchor.blockIndex);
    if (!Number.isFinite(blockIndex) || blockIndex < 0) { blockIndex = 0; }
    return {
      id: String(note.id || makeNoteId()),
      targetType: targetType,
      targetId: targetId,
      conceptId: targetType === "concept" ? targetId : "",
      placement: note.placement === "owner" ? "owner" : "anchor",
      section: String(note.section),
      anchor: {
        blockIndex: Math.floor(blockIndex),
        afterText: String(anchor.afterText || ""),
        blockId: String(anchor.blockId || ""),
        sectionKey: String(anchor.sectionKey || ""),
        contextBefore: String(anchor.contextBefore || ""),
        contextAfter: String(anchor.contextAfter || "")
      },
      title: String(note.title || "Untitled note"),
      body: String(note.body || ""),
      createdAt: String(note.createdAt || new Date().toISOString()),
      updatedAt: String(note.updatedAt || note.createdAt || new Date().toISOString())
    };
  }

  function makeNoteId() {
    return "note-" + Date.now().toString(36) + "-" + Math.random().toString(36).slice(2, 9);
  }

  function normalizeNoteAnchorContext(value) {
    return String(value || "").replace(/\s+/g, " ").trim();
  }

  function noteContextBefore(value) {
    var normalized = normalizeNoteAnchorContext(value);
    return normalized.slice(Math.max(0, normalized.length - 160));
  }

  function noteContextAfter(value) {
    return normalizeNoteAnchorContext(value).slice(0, 160);
  }

  function noteAnchorSpecs(blockId, sectionKey, sectionName, text) {
    var blocks = splitConceptBlocks(String(text || ""));
    var specs = [];
    for (var index = 0; index <= blocks.length; index += 1) {
      var before = blocks.slice(0, index).map(function(block) {
        return block.text || "";
      }).join(" ");
      var after = blocks.slice(index).map(function(block) {
        return block.text || "";
      }).join(" ");
      specs.push({
        blockId: String(blockId || ""),
        sectionKey: String(sectionKey || ""),
        section: String(sectionName || ""),
        blockIndex: index,
        contextBefore: index === 0 ? "" : noteContextBefore(before),
        contextAfter: index === blocks.length ? "" : noteContextAfter(after),
        legacyAfter: index === 0 ? "" : String(blocks[index - 1].text || "").slice(0, 160)
      });
    }
    return specs;
  }

  function blockNoteAnchorCandidates(block) {
    var title = block.title || contentBlockKindLabel(block.kind);
    var result = noteAnchorSpecs(block.block_id, "", title, block.body);
    function visit(parts, slots) {
      parts.forEach(function(part) {
        if (part.type !== "explanation" || part.slot.indexOf("~legacy-") === 0) { return; }
        var path = slots.concat([part.slot]);
        result = result.concat(noteAnchorSpecs(block.block_id, options.markup.localScopeKey(path),
          part.title, options.markup.contentText(part.parts)));
        visit(part.parts, path);
      });
    }
    visit(options.markup.parseContent(block.body), []);
    return result;
  }

  function noteAnchorCandidates(targetType, targetId) {
    var candidates = [];
    if (targetType === "concept") {
      var concept = getConcept(targetId);
      if (!concept) { return candidates; }
      if (conceptGraphicSvg(concept)) {
        candidates = candidates.concat(noteAnchorSpecs("", "graphic", "Graphic", ""));
      }
      conceptContentBlocks(concept).forEach(function(block) {
        var specs = blockNoteAnchorCandidates(block);
        specs.forEach(function(candidate) { candidate.legacySectionKey = "legacy:" + block.kind; });
        candidates = candidates.concat(specs);
      });
      if (Array.isArray(concept.study_questions) && concept.study_questions.length > 0) {
        candidates = candidates.concat(
          noteAnchorSpecs("", "study-questions", "Study Questions", "")
        );
      }
    } else if (targetType === "module") {
      var module = getModule(targetId);
      if (!module) { return candidates; }
      if (module.svg_detail || module.svg_icon) {
        candidates = candidates.concat(noteAnchorSpecs("", "graphic", "Graphic", ""));
      }
      moduleContentBlocks(module).forEach(function(block) {
        candidates = candidates.concat(blockNoteAnchorCandidates(block));
      });
    }
    return candidates;
  }

  function canonicalNoteAnchor(targetType, targetId, blockId, sectionKey, blockIndex) {
    blockId = String(blockId || "");
    sectionKey = String(sectionKey || "");
    blockIndex = Number(blockIndex) || 0;
    if (!blockId && !sectionKey) { return null; }
    var matches = noteAnchorCandidates(targetType, targetId).filter(function(candidate) {
      var sameScope = blockId
        ? candidate.blockId === blockId && candidate.sectionKey === sectionKey
        : candidate.sectionKey === sectionKey;
      return sameScope && candidate.blockIndex === blockIndex;
    });
    return matches.length === 1 ? matches[0] : null;
  }

  function uniqueBestNoteAnchor(candidates, anchor) {
    var before = normalizeNoteAnchorContext(anchor.contextBefore);
    var after = normalizeNoteAnchorContext(anchor.contextAfter);
    if (!before && !after) {
      var byIndex = candidates.filter(function(candidate) {
        return candidate.blockIndex === Number(anchor.blockIndex || 0);
      });
      return byIndex.length === 1 ? byIndex[0] : null;
    }
    var scored = candidates.map(function(candidate) {
      var score = 0;
      if (before && candidate.contextBefore === before) { score += 2; }
      if (after && candidate.contextAfter === after) { score += 1; }
      return {candidate: candidate, score: score};
    });
    var best = Math.max.apply(null, scored.map(function(item) { return item.score; }));
    if (best <= 0) { return null; }
    var matches = scored.filter(function(item) { return item.score === best; });
    return matches.length === 1 ? matches[0].candidate : null;
  }

  function adoptResolvedNoteAnchor(note, candidate) {
    if (!candidate) { return null; }
    var anchor = note.anchor || (note.anchor = {});
    if (!anchor.blockId && !anchor.sectionKey) {
      anchor.blockId = candidate.blockId;
      anchor.sectionKey = candidate.sectionKey;
      anchor.blockIndex = candidate.blockIndex;
      anchor.contextBefore = candidate.contextBefore;
      anchor.contextAfter = candidate.contextAfter;
    }
    return candidate;
  }

  function repairResolvedNoteAnchor(note, candidate) {
    if (!candidate) { return null; }
    var anchor = note.anchor || (note.anchor = {});
    anchor.blockId = candidate.blockId;
    anchor.sectionKey = candidate.sectionKey;
    anchor.blockIndex = candidate.blockIndex;
    anchor.contextBefore = candidate.contextBefore;
    anchor.contextAfter = candidate.contextAfter;
    note.updatedAt = new Date().toISOString();
    return candidate;
  }

  function resolveNoteAnchor(note) {
    if (note.placement === "owner") { return {placement: "owner"}; }
    var candidates = noteAnchorCandidates(note.targetType, note.targetId);
    var anchor = note.anchor || {};
    var scoped = [];
    if (anchor.blockId) {
      scoped = candidates.filter(function(candidate) {
        return candidate.blockId === String(anchor.blockId) &&
          candidate.sectionKey === (String(anchor.sectionKey || "").indexOf("legacy:") === 0
            ? "" : String(anchor.sectionKey || ""));
      });
    } else if (anchor.sectionKey) {
      scoped = candidates.filter(function(candidate) {
        return candidate.sectionKey === String(anchor.sectionKey) ||
          candidate.legacySectionKey === String(anchor.sectionKey);
      });
    }
    if (scoped.length > 0) {
      var resolved = uniqueBestNoteAnchor(scoped, anchor);
      if (resolved) {
        return String(anchor.sectionKey || "").indexOf("legacy:") === 0 && resolved.blockId
          ? repairResolvedNoteAnchor(note, resolved) : resolved;
      }

      // Early module-note builds could retain a valid stable block and
      // preceding paragraph while recording stale context fields. Use
      // that authored paragraph identity as a constrained repair path.
      var legacyAfter = normalizeNoteAnchorContext(anchor.afterText);
      var paragraphMatches = scoped.filter(function(candidate) {
        return legacyAfter &&
          normalizeNoteAnchorContext(candidate.legacyAfter) === legacyAfter;
      });
      if (paragraphMatches.length === 1) {
        return repairResolvedNoteAnchor(note, paragraphMatches[0]);
      }
      if (!legacyAfter && Number(anchor.blockIndex || 0) === 0) {
        var leadingMatches = scoped.filter(function(candidate) {
          return candidate.blockIndex === 0;
        });
        if (leadingMatches.length === 1) {
          return repairResolvedNoteAnchor(note, leadingMatches[0]);
        }
      }
      return null;
    }
    if (anchor.blockId || anchor.sectionKey) { return null; }

    // Version-1 notes and CSV rows used a visible title plus local index.
    var legacy = candidates.filter(function(candidate) {
      return candidate.section === String(note.section || "");
    });
    if (anchor.afterText) {
      var afterMatches = legacy.filter(function(candidate) {
        return normalizeNoteAnchorContext(candidate.legacyAfter) ===
          normalizeNoteAnchorContext(anchor.afterText);
      });
      if (afterMatches.length === 1) {
        return adoptResolvedNoteAnchor(note, afterMatches[0]);
      }
      return null;
    }
    var indexMatches = legacy.filter(function(candidate) {
      return candidate.blockIndex === Number(anchor.blockIndex || 0);
    });
    return indexMatches.length === 1
      ? adoptResolvedNoteAnchor(note, indexMatches[0])
      : null;
  }

  function noteAnchorStatus(note) {
    var targetExists = note.targetType === "concept"
      ? Boolean(getConcept(note.targetId))
      : Boolean(getModule(note.targetId));
    if (!targetExists) { return "missing-target"; }
    return resolveNoteAnchor(note) ? "resolved" : "unmatched";
  }

  function unresolvedNoteCount() {
    return userNotesState.notes.filter(function(note) {
      return noteAnchorStatus(note) !== "resolved";
    }).length;
  }

  function migrateUserNotesState() {
    if (!userNotesState || !Array.isArray(userNotesState.notes)) { return; }
    var before = JSON.stringify(userNotesState.notes);
    userNotesState.version = 2;
    userNotesState.notes.forEach(function(note) { resolveNoteAnchor(note); });
    if (JSON.stringify(userNotesState.notes) !== before) {
      personalDataStore.replaceNotes(userNotesState.notes);
    }
    safeLocalStorageSet(userNotesStorageKey, JSON.stringify(userNotesState));
  }

  function sameNoteAnchor(left, right) {
    return left && right &&
      left.blockId === right.blockId &&
      left.sectionKey === right.sectionKey &&
      left.blockIndex === right.blockIndex &&
      left.contextBefore === right.contextBefore &&
      left.contextAfter === right.contextAfter;
  }

  function notesForAnchor(targetType, targetId, anchorSpec) {
    return userNotesState.notes.filter(function(note) {
      return note.placement !== "owner" && note.targetType === String(targetType) &&
        note.targetId === String(targetId) &&
        sameNoteAnchor(resolveNoteAnchor(note), anchorSpec);
    }).sort(function(a, b) {
      return String(a.createdAt).localeCompare(String(b.createdAt));
    });
  }

  function noteCountForBlock(targetType, targetId, blockId, sectionKey) {
    blockId = String(blockId || "");
    sectionKey = String(sectionKey || "");
    var owner = (targetType === "module" ? getModule(targetId) : getConcept(targetId)) || {};
    var wrapsGraphic = blockId && (owner.content_blocks || []).some(function(block) {
      return block.block_id === blockId && block.graphic === "detail";
    });
    return userNotesState.notes.filter(function(note) {
      if (note.placement === "owner" || note.targetType !== String(targetType) || note.targetId !== String(targetId)) {
        return false;
      }
      var resolved = resolveNoteAnchor(note);
      if (!resolved) { return false; }
      return blockId
        ? (resolved.blockId === blockId && (!sectionKey || resolved.sectionKey === sectionKey)) ||
          (wrapsGraphic && resolved.sectionKey === "graphic")
        : resolved.sectionKey === sectionKey;
    }).length;
  }

  function ownerNotes(targetType, targetId) {
    return sortedUserNotes().filter(function(note) {
      return note.placement === "owner" && note.targetType === targetType && note.targetId === targetId;
    });
  }

  function renderOwnerNoteAction(targetType, targetId) {
    return '<button type="button" class="kg-note-block-action kg-note-owner-action"' +
      ' data-note-state="' + (ownerNotes(targetType, targetId).length ? "present" : "empty") +
      '" data-target-type="' + escapeHtml(targetType) + '" data-target-id="' + escapeHtml(targetId) +
      '" aria-label="Add a personal note to this ' + escapeHtml(targetType) +
      '" title="Add a personal note"><span class="kg-note-bubble-glyph" aria-hidden="true">+</span></button>';
  }

  function renderOwnerNotes(targetType, targetId) {
    var notes = ownerNotes(targetType, targetId);
    return notes.length ? '<section class="kg-owner-notes" aria-label="Personal notes">' +
      notes.map(function(note) { return renderUserNote(note); }).join("") + '</section>' : "";
  }

  function createOwnerNote(targetType, targetId) {
    return createUserNote(targetType, targetId, "Personal notes", 0, "", {placement: "owner"});
  }

  function revealNote(noteId, focusEditor) {
    window.requestAnimationFrame(function() {
      var input = noteEditorField(noteId, ".user-note-title-input") ||
        noteEditorField(noteId, ".user-note-edit");
      if (!input) { return; }
      var parent = input.parentElement;
      while (parent && parent.id !== "info_panel") {
        if (parent.tagName === "DETAILS") { parent.open = true; }
        parent = parent.parentElement;
      }
      options.onReveal(focusEditor ? input : input.closest("details.user-note"));
      input.focus({preventScroll: true});
      if (focusEditor) { input.select(); }
    });
  }

  function renderNoteBlockAction(targetType, targetId, sectionName, blockId, sectionKey, withReadToggle) {
    var count = noteCountForBlock(targetType, targetId, blockId, sectionKey);
    var hasNotes = count > 0;
    var label = hasNotes
      ? "Notes present in " + sectionName + "; add another note"
      : "Add a note to " + sectionName;
    return '<span class="kg-note-heading-actions' +
      (withReadToggle ? " kg-note-heading-actions-with-read" : "") + '">' +
      '<span class="kg-note-placement-instruction" role="status" aria-live="polite">' +
      'Choose paragraph ↓<span class="kg-visually-hidden">. The note will appear ' +
      'below it. Press Escape to cancel.</span>' +
      "</span>" +
      '<button type="button" class="kg-note-placement-cancel">Cancel</button>' +
      '<button type="button" class="kg-note-block-action' +
      (withReadToggle ? " kg-note-block-action-with-read" : "") +
      '" data-note-state="' + (hasNotes ? "present" : "empty") +
      '" data-target-type="' + escapeHtml(targetType) +
      '" data-target-id="' + escapeHtml(targetId) +
      '" data-section="' + escapeHtml(sectionName) +
      '" data-anchor-block-id="' + escapeHtml(blockId || "") +
      '" data-anchor-section-key="' + escapeHtml(sectionKey || "") +
      '" aria-label="' + escapeHtml(label) + '" aria-pressed="false" title="' +
      escapeHtml(label) + '">' +
      '<span class="kg-note-bubble-glyph" aria-hidden="true">' +
      "+</span></button></span>";
  }

  function findUserNote(noteId) {
    return userNotesState.notes.find(function(note) {
      return note.id === noteId;
    }) || null;
  }

  function noteTargetLabel(note) {
    if (note.targetType === "module") {
      var module = getModule(note.targetId) || {};
      return "Module " + (module.title || note.targetId);
    }
    var concept = getConcept(note.targetId) || {};
    return conceptDisplayId(note.targetId) +
      (concept.label ? " " + searchDisplayText(concept.label) : "");
  }

  function sortedUserNotes() {
    return userNotesState.notes.slice().sort(function(a, b) {
      var typeOrder = String(a.targetType).localeCompare(String(b.targetType));
      if (typeOrder !== 0) { return typeOrder; }
      var targetOrder = a.targetType === "concept"
        ? compareConceptIds(a.targetId, b.targetId)
        : compareModules(a.targetId, b.targetId);
      if (targetOrder !== 0) { return targetOrder; }
      return String(a.createdAt).localeCompare(String(b.createdAt));
    });
  }

  function renderNotesOverview() {
    var countEl = document.getElementById("kg_notes_count");
    var listEl = document.getElementById("kg_notes_list");
    if (!countEl || !listEl) { return; }

    var count = userNotesState.notes.length;
    var deleteAllButton = document.getElementById("kg_notes_delete_all");
    if (deleteAllButton) { deleteAllButton.disabled = count === 0; }
    countEl.innerText = count + " note" + (count === 1 ? "" : "s");
    if (count === 0) {
      listEl.innerHTML = '<div class="kg-note-list-empty">No notes yet.</div>';
      return;
    }

    listEl.innerHTML = sortedUserNotes().map(function(note) {
      var status = noteAnchorStatus(note);
      var warning = status === "resolved" ? "" :
        '<span class="kg-note-list-warning">' +
        (status === "missing-target" ? "Missing target" : "Needs placement") +
        "</span>";
      return '<button type="button" class="kg-note-list-item" data-note-id="' +
        escapeHtml(note.id) + '" data-target-type="' + escapeHtml(note.targetType) +
        '" data-target-id="' + escapeHtml(note.targetId) + '">' +
        '<span class="kg-note-list-concept">' + escapeHtml(noteTargetLabel(note)) + "</span>" +
        '<span class="kg-note-list-title">' + escapeHtml(note.title || "Untitled note") + "</span>" +
        warning +
        "</button>";
    }).join("");
  }

  function renderUserNote(note, occurrence) {
    var key = noteOccurrence(note.id, occurrence);
    var editing = note.id === editingNoteId && key === editingOccurrence;
    var body;
    if (editing) {
      body = '<div class="user-note-editor">' +
        '<label>Title<input class="user-note-title-input" data-note-id="' +
        escapeHtml(note.id) + '" value="' + escapeHtml(note.title || "") + '"></label>' +
        '<label>Note<textarea class="user-note-body-input" data-note-id="' +
        escapeHtml(note.id) + '">' + escapeHtml(note.body || "") + '</textarea></label>' +
        '<small class="user-note-maths-help">Maths: inline <code>\\(x^2\\)</code>; display <code>\\[E=mc^2\\]</code>.</small>' +
        '<div class="user-note-actions">' +
        '<button type="button" class="user-note-insert-maths" data-note-id="' +
        escapeHtml(note.id) + '">Insert maths</button>' +
        '<button type="button" class="user-note-close" data-note-id="' +
        escapeHtml(note.id) + '">Done</button>' +
        '<button type="button" class="user-note-delete" data-note-id="' +
        escapeHtml(note.id) + '">Delete</button>' +
        '<span class="user-note-saved">Saved locally</span></div></div>';
    } else {
      body = options.markup.renderBodyLines(note.body || "", "user-note-reading", {origin: "personal"});
    }
    var topLevel = note.placement === "owner";
    return options.markup.renderContentUnit({
      origin: "personal", id: note.id, occurrenceKey: key,
      capabilities: {edit: true, annotate: false, trackRead: false},
      level: topLevel ? "block" : "inline",
      className: "user-note" + (topLevel ? "" : " optional-detail"),
      open: openNotes.has(note.id), title: note.title || "Untitled note",
      bodyClass: "user-note-content", bodyHtml: body,
      actions: editing ? [] : [{capability: "edit",
        html: '<button type="button" class="user-note-edit" data-note-id="' +
          escapeHtml(note.id) + '">Edit</button>'}]
    });
  }

  function renderNotesAtAnchor(targetType, targetId, sectionName, anchorIndex, afterText, anchorSpec, context) {
    var occurrence = options.markup.occurrenceKey(context);
    anchorSpec = anchorSpec || {
      blockId: "", sectionKey: "", section: String(sectionName),
      blockIndex: Number(anchorIndex), contextBefore: "", contextAfter: ""
    };
    var html = "";
    notesForAnchor(targetType, targetId, anchorSpec).forEach(function(note) {
      html += renderUserNote(note, occurrence);
    });
    html += '<div class="kg-add-note-row">';
    html += '<button type="button" class="kg-add-note" data-section="' +
      escapeHtml(sectionName) + '" data-anchor-index="' + String(anchorIndex) +
      '" data-anchor-after="' + escapeHtml(afterText || "") +
      '" data-anchor-block-id="' + escapeHtml(anchorSpec.blockId || "") +
      '" data-anchor-section-key="' + escapeHtml(anchorSpec.sectionKey || "") +
      '" data-anchor-context-before="' + escapeHtml(anchorSpec.contextBefore || "") +
      '" data-anchor-context-after="' + escapeHtml(anchorSpec.contextAfter || "") +
      '" data-target-type="' + escapeHtml(targetType) +
      '" data-note-occurrence="' + escapeHtml(occurrence) +
      '" data-target-id="' + escapeHtml(targetId) + '">+ note</button>';
    html += "</div>";
    return html;
  }

  function renderNoteAnchoredBody(targetType, targetId, sectionName, blockId, sectionKey, text, context, capabilities) {
    var annotate = !capabilities || capabilities.annotate !== false;
    var blocks = splitConceptBlocks(String(text || ""));
    var specs = noteAnchorSpecs(blockId, sectionKey, sectionName, text);
    var html = annotate ? renderNotesAtAnchor(
      targetType, targetId, sectionName, 0, "", specs[0], context
    ) : "";
    blocks.forEach(function(textBlock, index) {
      html += '<div class="concept-line">' +
        (textBlock.text ? renderConceptText(textBlock.text, Object.assign({}, context,
          {legacyPrefix: "paragraph-" + index})) : "&nbsp;") +
        "</div>";
      if (annotate) { html += renderNotesAtAnchor(
        targetType,
        targetId,
        sectionName,
        index + 1,
        String(textBlock.text || "").slice(0, 160),
        specs[index + 1], context
      ); }
    });
    return html;
  }

  function renderUnmatchedNotes(targetType, targetId) {
    var notes = userNotesState.notes.filter(function(note) {
      return note.targetType === String(targetType) &&
        note.targetId === String(targetId) && noteAnchorStatus(note) === "unmatched";
    });
    if (notes.length === 0) { return ""; }
    var html = '<details class="kg-unmatched-notes" open>' +
      '<summary>Notes needing placement (' + notes.length + ")</summary>" +
      '<p>The original content changed, so these notes were not moved automatically.</p>';
    notes.forEach(function(note) {
      html += '<div class="kg-unmatched-note"><div class="kg-unmatched-note-location">Former section: ' +
        escapeHtml(note.section || "Unknown") + "</div>" + renderUserNote(note) + "</div>";
    });
    return html + "</details>";
  }

  function createUserNote(targetType, targetId, sectionName, anchorIndex, afterText, stableAnchor) {
    stableAnchor = stableAnchor || {};
    var now = new Date().toISOString();
    var note = {
      id: makeNoteId(),
      targetType: String(targetType),
      targetId: String(targetId),
      conceptId: targetType === "concept" ? String(targetId) : "",
      section: String(sectionName),
      placement: stableAnchor.placement === "owner" ? "owner" : "anchor",
      anchor: {
        blockIndex: Number(anchorIndex) || 0,
        afterText: String(afterText || ""),
        blockId: String(stableAnchor.blockId || ""),
        sectionKey: String(stableAnchor.sectionKey || ""),
        contextBefore: String(stableAnchor.contextBefore || ""),
        contextAfter: String(stableAnchor.contextAfter || "")
      },
      title: "Note",
      body: "",
      createdAt: now,
      updatedAt: now
    };
    userNotesState.notes.push(note);
    openEditor(note.id);
    saveUserNotes();
    return note;
  }

  function deleteAllNotes() {
    userNotesState.notes = [];
    editingNoteId = null;
    openNotes.clear();
    var saved = saveUserNotes();
    refreshActiveConcept();
    if (saved) { setNotesStatus("All notes deleted. Deletions will synchronise when connected."); }
  }

  function deleteUserNote(noteId) {
    userNotesState.notes = userNotesState.notes.filter(function(note) {
      return note.id !== noteId;
    });
    if (editingNoteId === noteId) { editingNoteId = null; }
    openNotes.delete(noteId);
    saveUserNotes();
  }

  function updateUserNote(noteId, fields) {
    var note = findUserNote(noteId);
    if (!note) { return; }
    Object.keys(fields).forEach(function(key) {
      note[key] = String(fields[key]);
    });
    note.updatedAt = new Date().toISOString();
    saveUserNotes();
    replaceNoteElement(noteId, null, true);
  }

  function noteEditorField(noteId, selector) {
    var fields = document.querySelectorAll(selector);
    for (var i = 0; i < fields.length; i++) {
      if (fields[i].getAttribute("data-note-id") === noteId) {
        return fields[i];
      }
    }
    return null;
  }

  function syncUserNoteFromEditor(noteId) {
    var note = findUserNote(noteId);
    if (!note) { return null; }
    var titleInput = noteEditorField(noteId, ".user-note-title-input");
    var bodyInput = noteEditorField(noteId, ".user-note-body-input");
    var title = titleInput ? String(titleInput.value || "") : note.title;
    var body = bodyInput ? String(bodyInput.value || "") : note.body;
    if (title === note.title && body === note.body) { return note; }
    note.title = title;
    note.body = body;
    note.updatedAt = new Date().toISOString();
    saveUserNotes();
    replaceNoteElement(noteId, null, true);
    return note;
  }

  function insertMaths(noteId) {
    var input = noteEditorField(noteId, ".user-note-body-input");
    if (!input) { return; }
    var start = input.selectionStart, end = input.selectionEnd;
    var example = "\\(\\gamma = 1/\\sqrt{1-v^2/c^2}\\)";
    input.setRangeText(example, start, end, "end");
    input.focus({preventScroll: true});
    input.dispatchEvent(new Event("input", {bubbles: true}));
  }

  function closeUserNote(noteId) {
    var note = syncUserNoteFromEditor(noteId);
    if (!note) { return; }
    editingNoteId = null;
    if (noteIsDefaultEmpty(note)) {
      deleteUserNote(noteId);
      refreshActiveConcept();
    } else {
      openNote(noteId);
      replaceNoteElement(noteId, ".user-note-edit");
    }
  }

  function notesToCsv() {
    var rows = [[
      "note_id",
      "target_type",
      "target_id",
      "target_label",
      "concept_id",
      "concept_label",
      "section",
      "placement",
      "anchor_index",
      "anchor_after",
      "anchor_block_id",
      "anchor_section_key",
      "anchor_context_before",
      "anchor_context_after",
      "title",
      "body",
      "created_at",
      "updated_at"
    ]];
    userNotesState.notes.forEach(function(note) {
      var concept = note.targetType === "concept" ? (getConcept(note.targetId) || {}) : {};
      rows.push([
        note.id,
        note.targetType,
        note.targetId,
        noteTargetLabel(note),
        note.targetType === "concept" ? note.targetId : "",
        concept.label || "",
        note.section,
        note.placement || "anchor",
        String((note.anchor && note.anchor.blockIndex) || 0),
        (note.anchor && note.anchor.afterText) || "",
        (note.anchor && note.anchor.blockId) || "",
        (note.anchor && note.anchor.sectionKey) || "",
        (note.anchor && note.anchor.contextBefore) || "",
        (note.anchor && note.anchor.contextAfter) || "",
        note.title || "",
        note.body || "",
        note.createdAt || "",
        note.updatedAt || ""
      ]);
    });
    return rows.map(function(row) {
      return row.map(kgCsv.escape).join(",");
    }).join("\n") + "\n";
  }

  function exportNotes() {
    var csv = notesToCsv();
    var blob = new Blob([csv], {type: "text/csv;charset=utf-8"});
    var url = URL.createObjectURL(blob);
    var link = document.createElement("a");
    link.href = url;
    link.download = "srkg-notes.csv";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    setNotesStatus("Exported " + userNotesState.notes.length + " note(s).");
  }

  function importNotesCsv(text) {
    var rows = kgCsv.parse(text, {allowUnclosedQuotes: true}).filter(function(row) {
      return row.some(function(value) { return String(value || "").trim(); });
    });
    if (rows.length < 2) { return 0; }
    var headers = {};
    rows[0].forEach(function(name, index) {
      headers[String(name).trim()] = index;
    });
    function value(row, name) {
      var index = headers[name];
      return index === undefined ? "" : String(row[index] || "");
    }

    var imported = 0;
    rows.slice(1).forEach(function(row) {
      var conceptId = value(row, "concept_id").trim();
      var targetType = value(row, "target_type").trim() || "concept";
      var targetId = value(row, "target_id").trim() || conceptId;
      var section = value(row, "section").trim();
      if (!targetId || !section || (targetType !== "concept" && targetType !== "module")) { return; }
      var noteId = value(row, "note_id").trim() || makeNoteId();
      var blockIndex = Number(value(row, "anchor_index"));
      if (!Number.isFinite(blockIndex) || blockIndex < 0) { blockIndex = 0; }
      var note = findUserNote(noteId);
      var payload = {
        id: noteId,
        targetType: targetType,
        targetId: targetId,
        conceptId: targetType === "concept" ? targetId : "",
        section: section,
        placement: value(row, "placement") === "owner" ? "owner" : "anchor",
        anchor: {
          blockIndex: Math.floor(blockIndex),
          afterText: value(row, "anchor_after"),
          blockId: value(row, "anchor_block_id"),
          sectionKey: value(row, "anchor_section_key"),
          contextBefore: value(row, "anchor_context_before"),
          contextAfter: value(row, "anchor_context_after")
        },
        title: value(row, "title") || "Imported note",
        body: value(row, "body"),
        createdAt: value(row, "created_at") || new Date().toISOString(),
        updatedAt: value(row, "updated_at") || new Date().toISOString()
      };
      resolveNoteAnchor(payload);
      if (note) {
        Object.assign(note, payload);
      } else {
        userNotesState.notes.push(payload);
      }
      imported += 1;
    });
    saveUserNotes();
    return imported;
  }

  function noteTitlesForConcept(nodeId) {
    return userNotesState.notes
      .filter(function(note) {
        return note.targetType === "concept" && note.targetId === String(nodeId) &&
          !noteIsDefaultEmpty(note);
      })
      .map(function(note) { return note.title || "Untitled note"; })
      .filter(Boolean);
  }

  return {
    setNotesStatus: setNotesStatus,
    noteAnchorSpecs: noteAnchorSpecs,
    canonicalNoteAnchor: canonicalNoteAnchor,
    unresolvedNoteCount: unresolvedNoteCount,
    migrateUserNotesState: migrateUserNotesState,
    renderNoteBlockAction: renderNoteBlockAction,
    renderOwnerNoteAction: renderOwnerNoteAction,
    renderOwnerNotes: renderOwnerNotes,
    createOwnerNote: createOwnerNote,
    revealNote: revealNote,
    findUserNote: findUserNote,
    renderNotesOverview: renderNotesOverview,
    renderNotesAtAnchor: renderNotesAtAnchor, openEditor: openEditor,
    renderNoteAnchoredBody: renderNoteAnchoredBody,
    renderUnmatchedNotes: renderUnmatchedNotes,
    createUserNote: createUserNote,
    deleteUserNote: deleteUserNote,
    deleteAllNotes: deleteAllNotes,
    updateUserNote: updateUserNote,
    noteEditorField: noteEditorField,
    closeUserNote: closeUserNote,
    importNotesCsv: importNotesCsv,
    noteTitlesForConcept: noteTitlesForConcept,
    exportNotes: exportNotes,
    reload: reload,
    openNote: openNote,
    editNote: editNote,
    insertMaths: insertMaths,
    noteToggled: noteToggled
  };
}
