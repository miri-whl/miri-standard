# Active Context

_Last updated: 2026-09-26._

## Current focus

**0.7.3 on `phase-0.7.3` — two commits, pushed, no PR yet.** 0.7.2 released 2026-09-24 with both artifacts and
a working index entry; the live site shows 0.7.2.

0.7.3 answers two miri-py findings and withdraws a document.

**Scoring.** They implemented `scoring-v2`, emitted a non-integral `effective_denominator`, and reported the two
schemas as contradictory. The blocker was real and the diagnosis one field off: the score denominator is the sum
of integer weights and never goes fractional; the NUMERATOR does, and `lint-report-v1` had no field for it, so a
report could not be recomputed by its reader. `scores.earned` closes it. The confusion was ours — `scoring-v2`
used "denominator" for two different quantities. Their preferred fix (widen the field to `number`) was declined:
two scores are comparable only alongside their denominators. They then hit a tier above the obligation that a run
cannot assess, and that is now settled from a rule v2 already stated — a tier is live if declared, not parked,
**and assessable by this run** — with `outcomes[].tiers_unassessable` required when one drops.

**The graph is gone.** `api-graph.json` and `MIRI-PY-010` are withdrawn. The document carried a name and a kind
per node: no signature, no identity surviving a rename, no way to see a symbol change shape. Of 270 measured API
updates, 128 were modifications, which a name-keyed graph cannot detect at all. `MIRI-PY-045` takes its 1 weight
as a SHOULD — a precomputed index under `.dist-info/`, declared in `sdk-manifest.json` `code_index`, format named
(SCIP) and producer not. Wheel Extensions §5.5 carries the case (42.55% to 66.36% executable with structured API
documentation) and its limits in the same breath. The Discovery Contract's `graph` operation now reads the
declared index and is optional, which is where a format the consumer cannot read belongs: a surface is a server,
so it affords the decoder and answers in JSON.

**Found by rendering the site:** the published check index had shown `MIRI-PY-016` as a live MUST worth 2 points
since 0.6.0. Withdrawn rows are now marked and carry no level, severity or weight.

**Three lessons carried forward, all still live:**

- _The sharpest claim in a document is the least verified._ Four of the last five miri-py findings were cases our
  own artifact could not exercise — every tiered check on their wheel earns its top tier, so the tier divergence
  only appears on the wheels a linter exists to judge.
- _A gate that cannot read its own repository's convention manufactures work rather than finding it._
- _A claim about coverage that nothing verifies is the defect we keep finding in other people's checks._
  `make check` claimed to run everything CI runs and omitted three steps.

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

1. **Open the PR for `phase-0.7.3`, merge, then tag promptly.** Two commits, pushed, `make check` green.
   `website/site.yaml` is at 0.7.3, so the site advertises artifacts that do not exist from the moment main
   moves — minutes, not hours, as 0.7.1 showed.
2. **Answer miri-py's SCIP proposal.** 359 lines, three questions in its §9, and 0.7.3 decides all three —
   no to SCIP as the wheel's consumer-facing format, yes as the `graph` operation's source, and `MIRI-PY-043`
   fixed by requiring `signature` rather than by respecification. Without the reply they have to infer the
   decisions from a changelog. The only substantive thing left in this release.
3. **Send the three earlier replies** if they have not gone: the four-blockers response, the
   integrity-semantics note, and the references response, which asks them to relabel their fix card from
   "Defined by" to "References".
4. **`MIRI-PY-043` passes vacuously when `signature` is absent** — a MUST comparing "signature-bearing fields"
   against a field `sdk-manifest-v1` makes optional and the sample SDK never populates. This is why their delta
   detection degenerated to key-set diffing. Requiring it newly fails conforming producers, so it is 0.8.0 with
   the sample SDK updated in the same change. **The next real gap.**
5. **Grade tiers in the fixture harness.** `tier_earned`, `earned` and `tiers_unassessable`, so a golden can
   assert them. Offered to miri-py, who offered to draft the arms; arms 3 and 4 (a tier assessable-and-unreached,
   and a tier unassessable) are the ones that would have caught the ambiguity they just hit.
6. **Decide on a predicate-and-builder check.** `MIRI-PY-005` documents that it verifies provenance is
   _published_, not what it says. Decidable; whether it earns weight is not decided.
7. **The generator profile** — Discovery Contract §7's four security MUSTs with no check family. Still the
   largest named hole in the standard itself, and still unstarted.
8. **Decide on PyPI.** `pkg:pypi/miri-standard-checks` is unclaimed, so `pip install miri-standard-checks` 404s
   and every consumer hardcodes the index URL.

Known and unfixed: `MIRI-PY-023` and `033` carry 4 weight that is not independently reachable, because
`lifecycle-v1` already enforces every clause they state — recorded in the fixtures README. `MIRI-PY-026`
checks that a `vex` URL serves a VEX document but not that the document says anything about _this_ artifact,
which is the vacuous-pass shape and needs CycloneDX's linkage vocabulary verified before a clause is written.
The wheel is not byte-reproducible across setuptools versions (unpinned), which is why a released index hash
must come from the release rather than a rebuild; the fixture pack is reproducible, after pinning gzip's
header mtime. 0.7.0's `content_sha256` is permanently unverifiable and its release notes say so.

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
