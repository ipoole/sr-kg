# Exact-build website deployment

Status: **stage 5 is live**, merged onto main on 4 November 2026. Pages publishes
verified local packages through GitHub Actions. Stage 6 (untracking generated
HTML and removing duplicate root deployment files) remains.
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

Until stage 6 root files remain deployment copies; tests require them to match
`website/`. Edit website sources, then refresh those copies until stage-6 cleanup.

## Rollback

Before cutover, nothing has changed on the live site. At cutover, the existing
main branch remains a usable branch-publishing fallback until stage 6. Subsequently,
redeploy a previous package using its recorded checksum, explicitly allowing the
older base. This restores both release and preview together. Do not delete release
attachments used for deployments or rollback. No force pushes are needed.

## Local packaging commands

After committing source changes and testing the generated viewer:

```bash
conda run -n sr-kg python tools/package_site.py package --bootstrap
# Later updates use --previous .deployment/current-site.tar.gz instead.
conda run -n sr-kg python tools/package_site.py verify .deployment/site.tar.gz --sha256 <printed-sha256>
```

Use `--channel preview --previous <current-package>` for a preview. The command
refuses a preview without a complete previous release. Every file has a manifest
hash, unsafe tar members are rejected, and local HTML links must resolve within
the assembled site. External CDN/Google URLs remain unchanged. Packages are
reproducible for identical bytes and metadata. Build archives live in ignored
`.deployment/`; do not commit them. Uncommitted tracked source changes prevent
packaging, while the generated viewer may differ from Git.

## Upload, validate, publish and rollback

All commands run from the repository root, with `gh auth status` working. After
the workflow is on main:

```bash
# Obtain the successful live base before preparing a release or preview update.
conda run -n sr-kg python tools/publish_site.py current
conda run -n sr-kg python tools/package_site.py package --previous .deployment/current-site.tar.gz
# For previews, add --channel preview; build/test that viewer first.
conda run -n sr-kg python tools/publish_site.py upload .deployment/site.tar.gz
conda run -n sr-kg python tools/publish_site.py request --tag <tag> --sha256 <sha256>
# Only this explicit flag requests a live deployment:
conda run -n sr-kg python tools/publish_site.py request --tag <tag> --sha256 <sha256> --deploy
# Restore a known earlier complete website:
conda run -n sr-kg python tools/publish_site.py request --tag <older-tag> --sha256 <older-sha256> --deploy --rollback
```

Uploads are non-latest prereleases containing `site.tar.gz` and `site.sha256`.
They are public like the repository: packages must contain only website files,
never personal data or credentials. Deployment tags target the recorded source
commit; product release tags remain separate. The workflow uses a read-only token
for validation; only its guarded main-branch deployment job has Pages/OIDC write
permissions. The built-in `GITHUB_TOKEN` suffices; no new account secret is needed.
An upload is not a publication. Check the Actions run and the live deployment
manifest after publishing, rather than assuming an accepted request succeeded.

The pre-merge rehearsal used a temporary branch-push trigger. That trigger and
candidate record were removed before cutover. The live workflow exposes only
manual dispatch, with deployment requiring an explicit request on main.
The workflow uses only standard-library Python for validation and never installs
generator dependencies. Pages transport artifacts expire after one day; durable
packages remain Release attachments for update bases and rollback.

## Preparation results

[Stage-4 rehearsal](artefact_deployment_rehearsal.md) records the uploaded candidate,
checksums, successful read-only Actions run, browser checks and unchanged live
configuration. Cache-busted live-manifest checks reject stale bases. A deployment
also waits for its expected manifest to become visible before releasing the
workflow lock; failure requires inspection before a retry. The Pages transport,
deployment and propagation check subsequently passed at stage 5;
see [cutover results](artefact_deployment_cutover.md). Live rollback has not been
needed or exercised. Keep deployment packages for that purpose.
