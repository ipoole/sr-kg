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
