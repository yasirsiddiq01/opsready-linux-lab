# Upgrade Notes — 1.7.1

Version 1.7.1 is a focused maintenance release for the pre-commerce Community application.

## Main changes

- fixes both Ruff findings in `opsready_lab/services/commercial.py`;
- gives the sidebar Reset session progress button a readable dark resting state;
- keeps the button text visible before hover;
- adds a three-phase Pro delivery roadmap to Plans;
- keeps live checkout disabled by default.

## Apply the patch

1. Stop Streamlit.
2. Back up `.streamlit/secrets.toml`.
3. Merge the 1.7.1 patch into the existing 1.7.0 project.
4. Run:

```powershell
python -m pytest -q
python -m ruff check .
python -m streamlit run app.py
```

## Manual checks

1. Confirm the sidebar Reset session progress text is visible without hovering.
2. Hover and keyboard-focus the button and confirm contrast remains clear.
3. Open Plans and confirm the Foundation, Founding beta, and Instructor phases render.
4. Confirm no Upgrade to Pro button appears with default commercial settings.
