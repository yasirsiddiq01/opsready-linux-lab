# Changelog

## 1.7.1 — 2026-07-23

- fixed Ruff import-order and `collections.abc.Mapping` findings in the commercial settings service;
- added a stable key and high-contrast resting style for the sidebar Reset session progress button;
- added a three-phase Pro delivery roadmap to the Plans page;
- added a commercial Pro roadmap document;
- kept checkout and paid fulfilment disabled by default;
- added regression coverage for the reset-button style and Pro roadmap.


## 1.7.0 — 2026-07-23

- Added a Plans page that separates the current free Community edition from the planned Pro edition.
- Added a fail-closed checkout configuration: sales remain unavailable unless sales, fulfilment, checkout, support, terms, privacy, and refund requirements all pass validation.
- Added optional waitlist and customer-portal links.
- Added commercial configuration support through Streamlit secrets or environment variables without embedding platform credentials.
- Added a Lemon Squeezy preparation pack with product listing copy, store-activation answers, pricing worksheet, Community/Pro feature boundary, seller checklist, and required owner decisions.
- Added draft Terms of Use, Privacy Policy, Refund and Cancellation Policy, and commercial disclosure templates with visible placeholders.
- Added a command-line commercial-readiness checker and automated validation for URLs, emails, and launch gates.
- Kept all payment functionality disabled by default; no checkout, webhook, licence validation, or paid access is activated in this release.

## 1.6.4 — 2026-07-18

- Added a large orange command token that visibly travels through every numbered execution stage.
- Added directional route arrows and an animated progress path behind the command token.
- Slowed stage highlighting so the learner can follow the Linux touchpoints in sequence.
- Added **Replay simulation** in Practice terminal and Guided command explorer.
- Replay restarts only the animation; it does not rerun the command, consume a terminal attempt, change output, or add progress.
- Added regression tests for visible motion markup and replay-only behaviour.

## 1.6.3 — 2026-07-18

- Corrected `basename` and `dirname` as path-string transformations rather than filesystem metadata reads.
- Clarified that these commands do not remove, open, or verify files or directories.
- Added plain-language Input, Action, Result, and System effect cards to every execution trace.
- Added explicit shell-pipeline traces using process stages and kernel pipe buffers.
- Added a separate file-type trace showing target-byte inspection and the local magic database.
- Added semantic regression tests for path-string commands, pipelines, state-changing examples, and all 150 effect summaries.

## 1.6.2 — 2026-07-18

- Added reviewed command-specific outputs for the Guided command explorer.
- Removed generic repeated text outputs.
- Replaced Load example with automatic insertion from the example selector.
- Replaced horizontally clipped trace strips with numbered compact diamond/zig-zag maps.

## 1.6.1 — 2026-07-18

- Simplified Command Lab into two clearly separated modes: Practice terminal and Guided command explorer.
- Moved the learning-mode choice before catalogue selection so terminal users no longer need to select a guided command first.
- Replaced the generic workstation-switch-router-server command animation with command-specific Linux execution traces.
- Added traces for shell built-ins, VFS/file reads, procfs, memory, storage, processes, systemd/D-Bus, journals, networking, DNS, firewall, containers, identities, permissions, kernel, security, and scheduling.
- Added exact touchpoint labels such as `/etc/passwd`, `/proc/meminfo`, `/run/systemd/private`, `/var/log/journal`, `/var/run/docker.sock`, and network targets.
- Added a compact result layout placing the execution trace and terminal output side by side on larger screens.
- Collapsed detailed flags, safety guidance, and next steps in Guided mode to reduce repeated scrolling.
- Removed editable arbitrary text from Guided mode; it now runs the reviewed example for the selected catalogue command.
- Added `/etc/os-release` to the virtual filesystem so the loaded `cat /etc/os-release` example succeeds.
- Added command-trace and UI regression tests.

## 1.6.0 — 2026-07-18

- Replaced the static Command Lab result area with an optional safe Interactive Linux Practice Terminal.
- Added 25 reviewed commands operating only on an in-memory virtual filesystem.
- Added stateful current-directory handling, relative paths, command history, explanations, and suggested next commands.
- Added a 10-supported-attempt limit per virtual terminal reset.
- Added scenario-dependent `df`, `free`, `ps`, and `uptime` output linked to the Health Dashboard.
- Blocked shell chaining, pipelines, redirection, substitution, parent traversal, network clients, process control, service control, and destructive commands.
- Retained Guided simulation for all 150 catalogue commands.
- Changed the initial sidebar state to automatic for mobile and tablet layouts.
- Added public viewer-toolbar and reduced browser-error-detail configuration.
- Added terminal security, state, health-linkage, limit, and Streamlit UI tests.

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
