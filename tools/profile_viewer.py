#!/usr/bin/env python3
"""Repeatable local Chromium timings; no network or real MathJax in this probe.

Run with the sr-kg environment. Results are comparative desktop measurements,
not device predictions or performance assertions. The public build is untouched.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
import statistics
import shutil
import sys
from tempfile import TemporaryDirectory
import time

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from playwright.sync_api import sync_playwright
from srkg.branding import PRODUCT_TITLE
from srkg.pipeline import generate_viewer_from_root


def profile(samples: int, cpu_rate: float) -> dict:
    with TemporaryDirectory(prefix="physicskg-profile-") as directory:
        output = Path(directory) / "viewer.html"
        bindings = output.parent / "lib/bindings"
        bindings.mkdir(parents=True)
        shutil.copy2(ROOT / "lib/bindings/utils.js", bindings / "utils.js")
        started = time.perf_counter()
        generate_viewer_from_root(data_root=str(ROOT / "data"), out_path=str(output),
                                  height="100vh", width="100%", title=PRODUCT_TITLE)
        build_ms = (time.perf_counter() - started) * 1000
        library = output.parent / "lib/vis-9.1.2"
        library.mkdir(parents=True)
        for name in ("vis-network.min.js", "vis-network.css"):
            shutil.copy2(ROOT / "lib/vis-9.1.2" / name, library / name)
        html = output.read_text(encoding="utf-8")
        html = re.sub(r'<script src="https://[^\"]*vis-network.min.js"[^>]*></script>',
                      '<script src="lib/vis-9.1.2/vis-network.min.js"></script>', html)
        html = re.sub(r'<link[^>]*href="https://[^\"]*vis-network.min.css"[^>]*>',
                      '<link rel="stylesheet" href="lib/vis-9.1.2/vis-network.css">', html)
        html = re.sub(r'<script defer src="https://[^\"]*mathjax[^\"]*"></script>',
                      '<script>Object.assign(window.MathJax,{typesetClear:function(){},'
                      'typesetPromise:function(){return Promise.resolve();}});</script>', html)
        output.write_text(html, encoding="utf-8")
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            context = browser.new_context(viewport={"width": 1280, "height": 800},
                                          reduced_motion="reduce")
            page = context.new_page()
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))

            page.route("https://**/*", lambda route: route.fulfill(body=""))
            session = context.new_cdp_session(page)
            session.send("Emulation.setCPUThrottlingRate", {"rate": cpu_rate})
            started = time.perf_counter()
            page.goto(output.as_uri(), wait_until="load")
            try:
                page.wait_for_function("() => typeof kgExecuteViewerCommand === 'function' && kgDisplayedGraphSnapshot()")
            except Exception as exc:
                raise RuntimeError("Viewer did not initialise: " + "; ".join(errors)) from exc
            if page.locator("#kg_splash_dialog[open]").count():
                page.locator("#kg_splash_dismiss").click()
            startup_ms = (time.perf_counter() - started) * 1000
            page.wait_for_timeout(300)
            measurements = page.evaluate("""async samples => {
              const result = {};
              const frame = () => new Promise(resolve => requestAnimationFrame(
                () => requestAnimationFrame(resolve)));
              async function command(value) {
                await kgExecuteViewerCommand(value, {origin:'tutorial'});
              }
              async function measure(name, action) {
                const values = [];
                for (let i=0; i<=samples; i++) {
                  const start = performance.now();
                  await action();
                  await frame();
                  if (i) values.push(performance.now()-start);
                }
                result[name] = values;
              }
              await measure('selection_pair', async () => {
                await command({command:'select',target:'concept:sr.mass_energy_equivalence'});
                await command({command:'select',target:'concept:sr.lorentz_transformations'});
              });
              await measure('fold_expand_pair', async () => {
                await command({command:'set-all-module-representations',value:'expanded'});
                await command({command:'set-all-module-representations',value:'folded'});
              });
              await command({command:'select',target:'concept:sr.mass_energy_equivalence'});
              await command({command:'set-context',preset:'foundations',depth:'transitive'});
              await command({command:'set-display-scope',value:'context'});
              await command({command:'expand-context-modules'});
              await measure('fit_fitpp', async () => {
                await command({command:'set-context',preset:'foundations',depth:'transitive'});
                await command({command:'fit',value:'context'});
                await command({command:'fit',value:'context'});
              });
              return result;
            }""", samples)
            if errors:
                raise RuntimeError("Browser errors: " + "; ".join(errors))
            version = browser.version
            browser.close()
    return {"chromium": version, "cpu_rate": cpu_rate, "samples": samples,
            "build_ms": round(build_ms, 1), "startup_ms": round(startup_ms, 1),
            "note": "Local vis assets, stub MathJax, reduced motion; operations include two animation frames.",
            "median_ms": {name: round(statistics.median(values), 1)
                          for name, values in measurements.items()}}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--samples", type=int, default=7)
    parser.add_argument("--cpu-rate", type=float, default=4)
    args = parser.parse_args()
    if args.samples < 1 or args.cpu_rate < 1:
        parser.error("samples and cpu-rate must be at least 1")
    print(json.dumps(profile(args.samples, args.cpu_rate), indent=2))
