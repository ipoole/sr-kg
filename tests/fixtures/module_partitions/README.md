# Reviewed partition snapshots

These independent membership snapshots preserve the adopted SR and GR partitions
for regression checks. They are test inputs, not proposals or authoring sources.
Runtime membership remains in `data/module_members.csv`.

When deliberately changing module boundaries, review the expected partition and
its metric assertions together. Tests compare membership, not the historical
sequence values in the SR snapshot.
