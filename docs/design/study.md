# Study Questions

This is the accepted interaction and data contract for the enhanced study
features. The authored schema, browser-local progress model, automatic and
self-assessed question cards, and Study scorecard are active.

## Purpose

Study questions should make retrieval practice inviting without turning the
atlas into a game or pretending that every useful answer can be machine graded.
They use two marking modes:

- `automatic` presents authored alternatives and marks the selected answer;
- `self_assessed` accepts free text, reveals the model answer, and asks the
  learner to mark their response correct or incorrect.

`question_type` describes the kind of exercise independently of its marking
mode. In particular, a `calculation` may be automatic or self-assessed.

## Attempt flow

An answer is not disclosed until the learner submits a response or explicitly
chooses **I don't know -- show answer**. This is a user-interface rule, not a
security boundary: the generated standalone page necessarily contains the
authored answers.

For an automatic question:

1. the learner selects one authored option or the viewer-supplied `?` option;
2. **Check answer** records the attempt;
3. the selected and correct options are identified, and the explanation is
   shown.

For a self-assessed question:

1. the learner enters a non-empty response, or chooses **I don't know**;
2. the model answer is shown alongside their response;
3. the learner records a correct or incorrect self-assessment.

There is no separate **Try again** action. After an incorrect attempt the
response controls remain available; a changed response followed by another
submission is a new attempt. Rechecking an unchanged response must not create
accidental duplicate attempts.

Once attempted, the answer remains available. The most recent outcome is one
of `correct`, `incorrect`, or `unknown`; attempt count is cumulative. The UI
uses a green tick for correct and a red cross, supplemented by text, for the
other outcomes. Feedback is deliberately restrained: it acknowledges success,
encourages review after a miss, and treats “I don't know” as a useful choice.

Question disclosure uses native `details` controls, response controls are
keyboard operable, and feedback is announced politely to assistive technology.
Colour is never the only result cue: ticks or crosses always appear with text.

## Progress and scorecard

Progress is local-first and keyed by stable `question_id`. Individual,
timestamped attempt events make cross-browser archive merging lossless; the
viewer derives the attempt count, latest outcome and latest-attempt time. It
does not store the learner's typed answer. The Study control-panel section
lists attempted questions, newest first, and summarises the number currently
correct out of the number attempted. Study events are included in the unified
[personal-data archive](personal_data.md).

Following a scorecard entry selects its concept, opens Practice details, and
brings the question into view. Progress can be reset per question or, with
confirmation, in full.

## Authored data

`study_questions.csv` owns the prompt, model answer or explanation, exercise
type, and marking mode. `study_question_options.csv` owns ordered alternatives
for automatic questions. An automatic question has at least two options and
exactly one correct option. A self-assessed question has no options. The viewer
adds the `?` option; it is never authored.

Multiple choice is preferred when plausible alternatives test the intended
knowledge without giving it away. Numerical and simple algebraic calculations
are particularly useful: selecting the correct formula and then evaluating it
is educational, while distractors can represent realistic sign, factor, unit,
inverse, or power errors. Explanation, comparison, and synthesis questions
should remain self-assessed when recognition would make them shallow.

Options initially retain authored order. Randomisation, automated free-text
grading, points, streaks, timers, badges, cloud synchronisation, and spaced
repetition are outside the first implementation.
