# Quickstart

This quickstart shows how to copy the public Stormforge operator layer without
importing private state.

## 1. Start From A Fresh Copy

Use the GitHub template button or clone the repo:

```bash
git clone https://github.com/welttowelt/stormforge-ecdsa-harness.git
cd stormforge-ecdsa-harness
```

Keep this repo as a public coordination/template layer. Put private operations
in a separate private repo or local folder.

## 2. Run The Safety Checks

```bash
scripts/redaction-check.sh
scripts/redaction-check.sh --history
scripts/check-public-harness.sh
```

Both should pass before you publish, screenshot, or share.

## 3. Copy The Templates

Start with:

- `templates/operator-card.md`
- `templates/mailbox-entry.md`
- `templates/route-packet.md`
- `templates/compute-request.md`
- `templates/public-note.md`

Use these as formats, not as a mandate. The core rule is that every compute
request should have an owner, validator, kill gate, and evidence label.

If you want a filled safe example first, read `examples/`.

## 4. Keep Private State Outside This Repo

Do not store these in the public repo:

- live mailbox history,
- API keys or tokens,
- pod endpoints or machine commands,
- scanner logs,
- private candidate diffs,
- raw nonces,
- local absolute paths,
- active route state.

Recommended local split:

```text
public-template-repo/
private-hunt-ops/
private-mailbox-or-notes/
private-runs-and-logs/
```

## 5. Update The Fixture Dashboard

The dashboard reads only:

```text
dashboard/fixtures/status.json
```

Replace it with demo or public data only. Run the redaction check after every
change.

Local preview:

```bash
python3 -m http.server 8787 --directory dashboard
```

## 6. Add Credits Before Sharing

If you use an idea from a person, repo, article, or group discussion, add it to:

- `docs/credits.md`
- `CREDITS.yaml`

Use:

- `uses` for direct code/tool dependencies,
- `inspired by` for process ideas,
- `based on` only for direct foundations,
- `group_context_unverified_publicly` when no public source exists.

## 7. First Operating Loop

For each route:

1. Refresh public current target.
2. Write a route packet.
3. Ask a critique worker to try to kill it.
4. Run cheap validation.
5. Dispatch paid compute only if the route has a validator and kill gate.
6. Treat scanner hits as `Prefilter`.
7. Submit only after official local validation and a fresh frontier check.

The most useful habit is not the dashboard. It is forcing every worker and every
compute job to explain what would prove the route dead.
