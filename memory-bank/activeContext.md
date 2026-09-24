# Active Context

_Last updated: 2026-09-23._

## Current focus

**0.7.2 on `phase-0.7.2` — uncommitted, awaiting the maintainer's review.** Nothing pushed, no PR.

**Two releases now exist, and the Downloads links work.** 0.7.0 was tagged 2026-09-21 and 0.7.1 on 2026-09-22;
both carry the definitions wheel, and 0.7.1 adds the fixture pack. The published index resolves
`miri-standard-checks` by name and carries the wheel's sha256, verified by installing from it into a clean venv.
The line in every earlier version of this file about zero tags and 404ing links is no longer true.

What 0.7.1 closed, all found by miri-py vendoring the wheel with no checkout: `content_sha256` hashed the
build's staging tree rather than the installed package, so no consumer could reproduce it by any encoding; the
manifest could not name the checklist revision it implements; `checks/consumption/` held two families on two
100-point scales with the id prefix as the only discriminator; and the fixture suites shipped nowhere. The
manifest now carries a `families` block, the package carries `verify_content()`, and the release attaches
`miri-standard-fixtures-<version>.tar.gz`.

What 0.7.2 carries, uncommitted: 31 references added across 26 checks, closing every numbered document named
in check prose but absent from that check's `references` — 21 PEPs miri-py reported, 6 RFCs, CycloneDX and
SPDX on the two checks that require those formats, and SLSA on `MIRI-PY-005`. `check_references.py` gates the
rule for PEPs and RFCs. `MIRI-PY-001` and `MIRI-PY-005` now state what passing them does **not** establish:
RECORD is carried inside the archive it describes, and PEP 740 is how an attestation is distributed rather
than what it says.

**SLSA and in-toto had appeared nowhere in 123 definitions.** The standard required provenance, ships
provenance on its own releases, and had never named the format its provenance is in.

**Three lessons carried forward, all still live:**

- _A frozen artifact has no test that it stayed frozen._ `check-v1` drifted silently; `scoring-v1` was frozen
  by textual edit after a first pass reformatted the whole file.
- _The sharpest claim in a document is the least verified._ Our own side gets checked thoroughly and then
  universals about someone else's repository are written from it.
- _A gate that cannot read its own repository's convention manufactures work rather than finding it._ The new
  reference gate's first draft matched only one of the two RFC URL spellings this repo uses, and reported two
  citations as missing that had been there all along.

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

1. **Review `phase-0.7.2`, then commit and tag.** Uncommitted; `make check` green; the wheel builds at
   `0.7.2.dev0`. `website/site.yaml` is already at 0.7.2, so the site advertises it the moment main moves —
   tag promptly after merge, as the 0.7.1 round showed.
2. **Send miri-py the three replies** — the four-blockers response, the integrity-semantics note, and the
   references response, which asks them to relabel their fix card from "Defined by" to "References" because
   four of the 21 PEPs are tooling instructions or prior art rather than the authority for the rule.
3. **Decide on a predicate-and-builder check.** `MIRI-PY-005` now documents that it verifies provenance is
   _published_, not what it says. A check on the SLSA predicate type and a non-empty `builder.id` is
   decidable; whether it earns weight is not decided.
4. **The generator profile** — Discovery Contract §7's four security MUSTs with no check family. Still the
   largest named hole in the standard itself, and still unstarted.
5. **Decide on PyPI.** `pkg:pypi/miri-standard-checks` is unclaimed, so `pip install miri-standard-checks`
   404s and every consumer hardcodes the index URL. Needs the name claimed and trusted publishing configured.

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
