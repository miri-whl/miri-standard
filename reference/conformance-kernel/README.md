# Conformance kernel — reference artifact

*Status: Reference, not normative. Versioned beside the check definitions; promoted to normative only when the test
below is met.*
*Source: the miri-py implementation team, `conformance-interop-contract-proposal.md`*
*Pinned at: miri-py `afc51324277d9cac04ad81201b6272b47d4ce4ff` (2026-09-17)*

## What this is

The interop contract miri-py's linter runs on: per-check **rule files** own *how* a check is verified, a small
**operator vocabulary** executes them, and the committee definitions in `standards/<target>/checks/` own identity,
level and weight. Two schemas are recorded here unmodified from the source, with their `$id` rebased to
`miri-whl.github.io`:

- `rule-v1.json` — the shape every rule file validates against.
- `operators-v1.json` — the four operators (`document.schema_valid`, `cli.invoke`, `mcp.invoke`, `native`) and their
  closed argument grammars.

The rule corpus itself lives in the miri-py repository at `src/miri_py/linter/checks/policy/rules/<family>/`, one
file per check ID. It is not vendored here: a snapshot of 51 rule files goes stale on their next commit, and a
pointer at a pinned SHA does not.

## Why reference and not normative

Declined as a standard-owned artifact in the standard's response, on the proposer's own measurements: the vocabulary
covers 51 of 79 behavioural checks and is inert for `python-wheel`, whose 36 of 40 checks are irreducibly
computational (their §3). A grammar frozen at that coverage would make `native` the escape hatch the proposal says it
is not. What *is* standard-owned from that proposal is the driver semantics — `scoring-v1.json`
`conformance.coverage` — because forfeit-never-silence is what makes a coverage percentage comparable between
implementations, and it does not depend on which grammar produced the verdicts.

## Promotion test

These schemas become normative when the three missing operator classes exist — multi-invocation comparison, key-set
closure, process observation — and the behavioural families are covered without `native` standing in for a missing
operator. The first of the three is on the critical path: the standard's own CLI harness already rejects a
submission with no control arm, so the comparison is demanded normatively and only the grammar cannot express it.
