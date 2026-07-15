# Version 1.5.2 Patch Instructions

This patch updates version 1.5.1.

1. Stop the running application with `Ctrl + C`.
2. Back up `.streamlit/secrets.toml`.
3. Extract the patch.
4. Copy the patch's `opsready-linux-lab` contents into the existing project.
5. Allow matching files to be replaced.
6. From the project root, remove obsolete files with one of these commands:

Windows PowerShell:

```powershell
.\scripts\cleanup_v152.ps1
```

Linux or macOS:

```bash
bash scripts/cleanup_v152.sh
```

7. Confirm `.streamlit/secrets.toml` still exists.
8. Run:

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m streamlit run app.py
```

The patch does not include your real secrets file.
