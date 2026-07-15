---
title: OpsReady Linux Lab
emoji: 🐧
colorFrom: blue
colorTo: indigo
sdk: streamlit
app_file: app.py
pinned: false
---

# OpsReady Linux Lab

OpsReady Linux Lab is a standalone educational application for learning Linux server operations and troubleshooting. It simulates commands and incidents without connecting to or modifying a real server.

## Included in version 1.5.2

- 150 Linux commands: 50 beginner, 50 intermediate, and 50 advanced
- learner guidance for every command: purpose, use case, output interpretation, flags, safe use, risk, and next step
- scenario-driven Health Dashboard Simulator with dynamic command evidence, severity classification, and diagnostic recommendations
- structured learning paths with session progress
- 50 evidence-first incident diagnosis scenarios with simulated event logs
- 45 reviewed assessment questions used by an explicit random test generator
- duplicate-question validation and sampling without replacement inside each test
- active tests remain fixed during normal reruns and can be restored from a saved seed
- one stateful tabbed Learning Workspace plus separate Assessment, Feedback, and Help pages
- animated Overview walkthrough with direct calls to action, replay, pause, and reduced-motion support
- animated workstation, switch, router, Linux server, evidence, and diagnosis flows for simulations
- high-contrast dropdown and multiselect panels with clear hover and selected states
- in-app product feedback with ratings, bug reports, feature requests, missing-topic requests, and optional contact permission
- local JSONL fallback and configurable persistent JSON webhook delivery
- free Google Sheets feedback collection setup
- enlarged learner-facing text, widgets, terminal output, metrics, and navigation
- automated content, scoring, assessment, and feedback tests
- Docker and local deployment support

## Independent project structure

```text
opsready-linux-lab/
├── app.py
├── opsready_lab/
│   ├── catalog/
│   ├── services/
│   │   ├── assessment_engine.py
│   │   ├── feedback.py
│   │   └── progress.py
│   ├── ui/
│   └── config.py
├── tests/
├── docs/
├── scripts/
├── .streamlit/
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── requirements.txt
```

For the full first-run and new-repository procedure, read [`START_HERE.md`](START_HERE.md).

## Quick start

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m streamlit run app.py
```

### Linux or macOS

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m streamlit run app.py
```

Open `http://localhost:8501` after Streamlit starts.

## Assessment generation

The assessment engine uses only the reviewed question bank. It creates a test when the learner explicitly presses **Generate test** or **Generate new test**.

For each test, it:

- filters questions by learning level;
- validates duplicate IDs and duplicate normalized question text;
- samples without replacement, so a question cannot repeat within the same test;
- shuffles the selected question order and answer options;
- saves a test seed and identifier so ordinary Streamlit reruns do not replace the active test.

There is no Qwen, external model, AI-provider configuration, API key, or model-generated learner content in version 1.5.2. See [`docs/ASSESSMENT_ENGINE.md`](docs/ASSESSMENT_ENGINE.md).

## Feedback collection before public launch

Local feedback files are not durable on most free hosting platforms. Configure a persistent endpoint before sharing the public application:

- [`docs/FEEDBACK_SETUP.md`](docs/FEEDBACK_SETUP.md)
- [`scripts/google_sheets_feedback_webhook.gs`](scripts/google_sheets_feedback_webhook.gs)
- [`.streamlit/secrets.toml.example`](.streamlit/secrets.toml.example)

## Docker

```bash
docker compose up --build
```

## Quality checks

```bash
make check
```

or:

```bash
python -m pytest -q
python -m ruff check .
python -m compileall -q app.py opsready_lab
```

## Safety boundary

The application never executes commands entered by the user. Real practice should be performed in a disposable WSL environment, virtual machine, container, or controlled cloud lab. Never run destructive commands on production infrastructure without authorisation, backups, impact assessment, and rollback planning.

## Current limitations

- progress is stored only in the current Streamlit browser session
- reviewed assessment tests can be rebuilt from their saved seed
- the feedback endpoint must be configured separately for durable public collection
- version 1.5.2 has no CAPTCHA or advanced spam protection
- the reviewed assessment bank currently contains 45 questions; expansion to 600 remains a separate content-development task
- the application is a simulator, not a real terminal sandbox or monitoring platform
