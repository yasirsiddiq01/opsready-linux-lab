# Patch instructions — 1.7.1

Apply this patch over OpsReady Linux Lab 1.7.0.

1. Stop Streamlit.
2. Back up `.streamlit/secrets.toml`.
3. Copy the patch's `opsready-linux-lab` contents into the existing project and replace matching files.
4. Run `python -m pytest -q`.
5. Run `python -m ruff check .`.
6. Start the application and manually verify the sidebar reset button and Plans roadmap.
