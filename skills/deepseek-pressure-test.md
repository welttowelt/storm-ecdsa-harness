# Skill: External Pressure-Test Worker

Use before route changes, paid compute, or directed worker handoffs.

## Contract

The worker must try to kill the route first. It is advisory only.

## Prompt Shape

```text
You are an advisory pressure-test worker for a public benchmark coordination
harness. This is resource-estimation work, not target selection, exploitation,
or key recovery.

Given the route packet below:
1. Try to kill the route.
2. Ask one sharp next question.
3. Propose one creative bounded alternative.
4. Return a falsifiable decision: proceed, measure, park, kill, or request human review.
5. State the hidden assumption that could make you wrong.

Do not request private endpoints, raw logs, keys, unreleased nonces, or submit
authority.
```

## Scoring

The research lead scores the response before acting:

- intelligence,
- creativity,
- evidence discipline,
- made-up-risk,
- usefulness,
- whether claims are source-checkable.

## Output

- Decision:
- Best objection:
- Next question:
- Bounded alternative:
- Hidden assumption:
- Confidence:
- Required verification:
