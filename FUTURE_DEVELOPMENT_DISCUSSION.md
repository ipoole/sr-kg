# Future Development Discussion

Verbatim-style transcript captured on 2026-07-16.

## User

````text
I'd like us to think about directions for future development.  I have some ideas but I'd like to hear yours first, including some that might be ambitious or radical.  Remember the overall purpose is a learning aid; although currently focussed on SR I will soon wish to apply it to other areas of theoretical physics, and perhaps beyond.  Give me your ideas.
````

## Assistant

````text
Yes. Thinking from the current shape of the project, I’d treat it less as “an SR graph viewer” and more as the beginning of a personal theoretical-physics learning environment.

The strongest future direction, in my view, is to make the graph serve three roles at once:

1. a map of concepts,
2. a curriculum engine,
3. a memory/testing system.

Right now it is mostly role 1, with early signs of 2 and 3.

Near-Term High-Value Directions

1. Generalise from SR to subjects
   
   Introduce the idea of a course, domain, or module: SR, classical mechanics, EM, QM, statistical mechanics, GR, QFT, maths methods, etc.

   Each would have its own nodes/edges/content, but share the same viewer. The important design question is whether concepts are globally identified, e.g. sr.lorentz_transform, em.maxwell_equations, qm.hamiltonian, or whether each subject remains isolated.

   I would lean toward global IDs eventually, because many of the most valuable links are cross-domain.

2. Add learning states to concepts
   
   Each concept could have a personal status:

   - unseen
   - seen
   - shaky
   - understood
   - review due
   - mastered

   This would turn the graph from a reference tool into a study tool. The graph could visually show what you know, what depends on unknown material, and what is ready to learn next.

3. Prerequisite-aware study planning
   
   Given a target concept, the system could generate a study path:

   > To understand stress-energy tensor, first review four-vectors, tensors, Lorentz transformations, conservation laws, four-momentum...

   This is a natural fit for your existing directed DAG work. The graph already knows prerequisite and derivation structure; it just doesn’t yet act like a tutor.

4. Better distinction between relation types
   
   Current relation types are a good start: PREREQUISITE, DERIVES_FROM, RELATED.

   I’d consider adding richer physics-learning relations:

   - EXAMPLE_OF
   - SPECIAL_CASE_OF
   - GENERALISES
   - ANALOGOUS_TO
   - CONTRASTS_WITH
   - LIMIT_OF
   - REPRESENTATION_OF
   - SOLVES
   - ASSUMES
   - FAILS_WHEN
   - MISCONCEPTION_ABOUT

   The radical value here is that physics understanding often comes from knowing how two concepts relate, not merely knowing both concepts.

Medium-Term Directions

5. Problem and exercise graph
   
   Add problems as first-class objects, not just study questions inside nodes.

   Problems could link to:

   - required concepts
   - tested concepts
   - common mistakes
   - solution strategies
   - difficulty
   - source
   - whether you solved it unaided

   Then you can ask: “Show me problems that test Lorentz covariance but avoid tensors” or “Give me one review problem for each weak prerequisite of Maxwell’s equations.”

6. Derivation graph
   
   A concept graph says “A derives from B”. A derivation graph would show the actual chain of mathematical steps.

   For example:

   - postulates
   - interval invariance
   - linear transformation assumption
   - Lorentz factor
   - Lorentz transformations
   - velocity addition
   - time dilation / length contraction

   This could become one of the most valuable features for theoretical physics, because derivations are often where understanding breaks down.

7. Misconception graph
   
   This is more radical, and I think very promising.

   Instead of only mapping correct concepts, explicitly map common wrong ideas:

   - “relativistic mass is always the best way to think”
   - “time dilation is just an optical illusion”
   - “four-vectors are just vectors with four components”
   - “gauge choice changes the physics”
   - “operators in QM are just variables”

   Each misconception can point to the concepts that repair it. This would make the tool much more tutor-like.

8. Multiple representations per concept
   
   Physics concepts often need several representations:

   - verbal
   - geometric
   - algebraic
   - operational/experimental
   - limiting-case intuition
   - worked example
   - analogy
   - warning/misconception

   Your current definition, derivation, explanation structure could evolve into more typed sections. That would help when moving beyond SR.

Ambitious / Radical Directions

9. A personal “physics atlas” rather than separate courses
   
   Instead of separate graphs for SR, QM, EM, etc., build a unified atlas where domains are filters/layers.

   Example cross-links:

   - Lorentz invariance connects SR, EM, GR, QFT.
   - Hamiltonian connects classical mechanics, QM, statistical mechanics.
   - Symmetry connects conservation laws, Noether’s theorem, gauge theory.
   - Fourier transform connects waves, QM, fields, statistical mechanics.
   - Manifolds connect GR, analytical mechanics, gauge theory.

   This could become genuinely powerful: a map of theoretical physics by conceptual dependency rather than textbook chapter order.

10. Socratic mode
   
   The system could ask questions based on graph structure:

   > You say you understand four-momentum. Can you explain why its norm is invariant?  
   > Which prerequisite does that rely on?  
   > What breaks if the metric signature changes?

   This need not require full AI integration at first. Even structured prompts derived from edges and study questions would be useful.

11. Auto-generated review paths
   
   A spaced-repetition layer could choose concepts and questions based on:

   - time since last review
   - self-rated confidence
   - failed questions
   - prerequisite importance
   - graph centrality
   - upcoming target topics

   This is where the “learning aid” purpose becomes strongest. It stops being a browser and starts deciding what you should study next.

12. Concept compression / expansion
   
   Different zoom levels could show different granularity.

   At high level:

   - Lorentz geometry
   - relativistic dynamics
   - fields
   - covariance

   Zoom in:

   - interval
   - metric
   - four-vector
   - four-velocity
   - four-momentum
   - stress-energy tensor

   This would help with large domains. A flat graph will eventually become too crowded.

13. Mathematical object registry
   
   This is a more technical/radical idea: track mathematical objects separately from concepts.

   For example:

   - \(x^\mu\)
   - \(u^\mu\)
   - \(p^\mu\)
   - \(F^{\mu\nu}\)
   - \(T^{\mu\nu}\)
   - \(\eta_{\mu\nu}\)

   Each object could know its type, domain, definition, transformation law, units, index structure, and where it appears. That would make the tool unusually useful for physics.

14. “Explain this equation” mode
   
   Eventually, you could click an equation and have each symbol linked to its concept/object.

   For example, in  
   \[
   p^\mu = m u^\mu
   \]
   clicking p, m, or u reveals the relevant node. This would be especially valuable in tensor-heavy subjects.

15. Source-backed knowledge
   
   For serious long-term use, each concept could have citations:

   - textbook source
   - chapter/page
   - lecture note
   - your own note
   - confidence/status
   - alternative convention

   This matters because advanced physics has convention conflicts: metric signatures, Fourier transform signs, units, notation, gauge choices, index placement.

The Big Architectural Direction

I would gradually separate the project into three layers:

1. Knowledge model
   
   Concepts, relations, questions, problems, equations, symbols, sources, user learning state.

2. Pedagogical engine
   
   Validation, prerequisite traversal, study-path generation, review scheduling, diagnostics, recommendations.

3. Viewer/UI
   
   Graph, detail panel, search, notes, filters, mobile/desktop layout.

At the moment, the static HTML generator is a sensible implementation. I would not rush to turn it into a web app. But the data model should evolve as if one day there may be multiple viewers: graph view, study queue, derivation view, symbol index, problem browser, print/export view.

My strongest recommendation: the next big conceptual step should be not prettier graph rendering, but turning the graph into a learner model. Once the system knows what you are trying to learn, what depends on what, and what you personally find weak, it becomes much more than a map.
````

## User

````text
Thanks, I'll comment on each suggestion by number.
1.  Certainly, this is my intention.  And yes the question of how to deal with overlapping concepts needs careful thought.
2. Hmm, not so much.
3. Ditto
4. Interesting, but the complexity would be too much to throw on the user to select which edges to enable.  Good if these richer relations enable other automated features - more powerful explanations
5. Perhaps, so effectively a database of questions which can be searched by concept, difficulty, type...   Certainly I want more questions.
6. Definitely.  We already have the "DERIVES_FROM" link, but I'm not sure how carefully it has been curated.  My original conception of this project was to be able to trace concepts back to fundamental postulates / axioms.   I'd like tighter linking of the derivation path.  Some way that the derivation of a concept can be laid out textually and mathematically with consistent notation.
7. Probably not as part of the graph, but I do want to include such misconceptions in the content, within explanations or optional-details.
8. Yes perhaps - that would be a good way of drawing out content.  Of course the geometric view would require graphics.
9. Yes, this closely relates to item 1.
10. Interesting.
11. Not so much.
12. Interesting, I think this relates to the notion of sub-graphs which I've been thinking of.  At a 30,000' view of theoretical physics, "Special relativity" is one bubble, yet at lower levels you want to see the details within the bubble.  
13. Yes why not.
14. Yes nice, but it sounds difficult to pre-bake that content, or perhaps you are thinking of an integrated LLM? (See I2 below).
15. Definitely.  I have been working through Susskind's TTM series; page or section references would be very helpful.

Here are some further ideas which I was thinking about:
I1. Interactive graphics.  Eg see coordinates skew as boost velocity is adjusted; see a vector field as charges are moved around; show how a vector potential field relates to the E and B fields....

I2. Integrate LLM access within the browser.  User would have to select and authenticate to the chosen LLM - cloud based or possibly local.  This might power some of the features you describe above (but I'd prefer static curation wherever possible).  Thinking the LLM could be integrated into the Notes system; enable AI chat, the LLM being given the text of the current (and linked?) concepts as context.  Request and response are recorded in the note.  Subsequently, a distillation of the conversation can be added to the static content.

I3. UI redesign.  The current UI has evolved with little forethought.  Two distinct views on the knowledge base have emerged: 1) the graph 2) the details panel.  That symmetry should be better reflected in the UI structure and layout.

I4. A historical / scientist dimension.   The history of science interests me, and seeing the historical emergence of concepts can be instructive.  So perhaps add "Scientist" as a graph node, with links showing influences.   Concepts would hold discovery date ranges.  A historical timeline presentation would then be possible.  Needs thought.

I5. I'd like to try (yet again) automatic ("physics based") layout, particularly for selected subsets (like Neighbours, Descendants).  I feel it should be possible to have the layout be direction aware - maybe add differential "gravity" depending on concept level.

I6. ... and I do want to work on my manual review of the current content, using the Notes feature, the export of which would then form a worklist of issues for us (mostly you) to work on.

There's a lot there - interested in your comments on all of the above.
````

## Assistant

````text
I think your comments point to a clearer direction: the project should become a multi-view knowledge base, not simply a larger graph. The same curated content should support graph view, derivation view, textual study view, symbol/equation view, historical view, and perhaps AI-assisted notes.

The important design principle is: do not force every dimension into one visible graph at once. Use one underlying data model, then project it into different views.

Comments On Your Responses

For 1 and 9, overlapping concepts are probably the central architectural issue. I would avoid duplicating “Lorentz transformation” separately inside SR, EM, GR, and QFT unless the local treatment is genuinely different. A good model might have a stable canonical concept plus subject-specific appearances:

concept = Lorentz transformation  
appears_in = SR, EM, GR, QFT  
local_role = foundational, covariance condition, tangent-space transformation, representation theory...

That lets you keep one identity while allowing different explanations by context.

For 2, 3, and 11, I agree they should not dominate if your preferred mode is curated study rather than app-managed learning. We can still keep light metadata such as “reviewed”, “needs work”, or “source issue”, but not build a whole gamified learner model.

For 4, yes: richer relations should not mean more UI clutter. The user should not have to manually juggle 14 edge types. I’d treat relation richness as semantic metadata for generated views and explanations. For example, the UI could expose simple filters like “dependencies”, “derivations”, “analogies”, “history”, while internally using more precise relations.

For 5, a searchable question database seems worthwhile, especially if linked to concepts and derivation steps. I would keep questions outside the main concept CSV eventually. A question can test multiple concepts, have difficulty, type, source, expected answer style, and maybe “common trap”. That is too much structure to sit comfortably inside node rows forever.

For 6, I think this is the most important direction. “Trace this back to postulates/axioms” is a strong identity for the project. I would distinguish:

- DERIVES_FROM as a graph-level relation
- a derivation object as a curated sequence of mathematical/textual steps
- a notation environment that fixes symbols, assumptions, units, signature, and conventions

That third part matters. A derivation is only really useful if notation is consistent and assumptions are explicit.

For 7 and 8, misconceptions and multiple representations probably belong inside structured concept content rather than as ordinary graph nodes. A concept page could have typed sections: verbal, geometric, algebraic, operational, limiting case, misconception, source note. The graph should not become noisy just because the content becomes richer.

For 12, yes, this is exactly subgraphs / bubbles / scale. I’d think in terms of compound concepts or modules. At the 30,000-foot level, “Special Relativity” is a node. Open it, and it becomes a graph. Same for “Lorentz geometry”, “Relativistic dynamics”, “Classical electromagnetism”, etc. This would solve the eventual scale problem better than trying to render everything at once.

For 13 and 14, a mathematical object registry is likely the practical route to clickable equations. I would not rely primarily on an LLM for that. You could pre-bake much of it by writing equations in a slightly annotated form, for example identifying symbols like p^\mu, u^\mu, F_{\mu\nu} with object IDs. It is work, but the payoff is high. An LLM could assist annotation, but curated symbol identity should be static.

For 15, source references are a definite yes. I would support references at multiple levels: concept-level, section-level, derivation-step-level, equation-level. For Susskind TTM, section or lecture references may be more stable and useful than only page numbers, depending on edition/format.

Your New Ideas

I1, interactive graphics, is one of the strongest ideas. This could make the project much more than a text graph. The key is to make graphics concept-specific and pedagogically constrained, not generic animations. Examples:

- Lorentz boost slider showing skewed axes and invariant light cone
- proper time along different worldlines
- field lines changing as charges move
- vector potential and curl relationship
- wave equation mode shapes
- phase/group velocity
- gauge transformation showing changed potential but unchanged fields

These should probably live as small reusable interactive components attached to concepts, not as arbitrary embedded scripts in CSV.

I2, LLM integration, is useful but should be treated as an assistant to curation, not the authority. I like your notes-based workflow: chat with concept context, save the exchange as a note, later distil into static content. That creates a sane human-in-the-loop path.

The hard parts are API keys, privacy, model choice, local-vs-cloud support, and prompt/context management. I would design it so the static viewer still works fully without an LLM. The LLM should be an optional layer over the current concept, neighbour concepts, selected derivation path, and user notes.

I3, UI redesign, is overdue conceptually. You now have two primary views: graph and details. I’d make that explicit. Perhaps the app shell has:

- graph workspace
- concept/document workspace
- shared navigation/search
- inspector/notes/source panel

The current left/right panel evolution was natural, but as the system grows it will need clearer information architecture. Especially if derivations, questions, timelines, and symbols arrive.

I4, historical/scientist dimension, is interesting but should probably be a separate projection rather than mixed into the main prerequisite graph. Scientists, papers, dates, institutions, and influences form a different kind of network. Concepts can have discovery/emergence date ranges and source events. Then you can generate a timeline view or historical influence graph without polluting the learning dependency graph.

I5, automatic layout is worth revisiting specifically for subsets. I remain sceptical about fully automatic layout for the whole graph, but optimistic for constrained local views. Direction-aware layout with vertical forces by pedagogical level, edge-length preferences by relation type, and collision constraints might work well for neighbours/descendants. A hybrid approach sounds best: manual/global layout, physics-assisted local layout.

I6, using Notes export as a worklist is very practical. This could become an editorial workflow:

- user reviews content in browser
- notes are exported
- notes become issue/worklist rows
- we classify them: typo, unclear explanation, missing derivation, bad edge, source needed, graphic needed
- static content is updated
- notes are retired or linked to changes

That is probably the best near-term path for improving content quality without overbuilding infrastructure first.

My Suggested Priority Order

1. Tighten the derivation model and notation consistency.
2. Add source/reference support.
3. Redesign content structure beyond definition/derivation/explanation.
4. Formalise subgraphs/modules for multi-domain expansion.
5. Use Notes export as an editorial worklist.
6. Prototype one or two interactive graphics.
7. Revisit local automatic layout.
8. Only then consider browser LLM integration.

The big strategic move is this: keep the graph as the navigational skeleton, but let richer views carry richer meaning. Derivations, equations, sources, timelines, questions, and interactive graphics should not all be squeezed into graph edges. They should be first-class views over the same curated knowledge base.
````

## User

````text
Much of these ideas revolve around the notion of a rich, complex, growing ... database of physics knowledge with many different views onto that knowledge base.  Currently, our knowledge base is held in two pretty simple CSV files - nodes and edges (and a library of SVG renderings).   Are we going to have to move to a formal relational database with SQL queries?  This scares me a little.
````

## Assistant

````text
No, not soon. And maybe not ever in the way you’re imagining.

A relational database with SQL is one possible storage layer, but it is not the same thing as having a rich knowledge model. You can grow the model quite a long way while still using plain files.

I would think of this in stages.

Stage 1: Structured Files

Keep the current approach, but split the CSVs as the model grows:

- concepts.csv
- relations.csv
- relation_types.csv
- questions.csv
- sources.csv
- concept_sources.csv
- derivations.csv
- derivation_steps.csv
- symbols.csv
- concept_symbols.csv
- graphics.csv
- modules.csv

This is still simple, inspectable, editable, version-controllable, and easy for us to validate with Python. It also fits your current workflow.

The danger is not “too many CSV files”. The danger is weak validation. But this project already has validation, so the natural next step is to make validation stronger as the schema grows.

Stage 2: A Build-Time Data Model

Even if the source remains CSV, Python can load it into richer internal objects:

CSV files -> validated Python knowledge model -> generated HTML/views

That gives you a proper model without requiring you to directly use SQL.

This is probably the sweet spot for the foreseeable future.

Stage 3: YAML/Markdown For Rich Content

CSV is poor for long mathematical prose. I would eventually move the heavy content out of CSV.

A concept could become something like:

content/concepts/lorentz_transform.md

with structured front matter:

id: sr.lorentz_transform
label: Lorentz transformation
module: special_relativity
layer: 3
sources:
  - ttm_sr:lecture_2

then Markdown/LaTeX content sections below.

Edges and compact metadata could remain in CSV. Rich prose belongs in Markdown much more naturally.

Stage 4: SQLite As An Internal Cache, Not Authoring Tool

If queries become slow or complex, we could generate a SQLite database during the build:

CSV/Markdown source files -> validation -> generated SQLite cache -> generated viewer

But you would not have to author SQL manually. SQLite would just be an implementation detail used by the generator.

That is very different from “you now need to maintain a database”.

What I Would Avoid For Now

I would avoid jumping straight to:

- PostgreSQL
- a server backend
- migrations
- ORM models
- admin UI
- writing SQL by hand
- making the browser depend on live database access

That would add a lot of operational weight before the knowledge model has stabilised.

My Recommendation

Stay file-based.

But evolve from:

nodes.csv + edges.csv

toward:

structured metadata tables + Markdown concept files + validation + generated static viewer

That gives you most of the benefits of a knowledge database without the psychological or technical burden of running one.

The key principle is: the source of truth should remain human-readable and version-controlled. A formal database can come later as a generated artifact if we need it.
````

## User

````text
Ok that's reassuring.
````

## Assistant

````text
Good. I think file-based source is the right instinct for this project.

The next sensible evolution is probably not “database”, but “better authored files plus stricter validation”: keep the source readable, let Python assemble the richer knowledge model, and generate whatever views we need from that.
````
