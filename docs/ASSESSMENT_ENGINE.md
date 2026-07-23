# Reviewed Assessment Engine

## Purpose

The assessment engine introduces controlled randomness without an external language model. Every learner-facing question comes from the reviewed question bank in `opsready_lab/catalog/exercises.py`.

## Test generation

A new test is created only after the learner presses **Generate test** or **Generate new test**.

The engine then:

1. filters the reviewed bank by selected level;
2. validates unique IDs and unique normalized question text;
3. samples questions without replacement;
4. shuffles the selected questions;
5. shuffles answer options independently;
6. stores the complete fixed test in Streamlit session state;
7. stores a test identifier, seed, level, and count in URL query parameters;
8. caches the fixed test locally when the deployment filesystem permits it.

## Rerun behaviour

Streamlit reruns the Python application after many widget interactions. The assessment engine does not generate a new test during those reruns. The existing test remains active until the learner explicitly requests another one.

If session state is lost after a browser reload, a reviewed test can be reconstructed from its saved seed.

## Duplicate prevention

`validate_question_bank()` rejects:

- duplicate question IDs;
- duplicate normalized question text;
- malformed options;
- answers that do not match an option;
- missing explanations.

`random.sample()` selects without replacement, preventing the same bank record from appearing twice in one generated test.

## Emergency backup

Three reviewed questions per level remain available as an internal emergency fallback. They are not a learner-selectable generator and are not connected to any model or external service.

## Current bank size

Version 1.6.1 contains 45 reviewed questions: 15 per level. Expanding the bank to 600 requires a separate editorial and technical-review workflow; it is not achieved by adding unreviewed generated questions.
