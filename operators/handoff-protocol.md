# Two-Model + Codex Handoff Protocol

## Roles

| Operator | Model | Primary roles |
|----------|-------|---------------|
| Kimi Storm | Kimi | Research lead, Engineering specialist, Submitter (boss) |
| Deep Storm | DeepSeek | Deep researcher, Skeptic, RCI/Redsky reviewer |
| Codex Storm | OpenAI Codex | External pressure-test worker, Source-check reviewer, bridge partner |

## Cycle

```text
1. Kimi Storm refreshes current target and writes route packet.
2. Kimi Storm posts route packet to mailbox -> Deep Storm + Codex Storm.
3. Deep Storm runs deep research + Redsky audit; returns ACK or OBJECTION.
4. Codex Storm runs pressure-test audit via bridge or shared link; returns bounded critique.
5. Kimi Storm reads ACKs, updates packet, runs cheap validation.
6. If compute gate is complete, Kimi Storm dispatches compute request.
7. Results are labeled Prefilter until official local validation passes.
8. Kimi Storm runs official local validation and fresh frontier recheck.
9. Kimi Storm writes public note and credits.
10. Kimi Storm opens submit gate only with explicit user flag.
```

## Mailbox addressing

```text
From -> To: Title -- UTC timestamp
Kimi Storm -> Deep Storm: Route packet review for <route-id>
Kimi Storm -> Codex Storm: External pressure test for <route-id>
Deep Storm -> Kimi Storm: Deep audit / ACK / OBJECTION for <route-id>
Codex Storm -> Kimi Storm: Pressure-test review for <route-id>
Kimi Storm -> all: Compute request / result / public note for <route-id>
```

## Bridge path

Codex Storm can reach Kimi Storm through:

```bash
cd <repo-root>
export KIMI_API_KEY="<kimi-api-key>"
python3 tools/kimi_bridge.py "Codex Storm | route: <route-id> | decision: needs fix | <your critique>"
```

Use a real key only in a private shell or secret manager. Public docs should use
placeholders and must not contain live tokens or transcripts.

The bridge maintains `tmp/kimi_bridge/transcript.jsonl` under `<repo-root>` so
both sides retain context across messages.

## Decision rules

- Deep Storm objection blocks compute until resolved or documented override.
- Codex Storm `needs fix` is advisory; Kimi Storm decides.
- `Prefilter` results never bypass official local validation.
- Submit gate requires explicit user `--submit` flag; no model opens it alone.

## Privacy boundary

- Kimi Storm may see private state (local paths, keys, nonces) in a private ops
  repo or local folder.
- Deep Storm sees only what is needed for proof/validation design; no live
  endpoints or raw nonces.
- Codex Storm sees only public route packets, public notes, and fixture data.
