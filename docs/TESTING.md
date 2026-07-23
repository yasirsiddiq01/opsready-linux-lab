# Testing

Run all checks with:

```bash
make check
```

The automated suite validates:

- minimum command, incident, and assessment counts
- required content fields and unique identifiers
- score idempotency and assessment-bank integrity
- deterministic random assessments and no repetition inside a test
- feedback validation and form reset behaviour
- exactly 25 reviewed Practice-mode commands
- stateful `cd`, relative paths, and virtual-file reads
- reviewed `awk`, `grep`, `sed`, and filesystem output
- Health Dashboard linkage for `df`, `free`, `ps`, and `uptime`
- run-limit enforcement
- blocked chaining, pipelines, redirection, substitution, traversal, network clients, runtimes, and destructive commands
- absence of shell-execution imports or fallbacks
- Streamlit Practice terminal rendering, execution, and blocked-input behaviour

Manual smoke test:

1. Start the app and open every navigation page.
2. Open Command Lab and confirm **Practice terminal** is the default mode.
3. Run `pwd`, `ls -la`, `cd projects`, and `cat readme.md`; confirm the directory is stateful.
4. Run `awk -F: '{print $1, $7}' /etc/passwd`.
5. Submit `pwd && whoami`, `curl https://example.com`, and `cat ../../etc/passwd`; confirm they are blocked without consuming a run.
6. Use all 10 supported attempts and confirm the eleventh is refused until reset.
7. Run a Health Dashboard scenario, return to Command Lab, and confirm `df`, `free`, `ps`, or `uptime` reflects it.
8. Switch to Guided command explorer and run one command outside the 25-command Practice subset.
9. Generate and submit an assessment.
10. Submit feedback and verify the persistent destination receives the row.
11. Test desktop, tablet, and one real mobile phone.

Expected automated result for version 1.7.1:

```text
57 non-UI tests passed
```


## Commercial readiness tests

The suite verifies that checkout is disabled by default, rejects non-HTTPS URLs and malformed support addresses, permits a waitlist without enabling payment, and only marks live checkout ready when fulfilment and all policy requirements are configured.

Run the owner-facing configuration check separately:

```bash
python scripts/check_commercial_readiness.py
```

A non-zero result is expected before the Pro fulfilment system and live policy URLs exist.
