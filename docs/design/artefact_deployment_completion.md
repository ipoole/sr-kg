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

Unit, full browser and live release/preview checks passed; their results and
deployment identities are recorded below.

Historical viewer extraction and Git history rewriting remain separate work.
No existing Git objects, branches or tags have been rewritten.

## Live update verification

Stage 6 is complete. Both packages below were built from cleanup commit
`b355f8965b7ef18dbaa724fc095a58808eb430e7`, with no generated viewer in Git.

| Update | Deployment tag | SHA-256 | Actions result |
| --- | --- | --- | --- |
| Preview | `site-20261104T205057838224Z-b355f896` | `c2da48a0742d4e31eaf632e2a7bfd0cedc31199ba7f757d02a140e66ca602b20` | [Succeeded](https://github.com/ipoole/sr-kg/actions/runs/41910571688) |
| Subsequent release | `site-20261104T205340323015Z-b355f896` | `bc568a745454958660c7c51f6103d859d21227d7c6c733d4216ad5491e930ddf` | [Succeeded](https://github.com/ipoole/sr-kg/actions/runs/41911024796) |

- The preview update preserved all 19 existing release files exactly. All 25 live
  files matched the combined preview package after deployment.
- The subsequent release update preserved all six preview files exactly. All 25
  final live files matched the release package after deployment.
- Desktop 1280×800 and phone 390×844 checks passed on both release and preview:
  graph startup, search, selection, Details, no horizontal overflow or JS errors.
  Isolated browser contexts confirmed shared-origin local storage between paths.
- A clean `git archive` snapshot, containing neither generated viewer nor root
  deployment duplicates, rebuilt and packaged all release bytes identically to
  the previous live release. No old working-tree deployment files were needed.
- 720 unit tests passed; all 350 browser tests passed in 228.08 s across three
  isolated Chromium processes. The removed unit test guarded temporary root copies.
- `publish_site.py current` downloaded the final combined package successfully.
  A stale preview package was rejected against the actual newer live manifest.
- Pages remains `workflow`, custom domain `physicskg.org`, enforced HTTPS true.
- `git ls-files output` contains only `output/interactive_graph.html`. Both local
  generated HTML files remain present and ignored. `.deployment/` remains ignored.

The stable preview URL is https://physicskg.org/preview/PhysicsKG.html. It currently
contains the same v4.5.0 viewer as the public release. Subsequent preview/release
updates use the complete currently deployed package as their base. Website source
and deployment source commits are pushed to main; no built HTML is added back.

There was no need to roll back a live deployment. Live rollback remains available
through earlier package attachments; it restores both channels together and may
therefore remove a preview introduced after that earlier package. Historical Git
objects have not been removed: this stops future HTML growth, while history cleanup
remains a separate task requiring its own explicit authorization.
