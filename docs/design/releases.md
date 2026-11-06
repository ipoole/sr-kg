# Release versioning

PhysicsKG uses a three-part product version `major.minor.patch`. This identifies
the published application and content release; it is independent of the layout,
personal-data and knowledge-base schema versions.

- **major** changes for a substantial product or content generation;
- **minor** changes for a visible feature addition;
- **patch** changes for fixes and small refinements.

The lower components begin at zero and reset when a higher component changes:
`4.0.0` may lead to `4.1.0`, then `4.1.1`, and eventually `5.0.0`. The single
source of the current value is `PRODUCT_VERSION` in `srkg/branding.py`. Generated
HTML exposes it in Quick Start, the Tools panel, document metadata and browser
runtime configuration.

Published releases should be tagged `vX.Y.Z` after their release commit reaches
`main`. Schema versions advance only when their own data contracts change; they
do not follow the product version.

**Tools → Version history** lists published versions, dates and short user-facing
summaries. Its source is `srkg/viewer_assets/release_history.json`, rendered into
the built viewer; add the new version when preparing a release. Keep the newest
entry first and use the publication date. Entries back to 4.0.0 were reconstructed
from publication commits on main, rather than intermediate branch commits.

The source release commit message must include a single `Release note:` line whose
text exactly matches the new Version history summary. Keep it brief and user-facing.
Prepare the history entry and product version before building and testing. Merge
source changes onto main and tag the source release commit `vX.Y.Z`. Package the
exact locally tested viewer and publish it through the explicit Actions workflow;
do not make a separate generated-HTML publication commit. Pushing main or a product
tag alone does not publish the website.

## Exact-build publishing

Pages now uses the [artefact deployment route](artefact_deployment.md). Package
releases use separate `site-*` tags and record source commits/checksums; they are
deployment records, not new product versions. Validation is the default; `--deploy`
explicitly publishes. Verify the workflow and live manifest after publication.

The generated viewer is ignored and untracked. Website sources live in
`website/`; the only tracked HTML in `output/` is the small legacy URL page.
Use the currently deployed complete package as the base for either release or
preview publication so the other channel survives. Hosted previews replace
GitHack/phone-preview publishing and share the public viewer's origin/personal data.
The deployment migration itself leaves the product at v4.5.0.

## Preview versions

Increment the product patch number before each new preview publication, starting
with preview 4.5.1. Use the next unused patch for the current major/minor line,
considering the public release and already published previews. Update
`PRODUCT_VERSION` and prepend a dated Version history entry whose summary starts
`Preview:` before building and testing. The displayed version then identifies the
actual review build, even while the public release retains its previous version.

Retrying the same immutable package or rolling back does not create a new version.
New preview content does. `site-*` package tags still identify exact deployments;
`vX.Y.Z` release tags are reserved for publication from main. Apply the normal
major/minor/patch policy when preparing the eventual public release. Consolidate
its branch preview entries into the public release's single dated history entry;
the immutable `site-*` packages retain the exact preview versions and sources.
The public release number can therefore be lower than its preceding previews
(for example, release 4.5.1 after preview 4.5.4). Those preview numbers remain
reserved: consult the deployment packages when choosing the next unused preview
patch, even after their entries have been consolidated.
