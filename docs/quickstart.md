# Quickstart

This quickstart shows how to copy the public Storm operator layer without
importing private state.

## 1. Start From A Fresh Copy

Use the GitHub template button or clone the repo:

```bash
git clone https://github.com/welttowelt/storm-ecdsa-harness.git
cd storm-ecdsa-harness
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
- `templates/audit-card.md`
- `templates/mailbox-entry.md`
- `templates/route-packet.md`
- `templates/compute-request.md`
- `templates/public-note.md`
- `templates/kimi-handoff.md`

Use these as formats, not as a mandate. The core rule is that every compute
request should have an owner, validator, kill gate, and evidence label.

If you want a filled safe example first, read `examples/`. If you need a
three-worker operating loop, read `operators/handoff-protocol.md` and the role
cards in `operators/`.

Use `docs/audit-loop.md` when you want the RCI/Tony plus Bluesky/Redsky review
cycle before changing docs, dispatching compute, or writing a public note.

You can also copy the audit roles as standalone skills:

- `skills/tony-rci-audit.md`
- `skills/bluesky-audit.md`
- `skills/redsky-audit.md`

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
private-storm-controller/
private-worker-mailbox/
private-runs-and-logs/
private-fleet-config/
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
3. Run Bluesky if the route needs a constructive path.
4. Run Redsky to try to kill the route before compute.
5. Run Tony/RCI to turn findings into smallest useful fixes and gates.
6. Run cheap validation.
7. Dispatch paid compute only if the route has a validator and kill gate.
8. Treat scanner hits as `Prefilter`.
9. Submit only after official local validation and a fresh frontier check.

For the full production mapping, read
`docs/production-shape.md`.

If a worker fails twice, repeats the same approach, or claims completion without
evidence, run `skills/pip-discipline.md` before the next attempt. It forces the
worker to read the failure signal, refresh public truth, invert the assumption,
name three different hypotheses, and define the next bounded check.

The most useful habit is not the dashboard. It is forcing every worker and every
compute job to explain what would prove the route dead.
