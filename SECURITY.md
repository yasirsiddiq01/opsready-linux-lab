# Security Policy

## Educational boundary

OpsReady Linux Lab does not execute entered commands and should not be modified to run arbitrary shell input without a separate sandbox-security design.

## Feedback security

- Store webhook URLs only in environment variables or Streamlit secrets.
- Never commit `.streamlit/secrets.toml`.
- Restrict access to response sheets or databases.
- Do not collect passwords, access tokens, private logs, internal IP addresses, or confidential system information.
- Optional email addresses are personal data and should be retained only as long as necessary.
- Version 1.5.2 has no CAPTCHA; monitor for spam and disable the endpoint if abused.

## Assessment integrity

- Learner-facing questions come only from the reviewed local bank.
- Duplicate IDs and duplicate normalized question text are rejected by validation.
- Correct answers must exactly match one listed option.
- Do not add unreviewed questions directly to production content.
- Keep review notes or source references outside learner-facing text when expanding the bank.

## Reporting problems

Before public launch, replace this section with a monitored project-owner security or support email address. Do not request vulnerability details through the public feedback form when they may contain sensitive technical information.
