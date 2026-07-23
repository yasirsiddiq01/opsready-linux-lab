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

## Included in version 1.7.1

- 150 Linux commands: 50 beginner, 50 intermediate, and 50 advanced
- learner guidance for every command: purpose, use case, output interpretation, flags, safe use, risk, and next step
- a compact safe Practice terminal with 25 reviewed commands, a virtual filesystem, command history, and 10 attempts per reset
- a separate Guided command explorer for the full 150-command catalogue
- command-specific execution traces showing shell parsing, kernel interfaces, VFS paths, procfs, systemd, journals, storage, container, security, or network touchpoints as appropriate
- scenario-driven Health Dashboard Simulator with dynamic command evidence, severity classification, and diagnostic recommendations
- structured learning paths with session progress
- 50 evidence-first incident diagnosis scenarios with simulated event logs
- 45 reviewed assessment questions used by an explicit random test generator
- duplicate-question validation and sampling without replacement inside each test
- active tests remain fixed during normal reruns and can be restored from a saved seed
- one stateful tabbed Learning Workspace plus separate Assessment, Feedback, and Help pages
- animated Overview walkthrough with direct calls to action, replay, pause, and reduced-motion support
- compact command-specific execution traces; local commands no longer show irrelevant switch or router stages
- high-contrast dropdown and multiselect panels with clear hover and selected states
- in-app product feedback with ratings, bug reports, feature requests, missing-topic requests, and optional contact permission
- local JSONL fallback and configurable persistent JSON webhook delivery
- free Google Sheets feedback collection setup
- enlarged learner-facing text, widgets, terminal output, metrics, and navigation
- automated content, scoring, assessment, and feedback tests
- a customer-facing Plans page separating the free Community edition from the planned Pro edition
- commercial safety gates that prevent a live checkout button until fulfilment, support, and legal-policy URLs are configured
- a Lemon Squeezy preparation pack covering product copy, activation answers, pricing decisions, seller readiness, and test-mode launch steps
- draft terms, privacy, refund, and commercial-disclosure templates with mandatory placeholders
- Docker and local deployment support

## Independent project structure

```text
opsready-linux-lab/
├── app.py
├── opsready_lab/
│   ├── catalog/
│   ├── services/
│   │   ├── assessment_engine.py
│   │   ├── execution_trace.py
│   │   ├── feedback.py
│   │   ├── practice_terminal.py
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

## Interactive practice terminal

Command Lab now separates two clear modes:

- **Practice terminal** — safely parses 25 reviewed commands against an in-memory virtual Linux filesystem. It preserves the current directory, shows command history, adapts selected system outputs to the Health Dashboard, and allows 10 supported attempts per reset.
- **Guided command explorer** — retains the complete 150-command catalogue with reviewed output, flags, risk guidance, and suggested next steps.

Both modes now use compact command-specific execution traces. For example, `pwd` shows the shell built-in and `getcwd()` path; `cat` shows the utility process, VFS, and target file; `systemctl` shows the control socket and systemd; and network commands show sockets, the kernel network stack, the interface, and the remote endpoint.

The interactive terminal never invokes a host shell, `subprocess`, a network client, or the hosting filesystem. Shell chaining, pipelines, redirection, command substitution, parent traversal, destructive commands, process control, and service control are blocked. See [`docs/PRACTICE_TERMINAL.md`](docs/PRACTICE_TERMINAL.md).

## Assessment generation

The assessment engine uses only the reviewed question bank. It creates a test when the learner explicitly presses **Generate test** or **Generate new test**.

For each test, it:

- filters questions by learning level;
- validates duplicate IDs and duplicate normalized question text;
- samples without replacement, so a question cannot repeat within the same test;
- shuffles the selected question order and answer options;
- saves a test seed and identifier so ordinary Streamlit reruns do not replace the active test.

There is no Qwen, external model, AI-provider configuration, API key, or model-generated learner content in version 1.7.1. See [`docs/ASSESSMENT_ENGINE.md`](docs/ASSESSMENT_ENGINE.md).

## Feedback collection before public launch

Local feedback files are not durable on most free hosting platforms. Configure a persistent endpoint before sharing the public application:

- [`docs/FEEDBACK_SETUP.md`](docs/FEEDBACK_SETUP.md)
- [`scripts/google_sheets_feedback_webhook.gs`](scripts/google_sheets_feedback_webhook.gs)
- [`.streamlit/secrets.toml.example`](.streamlit/secrets.toml.example)

## Commercial preparation

Version 1.7.1 prepares the Community application for a future Lemon Squeezy launch without accepting payment prematurely. The new **Plans** page shows the Community and planned Pro boundaries. A live checkout button appears only when both commercial gates are enabled and valid HTTPS checkout, terms, privacy, and refund URLs plus a support email are configured.

Start with:

- [`commercial/LEMON_SQUEEZY_SETUP.md`](commercial/LEMON_SQUEEZY_SETUP.md)
- [`commercial/COMMUNITY_PRO_MATRIX.md`](commercial/COMMUNITY_PRO_MATRIX.md)
- [`commercial/SELLER_READINESS_CHECKLIST.md`](commercial/SELLER_READINESS_CHECKLIST.md)
- [`commercial/PRE_LAUNCH_DECISIONS.md`](commercial/PRE_LAUNCH_DECISIONS.md)
- [`commercial/PRO_ROADMAP.md`](commercial/PRO_ROADMAP.md)

Run the application-side readiness check with:

```bash
python scripts/check_commercial_readiness.py
```

The check intentionally fails until paid fulfilment and all public policy links are ready. The current public repository remains the Community edition; paid-only implementation should be developed in a separate private repository.

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

The application never executes learner input on the host. Interactive Practice mode interprets reviewed syntax only against an in-memory virtual filesystem; Guided mode remains fully synthetic. Real command execution should be performed in a disposable WSL environment, virtual machine, container, or controlled cloud lab. Never run destructive commands on production infrastructure without authorisation, backups, impact assessment, and rollback planning.

## Current limitations

- progress is stored only in the current Streamlit browser session
- reviewed assessment tests can be rebuilt from their saved seed
- the feedback endpoint must be configured separately for durable public collection
- version 1.7.1 has no CAPTCHA or advanced spam protection
- the reviewed assessment bank currently contains 45 questions; expansion to 600 remains a separate content-development task
- the interactive terminal is a controlled simulator, not a real terminal sandbox or monitoring platform
- the 10-attempt terminal limit resets with the virtual terminal and is not an identity-based quota
