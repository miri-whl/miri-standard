# Active Context

_Last updated: 2026-09-18._

## Current focus

**0.6.0 on `phase-0.6` — BREAKING, committed, not yet pushed, no PR.** 0.5.0 merged to `main` as `6f4493c` on
2026-09-17 (PR #13) and is still untagged; nothing machine-readable depends on the tag since miri-py pins the SHA.

What 0.6.0 carries so far: `check-v3.json` (tiers, `conformance_tier`, the pure-function rule), `changelog-v1.json`,
`scoring-v1` tier schedule with T2 parked, `lint-report` `tier_earned`; four new checks `MIRI-PY-041`–`044` (the
staleness classes); tier tables on `007` `014` `015` `017` `037`; `016` withdrawn into `014`'s T3; twelve weight
changes; checklist stamp `0.3-draft`, 43 active. The design was settled with miri-py in
`substance-and-freshness-answers-1.md` — Q1 (conformance at a named tier, default T1) is the load-bearing answer.

**The three items promised in the merged interop reply are now written**: the five driver-semantics clauses live in
`scoring-v1` `conformance.coverage`, every one `const: true`, with `not_implemented` + a required `blocker` in
`lint-report-v1`; the conformance kernel's two schemas are recorded under `reference/conformance-kernel/` (reference,
not normative, pinned to miri-py `afc51324`, with the promotion test); the fixture recipe is normative with
`examples/fixtures/checksums.json` hashing every _input_ and `validate_fixtures.py` failing on drift — wheel bytes
deliberately not asserted, since the build is not reproducible. From miri-py, still: tier tables for
cli/surface/consumer and the multi-invocation operator draft.

**Coverage remains the biggest reality**: 361 of 400 weight has no test material and `MIRI-PY` is at zero; the four
new checks and every tier clause add to that number. miri-py's rule corpus (51 rules) is the largest body of
executable verification that exists for this standard.

**Three lessons from the 0.6.0 cycle, each caught late:**

- _A frozen artifact has no test that it stayed frozen._ `check-v1.json` had been silently rewritten to v2 semantics
  under a title saying "retained unchanged"; found by diffing against `main`, not by any gate. v2 was frozen by
  restoring from `main` and verifying programmatically. The same instruction (`git diff 0.5.0 --`) sits in both
  descriptions and is unverifiable until a tag exists.
- _"Everything already complies" is not "nothing was added."_ The pure-function rule was filed as a 0.5.1
  clarification; it is a new MUST that narrows what a check may be, so it is 0.6.0. The branch was renamed; the
  version follows the content.
- _Gate on the schema's own coupling, never on a vendor field, and read your own rule forwards._ The CI score gate
  read `is_conforming` (defined nowhere), then, rewritten, rejected `undetermined` — which the schema says is not
  non-conformance. It went red on miri-py's first 0.5.0-shaped report with nothing wrong.

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

1. **Push `phase-0.6` and open the PR.** `make check` is green; the site builds with the Tiers block.
2. **Push the #15 fix** (`proposal/substance-and-freshness-0.6`, one commit: headings and three dictionary words)
   so the proposal can merge. The remote ref still carries the old `-0.5.1` name; the PR is retitled.
3. **Tell miri-py the three rulings** they asked back for are decided and landed: Q1 design accepted as proposed; T2
   activation at 25 wheels from 10 independent publishers; `007` gains the T1 clause. Send the `main` SHA after merge.
4. **Sample SDK ships no `changelog.json`** and has no previous release, so `041`–`044` are excluded for it; a fixture
   with a two-release history is what would exercise them, as `greetctl` does for the CLI.

Then, unchanged in value: the generator profile (Discovery Contract §7, four rules, no suite); `MIRI-CLI-004`'s
converse; pointing `A13` at `E3`; the clause-to-check audit; Go and Rust.

## The open question that matters most

**Nothing detects metadata that is never read.** Three checks come near it (`MIRI-CONSUMER-022`, `050`,
`MIRI-SURFACE-040`) and none tests it. This is the failure the whole standard exists to prevent — a conformant
producer, surface and consumer all green while the metadata goes untouched — and it is what the Agent Integration
Contract was written to close but cannot itself verify. A binding that a user disables because it is noisy returns
the system to exactly that state, which §4.1 names explicitly: the failure is reachable through its own remedy.

## Working-tree note

`examples/fixtures/build/` and `examples/fixtures/cli/build/` are generated and gitignored; rebuild with
`make fixtures` and `make cli-fixtures`. `.generated/` is the local site render. `make check` runs everything CI
runs except the miri score gate — the link check is now included, and `make links` now fails on a dead link (it
used `find -exec`, which returned find's status, so it had never failed). `.markdownlintignore` is inert under cli2;
`memory-bank/` and `.claude/` are linted and link-checked, excluded from cspell only.
