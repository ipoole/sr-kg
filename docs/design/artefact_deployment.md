# Exact-build website deployment

Status: preparation on `untracked-artefact-deployment`; live Pages still publishes
from main's root. Issue 6.1 replaces that only at the explicit stage-5 cutover.
History rewriting and historical viewer extraction are separate work.

## Contract

The generator continues to produce `output/PhysicsKG.html` locally. Test that
build, then package its bytes unchanged. GitHub never runs the generator.
Website sources live in `website/`; their public paths remain at the site root.
The small legacy redirect remains at `output/interactive_graph.html`.

A package is a gzip tar archive containing the complete deployed site, including
any preview. It includes `deployment.json` with a unique deployment tag, source
commit, channel, and SHA-256 hashes of every other file. An external SHA-256 of
the archive is passed to the workflow. The archive is a GitHub Release attachment,
not a Git object or a long-lived Actions artifact. Release metadata records the
source commit and archive checksum. Only short-lived Pages transport artifacts
are needed. Standard Ubuntu runners and this public repository work on GitHub Free.

A release update replaces the website root and viewer while retaining `preview/`.
A preview update replaces only `preview/`, retaining the published release bytes.
Both start from the last successfully deployed complete package. First deployment
explicitly bootstraps from the current local release. Never guess the current
package from the newest uploaded release: an upload need not have been deployed.
The live `deployment.json` identifies the deployed package. Concurrent publication
is rejected when the live deployment has changed since the package was prepared;
workflow deployments are serialized. Rebase the package on the new live package
and retry. Rollback deliberately redeploys an older complete package.

The preview URL is `https://physicskg.org/preview/PhysicsKG.html`. It shares its
origin, browser personal data and Google authorization with the public viewer.
Use an isolated browser profile or export personal data before experimental tests.
A preview is not a separate security boundary.

## Preserved public paths and dependencies

Homepage, privacy, terms, CSS, icons, robots and sitemap retain their URLs, as do
`output/PhysicsKG.html`, its tutorial query strings and the legacy redirect.
`CNAME` remains `physicskg.org`; custom-domain and HTTPS settings remain in Pages.
OAuth JavaScript origins do not change. The viewer still uses existing CDN
resources (vis-network, Bootstrap and MathJax), Google Identity Services on demand,
and local `lib/bindings/utils.js` relative to its directory. Package local library
assets beneath both viewer directories, without rewriting viewer HTML.

## Stages and safety boundary

1. Record this contract and audit deployed resources.
2. Add website sources and deterministic packaging/verification tests. Retain
   tracked root copies and viewer so legacy Pages remains functional.
3. Add CLI upload and workflow: validation is the default; deployment requires an
   explicit request on main. Package download, checksums and safe extraction precede it.
4. Rebuild/test locally; upload a candidate; validate it in Actions on the feature
   branch without deploying. Keep an auditable rehearsal record.
5. **Switchover, separately authorized:** merge tooling, change Pages source to
   GitHub Actions, deploy candidate, verify public paths/HTTPS/Google connection.
   Until successful, retain branch-publishing files as the rollback route.
6. Remove generated HTML and duplicate deployment files from tracking, ignore
   build products, finish publication instructions and verify another release/preview.

During stages 1–4 root files remain deployment copies; tests require them to match
`website/`. Edit website sources, then refresh those copies until cutover.

## Rollback

Before cutover, nothing has changed on the live site. At cutover, the existing
main branch remains a usable branch-publishing fallback until stage 6. Subsequently,
redeploy a previous package using its recorded checksum, explicitly allowing the
older base. This restores both release and preview together. Do not delete release
attachments used for deployments or rollback. No force pushes are needed.
