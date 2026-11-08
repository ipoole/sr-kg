# Exact-build website deployment

Pages deploys locally built and tested packages through GitHub Actions. Generated
viewers are ignored/untracked; pushing source alone does not publish. Website
sources live in `website/`, and the small tracked legacy URL page remains at
`output/interactive_graph.html`. Public URLs, HTTPS and OAuth origins are unchanged.
The migration leaves the product at v4.5.0. History extraction/rewriting is separate.

## Build and publish

Use the project environment and commit/push source before packaging. Build and
test the viewer locally; GitHub never runs the generator. Retrieve the currently
successful complete-site package before preparing either channel:

```bash
conda run -n sr-kg python tools/generate_pyvis.py --data-root data --out output/PhysicsKG.html
# Run the appropriate unit/browser checks against the completed source/build.
conda run -n sr-kg python tools/publish_site.py current
conda run -n sr-kg python tools/package_site.py package --previous .deployment/current-site.tar.gz
conda run -n sr-kg python tools/publish_site.py upload .deployment/site.tar.gz
# Substitute the tag/checksum printed above; this first request only validates.
conda run -n sr-kg python tools/publish_site.py request --tag <tag> --sha256 <sha256>
# Explicit publication:
conda run -n sr-kg python tools/publish_site.py request --tag <tag> --sha256 <sha256> --deploy
```

Check the Actions result and live `deployment.json` after publication. Upload or
an accepted workflow request alone does not establish success. A fresh `current`
command retrieves the deployed archive for the next update. Do not infer the live
package from the newest uploaded Release; an upload need not have been deployed.
`--bootstrap` is only for initial setup with no live package, not routine updates.

## Hosted preview

Increment the product patch version, add a dated Preview history entry, then
build/test the desired viewer. See [Preview versions](releases.md#preview-versions).
Retrieve the current package, then substitute:

```bash
conda run -n sr-kg python tools/package_site.py package --channel preview --previous .deployment/current-site.tar.gz
```

Upload and explicitly deploy using the same commands. The preview is
`https://physicskg.org/preview/PhysicsKG.html`. Use `--viewer <path>` to package a
different locally built HTML file. No changes to the generated HTML are made.

The illustrated guide is also previewed at `https://physicskg.org/preview/user-guide.html`,
with its own styles, branding assets and screenshots. Its Home, atlas and policy links
lead to the public site; the guide itself and its images remain under `/preview/`.
Preview packaging copies these source files unchanged and does not update public pages.
Validation remains compatible with older packages that predate the guide.

A preview update replaces only `preview/`; a release update replaces the public
website while retaining `preview/`. Both require the last successful complete
package, including after a rollback. Previews share browser personal data and
Google authorization with the public viewer; use an isolated browser profile or
export personal data before experimental tests. This is not a security boundary.
Do not commit generated viewers or publish new builds to phone-preview/GitHack.

## Package and workflow contract

Packages live in ignored `.deployment/` locally and in public GitHub Release
attachments, outside Git history. Only website files belong in them, never
personal data or credentials. Each `site-*` prerelease targets the source commit
and includes `site.tar.gz`, `site.sha256`, and release notes recording channel,
base and checksum. Product `vX.Y.Z` tags remain separate. Standard Ubuntu runners
and this public repository work on GitHub Free; no new account secret is required.

The gzip tar contains the complete site plus `deployment.json`: schema, deployment
tag, source commit, channel, previous deployment tag and SHA-256 of every other
file. The workflow checks the archive SHA-256, source tag, individual file hashes,
safe archive paths and local HTML dependencies before extracting. Packaging is
reproducible for identical bytes/metadata. Uncommitted tracked source is rejected.

Deployments are serialized and require explicit manual dispatch on main. Validation
uses read-only repository permissions; only the deployment job has Pages/OIDC write
permissions. A stale live base is rejected: fetch current and repackage, rather than
bypassing the check. Cache-busted manifest checks wait for Pages propagation before
the workflow lock is released. If propagation fails, inspect the actual live state
before retrying. Pages transport artifacts expire after one day; Release attachments
remain for updates and rollback.

Root website files come from `website/`. Both viewer directories get local library
assets so relative `lib/bindings/utils.js` works. Existing CDN resources (vis-network,
Bootstrap, MathJax) and Google Identity Services on demand are unchanged. The deployed
`CNAME` stays `physicskg.org`; domain/HTTPS settings remain in GitHub Pages.

## Local inspection and rollback

To inspect the assembled website rather than the standalone generated viewer:

```bash
conda run -n sr-kg python tools/package_site.py verify .deployment/site.tar.gz --sha256 <sha256> --extract .deployment/inspect
conda run -n sr-kg python -m http.server 8765 --directory .deployment/inspect --bind 127.0.0.1
```

Use a new/empty extraction destination. The tiny legacy URL page and website sources
remain tracked; generated viewer files stay available locally after untracking.

Rollback redeploys an earlier complete package and restores both channels together:

```bash
conda run -n sr-kg python tools/publish_site.py request --tag <older-tag> --sha256 <older-sha256> --deploy --rollback
```

Do not delete attachment archives used for rollback. Current main no longer contains
branch-publishing deployment copies; do not switch Pages back to legacy publishing
on current main. No force pushes are needed for normal publication or rollback.

## Verification records

[Rehearsal](artefact_deployment_rehearsal.md), [switchover](artefact_deployment_cutover.md)
and [completion](artefact_deployment_completion.md) record the checks and deployment
identities. Those dated records describe their historical stages; this document is
the current operating procedure. Historical viewer extraction and Git history
rewriting have not been performed.
