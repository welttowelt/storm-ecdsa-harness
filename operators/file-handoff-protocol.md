# File-Based Handoff Protocol (Codex Storm <-> Kimi Storm)

## When to use this

Use this fallback when the Kimi Code API key is not active or when you prefer
not to route messages through the API bridge. It is slower than the bridge but
fully file-backed: no tokens, no rate limits, no endpoint dependency.

## Layout

Create one shared handoff file outside the public repo, for example in a private
ops folder:

```text
/private-ops/kimi-handoff/KIMI_HANDOFF.md
```

Do not commit this file. It contains live coordination state.

## File format

`KIMI_HANDOFF.md` has two sections:

```markdown
# KIMI_HANDOFF

## From Codex Storm

- Timestamp: <UTC>
- Route: <route-id>
- Action requested: <review | compute | submit-check | etc.>
- Context: <public-safe context>
- Exact question: <what Kimi Storm should answer>

## From Kimi Storm

- Timestamp: <UTC>
- Status: <ack | objection | done | needs-fix>
- Answer: <Kimi Storm's reply>
- Next owner: <who acts next>
```

## Cycle

1. Codex Storm writes the `From Codex Storm` section.
2. Human tells Kimi CLI: "Read /private-ops/kimi-handoff/KIMI_HANDOFF.md and
   reply in the From Kimi Storm section."
3. Kimi Storm reads the file, writes its reply, and saves.
4. Codex Storm reads the updated file and continues.

## Rules

- Keep the file outside the public repo.
- No private endpoints, keys, raw logs, or unreleased nonces in the handoff.
- Use route IDs and evidence labels from the Storm harness.
- Kimi Storm is still the boss: it decides whether to act, park, or override.
- Deep Storm can be cc'd by pasting the same public-safe context into its channel.

## Bridge vs file comparison

| Mode | Speed | Needs API key | Needs human relay | Best for |
|------|-------|---------------|-------------------|----------|
| API bridge | Fast | Yes | No | High-frequency back-and-forth |
| File handoff | Slow | No | Yes | Robust fallback, heavy reviews |
