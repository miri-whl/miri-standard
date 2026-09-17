# A shared conformance kernel: rule files, an operator vocabulary, and a driver

*Version: 0.1*
*Status: Proposal — offering the interop contract miri-py now runs on*
*Created: 2026-09-16*
*From: the miri-py implementation team*
*Pinned at: `6f4493c38fc36557845c13a41d78567d5ee80d1f` (0.5.0 on `main`)*

## Summary

miri-py's linter now executes the standard's four check families through one
config-driven kernel: committee YAML definitions own identity/level/weight,
per-check **rule files** own verification, and a small **operator vocabulary**
executes them. Framework code carries zero check ids; a family is wired by
configuration naming its definitions directory, rules directory, and — for
behavioural families — the subject argv under test.

We are offering the three artifacts that make a second implementation a
well-specified project rather than a reverse-engineering one:

1. **`rule-v1.json`** — the schema every rule file validates against.
2. **`operators-v1.json`** — the operator vocabulary and per-operator
   argument grammars.
3. **The driver semantics** below: how a conformant runner loads, executes,
   and — critically — how it accounts for what it does not cover.

Both schemas accompany this document in `schemas/`. Everything below is
implemented and measured, not designed: the coverage table at the end is our
own scorecard under this contract.

## 1. The shape: three layers, one direction

| Layer | Owns | Lives in |
|---|---|---|
| Committee definition (yours) | id, level, weight, severity, fires_when | `standards/<family>/checks/` |
| Rule file (per implementation, shareable) | HOW the check is verified: operator + arguments | `rules/<family>/<CHECK-ID>.yaml` |
| Configuration | WHICH families run, WHERE definitions/rules live, WHO is under test | one config file |

A rule file is small and closed:

```yaml
check: MIRI-CLI-013
rule:
  operator: cli.invoke
  argv: [score, /nope.whl, --json]
  expect:
    exit_code: {ne: 0}
    stdout_json:
      ok: {eq: false}
      error.code: {eq: INVALID_PACKAGE_PATH}
      schema_version: {matches: "^[0-9]+$"}
```

The rule says WHAT must hold; configuration says WHO answers. The same rule
files drove our CLI under `python -m miri_py`; a Rust CLI wires its own argv
and runs the identical files. That is the sharing this contract buys: for
behavioural families, the rule corpus is written once per standard, not once
per implementation.

## 2. The operator vocabulary

Four operators cover the four families today (`operators-v1.json` is
normative for argument shapes; all grammars are closed —
`additionalProperties: false` throughout):

- **`document.schema_valid`** — a named artifact document validates against a
  named schema. Pure data.
- **`cli.invoke`** — one invocation of the configured subject argv: judge
  exit code, a dotted-path expectation grammar over the stdout JSON envelope,
  and regex must/must-not over both raw streams. `stdin` may carry input (the
  default closes the stream, so a reading subject gets EOF rather than a
  hang).
- **`mcp.invoke`** — one JSON-RPC exchange with the configured surface
  subject, judged on TWO layers: `response_json` against the raw JSON-RPC
  response, `envelope_json` against the section-4 envelope parsed from the
  MCP text content.
- **`native`** — a named binding to a hand-written implementation behind a
  `(context, definition) -> outcome` contract.

The shared expectation grammar (used by both invoke operators) is dotted-path
with exactly five judgments — `eq / ne / in / exists / matches` — and
deliberately no control flow: a rule that needs comparison across
invocations, key-set closure, or array joins is a rule this language refuses
to express, and the check stays accounted for rather than half-verified (see
section 4).

## 3. `native` is a contract, not an escape hatch

Measurement, not taste, decided what stays native. We attempted to migrate
the python-wheel family and found every one of its 36 native checks
computational by nature: RECORD reconciliation, Core-Metadata and PEP 440
parsing, build-window timestamps, cross-document version joins, subprocess
execution of shipped examples, network attestation probes. Wrapping any of
these in a single-use operator is the same computation renamed — a second
language still writes the parser, so nothing is shared but indirection.

What IS shared for such checks is the **obligation list**: the rule file
names the binding (`miri_py.linter.checks.implementations:
check_wheel_structure`), so a conformant implementation ships a resolvable
implementation per named native rule, and our loader refuses to run with an
unimportable binding. The 40 python-wheel rule files — 4 schema-valid, 36
named native obligations — are the family's verification manifest, and a
second implementation reuses the manifest even where it cannot reuse the
code.

## 4. Driver semantics: forfeit, never silence

The part we most want standardized, because it is where conformance claims
rot:

1. A family run loads the committee definitions, then the rules; **every
   defined check reports an outcome** — pass, fail, or skip.
2. A check with no rule file **skips with its weight forfeited**. It is
   never silently passed; the family's score cannot exceed what its rules
   actually verify.
3. A rule that cannot execute (unlaunchable subject, unimportable binding)
   fails loudly at load or run time — never a quiet skip.
4. Coverage is reported per family (`N pass / N fail / N not yet covered
   (of M)`), and every uncovered check carries a *named* blocker in the
   implementation's ledger, so "not yet covered" is a work item, not a fog.

## 5. Fixture subjects, from your own pack

The consumer family only became drivable when the fixtures became
*installed distributions*: our rules invoke the real CLI resolving a real
environment, so we build `greet-bare` / `greet-miri` / `greet-adversarial`
wheels from the fixture pack vendored at the pinned SHA (mirroring
`examples/fixtures/build_fixtures.py` exactly — same variant table, same
pyproject, same byte-identity check) and install them before the family
runs. We would welcome the standard shipping prebuilt fixture wheels, or
blessing the build recipe, so every implementation installs identical bytes.

One divergence found on the way, already known upstream: the goldens' event
shape carries `package_kind` and a distribution name, while the pinned
`agent-event-v1` takes an import name and closes `subject` — our trigger
rules use the pinned schema.

## 6. Our scorecard under this contract

Measured on miri-py at the SHA above, every rule live-verified against the
running subject before authoring, and every uncovered check ledgered by
named blocker:

| Family | Rules | Result | Not covered, and why |
|---|---|---|---|
| python-wheel | 4 schema-valid + 36 native obligations | scored by `miri score` | — (measured decision, section 3) |
| cli | 24 `cli.invoke` | 24 pass / 0 fail | 19: env/TTY control, multi-invocation comparison, fixture-conditional subjects, array joins |
| surface | 12 `mcp.invoke` | 12 pass / 0 fail | 6: key-set closure operator, corrupt-document fixture, process observation, multi-request state |
| consumer | 15 `cli.invoke` (fixture wheels) | 15 pass / 0 fail | 3: network abstinence is process observation; publisher-independence compares two arms; trust revocation needs prior-read state |

The blockers cluster into exactly three missing operator classes
(key-set closure, multi-invocation comparison, process observation) — we
would rather grow the vocabulary with the committee than fork it.

## The ask

1. Adopt `rule-v1.json` and `operators-v1.json` (or successors) as
   standard-owned interop artifacts, versioned beside the check
   definitions.
2. State the driver semantics of section 4 normatively — forfeit-never-
   silence is what makes a coverage percentage comparable between
   implementations.
3. Ship or bless installable fixture wheels (section 5).
4. Treat the three missing operator classes as the roadmap for verifying
   the currently test-bound checks.
