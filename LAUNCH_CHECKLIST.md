# Free Public Launch Checklist

## Product

- [ ] Test every Learning Workspace tab.
- [ ] Generate and complete at least one reviewed random assessment at each level.
- [ ] Confirm a generated test does not change during ordinary widget reruns.
- [ ] Confirm Generate new test creates a different test.
- [ ] Confirm no question is duplicated inside one test.
- [ ] Confirm Reset session progress works.
- [ ] Confirm no entered Linux command is executed.
- [ ] Test desktop and mobile-width layouts.

## Feedback

- [ ] Configure `OPSREADY_FEEDBACK_WEBHOOK_URL` or Streamlit feedback secrets.
- [ ] Submit a test response.
- [ ] Confirm the response appears in the persistent destination.
- [ ] Confirm the app no longer shows the local-storage setup warning.
- [ ] Restrict access to the response sheet or database.
- [ ] Decide how often feedback will be reviewed.
- [ ] Define labels such as bug, content, usability, feature, and accessibility.

## Privacy and communication

- [ ] Add the project-owner contact email to the public project page.
- [ ] Publish a short feedback privacy notice covering purpose, optional email, retention, access, and deletion requests.
- [ ] Do not request credentials, private logs, tokens, IP addresses, or confidential system information.
- [ ] Decide how long optional email addresses will be retained.

## Repository and deployment

- [ ] Run `python -m pytest -q`.
- [ ] Run `python -m ruff check .`.
- [ ] Run `python -m compileall -q app.py opsready_lab`.
- [ ] Confirm `.streamlit/secrets.toml` is not committed.
- [ ] Confirm `runtime/` and `.runtime/` are not committed.
- [ ] Deploy from a clean repository checkout.
- [ ] Verify the Streamlit health endpoint.

## Launch message

- [ ] State clearly that this is a free public preview.
- [ ] Explain that it is a simulator, not a real server or certification substitute.
- [ ] Ask users to complete at least one learning path or assessment before giving feedback.
- [ ] Avoid promising paid features or release dates that are not committed.

## Visual checks

- [ ] Overview animation plays at 100% browser zoom without horizontal overflow.
- [ ] Pause, replay, and reduced-motion fallback work.
- [ ] Start Learning opens Command Lab.
- [ ] Run Health Simulation opens Health Dashboard.
- [ ] Solve an Incident opens Incident Lab.
- [ ] Dropdown and multiselect option panels use a solid background with readable text.
- [ ] Command, health, and incident result flows animate from workstation to diagnosis.
- [ ] Mobile/narrow layout stacks nodes without clipping.

## Assessment-engine checks

- [ ] Confirm the Assessment page contains no model, provider, API-key, or AI-generator controls.
- [ ] Confirm the source is shown as Reviewed random bank.
- [ ] Confirm 5-, 10-, and 15-question tests can be generated where enough reviewed questions exist.
- [ ] Confirm answer options are shuffled while the correct answer remains valid.
- [ ] Confirm the active reviewed test can be restored after a browser reload.
- [ ] Confirm dropdown controls and opened option menus are solid white in Chrome and Edge.
