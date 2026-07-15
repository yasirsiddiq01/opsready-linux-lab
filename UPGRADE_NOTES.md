# Upgrade Notes — 1.5.2

Version 1.5.2 removes Qwen and every model-provider option from the assessment system.

## Removed

- Qwen-compatible HTTP generation
- assessment-provider API URL, API key, model, timeout, and enablement settings
- AI-generated test selector and explanation panel
- generation cooldown and provider fallback workflow
- provider response parsing and schema-validation code
- Qwen-specific tests and documentation

## Retained and strengthened

- reviewed random question bank
- explicit **Generate test** and **Generate new test** actions
- stable active test during ordinary Streamlit reruns
- test restoration from identifier and seed
- shuffled question order and answer options
- three reviewed emergency questions per level as an internal fallback
- duplicate-ID and duplicate-normalized-question validation
- sampling without replacement, preventing repetition inside one test

## Important limitation

The bank still contains 45 reviewed questions. Expanding it to 600 is a separate editorial task and is not included in this removal patch.

## Update procedure

1. Stop Streamlit.
2. Copy the 1.5.2 patch over the 1.5.1 project.
3. Keep `.streamlit/secrets.toml`.
4. Run:

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m streamlit run app.py
```
