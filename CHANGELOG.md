# Changelog

## 1.5.2 — 2026-07-14

- Removed Qwen, external assessment-provider configuration, API-key settings, model-generation code, learner-facing AI options, cooldown logic, and provider tests.
- Renamed the assessment service to `assessment_engine.py`.
- Kept only reviewed-bank random assessments.
- Added duplicate-ID and duplicate-normalized-question validation before test generation.
- Confirmed sampling without replacement so a question cannot repeat inside one test.
- Kept three reviewed emergency questions per level as an internal fallback, not a learner-selectable generator.
- Updated documentation, security guidance, launch checks, and secrets templates to remove all model-provider setup.

## 1.5.1 — 2026-07-14

- Fixed two environment-dependent feedback UI tests that failed when a real Google Sheets webhook was configured.
- Added `OPSREADY_FEEDBACK_FORCE_LOCAL=true` for deterministic local feedback testing.
- Added `pythonpath = ["."]` to pytest configuration so `python -m pytest -q` works without an editable package installation.
- Hid the experimental AI assessment option unless a complete server-side provider configuration is present.
- Reframed the AI generator as an optional source of extra question variation, not a required learner feature.
- Added an in-app explanation of how AI-generated tests are created, validated, and replaced by reviewed backups on failure.
- Kept the reviewed 45-question random bank as the only visible assessment mode in the default free-beta configuration.

## 1.5.0 — 2026-07-14

- Strengthened selectbox and multiselect styling across closed controls, combobox layers, portal menus, listboxes, hover states, and selected options.
- Replaced static fifteen-question assessment pages with an explicit test-generation workflow.
- Added deterministic random tests generated from the validated 45-question bank.
- Added an optional server-side Qwen-compatible assessment generator with strict JSON/schema validation.
- Added three reviewed fallback questions for each level when the assessment agent is unavailable or invalid.
- Added a 20-second per-session cooldown for AI generation.
- Stored active test identifiers and seeds in URL query parameters and cached generated tests server-side.
- Ensured normal Streamlit reruns do not regenerate or replace the active test.
- Added tests for random-test stability, fallback coverage, provider parsing, cache round trips, and assessment UI behaviour.

## 1.4.0 — 2026-07-14

- Added an animated Overview hero that demonstrates the command-to-diagnosis workflow without external video assets.
- Added direct Overview calls to action for Command Lab, Health Dashboard, and Incident Lab.
- Added pause, replay, and reduced-motion behaviour for the Overview animation.
- Added reusable animated infrastructure flows with workstation, switch, router, Linux server, evidence, and diagnosis nodes.
- Added simulation-flow animations to Command Lab, Health Dashboard, and Incident Lab results.
- Replaced the pre-rendered workspace panels with stateful high-contrast workspace tabs so Overview buttons can open the requested section directly.
- Strengthened select-box and multiselect contrast, including opened dropdown menus, hover states, and selected options.
- Added UI regression tests for the Overview hero, calls to action, workspace navigation, and animated health flow.

## 1.3.0 — 2026-07-14

- Expanded the command catalogue to 150 commands with 50 commands at each level.
- Expanded the incident catalogue to 50 operational scenarios.
- Expanded assessments to 45 questions with 15 questions at each level.
- Rebuilt Health Dashboard as an explicit scenario simulator with dynamic command evidence and changing diagnosis.
- Added scenario presets for healthy baseline, CPU saturation, memory pressure, disk capacity, storage bottleneck, connection surge, and mixed degradation.
- Added a clear purpose and four-step workflow to Incident Lab.
- Added synthetic incident event logs and category filtering.
- Moved feedback confirmation directly below the submit button.

## 1.2.1 — 2026-07-14

- Clear feedback form fields only after a successfully accepted submission.
- Preserve entered values when validation fails so learners can correct the form without retyping it.
- Replace the persistent “previous feedback” banner with a one-time submission result notice.
- State explicitly that the form is ready for another response after submission.
- Add an automated UI regression test for successful feedback-form reset.
- Include the hardened Google Sheets webhook script with health-check, write locking, and spreadsheet-formula protection.

## 1.2.0 — 2026-07-14

- Added a dedicated in-app Feedback page for the free public preview.
- Added structured learner, usability, content, bug, feature, accessibility, and recommendation fields.
- Added consent controls, optional contact permission, submission references, and warnings against confidential data.
- Added JSONL local fallback storage and optional persistent JSON-webhook delivery.
- Added a free Google Sheets and Apps Script collection workflow.
- Added feedback validation, delivery tests, secret templates, and deployment documentation.
- Added feedback calls to action in the learning overview and assessment results.
- Corrected package metadata so the Python package version matches the application release.

## 1.1.0 — 2026-07-14

- Added learner-focused guidance for all 29 commands: when to use, how to read output, and suggested next step.
- Expanded the Health Dashboard with measurement definitions, simulated-system explanation, dynamic findings, and recommended diagnostic commands.
- Increased application, widget, terminal, metric, and navigation text sizes.
- Combined Overview, Command Lab, Health Dashboard, Learning Paths, and Incident Lab into one tabbed Learning Workspace.
- Reworked each assessment level into one complete eight-question test with a single submission and detailed answer review.
- Added validation tests for command learning guidance and assessment question counts.

## 1.0.0 — 2026-07-13

- Initial standalone release.
- Added 29 command simulations, 10 incidents, 24 assessment questions, learning paths, session scoring, tests, and deployment files.
