# Consumption Standards (v0.3)

The producer standards (`standards/python/`, `standards/cli/`) define what an artifact must **ship**. This suite —
new in **0.3-draft** — defines how an agent **consumes** what was shipped: how it discovers the metadata at decision
time, what it reads for a given task, and what a conformant consumer is. It closes the producer→consumer loop the
first three review rounds kept flagging.

The suite is deliberately disciplined: it specifies **mechanisms, never benefits**. Whether consuming this metadata
improves agent outcomes is an empirical question with a pre-registered experiment attached; no normative text here
asserts effectiveness. The consumption *mechanism* is nonetheless a prerequisite — the experiment cannot run without
it, and the standard cannot say what makes the producer metadata worth shipping until the consumption contract exists.

## Documents

- [Discovery Contract](discovery-contract.md) — how a consumer obtains a package's MIRI metadata at decision time: a
  transport-agnostic metadata-query contract, with an MCP context server as its first binding.
- [Consumption Map](consumption-map.md) — the task-to-document reading contract: per agent task, what to read and in
  what order, what not to do, and an audit of what every metadata element is for.
- Consumer Conformance *(Planned)* — `MIRI-CONSUMER-NNN` checks, numbered against a reference consumer tool driven on
  the fixture set below.

## Fixtures

[`examples/fixtures/`](../../examples/fixtures/) holds one trivial package built three ways — **identical source,
different shipped metadata**: a `bare` variant (the honest-degradation baseline), a conforming `miri` twin, and an
`adversarial` twin whose metadata forges envelope signals, claims symbols that do not exist, pads its index to defeat
a cap, and carries injection text. Source identity is enforced mechanically by the build script, and
`tools/validate_fixtures.py` asserts each attack is still live, so the checks written against them cannot quietly
become vacuous.

## Origin

This suite grows out of the panel-reviewed
[Consumption Specification RFC](../../proposals/20260821-consumption-specification.md). The RFC's Open Questions and
the panel's must-fixes (a real wire contract, not one tool's behavior; the task map split into normative order vs
informative heuristics; the verification recipe reshaped to a safe pointer; the circularity firewall) are being worked
into these documents as they are drafted.
