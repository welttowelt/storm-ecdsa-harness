# Safety And Disclosure

This project coordinates public resource-estimation benchmark research. It is
dual-use at the primitive level because ECDSA point addition appears inside
Shor-style cryptanalysis, but this repo is not an operational attack guide.

## Purpose

The purpose is to estimate and reduce benchmark circuit costs so the community
can reason more clearly about post-quantum migration timelines.

## Limits

This repo must not include:

- target selection,
- key recovery workflows,
- exploitation instructions,
- private compute access,
- raw scanner logs,
- unreleased winning nonces,
- private candidate diffs.

## Writing Rule

Every public artifact should stand alone for a cold reader:

- state the benchmark purpose,
- label evidence,
- name the validation gate,
- distinguish `Prefilter` from validated results,
- credit sources and inspirations.

## Publication Rule

If a result depends on another person's public tool, route, or process idea,
credit it in the public note. If the source is private group discussion, label
it as group-discussion inspiration rather than a public citation.

