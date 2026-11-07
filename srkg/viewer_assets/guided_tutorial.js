/* Guided playback, pointer/spotlight state, narration and input locking; presentation is a separate port. */
function kgCreateGuidedTutorial(options) {
  "use strict";
  var tutorialData = options.routes;
  var resolveTutorialPointerTarget = options.targets.resolveTutorialPointerTarget;
  var executeViewerCommand = options.execute;
  var captureTutorialPresentation = options.presentation.capture;
  var restoreTutorialPresentation = options.presentation.restore;
  var replayTutorialCommands = options.presentation.replay;
  var nextAnimationFrames = options.settle;
  var hideNodeTooltip = options.hover.hide, restoreHoveredEdge = options.hover.restore;
  var dismissSplash = options.workspace.dismissSplash, setControlsVisible = options.workspace.setControlsVisible;
  var visualViewportRect = options.camera.visualViewportRect, intersectRects = options.camera.intersectRects;
  var replaceTypesetContent = options.details.replaceTypesetContent;
  var cssAttributeValueEscape = options.markup.cssAttributeValueEscape;
  var escapeHtml = options.markup.escapeHtml, renderConceptText = options.markup.renderConceptText;
  var tutorialPlayback = {
    selectedId: null,
    activeRoute: null,
    baseline: null,
    exploreSnapshot: null,
    exploring: false,
    stepIndex: -1,
    transitioning: false
  };
  var tutorialPointerState = {
    target: null,
    label: "",
    rect: null,
    visible: false
  };
  function isGuiding() { return Boolean(tutorialPlayback.activeRoute && !tutorialPlayback.exploring); }

  function tutorialMotionDuration() {
    return window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches
      ? 0
      : 360;
  }

  function positionTutorialPointer(resolved, target) {
    var pointer = document.getElementById("kg_tutorial_pointer");
    var halo = document.getElementById("kg_tutorial_halo");
    if (!pointer || !halo || !resolved) { return; }
    var rect = resolved.rect;
    var padding = 6;
    halo.hidden = false;
    halo.style.left = (rect.x - padding) + "px";
    halo.style.top = (rect.y - padding) + "px";
    halo.style.width = (rect.width + padding * 2) + "px";
    halo.style.height = (rect.height + padding * 2) + "px";
    pointer.hidden = false;
    pointer.style.transform = "translate3d(" +
      (rect.x + rect.width / 2 - 3) + "px," +
      (rect.y + rect.height / 2 - 2) + "px,0)";
    tutorialPointerState = {
      target: String(target || "narration"),
      label: resolved.label,
      rect: Object.assign({}, rect),
      visible: true
    };
    document.getElementById("kg_tutorial_target_description").textContent =
      "Target: " + resolved.label;
  }

  function refreshTutorialPointerPosition() {
    if (!tutorialPointerState.visible || !tutorialPointerState.target) { return; }
    var resolved = resolveTutorialPointerTarget(tutorialPointerState.target);
    if (resolved) { positionTutorialPointer(resolved, tutorialPointerState.target); }
  }

  async function moveTutorialPointer(target) {
    var resolved = resolveTutorialPointerTarget(target);
    if (!resolved) { throw new Error("Tutorial target is not available: " + target); }
    clearTutorialBlockSpotlight();
    if (String(target).indexOf("details:block:") === 0) {
      var spotlightBlockId = String(target).slice("details:block:".length);
      var spotlightBlock = document.querySelector(
        '#info_panel [data-content-block-id="' +
        cssAttributeValueEscape(spotlightBlockId) + '"]'
      );
      if (spotlightBlock) {
        spotlightBlock.classList.add("kg-tutorial-block-spotlight");
      }
    }
    var pointer = document.getElementById("kg_tutorial_pointer");
    if (pointer) { pointer.classList.remove("kg-settled"); }
    var duration = tutorialMotionDuration();
    if (pointer && !tutorialPointerState.visible && duration) {
      var narration = document.getElementById("kg_tutorial_narration");
      var start = narration ? narration.getBoundingClientRect() : null;
      if (start && start.width && start.height) {
        pointer.hidden = false;
        pointer.style.transform = "translate3d(" +
          (start.left + start.width / 2 - 3) + "px," +
          (start.top + 8) + "px,0)";
        void pointer.offsetWidth;
      }
    }
    positionTutorialPointer(resolved, target);
    if (duration) {
      await new Promise(function(resolve) { setTimeout(resolve, duration); });
    }
  }

  async function pulseTutorialPointer() {
    var pointer = document.getElementById("kg_tutorial_pointer");
    if (!pointer || pointer.hidden || tutorialMotionDuration() === 0) { return; }
    pointer.classList.remove("kg-clicking");
    void pointer.offsetWidth;
    pointer.classList.add("kg-clicking");
    await new Promise(function(resolve) { setTimeout(resolve, 240); });
    pointer.classList.remove("kg-clicking");
  }

  function hideTutorialPointer(options) {
    options = options || {};
    var previousState = tutorialPointerState;
    var pointer = document.getElementById("kg_tutorial_pointer");
    var halo = document.getElementById("kg_tutorial_halo");
    if (pointer) {
      pointer.hidden = true;
      pointer.classList.remove("kg-clicking");
    }
    if (halo) { halo.hidden = true; }
    clearTutorialBlockSpotlight();
    tutorialPointerState = options.preserveTarget
      ? {
          target: previousState.target,
          label: previousState.label,
          rect: previousState.rect,
          visible: false
        }
      : {target: null, label: "", rect: null, visible: false};
    document.getElementById("kg_tutorial_target_description").textContent = "";
  }

  function clearTutorialEmphasis(options) {
    hideTutorialPointer(options);
    hideNodeTooltip();
    restoreHoveredEdge();
  }

  function tutorialActionIsHover(action) {
    var command = String(action && action.command || "");
    return command === "show-graph-concept-hover" ||
      command === "show-graph-edge-hover";
  }

  function tutorialPointerIsTransientAction(target) {
    target = String(target || "");
    return target.indexOf("control:") === 0 ||
      target === "details:derived-from-show-graph" ||
      target === "details:where-used-show-graph";
  }

  function settleTutorialPointer(target) {
    if (tutorialPointerIsTransientAction(target)) {
      hideTutorialPointer({preserveTarget: true});
    } else {
      refreshTutorialPointerPosition();
      document.getElementById("kg_tutorial_pointer").classList.add("kg-settled");
    }
  }

  function clearTutorialBlockSpotlight() {
    document.querySelectorAll(".kg-tutorial-block-spotlight").forEach(function(block) {
      block.classList.remove("kg-tutorial-block-spotlight");
    });
  }

  function setGuidedTutorialActive(active) {
    document.body.classList.toggle("kg-tutorial-active", Boolean(active));
    [
      "kg_app_header",
      "kg_graph_context_panel",
      "kg_controls",
      "kg_search_section",
      "info_panel",
      "kg_pane_splitter"
    ].forEach(function(id) {
      var element = document.getElementById(id);
      if (!element) { return; }
      element.inert = Boolean(active);
      if (active) { element.setAttribute("aria-disabled", "true"); }
      else { element.removeAttribute("aria-disabled"); }
    });
  }

  function blockInteractionDuringGuidedTutorial(event) {
    if (!tutorialPlayback.activeRoute || tutorialPlayback.exploring) { return; }
    var target = event.target && event.target.closest
      ? event.target.closest(".kg-tutorial-narration")
      : null;
    if (target) { return; }
    if (event.type === "keydown" && (event.metaKey || event.ctrlKey || event.altKey)) {
      return;
    }
    event.preventDefault();
    event.stopImmediatePropagation();
  }

  function tutorialPointerSnapshot() {
    return {
      target: tutorialPointerState.target,
      label: tutorialPointerState.label,
      visible: tutorialPointerState.visible,
      x: tutorialPointerState.rect
        ? tutorialPointerState.rect.x + tutorialPointerState.rect.width / 2
        : null,
      y: tutorialPointerState.rect
        ? tutorialPointerState.rect.y + tutorialPointerState.rect.height / 2
        : null,
      halo: tutorialPointerState.rect ? Object.assign({}, tutorialPointerState.rect) : null
    };
  }

  function tutorialRouteById(tutorialId) {
    return (tutorialData || []).find(function(route) {
      return String(route.tutorial_id) === String(tutorialId);
    }) || null;
  }

  function tutorialCommandsThrough(route, stepIndex) {
    var commands = [];
    (route.steps || []).slice(0, stepIndex + 1).forEach(function(step) {
      (step.prepare || []).forEach(function(command) { commands.push(command); });
      tutorialStepActions(step).forEach(function(item) { commands.push(item.action); });
    });
    return commands;
  }

  function tutorialStepActions(step) {
    return step.actions || [{action: step.action, pointer: step.pointer, pause_ms: 0}];
  }

  function tutorialFinalAction(step) {
    var actions = tutorialStepActions(step);
    return actions[actions.length - 1];
  }

  function renderTutorialList() {
    var list = document.getElementById("kg_tutorial_list");
    if (!list) { return; }
    if (!tutorialData || !tutorialData.length) {
      list.innerHTML = '<span class="kg-muted-label">No tutorials in this build.</span>';
      return;
    }
    var categories = [
      {id: "interface", title: "Using PhysicsKG"},
      {id: "physics", title: "Physics routes"}
    ];
    list.innerHTML = categories.map(function(category) {
      var routes = tutorialData.filter(function(route) {
        return route.category === category.id;
      });
      if (!routes.length) { return ""; }
      return '<div class="kg-tutorial-list-group">' + escapeHtml(category.title) + '</div>' +
        routes.map(function(route) {
          return '<button type="button" class="kg-tutorial-select" data-tutorial-id="' +
            escapeHtml(route.tutorial_id) + '" aria-current="false">' +
            '<span class="kg-tutorial-list-title">' + escapeHtml(route.title) + '</span>' +
            '<span class="kg-tutorial-list-summary">' + escapeHtml(route.summary) + '</span>' +
            '</button>';
        }).join("");
    }).join("");
  }

  function selectTutorialIntroduction(tutorialId) {
    var route = tutorialRouteById(tutorialId);
    if (!route) { return; }
    tutorialPlayback.selectedId = String(route.tutorial_id);
    document.querySelectorAll(".kg-tutorial-select").forEach(function(button) {
      button.setAttribute(
        "aria-current",
        String(button.getAttribute("data-tutorial-id")) === tutorialPlayback.selectedId
          ? "true"
          : "false"
      );
    });
    document.getElementById("kg_tutorial_intro_title").textContent = route.title;
    var launchUrl = new URL(window.location.href);
    launchUrl.hash = "";
    launchUrl.searchParams.set("tutorial", route.tutorial_id);
    document.getElementById("kg_tutorial_launch_link").href = launchUrl.href;
    document.getElementById("kg_tutorial_intro_summary").textContent = route.summary;
    document.getElementById("kg_tutorial_intro_length").textContent =
      String((route.steps || []).length) +
      ((route.steps || []).length === 1 ? " step" : " steps");
    document.getElementById("kg_tutorial_intro").hidden = false;
  }

  function setTutorialTransitioning(value) {
    tutorialPlayback.transitioning = Boolean(value);
    renderTutorialNarration();
  }

  function renderTutorialNarration(errorMessage) {
    var card = document.getElementById("kg_tutorial_narration");
    if (!card) { return; }
    var route = tutorialPlayback.activeRoute;
    var active = Boolean(route && tutorialPlayback.stepIndex >= 0);
    card.hidden = !active;
    if (!active) { return; }
    var steps = route.steps || [];
    var step = steps[tutorialPlayback.stepIndex];
    document.getElementById("kg_tutorial_first_step_guidance").hidden =
      tutorialPlayback.stepIndex !== 0 || tutorialPlayback.exploring;
    document.getElementById("kg_tutorial_title").textContent = route.title;
    document.getElementById("kg_tutorial_progress").textContent =
      String(tutorialPlayback.stepIndex + 1) + " / " + String(steps.length);
    document.getElementById("kg_tutorial_step_title").textContent = step.title;
    var commentary = document.getElementById("kg_tutorial_commentary");
    replaceTypesetContent(commentary, renderConceptText(step.commentary || ""));
    var error = document.getElementById("kg_tutorial_error");
    error.hidden = !errorMessage;
    error.textContent = errorMessage || "";
    document.getElementById("kg_tutorial_back").disabled =
      tutorialPlayback.transitioning || tutorialPlayback.exploring ||
      tutorialPlayback.stepIndex <= 0;
    document.getElementById("kg_tutorial_next").disabled =
      tutorialPlayback.transitioning || tutorialPlayback.exploring ||
      tutorialPlayback.stepIndex >= steps.length - 1;
    document.getElementById("kg_tutorial_exit").disabled = tutorialPlayback.transitioning;
    var exploreButton = document.getElementById("kg_tutorial_explore");
    exploreButton.disabled = tutorialPlayback.transitioning;
    exploreButton.textContent = tutorialPlayback.exploring
      ? "Continue with tutorial"
      : "Explore from here";
    document.getElementById("kg_tutorial_explore_status").hidden =
      !tutorialPlayback.exploring;
    positionTutorialNarration();
    if (window.MathJax && MathJax.typesetPromise) {
      MathJax.typesetPromise([commentary]).catch(function(err) {
        console.warn("Tutorial MathJax typesetting failed:", err);
      }).then(function() {
        positionTutorialNarration();
      });
    }
  }

  function positionTutorialNarration() {
    var card = document.getElementById("kg_tutorial_narration");
    if (!card) { return; }
    var exploring = !card.hidden && tutorialPlayback.exploring;
    card.classList.toggle("kg-exploring", exploring);
    var docked = !card.hidden && !exploring && window.matchMedia("(max-width: 850px)").matches;
    document.body.classList.toggle("kg-tutorial-phone-docked", docked);
    if (!docked) {
      document.documentElement.style.removeProperty("--kg-tutorial-dock-height");
    }
    if (card.hidden) { return; }
    card.style.right = "auto";
    if (exploring) {
      var exploreViewport = visualViewportRect();
      card.style.top = "auto";
      card.style.bottom = (Math.max(0, window.innerHeight - exploreViewport.bottom) + 7) + "px";
      card.style.left = "auto";
      card.style.right = "7px";
      return;
    }
    if (docked) {
      var viewport = visualViewportRect();
      var bottomInset = Math.max(0, window.innerHeight - viewport.bottom) + 7;
      card.style.top = "auto";
      card.style.bottom = bottomInset + "px";
      card.style.left = (viewport.left + viewport.width / 2) + "px";
      document.documentElement.style.setProperty(
        "--kg-tutorial-dock-height", (card.offsetHeight + bottomInset + 7) + "px"
      );
      return;
    }
    var anchor = document.getElementById("kg_graph_pane");
    var rect = anchor ? anchor.getBoundingClientRect() : null;
    if (!rect || !rect.width || !rect.height) {
      anchor = document.getElementById("kg_workspace");
      rect = anchor ? anchor.getBoundingClientRect() : null;
    }
    if (!rect || !rect.width || !rect.height) { return; }
    var inset = window.matchMedia("(max-width: 850px)").matches ? 7 : 12;
    card.style.bottom = "auto";
    card.style.left = (rect.left + rect.width / 2) + "px";
    card.style.top = Math.max(
      rect.top + inset,
      rect.bottom - card.offsetHeight - inset
    ) + "px";
    var tooltip = document.getElementById("kg_node_tooltip");
    if (
      tooltip && tooltip.style.display !== "none" &&
      intersectRects(card.getBoundingClientRect(), tooltip.getBoundingClientRect())
    ) {
      card.style.top = (rect.top + inset) + "px";
    }
  }

  async function runTutorialStep(stepIndex, replay) {
    if (
      tutorialPlayback.transitioning || tutorialPlayback.exploring ||
      !tutorialPlayback.activeRoute
    ) { return; }
    var route = tutorialPlayback.activeRoute;
    if (stepIndex < 0 || stepIndex >= route.steps.length) { return; }
    setTutorialTransitioning(true);
    clearTutorialEmphasis();
    try {
      if (replay) {
        await replayTutorialCommands(
          tutorialPlayback.baseline,
          tutorialCommandsThrough(route, stepIndex)
        );
        setControlsVisible(false);
        tutorialPlayback.stepIndex = stepIndex;
        var replayStep = route.steps[stepIndex];
        var replayAction = tutorialFinalAction(replayStep);
        await moveTutorialPointer(
          replayAction.pointer ? replayAction.pointer.target : "narration"
        );
        settleTutorialPointer(replayAction.pointer ? replayAction.pointer.target : "narration");
      } else {
        var step = route.steps[stepIndex];
        tutorialPlayback.stepIndex = stepIndex;
        renderTutorialNarration();
        var prepare = step.prepare || [];
        for (var index = 0; index < prepare.length; index += 1) {
          await executeViewerCommand(prepare[index], {origin: "tutorial"});
        }
        var actions = tutorialStepActions(step);
        for (var actionIndex = 0; actionIndex < actions.length; actionIndex += 1) {
          var item = actions[actionIndex];
          clearTutorialEmphasis();
          var stepPointerTarget = item.pointer ? item.pointer.target : "narration";
          await moveTutorialPointer(stepPointerTarget);
          await pulseTutorialPointer();
          await executeViewerCommand(item.action, {origin: "tutorial"});
          await nextAnimationFrames(2);
          settleTutorialPointer(stepPointerTarget);
          if (actionIndex < actions.length - 1 && item.pause_ms) {
            await new Promise(function(resolve) { setTimeout(resolve, item.pause_ms); });
          }
        }
      }
      renderTutorialNarration();
    } catch (error) {
      renderTutorialNarration("Tutorial stopped: " + String(error.message || error));
    } finally {
      setTutorialTransitioning(false);
    }
  }

  async function startSelectedTutorial() {
    if (tutorialPlayback.transitioning || tutorialPlayback.activeRoute) { return; }
    var route = tutorialRouteById(tutorialPlayback.selectedId);
    if (!route || !route.steps || !route.steps.length) { return; }
    tutorialPlayback.baseline = captureTutorialPresentation();
    tutorialPlayback.activeRoute = route;
    tutorialPlayback.exploreSnapshot = null;
    tutorialPlayback.exploring = false;
    tutorialPlayback.stepIndex = -1;
    setControlsVisible(false);
    setGuidedTutorialActive(true);
    await runTutorialStep(0, false);
  }

  function defaultGuidedTutorial() {
    return tutorialRouteById("using-physicskg") ||
      (tutorialData || []).find(function(route) { return route.category === "interface"; }) ||
      (tutorialData || [])[0] || null;
  }

  async function startTutorialById(tutorialId) {
    if (tutorialPlayback.activeRoute || tutorialPlayback.transitioning) { return false; }
    var route = tutorialRouteById(tutorialId);
    if (!route) { return false; }
    selectTutorialIntroduction(route.tutorial_id);
    var dialog = document.getElementById("kg_splash_dialog");
    if (dialog && dialog.open) { dismissSplash(); }
    await startSelectedTutorial();
    return Boolean(tutorialPlayback.activeRoute);
  }

  function requestedTutorialId() {
    try {
      return new URL(window.location.href).searchParams.get("tutorial");
    } catch (error) {
      return null;
    }
  }

  async function exitTutorial() {
    if (tutorialPlayback.transitioning || !tutorialPlayback.activeRoute) { return; }
    setTutorialTransitioning(true);
    var baseline = tutorialPlayback.baseline;
    try {
      clearTutorialEmphasis();
      await restoreTutorialPresentation(baseline);
      tutorialPlayback.activeRoute = null;
      tutorialPlayback.baseline = null;
      tutorialPlayback.exploreSnapshot = null;
      tutorialPlayback.exploring = false;
      tutorialPlayback.stepIndex = -1;
      document.getElementById("kg_tutorial_narration").hidden = true;
      positionTutorialNarration();
    } finally {
      setGuidedTutorialActive(false);
      tutorialPlayback.transitioning = false;
    }
  }

  async function toggleTutorialExploration() {
    if (tutorialPlayback.transitioning || !tutorialPlayback.activeRoute) { return; }
    if (!tutorialPlayback.exploring) {
      tutorialPlayback.exploreSnapshot = captureTutorialPresentation();
      tutorialPlayback.exploring = true;
      clearTutorialEmphasis();
      setGuidedTutorialActive(false);
      renderTutorialNarration();
      return;
    }
    setTutorialTransitioning(true);
    try {
      tutorialPlayback.exploring = false;
      setGuidedTutorialActive(true);
      renderTutorialNarration();
      await nextAnimationFrames(2);
      await restoreTutorialPresentation(tutorialPlayback.exploreSnapshot);
      var step = tutorialPlayback.activeRoute.steps[tutorialPlayback.stepIndex];
      var finalAction = tutorialFinalAction(step);
      await moveTutorialPointer(finalAction.pointer ? finalAction.pointer.target : "narration");
      if (tutorialActionIsHover(finalAction.action)) {
        await executeViewerCommand(finalAction.action, {origin: "tutorial"});
      }
      settleTutorialPointer(finalAction.pointer ? finalAction.pointer.target : "narration");
      renderTutorialNarration();
      tutorialPlayback.exploreSnapshot = null;
    } catch (error) {
      tutorialPlayback.exploring = true;
      setGuidedTutorialActive(false);
      renderTutorialNarration(
        "Could not resume the tutorial: " + String(error.message || error)
      );
    } finally {
      setTutorialTransitioning(false);
    }
  }

  function tutorialPlaybackSnapshot() {
    return {
      active: Boolean(tutorialPlayback.activeRoute),
      tutorialId: tutorialPlayback.activeRoute
        ? tutorialPlayback.activeRoute.tutorial_id
        : null,
      selectedId: tutorialPlayback.selectedId,
      stepIndex: tutorialPlayback.stepIndex,
      exploring: tutorialPlayback.exploring,
      transitioning: tutorialPlayback.transitioning
    };
  }

  function initialiseTutorialPlayback() {
    renderTutorialList();
    var defaultRoute = defaultGuidedTutorial();
    var splashStart = document.getElementById("kg_splash_start_tutorial");
    splashStart.hidden = !defaultRoute;
    document.getElementById("kg_tutorial_list").addEventListener("click", function(event) {
      var button = event.target.closest(".kg-tutorial-select");
      if (button) { selectTutorialIntroduction(button.getAttribute("data-tutorial-id")); }
    });
    document.getElementById("kg_tutorial_start").addEventListener("click", startSelectedTutorial);
    document.getElementById("kg_tutorial_back").addEventListener("click", function() {
      runTutorialStep(tutorialPlayback.stepIndex - 1, true);
    });
    document.getElementById("kg_tutorial_next").addEventListener("click", function() {
      runTutorialStep(tutorialPlayback.stepIndex + 1, false);
    });
    document.getElementById("kg_tutorial_explore").addEventListener(
      "click", toggleTutorialExploration
    );
    document.getElementById("kg_tutorial_exit").addEventListener("click", exitTutorial);
    splashStart.addEventListener("click", function() {
      if (defaultRoute) { startTutorialById(defaultRoute.tutorial_id); }
    });
  }

  [
    "click", "dblclick", "pointerdown", "pointerup", "touchstart",
    "touchmove", "wheel", "keydown", "input", "change", "submit"
  ].forEach(function(eventName) {
    document.addEventListener(
      eventName,
      blockInteractionDuringGuidedTutorial,
      {capture: true, passive: false}
    );
  });

  return {
    refreshTutorialPointerPosition: refreshTutorialPointerPosition,
    tutorialPointerSnapshot: tutorialPointerSnapshot,
    tutorialRouteById: tutorialRouteById,
    positionTutorialNarration: positionTutorialNarration,
    startTutorialById: startTutorialById,
    requestedTutorialId: requestedTutorialId,
    tutorialPlaybackSnapshot: tutorialPlaybackSnapshot,
    initialiseTutorialPlayback: initialiseTutorialPlayback,
    isGuiding: isGuiding
  };
}
