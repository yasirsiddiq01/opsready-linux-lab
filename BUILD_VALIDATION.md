# Build Validation — OpsReady Linux Lab 1.5.2

Validation completed on 2026-07-14.

## Automated checks

```text
34 tests passed
Ruff checks passed
Python compilation passed
Streamlit startup passed
Health endpoint returned: ok
```

## Assessment verification

- Qwen and external model-provider code removed
- no learner-facing AI or model-generator selector
- no assessment API-key or model settings in the secrets template
- reviewed-bank test generation only
- duplicate question IDs rejected
- duplicate normalized question text rejected
- sampling without replacement prevents duplicates inside one test
- saved seeds reconstruct the same reviewed test
- different seeds create different random selections
- three reviewed emergency questions remain available per level internally

## Content counts

```text
150 Linux commands
50 incidents
45 reviewed assessment questions
```

The planned 600-question expansion is not part of version 1.5.2.
