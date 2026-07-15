# Testing

Run all checks with:

```bash
make check
```

The test suite validates:

- minimum content counts
- required command fields
- unique incident and question identifiers
- answer membership in options
- positive score values
- score idempotency
- zero-denominator accuracy behaviour
- deterministic random assessment generation
- no duplicate questions inside a generated test
- duplicate ID and duplicate normalized-text rejection
- three-question reviewed emergency coverage for every level
- generated-test cache round trips
- absence of learner-facing model or AI-generator controls

Manual smoke test:

1. Start the app.
2. Open every navigation page.
3. Run one command from each level.
4. Complete one incident correctly and one incorrectly.
5. Open Assessment and confirm no test is generated before the button is pressed.
6. Generate a reviewed random test and confirm normal widget reruns keep the same test ID.
7. Generate another test and confirm the ID and question set change.
8. Confirm the page contains no Qwen, model-provider, or AI-generator options.
9. Answer assessment questions and verify that repeated submissions do not increase the score.
10. Reset progress and verify that all session counters return to zero.

## Interface checks

Before public deployment, verify the Overview animation at 100% zoom, dropdown contrast in closed and opened states, reduced-motion fallback, assessment generation controls, test persistence during reruns, and feedback delivery.
