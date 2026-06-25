# Skill: Tony / RCI Audit

Use before rewriting a note, changing a route packet, approving a compute
request, or making a public claim.

## Goal

Turn vague critique into a concrete fix. The worker should inspect the actual
artifact, identify specific problems, cite evidence, explain the effect, propose
the smallest useful fix, and name the gate that proves the fix worked.

## Public Boundary

Do not request or expose:

- private endpoints,
- account details,
- keys or tokens,
- raw logs,
- unreleased nonces,
- live candidate diffs,
- private mailbox history,
- submit authority.

When the artifact depends on private state, stop at the handoff boundary and
name the public or local evidence needed next.

## Protocol

1. Read the target artifact directly.
2. Name the decision being audited.
3. Identify concrete problems, not vibes.
4. Cite the source line, field, claim, command, or missing check.
5. Explain the effect on routing, safety, quality, or public claims.
6. Propose the smallest useful fix.
7. Define the gate that would prove the issue is resolved.
8. Return a proceed, park, kill, or request-human-review decision.

## Output

```text
Tony / RCI audit:
- Decision audited:
- Problem:
- Evidence:
- Effect:
- Smallest useful fix:
- Gate:
- Decision:
- Owner:
- Next action:
```

## Completion Gate

Do not approve the artifact until the named gate has run or the missing check is
listed as a blocker.
