# Training content model

## Command records

Each command requires:

- level
- category
- operational area
- summary
- safe example
- simulated output
- safe-use guidance
- risk statement
- flags and meanings

## Incident records

Each incident requires:

- unique identifier
- level
- title and brief
- observable symptoms
- diagnostic question
- options and one preferred first action
- evidence
- root cause
- remediation sequence
- unsafe action warning
- score value

## Assessment question records

Each reviewed assessment question requires:

- unique identifier
- level
- topic
- question
- options
- correct answer
- explanation
- score value

## Editorial rule

The preferred answer should be the safest diagnostic action that reduces uncertainty before changing system state. Questions should avoid relying on obscure syntax or distribution-specific behaviour unless clearly labelled.

## Generated assessment test records

Each random test stores a test identifier, selected level, source, creation timestamp, seed, notice, and the complete fixed question list. A test is replaced only through an explicit learner action.

The engine validates duplicate IDs and duplicate normalized question text before sampling. It samples without replacement, preventing duplicate records inside one test.


## Practice terminal state

The interactive terminal uses session-only dictionaries containing the current virtual path, reviewed virtual files, directory names, attempts used, and command history. Command handlers return a structured result with status, output, explanation, next step, base command, and whether an attempt was consumed.

No terminal record contains or references a host path.
