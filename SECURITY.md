# Security Policy

## Educational boundary

OpsReady Linux Lab does not execute learner input on the host. Guided command output is synthetic. Interactive Practice mode parses a reviewed command subset and operates only on an in-memory virtual filesystem.

## Practice-terminal security

- Never add `subprocess`, `os.system`, `shell=True`, or a generic shell fallback.
- Keep command parsing explicit and option-specific.
- Block shell chaining, pipelines, redirection, command substitution, parent traversal, network clients, process control, service control, mounting, shutdown, and destructive filesystem commands.
- Do not map virtual paths to the host filesystem.
- Treat the 10-attempt limit as a learning control, not authentication or anti-abuse enforcement.
- Add tests before extending the reviewed command set.
- A real executable terminal requires a separate sandbox service and security review.

## Feedback security

- Store webhook URLs only in environment variables or Streamlit secrets.
- Never commit `.streamlit/secrets.toml`.
- Restrict access to response sheets or databases.
- Do not collect passwords, access tokens, private logs, internal IP addresses, or confidential system information.
- Optional email addresses are personal data and should be retained only as long as necessary.
- Version 1.7.1 has no CAPTCHA; monitor for spam and disable the endpoint if abused.

## Assessment integrity

- Learner-facing questions come only from the reviewed local bank.
- Duplicate IDs and duplicate normalized question text are rejected by validation.
- Correct answers must exactly match one listed option.
- Do not add unreviewed questions directly to production content.
- Keep review notes or source references outside learner-facing text when expanding the bank.

## Reporting problems

Before a wider launch, replace this section with a monitored project-owner security or support email address. Do not request vulnerability details through the public feedback form when they may contain sensitive technical information.


## Commercial checkout safety

- Checkout is disabled by default.
- A live upgrade link requires both `sales_enabled` and `fulfilment_ready`.
- Checkout and policy links must use HTTPS.
- No Lemon Squeezy API key or webhook secret belongs in the public Community repository.
- Webhook signatures must be verified in a separate backend before subscription state changes.
- The public Community app must not contain private Pro source code or rely on client-side checks for paid access.
