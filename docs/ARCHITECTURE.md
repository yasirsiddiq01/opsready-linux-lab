# Architecture

## Entry point

`app.py` configures Streamlit, initialises session progress, and routes the four public navigation pages:

- Learning Workspace
- Assessment
- Feedback
- Help

## Package boundaries

### `opsready_lab/catalog`

Static reviewed educational content:

- command definitions and learner guidance
- incident scenarios
- assessment questions

### `opsready_lab/services/assessment_engine.py`

Explicit assessment-test generation, deterministic seeded random selection, duplicate-bank validation, sampling without replacement, option shuffling, reviewed emergency fallback questions, and temporary JSON cache persistence.

### `opsready_lab/services/progress.py`

Session-only completion and scoring logic. It prevents duplicate score awards in the same browser session.

### `opsready_lab/services/feedback.py`

Feedback record construction, input normalisation, validation, JSONL fallback persistence, webhook URL validation, JSON delivery, and delivery-status reporting.

### `opsready_lab/ui/theme.py`

Reusable presentation helpers and global learner-facing typography.

### `opsready_lab/config.py`

Application name, version, tagline, and slug.

## State model

Learning progress is held in Streamlit session state and is intentionally non-persistent in the free validation version. The active assessment test is stored in session state, cached under `.runtime/assessment_tests/`, and referenced through URL query parameters. Reviewed tests can be rebuilt from their seed. Feedback is separate: it can be delivered to an external persistent webhook while a local JSONL copy acts as a development fallback.

## Security boundary

The application never invokes a shell or executes learner input. Feedback webhook URLs are read from environment variables or private Streamlit secrets and must not be committed to source control. Assessment generation has no external model or API dependency.

## Visual simulation layer

`opsready_lab/ui/animations.py` contains the self-contained Overview hero and reusable operational-flow animation. The implementation uses inline SVG and CSS only; it does not require a video file, JavaScript component, external CDN, or third-party animation service.

Workspace navigation is stored in `st.session_state.workspace_tab`. This allows Overview call-to-action buttons to open Command Lab, Health Dashboard, or Incident Lab directly while keeping all learning sections in one tab-style workspace.
