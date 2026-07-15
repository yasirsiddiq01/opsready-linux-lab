# Deployment

## Required pre-launch step

Configure durable feedback delivery before sharing the application publicly. See [`FEEDBACK_SETUP.md`](FEEDBACK_SETUP.md). Local `runtime/feedback.jsonl` storage is intended only for development and may disappear on hosted restarts.

## Streamlit Community Cloud

1. Create a new repository containing this package.
2. Select `app.py` as the application entry point.
3. Use `requirements.txt` for runtime dependencies.
4. Add the feedback webhook in the Streamlit secrets editor:

```toml
[feedback]
webhook_url = "https://your-private-feedback-endpoint"
```

5. Confirm a test response reaches the persistent destination.
6. Confirm the health page and assessments load after deployment.

## Hugging Face Spaces

The README includes Streamlit Space metadata. Upload the package and add this repository secret:

```text
OPSREADY_FEEDBACK_WEBHOOK_URL=https://your-private-feedback-endpoint
```

## Docker

```bash
docker compose up --build
```

Pass the endpoint as an environment variable in production:

```text
OPSREADY_FEEDBACK_WEBHOOK_URL=https://your-private-feedback-endpoint
```

The container exposes port `8501` and includes a Streamlit health check.

## Production limitations

The current application uses in-memory session progress. Horizontal scaling, persistent progress, accounts, payments, advanced anti-spam controls, and coordinated session handling require external services.
