# Offline Equation Rendering

Offline operation is currently low priority; no implementation is scheduled.

## Motivation

The viewer should support studying physics entirely off-grid—even in a tent.
Currently the generated HTML loads MathJax from a CDN at browser runtime.
Caching is not a reliable offline guarantee.

## Options

- **Bundle MathJax:** embedding the current TeX-to-SVG library adds roughly
  2.1 MB. The measured viewer was about 2.08 MB, so this would roughly double
  its size before any additional components needed for complete offline support.
  A neighbouring local library file avoids enlarging the HTML but requires
  distributing multiple files.
- **Pre-render equations:** generate SVG equations during the build and embed
  them in the HTML. The browser can display authored mathematics offline without
  a runtime maths renderer. Output size depends on equation count, duplication
  and possible glyph sharing; it needs measurement rather than assumption.

## Tentative conclusion

Pre-rendering is promising because authored KB content is known at build time.
It must cover labels, details, questions, previews, tooltips and search results,
including content revealed after navigation. It adds build-time rendering work;
new mathematics entered in personal notes would still need a runtime renderer.

Before choosing, compare a pre-rendered build with a bundled-library build for
size, readability and behaviour with networking disabled. Audit other external
assets too: offline equations alone do not prove the whole viewer works offline.
This is a direction to investigate, not an implementation commitment.

## Open decision

Must mathematics newly entered in personal notes render offline too? Pre-rendering
alone covers authored content, but not new user-entered equations. Decide this
requirement before choosing a rendering approach when offline work is prioritised.
