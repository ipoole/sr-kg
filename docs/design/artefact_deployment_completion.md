# Deployment migration completion — 4 November 2026

## Source cleanup

Generated viewers in `output/*.html` are ignored and no longer tracked. The local
`output/PhysicsKG.html` and older GR-only build were retained. The small hand-authored
`output/interactive_graph.html` remains tracked. Root website deployment duplicates
were removed; `website/` is the sole source for those pages and branding assets.
Packaging preserves their deployed root paths. Library sources remain in `lib/`.

AGENTS.md, README, release instructions and architecture now describe exact-build
publishing and same-origin hosted previews. The temporary root-copy test and
tracked-viewer exception were removed; favicon tests inspect website source assets.
No product-version bump or Version history change is required for this migration.

Unit checks pass after cleanup: 720 tests. Full browser and live release/preview
verification are in progress; their deployment identities/results will be recorded
below before stage 6 is marked complete.

Historical viewer extraction and Git history rewriting remain separate work.
No existing Git objects, branches or tags have been rewritten.
