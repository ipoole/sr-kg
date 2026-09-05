# Open Issues

## 1. Content and implementation

1. Include `CONSTRUCTED_FROM` alongside `DERIVES_FROM` throughout derivation-path
traversal, including ancestry and downstream trees. Preserve relation labels and
check navigation, focus and cycle handling. Current trees use only
`DERIVES_FROM`; this is accepted work, not an open policy question.
2. Add the GR gravitational-waves module and fully author its concepts with
graphics and icons. See the
[General Relativity plan](authoring/general_relativity_concept_plan.md).

## 2. Viewer requests

1. Consider persistent per-focus layouts and their export, separately from the
existing global-layout workflow. Focussed adjustments are currently temporary;
global layout export and publication already work. See [Layout](design/layout.md).
2. Add graphics to modules as icons in the graph and possibly in module details.
This will require space within the module box, perhaps with the icon above smaller
text.
3. Make Search easier to discover, perhaps by placing it in the masthead rather
than under Tools.
4. Consider recording whether an edge relation belongs in the Full-graph
background in the edge key. The viewer currently hardwires the structural set;
lens-selected foreground edges must continue to override that background filter.

## 3. Documents

1. Rename all documents under `/docs` and their references to use lowercase
filenames consistently.
