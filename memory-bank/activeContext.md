# Active Context

_Last updated: 2026-09-08._

## Current focus

**v0.5.0, on `phase-0.4.1`** — committed, pushed, not yet merged. The branch carries six commits and `main` is
behind; opening the PR is the immediate next action.

The branch name is deliberate and should not be tidied. The work began as 0.4.1 (four fixes from the first binding)
and became a minor release when it gained the Production Maps, which are additions. The version followed the content
rather than the content being trimmed to fit the version; renaming the branch afterwards would be churn.

**Six adversarial panels reviewed 0.5.0 on 2026-09-08 and it did not survive them.** Roughly forty defects, every one
confirmed by direct verification, zero false positives. Scores: goldens 26, schema 34, vacuous-pass 34, CLI fixtures
34, derivation 55, coherence 58. The register and the first remediation pass live in `memory-
bank/tasks/0.5.0-remediation/`. **0.5.0 must not merge until the residue there is closed** — most urgently the CLI
fixtures, which still ship no goldens and therefore grade nothing.

The root cause is worth carrying forward, because it survived my own review twice during the fix pass: assertions get
written against the artifact the author just wrote, not against a behavior an implementation must produce. Its
signature is one-directional verification — every claim made gets checked, and nothing gets checked against what was
not claimed.

**The core loop is structurally complete.** Every actor has a specification, a weighted check family, an ordered map,
executable fixtures, and goldens — though the CLI fixtures grade nothing until `expected/` is populated:

| Actor | Spec | Checks | Ordered map | Fixtures |
| --- | --- | --- | --- | --- |
| Wheel producer | Python suite | 40 | Production Map | 10 build variants |
| CLI producer | CLI suite | 43 | Production Map (CLI) | `greetctl`, 4 arms |
| Surface | Discovery Contract | 18 | Contract §3 | shared |
| Consumer | Consumer Conformance | 17 | Consumption Map | shared + 16 A-goldens |
| Binding | Agent Integration Contract | (scored via consumer) | Contract §3 | 8 E-goldens |

## Recent decisions

- **0.5.0 absorbed work that arrived after it was numbered.** When the maintainer asked to add the Production Map to
  0.4.1, the answer was to renumber the release, not to refuse the work. Same again when the CLI gaps were closed
  after the first 0.5.0 commit: "we want to do this in 0.5.0". The version is a description of content, not a budget.
- **A CLI fixture needs a release _history_, not just variants.** Five `MIRI-CLI` checks (14 of 100 weight) are
  claims about what the binary _used to do_. `greetctl` therefore ships `miri-1.0.0` and `miri-1.1.0` as two arms of
  the same tool. This is the one structural difference from the wheel fixtures.
- **Goldens are authored from the spec, never captured from an implementation** — which is what keeps a binding's
  author from also being the author of its acceptance criteria.
- **A negative assertion is not a discriminating test.** `A13` asserts only that output does not echo the attention
  bid, which a consumer that never fires satisfies trivially. `E3` pairs a required _positive_ envelope on the arm
  carrying the bid with a required _absent_ shape on the control. Neither arm decides it alone.
- **Not-applicable is not a pass**, applied again to `MIRI-CONSUMER-041`: a conditional check whose condition does
  not hold leaves _both_ numerator and denominator. Demoting it to SHOULD would have kept the vacuity and merely
  weighted it less.

## The recurring defect: the vacuous pass

A check that tests the _form_ of a behavior without testing that the behavior _occurs_. Four found in one cycle —
`MIRI-CLI-013`, `034`, `022`, and `MIRI-CONSUMER-041`. Three of the four were CLI, and all three were found by hand
while dogfooding a real tool, because until 0.5.0 no CLI fixture existed. The consumer one surfaced the moment
fixture work touched it. That asymmetry is the argument for fixtures, not a coincidence.

Watch for it in any newly authored check. Four instances in freshly written checks suggests a drafting habit rather
than bad luck.

## Next steps

Immediate:

1. **Open the PR** for `phase-0.4.1` → `main`. Note two commits share a subject line (`794d043`, `fce0a16`); they
   are genuinely different, just a reused message.
2. **Tell miri-py the event goldens exist.** They were blocked on them. The message must also say 0.5.0 is landing
   and they should re-pin — an earlier message claimed two fixes were committed when they were on an unpushed local
   branch, and they correctly found nothing.

Then, in rough order of value:

- **The generator profile.** [Discovery Contract §7](../standards/consumption/discovery-contract.md) binds the
  harness-configuration generator with four normative rules and no suite scores them. Consumer Conformance §4 calls
  this bounded and deliberate: the rules are normative today, what is missing is the suite. Largest named hole.
- **`MIRI-CLI-004`'s converse** — a subcommand reachable in `--help` but absent from `--describe`. Decidable,
  unchecked, recorded in CLI Production Map §4. Needs a new ID and a weight redistribution across 43 checks.
- **Point `A13` at `E3`** rather than leaving its weaker standalone assertion to carry the case.
- **The clause-to-check audit** — roughly 196 normative clauses against 89 `fires_when` clauses. Where more vacuous
  passes are likely hiding.
- **Go and Rust** remain scope-sketch READMEs.

## The open question that matters most

**Nothing detects metadata that is never read.** Three checks come near it (`MIRI-CONSUMER-022`, `050`,
`MIRI-SURFACE-040`) and none tests it. This is the failure the whole standard exists to prevent — a conformant
producer, surface and consumer all green while the metadata goes untouched — and it is what the Agent Integration
Contract was written to close but cannot itself verify. A binding that a user disables because it is noisy returns
the system to exactly that state, which §4.1 names explicitly: the failure is reachable through its own remedy.

## Working-tree note

`examples/fixtures/build/` and `examples/fixtures/cli/build/` are generated and gitignored; rebuild with
`make fixtures` and `make cli-fixtures`. `.generated/` is the local site render. `make check` runs everything CI
runs except the link check and the miri score gate.
