# Audit Process

Every active route should survive critique before paid compute or public claims.

## Loop

```text
Bluesky -> Redsky -> RCI -> implement smallest useful fix -> verify -> repeat
```

Use PUA/PIP when a worker repeats failed assumptions, gives vague progress, or
stops after a shallow NACK.

## Required Audit Output

- Problem
- Evidence
- Effect
- Smallest useful fix
- Gate
- Verification result
- Next owner
- `no_submit_ack=yes`

## Redsky Checks

- Is the current target fresh?
- Is the source/base current?
- Is the evidence label honest?
- Is the validator real?
- Is the expected edge positive after full costs?
- Is there a stop condition?
- Is compute or submit overclaimed?

## Bluesky Checks

- What would make this route real?
- What smallest measurement would unlock it?
- What alternate formulation preserves upside?
- What can be tested without paid compute?
