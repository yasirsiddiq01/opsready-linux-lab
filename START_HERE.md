# Start Here

## 1. Extract into a separate folder

Keep this project independent from the earlier portfolio repository.

```text
opsready-linux-lab/
```

## 2. Create the environment

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

### Linux or macOS

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

## 3. Run validation

```bash
python -m pytest -q
python -m ruff check .
python -m compileall -q app.py opsready_lab
```

## 4. Run the application

```bash
python -m streamlit run app.py
```

Open `http://localhost:8501`.

## 5. Configure feedback persistence

Do not publicly launch using only the local feedback file. Follow [`docs/FEEDBACK_SETUP.md`](docs/FEEDBACK_SETUP.md) and configure either:

```text
OPSREADY_FEEDBACK_WEBHOOK_URL
```

or:

```toml
[feedback]
webhook_url = "https://your-private-feedback-endpoint"
```

Submit a test response and verify that it reaches the destination.

## 6. Verify assessment behaviour

The app uses only its reviewed question bank. Confirm that:

- no test appears until **Generate test** is pressed;
- the active test remains unchanged during ordinary reruns;
- **Generate new test** produces another random test;
- a test contains no duplicate question;
- changing the level does not replace an active test until generation is requested.

## 7. Create an independent Git repository

### Windows

```powershell
.\scripts\init_repository.ps1
```

### Linux or macOS

```bash
bash scripts/init_repository.sh
```

## 8. Complete the public-launch checklist

Read [`LAUNCH_CHECKLIST.md`](LAUNCH_CHECKLIST.md). Do not publish the free link until feedback persistence, privacy contact details, tests, and mobile checks are complete.
