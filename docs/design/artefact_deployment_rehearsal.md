# Deployment rehearsal — 4 November 2026

Stages 1–4 complete on `untracked-artefact-deployment`. **No live switchover.**

## Candidate

- Source commit: `760e7ee35cd6e2f425a11b9f165c441aecae1f5e`.
- Deployment tag: `site-20261104T200252432443Z-760e7ee3`.
- [Uploaded package](https://github.com/ipoole/sr-kg/releases/tag/site-20261104T200252432443Z-760e7ee3).
- Archive SHA-256: `4f14cd1c48f6e3a92c3e5c2bf18adeefab8d3b2f5857de87781206e58e7543dc`.
- Archive contains 19 website files plus its manifest; local copy is ignored at
  `.deployment/site.tar.gz`. Viewer bytes match the regenerated v4.5.0 product.
- Upload/download round trip produced a byte-for-byte identical archive.

## Verification

- 721 unit tests passed. The normal unit command intentionally skips browser cases.
- All 350 browser cases passed in three isolated Chromium processes: 238.76 s.
- Exact extracted website served over local HTTP at desktop 1280×800 and phone
  390×844: homepage, release and preview viewer, real CDN dependencies, search,
  Lorentz-transformations selection, Details and no horizontal overflow; no JS errors.
- Actual-byte release → preview → release packaging round trip preserved the
  unaffected channel at each step.
- Unit checks cover stale-base rejection, explicit rollback, checksum corruption,
  unsafe/duplicate archive members, missing dependencies, deterministic output,
  upload-only behaviour, explicit deployment gating and Pages propagation checks.
- [GitHub validation run](https://github.com/ipoole/sr-kg/actions/runs/41902916184)
  succeeded: downloaded candidate, verified source tag and archive/file checksums,
  checked local resources and safely extracted it. Both the Pages transport upload
  and the deployment job were **skipped**.
- Read-only live-base check succeeded: the current legacy website has no deployment
  manifest, as expected before the initial bootstrap.

The installed GitHub CLI is 2.4.0. Rehearsal caught its lack of the newer `--latest`
flag; upload uses `--prerelease`, compatible with this version and excluded from
GitHub's Latest release designation. No dependency installation was needed.

## Unchanged live configuration

Confirmed after rehearsal through GitHub's API:

- Pages build type: `legacy`.
- Source: `main`, `/`.
- Custom domain: `physicskg.org`.
- HTTPS enforced: true.
- Main has not been merged into or pushed by this work.
- Generated viewer and root deployment copies remain tracked and unchanged.

## Remaining boundary

Stages 5–6 require a separate instruction. First merge the prepared source, remove
the temporary branch-push rehearsal trigger/record, and switch Pages source to
GitHub Actions. Explicitly deploy a freshly verified bootstrap package, check the
public site and Google connection, then remove tracked build/duplicate files and
verify subsequent release/preview updates. Actual Pages deployment, its transport
artifact and live rollback have deliberately **not** been exercised yet; these
cannot be tested end to end without crossing the agreed switchover boundary.

Historical extraction and Git history rewriting remain separate tasks.
