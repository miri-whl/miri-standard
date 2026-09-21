# Active Context

_Last updated: 2026-09-21._

## Current focus

**0.7.0 on `phase-0.7-stage-1` — committed, not pushed, no PR.** 0.6.0 merged to `main` as `a769e50`; the wheel,
the Downloads page and the PEP 503 index merged as `297c324`. Still **zero tags**, so the release job has never
run and every link on the Downloads page 404s.

What 0.7.0 carries: the **greetlib wheel fixtures** — nine arms, seven goldens, `examples/fixtures/python/` — which
gave the `MIRI-PY` family its first test material (0/43 checks with material to 18/43, 0 to 50 weight; untested
weight across all families 237 of 400 to 187, counting every active check
any golden names). `lint-report-v1` gained `evidence`, so attribution is gradeable from a
conforming report. `scoring-v2.json` supersedes v1 for the tier arithmetic. `MIRI-PY-009` gained an anti-vacuity
clause and the `previous-release` capability it needs. The definitions wheel conforms (98 of 53.0, zero MUST
failures) and the release job gates on it.

**Five adversarial panels ran against this branch and found more than any round this session.** The worst was
about honesty rather than code: 0.6.0's `scoring-v1` DID specify the tier rule (a parked T2's share is parked in
T1), and a draft deleted that sentence while asserting the schema had never said which reading was right — framing
the adoption of the reference implementation's arithmetic as a clarification. Three claims about miri-py were also
false, and the pattern behind them is the lesson: **the sharpest claim in a document was the least verified.** Our
own side was checked thoroughly and universals about someone else's repository were written from it.

**Three lessons carried forward from 0.6.0, all still live:**

- _A frozen artifact has no test that it stayed frozen._ `check-v1` drifted silently; `scoring-v1` was frozen by
  textual edit this time after a first pass reformatted the whole file.
- _"Everything already complies" is not "nothing was added."_
- _Gate on the schema's own coupling, never on a vendor field, and read your own rule forwards._

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

1. **Push `phase-0.7-stage-1` and open the PR.** `make check` green; four commits.
2. **Tag.** Zero tags exist. Nothing has ever been built by the release job.
3. **Send miri-py the dogfooding report** — six findings, three of which correct earlier drafts of the same
   document, plus the `compare`-operator response awaiting their three answers.
4. **The generator profile** — Discovery Contract §7's four security MUSTs with no check family. The largest named
   hole in the standard itself, and unstarted.

Known and unfixed: `MIRI-PY-023` and `033` carry 4 weight that is not independently reachable, because
`lifecycle-v1` already enforces every clause they state — recorded in the fixtures README. The wheel is not
reproducible across setuptools versions (unpinned). `pkg:pypi/miri-standard-checks` is unclaimed on PyPI.

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
