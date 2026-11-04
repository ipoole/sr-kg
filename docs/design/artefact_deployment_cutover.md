# Pages switchover — 4 November 2026

**Stage 5 complete.** Exact-build package deployment is now the live publishing
route. Main source pushes alone no longer publish. Product version remains
v4.5.0 because the website/application bytes have not changed.

## Deployment record

- Prepared tooling merged onto main: `0d5ab869ac7a25ecc7a0ef0681ddd02bfd6cd5e2`.
- Temporary rehearsal trigger and candidate record removed before merge; only
  manual workflow dispatch remains.
- Freshly regenerated local viewer and all 19 packaged files were byte-for-byte
  identical to the stage-4 tested site. The existing 350-case full browser pass
  therefore covers the same application bytes.
- Main-branch manual validation passed:
  [run 41908530322](https://github.com/ipoole/sr-kg/actions/runs/41908530322).
- Final legacy Pages deployment completed before switching the source.
- Pages `build_type` changed from `legacy` to `workflow`; custom domain
  `physicskg.org` and enforced HTTPS preserved. No Google Cloud settings changed.
- Package tag: `site-20261104T203800133794Z-0d5ab869`.
- [Package release](https://github.com/ipoole/sr-kg/releases/tag/site-20261104T203800133794Z-0d5ab869).
- SHA-256: `17da47d7b7d10c03deb25ddecb0496d507d7455b8a664f688d5d940953a707fa`.
- Live deployment succeeded, including Pages transport upload, base validation,
  configure/deploy actions and visible-manifest propagation check:
  [run 41908669001](https://github.com/ipoole/sr-kg/actions/runs/41908669001).

## Post-deployment checks

- Live `deployment.json` matches the expected package manifest.
- Every one of the 19 live website files matches the local package's SHA-256:
  homepage, privacy/terms, styles/icons, robots/sitemap, CNAME, viewer, legacy
  redirect and local library assets.
- HTTP redirects to HTTPS; the former github.io viewer URL reaches the custom domain.
- Actual public viewer works at desktop 1280×800 and phone 390×844: graph startup,
  search, Lorentz-transformations selection and Details, with no horizontal
  overflow or JavaScript errors.
- Connect Google Drive opens accounts.google.com using the existing OAuth client.
  No account credentials were entered and no real personal-data synchronization
  was performed during this isolated-browser check.
- `publish_site.py current` successfully downloads the deployed package as the
  base for future updates; its checksum matches the uploaded local archive.
- 721 unit tests pass after the workflow cleanup; its policy test also confirms
  that workflow dispatch is the sole trigger.

## Fallback and remaining work

Root deployment copies and `output/PhysicsKG.html` remain tracked and unchanged.
If needed before stage 6, restore Pages to `legacy`, source `main`, path `/`, and
request a branch build. Original settings are saved locally in ignored
`.deployment/pages-before-cutover.json`. No fallback was needed.

Stage 6 is not performed: remove the generated viewer and duplicate deployment
files from tracking, keep the tiny legacy redirect source, finish cleanup of
transitional guards/instructions, and verify subsequent release and hosted-preview
updates. The preview path is not deployed by this initial release-only bootstrap.
Live rollback has not been exercised; previous complete packages remain available.
Historical extraction and repository history rewriting are still separate work.
