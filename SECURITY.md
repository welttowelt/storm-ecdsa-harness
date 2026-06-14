# Security And Disclosure

This repo is a public coordination harness for benchmark research. It must not
contain private operational material.

## Do Not Commit

- API keys, tokens, secrets, private keys, or credential helper output.
- Remote machine endpoints, ports, account names, or command transcripts.
- Live mailbox content or private chat exports.
- Raw run logs, scan logs, unreleased candidate diffs, or unreleased nonces.
- Private local paths or account-specific directory layouts.

## Required Before Publishing

Run:

```bash
scripts/redaction-check.sh
```

Then manually review:

- `README.md`
- `docs/credits.md`
- `CREDITS.yaml`
- dashboard fixture files
- all templates

## Issue Reporting

If you find private material in a published version, open a private disclosure
channel with the maintainer first. Do not repost the sensitive material in a
public issue.

