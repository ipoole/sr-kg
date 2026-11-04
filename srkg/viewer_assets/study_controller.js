/* Study/read state, completion summaries, question rendering and marking. */
function kgCreateStudyController(options) {
  "use strict";
  var escapeHtml = options.markup.escapeHtml;
  var renderConceptText = options.markup.renderConceptText;
  var renderStudyText = options.markup.renderStudyText;
  var getConcept = options.content.getConcept;
  var getModule = options.content.getModule;
  var conceptDisplayId = options.content.conceptDisplayId;
  var searchDisplayText = options.content.searchDisplayText;
  var moduleMemberIds = options.content.moduleMemberIds;
  var personalDataStore = options.store;
  var conceptData = options.concepts, moduleData = options.modules;
  var studyProgressStorageKey = options.storageKeys.study, contentReadProgressStorageKey = options.storageKeys.read;
  var safeLocalStorageSet = options.writeStorage;
  var schedulePersonalDataAutoSync = options.onSave;
  var replaceTypesetContent = options.replaceContent;
  var network = options.network;
  var studyQuestionIndex = buildStudyQuestionIndex(), contentBlockIndex = buildContentBlockIndex();
  var contentOwnerBlockIdsCache = {}, graphCompletionStateCache = null;
  var studyProgressState = loadStudyProgress(), contentReadProgressState = loadContentReadProgress();
  var retryingQuestions = new Set(); // Local presentation state; never resets synced attempts.
  function reload() {
    studyProgressState = loadStudyProgress(); contentReadProgressState = loadContentReadProgress();
  }
  function getState() { return copyStudyProgress(studyProgressState); }
  function getQuestion(id) { var value = studyProgressState.questions[String(id)]; return value ? copyStudyProgress(value) : null; }
  function indexedQuestion(id) { return studyQuestionIndex[String(id)] || null; }
  function isRead(id) { return contentReadProgressState.blocks[String(id || "")] === true; }

  function buildStudyQuestionIndex() {
    var index = {};
    Object.keys(conceptData || {}).forEach(function(conceptId) {
      var concept = conceptData[conceptId] || {};
      var questions = Array.isArray(concept.study_questions)
        ? concept.study_questions
        : [];
      questions.forEach(function(question) {
        var questionId = String(question && question.question_id || "");
        if (!questionId) { return; }
        index[questionId] = {
          conceptId: String(conceptId),
          question: question
        };
      });
    });
    return index;
  }

  function buildContentBlockIndex() {
    var index = {};
    function addBlocks(ownerType, ownerId, blocks) {
      (Array.isArray(blocks) ? blocks : []).forEach(function(block) {
        var blockId = String(block && block.block_id || "");
        if (!blockId) { return; }
        index[blockId] = {
          ownerType: ownerType,
          ownerId: String(ownerId),
          title: String(block.title || "")
        };
      });
    }
    Object.keys(conceptData || {}).forEach(function(conceptId) {
      addBlocks("concept", conceptId, conceptData[conceptId].content_blocks);
    });
    Object.keys(moduleData || {}).forEach(function(moduleId) {
      addBlocks("module", moduleId, moduleData[moduleId].content_blocks);
    });
    return index;
  }

  function loadContentReadProgress() {
    return personalDataStore.getReadingState(contentBlockIndex);
  }

  function saveContentReadProgress() {
    return safeLocalStorageSet(
      contentReadProgressStorageKey,
      JSON.stringify(contentReadProgressState)
    );
  }

  function contentOwnerBlockIds(ownerType, ownerId) {
    ownerType = String(ownerType || "");
    ownerId = String(ownerId || "");
    var cacheKey = ownerType + "::" + ownerId;
    if (contentOwnerBlockIdsCache[cacheKey]) {
      return contentOwnerBlockIdsCache[cacheKey];
    }
    var blockIds = Object.keys(contentBlockIndex).filter(function(blockId) {
      var block = contentBlockIndex[blockId];
      return block.ownerType === ownerType && block.ownerId === ownerId;
    });
    if (ownerType === "module") {
      moduleMemberIds(getModule(ownerId)).forEach(function(conceptId) {
        blockIds = blockIds.concat(contentOwnerBlockIds("concept", conceptId));
      });
    }
    contentOwnerBlockIdsCache[cacheKey] = blockIds;
    return blockIds;
  }

  function contentOwnerReadComplete(ownerType, ownerId) {
    var blockIds = contentOwnerBlockIds(ownerType, ownerId);
    return blockIds.length > 0 && blockIds.every(function(blockId) {
      return contentReadProgressState.blocks[blockId] === true;
    });
  }

  function renderContentReadCompletionIndicator(ownerType, ownerId) {
    var complete = contentOwnerReadComplete(ownerType, ownerId);
    return '<span class="content-read-complete-indicator" role="img"' +
      ' aria-label="All content blocks read" title="All content blocks read"' +
      ' data-content-owner-type="' + escapeHtml(ownerType) + '"' +
      ' data-content-owner-id="' + escapeHtml(ownerId) + '"' +
      (complete ? "" : " hidden") + ">✓</span>";
  }

  function renderStudyQuestionCompletionIndicator(ownerType, ownerId) {
    var complete = graphCompletionState(ownerType, ownerId).questions;
    return '<span class="study-question-complete-indicator" role="img"' +
      ' aria-label="All study questions complete" title="All study questions complete"' +
      ' data-study-owner-type="' + escapeHtml(ownerType) + '"' +
      ' data-study-owner-id="' + escapeHtml(ownerId) + '"' +
      (complete ? "" : " hidden") + ">✓</span>";
  }

  function updateContentReadCompletionIndicators() {
    document.querySelectorAll(".content-read-complete-indicator").forEach(
      function(indicator) {
        indicator.hidden = !contentOwnerReadComplete(
          indicator.getAttribute("data-content-owner-type"),
          indicator.getAttribute("data-content-owner-id")
        );
      }
    );
  }

  function updateStudyQuestionCompletionIndicators() {
    document.querySelectorAll(".study-question-complete-indicator").forEach(
      function(indicator) {
        indicator.hidden = !graphCompletionState(
          indicator.getAttribute("data-study-owner-type"),
          indicator.getAttribute("data-study-owner-id")
        ).questions;
      }
    );
  }

  function setContentBlockRead(blockId, isRead) {
    blockId = String(blockId || "");
    if (!contentBlockIndex[blockId]) { return false; }
    personalDataStore.setRead(blockId, isRead);
    contentReadProgressState = loadContentReadProgress();
    saveContentReadProgress();
    updateContentReadCompletionIndicators();
    renderStudyScorecard();
    schedulePersonalDataAutoSync();
    if (network && network.redraw) { network.redraw(); }
    return true;
  }

  function loadStudyProgress() {
    return personalDataStore.getStudyState(studyQuestionIndex);
  }

  function copyStudyProgress(value) {
    return JSON.parse(JSON.stringify(value));
  }

  function saveStudyProgress() {
    return safeLocalStorageSet(
      studyProgressStorageKey,
      JSON.stringify(studyProgressState)
    );
  }

  function announceStudyProgressChange(questionId) {
    try {
      window.dispatchEvent(new CustomEvent("kg:study-progress-changed", {
        detail: {questionId: questionId || ""}
      }));
    } catch (err) {
      // Progress remains usable in older browsers without CustomEvent.
    }
    updateStudyQuestionCompletionIndicators();
    if (network && network.redraw) { network.redraw(); }
  }

  function recordStudyAttempt(questionId, outcome, attemptedAt) {
    questionId = String(questionId || "");
    outcome = String(outcome || "");
    if (!studyQuestionIndex[questionId] ||
        ["correct", "incorrect", "unknown"].indexOf(outcome) === -1) {
      return null;
    }
    var date = attemptedAt ? new Date(attemptedAt) : new Date();
    if (Number.isNaN(date.getTime())) { date = new Date(); }
    retryingQuestions.delete(questionId);
    personalDataStore.addStudyAttempt(questionId, outcome, date.toISOString());
    studyProgressState = loadStudyProgress();
    saveStudyProgress();
    var entry = studyProgressState.questions[questionId];
    schedulePersonalDataAutoSync();
    announceStudyProgressChange(questionId);
    return copyStudyProgress(entry);
  }

  function resetStudyQuestion(questionId) {
    questionId = String(questionId || "");
    retryingQuestions.delete(questionId);
    if (!Object.prototype.hasOwnProperty.call(studyProgressState.questions, questionId)) {
      return false;
    }
    personalDataStore.resetStudy(questionId);
    studyProgressState = loadStudyProgress();
    saveStudyProgress();
    schedulePersonalDataAutoSync();
    announceStudyProgressChange(questionId);
    return true;
  }

  function resetAllStudyProgress() {
    retryingQuestions.clear();
    personalDataStore.resetStudy("");
    studyProgressState = loadStudyProgress();
    saveStudyProgress();
    schedulePersonalDataAutoSync();
    announceStudyProgressChange("");
    return true;
  }

  function conceptQuestionIds(conceptId) {
    var concept = getConcept(conceptId) || {};
    return (Array.isArray(concept.study_questions) ? concept.study_questions : [])
      .map(function(question) {
        return String(question && question.question_id || "");
      })
      .filter(Boolean);
  }

  function questionsComplete(questionIds) {
    questionIds = (questionIds || []).filter(function(questionId, index, ids) {
      return questionId && ids.indexOf(questionId) === index;
    });
    return questionIds.length > 0 && questionIds.every(function(questionId) {
      var progress = studyProgressState.questions[questionId];
      return progress && progress.lastOutcome === "correct";
    });
  }

  function graphCompletionState(ownerType, ownerId) {
    ownerType = String(ownerType || "");
    ownerId = String(ownerId || "");
    if (
      !graphCompletionStateCache ||
      graphCompletionStateCache.readState !== contentReadProgressState ||
      graphCompletionStateCache.studyState !== studyProgressState
    ) {
      graphCompletionStateCache = {
        readState: contentReadProgressState,
        studyState: studyProgressState,
        values: {}
      };
    }
    var cacheKey = ownerType + "::" + ownerId;
    if (graphCompletionStateCache.values[cacheKey]) {
      return graphCompletionStateCache.values[cacheKey];
    }
    var questionIds = [];
    if (ownerType === "concept") {
      questionIds = conceptQuestionIds(ownerId);
    } else if (ownerType === "module") {
      moduleMemberIds(getModule(ownerId)).forEach(function(conceptId) {
        questionIds = questionIds.concat(conceptQuestionIds(conceptId));
      });
    }
    var state = {
      read: contentOwnerReadComplete(ownerType, ownerId),
      questions: questionsComplete(questionIds)
    };
    graphCompletionStateCache.values[cacheKey] = state;
    return state;
  }

  function attemptedStudyQuestions() {
    return Object.keys(studyProgressState.questions).map(function(questionId) {
      var indexed = studyQuestionIndex[questionId];
      if (!indexed) { return null; }
      var concept = getConcept(indexed.conceptId) || {};
      var questions = Array.isArray(concept.study_questions)
        ? concept.study_questions
        : [];
      return {
        questionId: questionId,
        conceptId: indexed.conceptId,
        concept: concept,
        question: indexed.question,
        questionNumber: questions.indexOf(indexed.question) + 1,
        progress: studyProgressState.questions[questionId]
      };
    }).filter(Boolean).sort(function(a, b) {
      return String(b.progress.lastAttemptAt).localeCompare(
        String(a.progress.lastAttemptAt)
      );
    });
  }

  function studyQuestionPrompt(question) {
    return searchDisplayText(
      question && (question.prompt || question.question) || "Question"
    );
  }

  function renderStudyScorecard() {
    var summary = document.getElementById("kg_study_summary");
    var list = document.getElementById("kg_study_list");
    var badge = document.getElementById("kg_study_badge");
    var resetAll = document.getElementById("kg_study_reset_all");
    if (!summary || !list || !badge || !resetAll) { return; }

    var entries = attemptedStudyQuestions();
    var correctCount = entries.filter(function(entry) {
      return entry.progress.lastOutcome === "correct";
    }).length;
    var totalQuestions = Object.keys(studyQuestionIndex).length;
    var readableConceptIds = Object.keys(conceptData || {}).filter(function(conceptId) {
      return contentOwnerBlockIds("concept", conceptId).length > 0;
    });
    var readConcepts = readableConceptIds.filter(function(conceptId) {
      return contentOwnerReadComplete("concept", conceptId);
    }).length;
    summary.textContent = "Questions " + correctCount + "/" + totalQuestions +
      " correct \u00b7 Concepts " + readConcepts + "/" + readableConceptIds.length +
      " read";
    badge.textContent = correctCount + "/" + totalQuestions;
    resetAll.hidden = entries.length === 0;
    list.innerHTML = entries.map(function(entry) {
      var outcome = entry.progress.lastOutcome;
      var attempts = entry.progress.attemptCount;
      var conceptLabel = conceptDisplayId(entry.conceptId) +
        (entry.concept.label ? " " + searchDisplayText(entry.concept.label) : "");
      var questionLabel = entry.questionNumber > 0
        ? "Question " + entry.questionNumber + ": "
        : "";
      return '<div class="kg-study-row" data-question-id="' +
        escapeHtml(entry.questionId) + '">' +
        '<button type="button" class="kg-study-question-link" data-question-id="' +
        escapeHtml(entry.questionId) + '">' +
        '<span class="kg-study-question-concept">' + escapeHtml(conceptLabel) + "</span>" +
        '<span class="kg-study-question-prompt">' + escapeHtml(
          questionLabel + studyQuestionPrompt(entry.question)
        ) + "</span>" +
        '<span class="kg-study-question-meta" data-outcome="' +
        escapeHtml(outcome) + '"><span aria-hidden="true">' +
        studyOutcomeIcon(outcome) + "</span> " +
        escapeHtml(studyOutcomeText(outcome)) + " · " + attempts + " attempt" +
        (attempts === 1 ? "" : "s") + "</span></button>" +
        '<button type="button" class="kg-study-reset-question" data-question-id="' +
        escapeHtml(entry.questionId) + '" aria-label="Reset progress for ' +
        escapeHtml(conceptLabel) + '">Reset</button></div>';
    }).join("");
  }

  function renderContentBlockReadToggle(blockId, title) {
    var checked = contentReadProgressState.blocks[String(blockId || "")] === true;
    return '<input type="checkbox" class="content-block-read-toggle"' +
      ' aria-label="Mark ' + escapeHtml(title) + ' as read"' +
      ' title="Mark as read"' +
      (checked ? " checked" : "") +
      ">";
  }

  function studyOutcomeText(outcome) {
    if (outcome === "correct") { return "Correct"; }
    if (outcome === "unknown") { return "I don’t know"; }
    if (outcome === "incorrect") { return "Incorrect"; }
    return "";
  }

  function studyOutcomeIcon(outcome) {
    return outcome === "correct" ? "✓" : "✕";
  }

  function studyOutcomeFeedbackText(outcome) {
    if (outcome === "correct") { return "Correct — nicely done."; }
    if (outcome === "unknown") {
      return "No problem — review the answer, then try when ready.";
    }
    if (outcome === "incorrect") {
      return "Not quite — review the answer and have another go.";
    }
    return "";
  }

  function studyOptionResultHtml(result) {
    var text = "";
    if (result === "correct") { text = "✓ Correct answer"; }
    if (result === "incorrect") { text = "✕ Your answer"; }
    if (result === "unknown") { text = "✕ I don’t know"; }
    return text
      ? '<span class="study-option-result" data-outcome="' +
        escapeHtml(result) + '">' + escapeHtml(text) + "</span>"
      : "";
  }

  function studyQuestionStatusHtml(progress) {
    var outcome = progress && progress.lastOutcome ? progress.lastOutcome : "";
    if (!outcome) {
      return '<span class="study-question-status" data-outcome=""></span>';
    }
    var retry = outcome === "incorrect";
    var tag = retry ? "button" : "span";
    return '<' + tag + ' class="study-question-status' + (retry ? ' study-retry' : '') +
      '" data-outcome="' + escapeHtml(outcome) + '"' +
      (retry ? ' type="button" aria-label="Try this question again; previous answer incorrect" title="Try again without showing the answer"' : '') +
      '><span aria-hidden="true">' + studyOutcomeIcon(outcome) + "</span> " +
      escapeHtml(studyOutcomeText(outcome)) + "</" + tag + ">";
  }

  function automaticQuestionCorrectOption(question) {
    var options = Array.isArray(question && question.options) ? question.options : [];
    return options.find(function(option) { return option && option.is_correct === true; }) || null;
  }

  function automaticQuestionFeedbackHtml(question, progress) {
    if (!progress || !progress.lastOutcome) { return ""; }
    var answer = question && question.answer ? question.answer : "";
    var html = '<div class="study-question-feedback">';
    html += '<div class="study-question-result" data-outcome="' +
      escapeHtml(progress.lastOutcome) + '"><span aria-hidden="true">' +
      studyOutcomeIcon(progress.lastOutcome) + "</span> " +
      escapeHtml(studyOutcomeFeedbackText(progress.lastOutcome)) + "</div>";
    if (answer) {
      html += renderStudyText(answer, "concept-body study-answer-body");
    }
    html += "</div>";
    return html;
  }

  function renderAutomaticStudyQuestion(question, index) {
    var questionId = String(question.question_id || "");
    var prompt = question.prompt || question.question || "";
    var options = Array.isArray(question.options) ? question.options : [];
    var progress = studyProgressState.questions[questionId] || null;
    var visibleProgress = retryingQuestions.has(questionId) ? null : progress;
    var correctOption = automaticQuestionCorrectOption(question);
    var inputName = "study-response-" + questionId;
    var html = '<details class="study-question study-question-automatic" data-question-id="' +
      escapeHtml(questionId) + '" open>';
    html += '<summary class="study-question-heading"><span class="study-question-title">Question ' +
      (index + 1) + "</span>" + studyQuestionStatusHtml(progress) + "</summary>";
    html += '<div class="study-question-body">';
    html += renderStudyText(prompt, "concept-body study-question-prompt");
    html += '<fieldset class="study-options"><legend class="kg-visually-hidden">Choose one answer</legend>';
    options.forEach(function(option) {
      var optionId = String(option.option_id || "");
      var result = visibleProgress && correctOption && optionId === String(correctOption.option_id)
        ? "correct"
        : "";
      html += '<label class="study-option" data-option-id="' + escapeHtml(optionId) + '"' +
        (result ? ' data-result="' + result + '"' : "") + ">";
      html += '<input type="radio" name="' + escapeHtml(inputName) + '" value="' +
        escapeHtml(optionId) + '">';
      html += '<span class="study-option-text">' + renderConceptText(option.text || "") + "</span>";
      html += studyOptionResultHtml(result);
      html += "</label>";
    });
    html += '<label class="study-option study-option-unknown" data-option-id="__unknown__">';
    html += '<input type="radio" name="' + escapeHtml(inputName) + '" value="__unknown__">';
    html += '<span class="study-option-text">? — I don’t know; show me the answer</span>';
    html += "</label></fieldset>";
    html += '<button type="button" class="study-check-answer" disabled>Check answer</button>';
    html += '<div class="study-feedback-host" role="status" aria-live="polite" aria-atomic="true">' +
      automaticQuestionFeedbackHtml(question, visibleProgress) + "</div>";
    html += "</div></details>";
    return html;
  }

  function selfAssessedQuestionFeedbackHtml(question, progress, response, pending) {
    if (!pending && (!progress || !progress.lastOutcome)) { return ""; }
    var html = '<div class="study-question-feedback study-self-feedback">';
    if (pending) {
      html += '<div class="study-question-result study-review-prompt">' +
        "Compare your answer, then mark it honestly.</div>";
    } else {
      html += '<div class="study-question-result" data-outcome="' +
        escapeHtml(progress.lastOutcome) + '"><span aria-hidden="true">' +
        studyOutcomeIcon(progress.lastOutcome) + "</span> " +
        escapeHtml(studyOutcomeFeedbackText(progress.lastOutcome)) + "</div>";
    }
    if (response) {
      html += '<div class="study-answer-label">Your answer</div>';
      html += renderStudyText(response, "concept-body study-your-answer");
    }
    html += '<div class="study-answer-label">Model answer</div>';
    html += renderStudyText(question.answer || "", "concept-body study-answer-body");
    if (pending) {
      html += '<div class="study-self-mark-actions" aria-label="Mark your answer">';
      html += '<button type="button" class="study-self-mark" data-outcome="correct">✓ Correct</button>';
      html += '<button type="button" class="study-self-mark" data-outcome="incorrect">✕ Incorrect</button>';
      html += "</div>";
    }
    html += "</div>";
    return html;
  }

  function renderSelfAssessedStudyQuestion(question, index) {
    var questionId = String(question && question.question_id || "");
    var prompt = question && (question.prompt || question.question)
      ? (question.prompt || question.question)
      : "";
    if (!prompt) { return ""; }
    var progress = studyProgressState.questions[questionId] || null;
    var html = '<details class="study-question study-question-self-assessed" data-question-id="' +
      escapeHtml(questionId) + '" open>';
    html += '<summary class="study-question-heading"><span class="study-question-title">Question ' +
      (index + 1) + "</span>" + studyQuestionStatusHtml(progress) + "</summary>";
    html += '<div class="study-question-body">';
    html += renderStudyText(prompt, "concept-body study-question-prompt");
    html += '<label class="study-self-response-label">Your answer';
    html += '<textarea class="study-self-response" rows="3"></textarea></label>';
    html += '<div class="study-self-actions">';
    html += '<button type="button" class="study-self-check-answer">Check answer</button>';
    html += '<button type="button" class="study-self-unknown">? I don’t know — show answer</button>';
    html += "</div>";
    html += '<div class="study-response-validation" role="alert"></div>';
    html += '<div class="study-feedback-host" role="status" aria-live="polite" aria-atomic="true">' +
      selfAssessedQuestionFeedbackHtml(question, retryingQuestions.has(questionId) ? null : progress, "", false) + "</div>";
    html += "</div></details>";
    return html;
  }

  function studyOptionElement(card, optionId) {
    var match = null;
    card.querySelectorAll(".study-option").forEach(function(optionElement) {
      if (!match && optionElement.getAttribute("data-option-id") === optionId) {
        match = optionElement;
      }
    });
    return match;
  }

  function setStudyOptionResult(optionElement, result) {
    if (!optionElement) { return; }
    optionElement.removeAttribute("data-result");
    var oldResult = optionElement.querySelector(".study-option-result");
    if (oldResult) { oldResult.remove(); }
    if (!result) { return; }
    optionElement.setAttribute("data-result", result);
    optionElement.insertAdjacentHTML("beforeend", studyOptionResultHtml(result));
  }

  function applyAutomaticQuestionResult(card, question, progress, selectedOptionId) {
    var correctOption = automaticQuestionCorrectOption(question);
    card.querySelectorAll(".study-option").forEach(function(optionElement) {
      setStudyOptionResult(optionElement, "");
    });
    if (correctOption) {
      var correctElement = studyOptionElement(card, String(correctOption.option_id));
      setStudyOptionResult(correctElement, "correct");
    }
    if (progress.lastOutcome !== "correct") {
      var selectedElement = studyOptionElement(card, selectedOptionId);
      if (selectedElement) {
        setStudyOptionResult(
          selectedElement,
          progress.lastOutcome === "unknown" ? "unknown" : "incorrect"
        );
      }
    }
    setStudyCardStatus(card, progress.lastOutcome);
    var feedbackHost = card.querySelector(".study-feedback-host");
    if (feedbackHost) {
      replaceTypesetContent(
        feedbackHost,
        automaticQuestionFeedbackHtml(question, progress)
      );
    }
    var button = card.querySelector(".study-check-answer");
    if (button) { button.disabled = true; }
    card.setAttribute("data-last-submitted-option-id", selectedOptionId);
    if (window.MathJax && MathJax.typesetPromise) {
      MathJax.typesetPromise([card]).catch(function(err) {
        console.warn("MathJax study feedback typesetting failed:", err);
      });
    }
  }

  function submitAutomaticStudyQuestion(card) {
    if (!card) { return; }
    var questionId = String(card.getAttribute("data-question-id") || "");
    var indexed = studyQuestionIndex[questionId];
    var question = indexed && indexed.question;
    var selected = card.querySelector('input[type="radio"]:checked');
    if (!question || !selected) { return; }
    var selectedOptionId = String(selected.value || "");
    if (card.getAttribute("data-last-submitted-option-id") === selectedOptionId) {
      return;
    }
    var correctOption = automaticQuestionCorrectOption(question);
    var outcome = selectedOptionId === "__unknown__"
      ? "unknown"
      : (correctOption && selectedOptionId === String(correctOption.option_id)
        ? "correct"
        : "incorrect");
    var progress = recordStudyAttempt(questionId, outcome);
    if (!progress) { return; }
    applyAutomaticQuestionResult(card, question, progress, selectedOptionId);
  }

  function setStudyCardStatus(card, outcome) {
    var status = card && card.querySelector(".study-question-status");
    if (!status) { return; }
    status.outerHTML = studyQuestionStatusHtml(outcome ? {lastOutcome: outcome} : null);
  }

  function retryStudyQuestion(card) {
    if (!card) { return; }
    var questionId = String(card.getAttribute("data-question-id") || "");
    var progress = getQuestion(questionId);
    if (!studyQuestionIndex[questionId] || !progress || progress.lastOutcome !== "incorrect") { return; }
    retryingQuestions.add(questionId);
    card.removeAttribute("data-last-submitted-option-id");
    card.removeAttribute("data-pending-response");
    card.querySelectorAll('input[type="radio"]').forEach(function(input) { input.checked = false; });
    card.querySelectorAll('.study-option').forEach(function(option) { setStudyOptionResult(option, ""); });
    var textarea = card.querySelector(".study-self-response");
    if (textarea) { textarea.value = ""; }
    var feedback = card.querySelector(".study-feedback-host");
    if (feedback) { replaceTypesetContent(feedback, ""); }
    var validation = card.querySelector(".study-response-validation");
    if (validation) { validation.textContent = ""; }
    var check = card.querySelector(".study-check-answer");
    if (check) { check.disabled = true; }
    card.querySelectorAll('.study-self-check-answer, .study-self-unknown').forEach(function(button) {
      button.disabled = false;
    });
    card.open = true;
    var input = textarea || card.querySelector('input[type="radio"]');
    if (input) { input.focus({preventScroll: true}); }
  }

  function typesetStudyCard(card) {
    if (window.MathJax && MathJax.typesetPromise) {
      MathJax.typesetPromise([card]).catch(function(err) {
        console.warn("MathJax study feedback typesetting failed:", err);
      });
    }
  }

  function renderSelfAssessedFeedback(card, question, progress, response, pending) {
    var feedbackHost = card.querySelector(".study-feedback-host");
    if (feedbackHost) {
      replaceTypesetContent(
        feedbackHost,
        selfAssessedQuestionFeedbackHtml(question, progress, response, pending)
      );
    }
    typesetStudyCard(card);
  }

  function submitSelfAssessedQuestion(card) {
    if (!card) { return; }
    var questionId = String(card.getAttribute("data-question-id") || "");
    var indexed = studyQuestionIndex[questionId];
    var question = indexed && indexed.question;
    var textarea = card.querySelector(".study-self-response");
    var response = textarea ? String(textarea.value || "").trim() : "";
    var validation = card.querySelector(".study-response-validation");
    if (!question || !textarea) { return; }
    if (!response) {
      if (validation) { validation.textContent = "Enter an answer, or choose I don’t know."; }
      textarea.focus();
      return;
    }
    if (validation) { validation.textContent = ""; }
    card.setAttribute("data-pending-response", response);
    renderSelfAssessedFeedback(card, question, null, response, true);
    var checkButton = card.querySelector(".study-self-check-answer");
    if (checkButton) { checkButton.disabled = true; }
  }

  function markSelfAssessedQuestion(card, outcome) {
    if (!card || ["correct", "incorrect"].indexOf(outcome) === -1) { return; }
    var questionId = String(card.getAttribute("data-question-id") || "");
    var indexed = studyQuestionIndex[questionId];
    var question = indexed && indexed.question;
    var response = String(card.getAttribute("data-pending-response") || "");
    if (!question || !response) { return; }
    var progress = recordStudyAttempt(questionId, outcome);
    if (!progress) { return; }
    card.removeAttribute("data-pending-response");
    setStudyCardStatus(card, outcome);
    renderSelfAssessedFeedback(card, question, progress, response, false);
    var unknownButton = card.querySelector(".study-self-unknown");
    if (unknownButton) { unknownButton.disabled = true; }
  }

  function submitUnknownSelfAssessedQuestion(card) {
    if (!card) { return; }
    var questionId = String(card.getAttribute("data-question-id") || "");
    var indexed = studyQuestionIndex[questionId];
    var question = indexed && indexed.question;
    if (!question) { return; }
    var progress = recordStudyAttempt(questionId, "unknown");
    if (!progress) { return; }
    card.removeAttribute("data-pending-response");
    setStudyCardStatus(card, "unknown");
    renderSelfAssessedFeedback(card, question, progress, "", false);
    var checkButton = card.querySelector(".study-self-check-answer");
    var unknownButton = card.querySelector(".study-self-unknown");
    if (checkButton) { checkButton.disabled = true; }
    if (unknownButton) { unknownButton.disabled = true; }
  }

  return {
    renderContentReadCompletionIndicator: renderContentReadCompletionIndicator,
    renderStudyQuestionCompletionIndicator: renderStudyQuestionCompletionIndicator,
    updateContentReadCompletionIndicators: updateContentReadCompletionIndicators,
    setContentBlockRead: setContentBlockRead,
    recordStudyAttempt: recordStudyAttempt,
    resetStudyQuestion: resetStudyQuestion,
    resetAllStudyProgress: resetAllStudyProgress,
    graphCompletionState: graphCompletionState,
    renderStudyScorecard: renderStudyScorecard,
    renderAutomaticStudyQuestion: renderAutomaticStudyQuestion,
    renderSelfAssessedStudyQuestion: renderSelfAssessedStudyQuestion,
    submitAutomaticStudyQuestion: submitAutomaticStudyQuestion,
    retryStudyQuestion: retryStudyQuestion,
    renderSelfAssessedFeedback: renderSelfAssessedFeedback,
    submitSelfAssessedQuestion: submitSelfAssessedQuestion,
    markSelfAssessedQuestion: markSelfAssessedQuestion,
    submitUnknownSelfAssessedQuestion: submitUnknownSelfAssessedQuestion,
    renderContentBlockReadToggle: renderContentBlockReadToggle,
    reload: reload,
    getState: getState,
    getQuestion: getQuestion,
    indexedQuestion: indexedQuestion,
    isRead: isRead
  };
}
