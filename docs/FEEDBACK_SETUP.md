# Feedback Collection Setup

OpsReady Linux Lab 1.2 includes an in-app feedback form. The form always attempts to save a local JSONL fallback, but local files on free hosting platforms may disappear after a restart, rebuild, or redeployment.

**Configure a persistent webhook before sharing the public link.** A free Google Sheet with Google Apps Script is sufficient for initial validation.

## Collected fields

The form records:

- submission ID and UTC timestamp
- application version and anonymous browser-session ID
- learner role and Linux experience
- feedback categories and sections used
- usefulness, ease, confidence, and recommendation ratings
- most useful feature, priority improvement, and missing content
- bug/confusion report and details
- optional email and contact permission
- consent to store and use the feedback

The form explicitly tells users not to submit credentials, private logs, tokens, IP addresses, or confidential information.

## Option A: Google Sheets webhook — recommended free setup

### 1. Create the sheet

1. Create a new Google Sheet.
2. Rename it to `OpsReady Linux Lab Feedback`.
3. Open **Extensions → Apps Script**.
4. Delete the default code.
5. Copy the contents of [`scripts/google_sheets_feedback_webhook.gs`](../scripts/google_sheets_feedback_webhook.gs).
6. Save the project.

### 2. Deploy the Apps Script

1. Select **Deploy → New deployment**.
2. Choose **Web app**.
3. Execute as: **Me**.
4. Who has access: **Anyone**.
5. Deploy and authorise the script.
6. Copy the web-app URL ending in `/exec`.

The webhook URL must be treated as a secret. Do not commit it to GitHub.

### 3. Configure Streamlit locally

Copy the example file:

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

On Windows PowerShell:

```powershell
Copy-Item .streamlit\secrets.toml.example .streamlit\secrets.toml
```

Edit `.streamlit/secrets.toml`:

```toml
[feedback]
webhook_url = "https://script.google.com/macros/s/REPLACE_WITH_DEPLOYMENT_ID/exec"
```

The real secrets file is excluded by `.gitignore`.

### 4. Configure hosted deployments

For Hugging Face Spaces or container hosting, add this private environment variable:

```text
OPSREADY_FEEDBACK_WEBHOOK_URL=https://script.google.com/macros/s/REPLACE_WITH_DEPLOYMENT_ID/exec
```

For Streamlit Community Cloud, add this in the application secrets editor:

```toml
[feedback]
webhook_url = "https://script.google.com/macros/s/REPLACE_WITH_DEPLOYMENT_ID/exec"
```

### 5. Test before launch

1. Restart the app after adding the secret.
2. Open **Feedback**.
3. Confirm the local-storage setup warning is no longer displayed.
4. Submit a test response.
5. Confirm a new row appears in the Google Sheet.
6. Delete the test row before launch if required.

## Option B: Generic JSON webhook

Set `OPSREADY_FEEDBACK_WEBHOOK_URL` to any HTTPS endpoint that accepts a JSON POST and returns an HTTP 2xx response. This can be a Make.com scenario, Pipedream workflow, serverless function, or your own API.

The payload keys are defined by `FeedbackRecord` in `opsready_lab/services/feedback.py`.

## Local development fallback

Without a webhook, submissions are appended to:

```text
runtime/feedback.jsonl
```

Change the path with:

```text
OPSREADY_FEEDBACK_FILE=/absolute/path/to/feedback.jsonl
```

The `runtime/` directory is ignored by Git and must not be treated as durable production storage.

## Operational limitations

- There is no CAPTCHA in version 1.3. A public endpoint may receive spam.
- Google Sheets is appropriate for small-scale validation, not high-volume analytics.
- Restrict sheet access to the project owner and authorised collaborators.
- Delete optional email addresses when no longer needed.
- Publish an appropriate privacy notice before collecting feedback publicly.
- Do not promise confidentiality for data users were explicitly instructed not to submit.
