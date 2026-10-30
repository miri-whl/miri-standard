# Changelog

All notable changes to the Miri Standard are recorded here.

Versions follow the policy in [standards/README.md](standards/README.md#versioning): a **major** version marks a
breaking change, a **minor** version a backward-compatible addition, and a **patch** version bug fixes and
clarifications only. That policy is a contract with implementers. A reader should be able to see `0.3.1` and know
it contains no additions without having to check.

While the major version is 0 the standard is in initial development, so a **minor** bump may carry a breaking
change ([Semantic Versioning §4](https://semver.org/#spec-item-4)). Where one does, the entry says **BREAKING** in
its first line and names what breaks. From 1.0.0 onward a breaking change takes a major bump.

## Unreleased

**For implementers:** No check changed ID, level, weight, category or `fires_when`. The Discovery Contract moves to
0.4.0-draft to record the §3.8 additions that shipped in 0.7.3. One consumption golden (`E2`) has a corrected
read-order, and its expected response is unchanged.

### Fixed

- **Errata in the consumption specs.** Each correction makes the text agree with a rule stated elsewhere. No RFC 2119
  keyword was added or removed.
  - Discovery Contract: §3.2.3 named `sdk-manifest.json` twice; §10 called Consumer Conformance "forthcoming"; the
    §4.1 `package` row now names the `UNAUTHENTICATED` exception from §7.1; two implementation-status notes in §4.2
    and §6.3 were out of date and are removed. The abstract names the three programs the contract binds.
  - Consumption Map: the §3 routing diagram showed the wrong first read for tasks 3.1, 3.2 and 3.3; §6 said the
    consumer checks "will be numbered"; the §5 table cited §6 for `graph`, which is §3.8; "Three rules" headed six.
  - Agent Integration Contract: §3.1 still argued for two REQUIRED kinds; the §4.6 worked example now follows
    Consumption Map §3.5 step by step, and golden `E2` matches it; §6.1 and §7 lines written for 0.4.0 now name
    `dependency.version_change` where they meant it.
  - Consumer Conformance: the §4 diagram said 15 checks (there are 18). Surface Conformance: the Discovery Contract
    places obligations on three programs, and its abstract said two.
  - Production Map (Python): it counted forty checks. It now counts 45 definitions, 43 active, recomputes the
    capability arithmetic, names all four `previous-release` checks (`009`, `030`, `034`, `043`) and places
    `MIRI-PY-045` in Stage 2. The Python linter checklist names the same four.
  - Check definitions: `MIRI-SURFACE-012` counted fifteen consumer checks (eighteen); `MIRI-SURFACE-030`'s
    suggested fix said `document` reports `cap` (it reports `max_bytes`).
- **The site.** Spec references on the 36 consumer and surface check pages returned 404; they now open the rendered
  spec. Check pages named schema `check-v1` while every definition declares `check-v3`. Withdrawn checks `MIRI-PY-010`
  and `MIRI-PY-016` rendered as live and now carry a withdrawn notice and weight 0. The home page and the Python index
  counted the two withdrawn checks. Category totals repeated on the index pages and now sum to 100. Wrapped list
  items rendered as one bullet per source line. The sidebar listed two shipped schemas as planned. The origin page's
  `lifecycle.json` example failed `lifecycle-v1.json`, and the page said version 0.1. Why-consumption predated
  Surface Conformance and the eleven-variant fixture set.

### Changed

- **Writing pass across the published text.** The specs, the changelog, the glossary, the docs pages and the prose
  fields of all 124 check definitions lost their em dashes, banned words and sealing sentences under
  `WRITING-RULES.md`. Long sentences were split and revision history ("an earlier version said…") left the normative
  text; the earlier wording stays in the repository history. `fires_when` clauses and code blocks are untouched.
- **Honest degradation** stays as a defined term (the `MIRI-CONSUMER-001` to `003` category) and has a glossary entry,
  as does **blast radius**. `tools/check_writing.py` allows the phrase and flags every other use of the word. It now
  also catches a spaced hyphen used as a dash.
- **The home page** opens with a "Start here" list by role. Every page has a description and link-preview tags, and
  the site publishes `sitemap.xml`, `robots.txt` and a 404 page.

## 0.7.4 (2026-10-18)

**For implementers:** No check changed level, weight or intent. Checks `006`, `014`, `015`, `037` and `038` now pass
only on a file the installed package can open, and a linter that tests archive presence must change.

### Fixed

- **"Reachability" is now stated once, normatively, instead of being re-derived by every implementer.** Five checks and
  one tier clause require a file to live inside an installed import package: `006`, `014`, `015`, `037`, `038`, and
  `014`'s T3 clause. Of all 45 definitions, only `MIRI-PY-006` contained the words `import package`. The clause in the
  checklist preamble now governs all six.

  **Two checks said the opposite.** `MIRI-PY-014` required `examples/quickstart.py` *"present in the built wheel"* and
  fired when it was *"absent from the built wheel"*. Both phrases describe archive presence, the reading the new
  clause excludes. An implementer who followed that text as written produced the defect. Both clauses are corrected.

  Reported by the miri-py team. They implemented the defect twice, three weeks apart, and the second time was in
  `MIRI-PY-006`, the one check whose text already carried the rule. On two wheels from one source tree, with
  byte-identical Python and file placement the only difference, the checks separating the working wheel from the broken
  one went from 1 to 9 once they scoped correctly.

  A wheel routing `examples/` or `agent-metadata/` through the PEP 427 `.data` scheme installs those files to
  `<venv>/examples/`, detached from the package. `importlib.resources` cannot reach them there. The files exist and are
  listed in `RECORD`, and nothing that needs them can open them.

- **Remediation text must tell an absent file from an unreachable one.** The two have opposite fixes (write the file, or
  move the one you already wrote), and a check failing on reachability SHOULD name the path the file shipped at.
  miri-py's linter gave the right verdict with the wrong diagnosis: a panel found its fix card telling a producer who
  *had* written a quickstart to write another.

- **`docs/glossary.md` gains Reachable** and separates it from *present*, the near neighbor whose confusion caused the
  defect above.

- **A dead citation.** Both links to `scanrook.io` in `update-and-vulnerability-signaling.md` had stopped resolving; the
  host returns 502 at the root. They now cite NIST IR 7696, *CPE Name Matching Specification 2.3*, and the sentence is
  reworded: the old link supported CPE matching being *unreliable*, and the NIST document specifies how matching
  *works*. The unreliability claim now rests on the mechanism and on `cve-bin-tool`'s documented byte-signature
  fallback, already cited beside it.

- **A release job that would publish a tag from any branch.** 0.7.3 was first tagged on a feature branch and published
  as a real release (wheel, fixture pack, hash in the index) built from a tree `main` did not contain, including work
  from this version that had not been reviewed. Correcting it meant deleting a published artifact ten minutes old and
  publishing different bytes at the same version. That is the same-version replacement that `MIRI-CONSUMER-052` tells
  consumers to distrust. The wheel at digest `7d5acd05…` no longer resolves; `0.7.3` is now `235591bb…`, built from
  `f97b547` on `main`. `publish-checks.yml` now refuses a tag that `main` does not contain.

### Changed

- **An editorial pass removed manufactured closure from the published site.** A panel read the three visitor-facing
  pages, then all 143, then `agent-integration-contract` alone, looking for tidy sentences that seal a section without
  making a further claim. It removed *"That is the whole of it"*, *"That gap is not cosmetic"*, *"It promises no magic
  beyond that"* and the epigram *"Silence is the violation, not the absence of findings"*. It also removed five bold
  topic-sentence openers, two phrases praising the writing instead of making a claim, and 14 em dashes standing in for a
  colon or a full stop. The removals were in the hand-written narrative documents, a quarter of them in
  `agent-integration-contract`.

  The landing page closed by mirroring the *Beggars in Spain* quote (*"gaps where information ought to go"* → *"the
  standard fills the gaps"*) and now states what a wheel omits; `origin-story` had repeated that line nearly verbatim
  one click away. No meaning changed.

## 0.7.3 (2026-10-18)

**For implementers:** `MIRI-PY-010` is withdrawn and its point moves to the new `MIRI-PY-045`. Reports gain
`scores.earned` and `outcomes[].tiers_unassessable`, and an unassessable tier is no longer live. Resync and rescore.

**Rebuilt the same day.** The first 0.7.3 wheel, digest `7d5acd05…`, came from a feature branch and no longer resolves.
The current wheel is `235591bb…`, built from `f97b547` on `main`; if you downloaded 0.7.3 early, download it again.

`api-graph.json` is withdrawn, and `MIRI-PY-010` with it. A wheel need not ship the document and a consumer must not
expect it; the schema stays published and frozen so anything already validating against it still can.

**This patch carries a withdrawal and four additions, and the versioning policy would place them in a minor.** The
additions are `MIRI-PY-045`, the `sdk-manifest.json` field `code_index`, Miri Wheel Extensions §5.5, and the Discovery
Contract's optional `graph` behavior. Two fixes below also add report fields (`scores.earned` and
`outcomes[].tiers_unassessable`). The withdrawn check is a SHOULD worth 1 point, and its weight moved to `MIRI-PY-045`
in the same change. No MUST moved and no wheel becomes invalid: `code_index` is optional, and carrying `api-graph.json`
does not make a wheel non-conforming. The largest effect on any published score is one point.

### Removed

- **`api-graph.json`, and `MIRI-PY-010` (SHOULD, 1 point) which validated it.** The document carried a name and a kind
  per node and nothing else. It had no signature, no position, no identity surviving a rename, and no way to tell
  whether a symbol **changed shape** between releases. It was optional and only that one check read it; the delta checks
  that need structure (`030`, `043`, `044`) read `sdk-manifest.json` `api_index` instead. Extending it would have meant
  rebuilding what a published format already specifies.

  Agent Metadata §4.5 keeps its heading so §4.6 and §4.7 do not renumber and every citation still resolves.

### Added

- **`MIRI-PY-045`: a precomputed code index, declared (SHOULD, 1 point).** It takes the withdrawn check's weight, and
  the target still sums to exactly 100 with Agent Metadata Core still at 24. A wheel SHOULD carry an index under
  `.dist-info/`, beside the SBOM documents PEP 770 puts there, and declare its path and format in `sdk-manifest.json`
  `code_index`. It is a SHOULD and not a MUST because no toolchain produces these for wheels today. A MUST whose
  expected result is near-universal non-compliance is one nobody treats as real.

  **The standard names the format and not the producer**, as it names the wheel format and not the build backend. SCIP
  is a published format with a protobuf schema, several indexers and existing consumers. Of the two Python indexers
  measured, one is mature and needs npm; the other installs with pip and was two days old.

- **Miri Wheel Extensions §5.5: why a declared code index helps.** An agent writes against the API it was trained on.
  Across 270 real API updates in eight Python libraries, 25.36% of generations ignored the update, 16.4% used only the
  removed API, and 12.3% mixed old and new APIs in one file. Supplying structured API documentation raised the share of
  generated code that **executes from 42.55% to 66.36%**, the largest single intervention measured, against 2.34 points
  for chain-of-thought prompting. That study supplied the documentation by hand in a prompt, and carrying it in the
  wheel means nobody has to.

  **128 of those 270 updates were modifications.** A name-keyed graph cannot see that class, and that class produces the
  mixed-API failure: the name still resolves and the call is wrong.

  §5.5 also states the limits. Read whole, an index costs *more* than reading the source; queried for one symbol, it is
  22x cheaper. The benefit depends on the consumer having a decoder, and for that reason `code_index` declares the
  format while `api_index` stays the readable surface for everyone else. It is unsettled which reduction is safe
  (stripping all occurrences may break readers that locate definitions through them). Cross-indexer symbol stability is
  untested. `code_index.reduction` and `produced_by` record both for later measurement.

- **`sdk-manifest.json` gains `code_index`**: `path` (must be under `.dist-info/`), `format` (a closed set of one), and
  optional `reduction` and `produced_by`. Because the field is optional, no existing wheel becomes invalid.

- **The Discovery Contract's `graph` operation now reads the declared index**, and is explicitly optional. Where no
  `code_index` is declared, a surface returns `present: false` with a reason, as for any absent document. A surface
  never synthesizes the graph from `api_index`. A name-keyed index cannot express an edge, and inventing one would put a
  guess behind a field a consumer uses to plan a change.

  **A surface is the right place for a format the consumer cannot read.** A surface is a server that can afford a
  protobuf decoder and answers in the envelope's JSON, and the consumer keeps a JSON-only contract. A consumer holding
  only the wheel still reads `api_index` and loses nothing it had. A consumer with a surface also gets the relations
  between symbols, now with signatures: an edge can say `transfer` still exists and takes a third argument.

  The Consumption Map records the withdrawal against its own element→task rule. `api-graph.json` had survived a review
  by being given a consumption role, and was withdrawn once a published index could serve that role.

Proposed by miri-py. They measured their own graph at 438 nodes carrying `{"type": "class"}` per node, priced three
index reductions, and published a negative result about token efficiency beside the positive one about correctness. We
declined the part they asked for (SCIP as the wheel's consumer-facing format) and took the shape their own §8 identified
as sound.

### Fixed

- **The site presented withdrawn checks as live.** `MIRI-PY-016` had rendered in the check index as a MUST worth 2
  points since 0.6.0. A definition keeps the level and weight it had when withdrawn. The index printed them without
  qualification, and a reader of the published site saw a current obligation. Withdrawn rows now carry a
  `withdrawn <version>` badge, show dashes for level, severity and weight, and recede visually. The page and the ID
  stay, because a report naming a withdrawn check must still resolve to a definition.

- **`scoring-v2` specified a numerator `lint-report-v1` had no field for.** A tiered check earns
  `weight × (shares up to tier_earned) ÷ (shares of its live tiers)`, and the sum at full precision is fractional.
  `scores` carried `conformance` (a rounded percentage) and `effective_denominator` (an integer), and nothing for the
  sum those were computed from. `scoring-v2` asks a consumer to be able to recompute the score, and a reader given `79`
  and `17` could not. `scores.earned` closes it: MUST be present when a tiered check contributed, optional otherwise.

  **`effective_denominator` stays an integer, deliberately.** miri-py emitted `56.57` there, found that it failed the
  wire schema, and reported the two schemas as contradictory. That schema uses the word *denominator* for two
  different things. The **share** denominator is one check's live shares; the **score** denominator is the sum of the
  integer weights of every check that applied, and tier arithmetic never touches it. Widening the field to `number`
  would have encoded the conflation and made two linters' denominators incomparable. The sentence in `scoring-v2` now
  distinguishes them.

- **A tier the run cannot assess is not live for that run.** miri-py raised this right after implementing the fix above.
  Take a check whose obligation was assessed but whose tier *above* it could not be (T3 needing a capability the linter
  lacks). Three readings give an integral denominator, and they disagree. `scoring-v2` now settles it from a rule it
  already stated: a tier is live if it is declared, is not parked, **and is assessable by this run**. An unassessable
  tier therefore leaves the check's share denominator the same way a parked tier does:

  - a tier **at or below** `conformance_tier` that cannot be assessed means the check's own obligation went unassessed:
    the **check** forfeits, never passes, and for a MUST withdraws the grade;
  - a tier **above** `conformance_tier` that cannot be assessed drops from the live set, and a check earning the highest
    tier that *was* live takes full weight with no deduction for a ceiling the run could not reach.

  Neither case charges the artifact for the linter's environment. `forfeited_must_withdraws_grade` already forbids that,
  and a forfeit is no discount. `outcomes[].tiers_unassessable` is now required when a tier was dropped. A percentage
  over a reduced live set is comparable to one over the full set only when the reader can see which tiers left it.

  **This agrees with the reading miri-py chose on their wheel and disagrees with it as a rule.** Their reading (the
  check applied, so it takes full weight) gives the same number where the missing tier was unassessable. It over-credits
  every tiered check that failed to reach a tier that *was* assessable: weight 5 earning T1 with T3 available scores 5.0
  under their rule and 3.5714 under this one. `example-lies-1.1.0` was built to expose that second case. miri-py shipped
  the v1 fold instead of a report that fails the published schema, and flagged the choice when they made it. Their own
  wheel is unaffected because every tiered check on it earns its top tier.

## 0.7.2 (2026-09-24)

**For implementers:** No check changed level, weight or intent, and no schema changed. Resync for new `references` and
two clarifications (`MIRI-PY-001`, `MIRI-PY-005`); a linter correct today stays correct.

### Added

- **The tier boundary is demonstrated by an artifact for the first time.** 0.6.0 shipped tiered checks with the rule
  that *the MUST boundary sits at the lie, not at thinness*: a check earns weight on a schedule and fails only below its
  `conformance_tier`. Nothing in the suite distinguished the two cases. `example-lies-1.1.0`'s `quickstart.py` calls
  `greetlib.shout()`, a symbol no release's `api_index` carries. The file is present and compiles, and the arm **earns
  T0** and fails T1: a MUST failure for `MIRI-PY-014`, weight 5. Its control is `conforming-1.1.0`, whose example is
  **thin, accurate and conforming**, reaching T1 and no higher. A linter reporting both has implemented
  thinness-as-failure. Tiers were introduced to stop that.

  The fixtures README states what is still uncovered: tier *earning* above the boundary. No arm reaches T3, and the
  goldens grade pass/fail instead of `tier_earned`. Three of the five tiered checks have no tier material at all.

- **Four native fixture arms, and `MIRI-PY-024` is falsifiable for the first time.** It is a MUST worth 4 weight, and it
  had never been *applicable* to anything in the suite. The check is conditional on the wheel carrying a native
  component, and all eight arms were pure Python. It was excluded instead of passed. `native-sbom` bundles a stub `.so`
  and a vendored `libs/libgreet-2.1.so` and covers them in a CycloneDX document. `native-nosbom` bundles the same and
  ships no `.dist-info/sboms/`. `native-mismatch` ships a valid SBOM covering `libssl`, a library the wheel does not
  carry. `native-badpurl` covers the right library with a purl that cannot parse (`MIRI-PY-025`).

  The three goldens, `P8` through `P10`, **all pair against `native-sbom` instead of the usual control**. A
  conditional check cannot be paired against an arm that is excluded from it. The control also has to bundle the same
  library, or a linter could earn these cases by reporting on any wheel containing a `.so`. The distinguishing fact
  has to be the SBOM.

  `native-mismatch` tests clause 2, the anti-vacuity half, which a linter is most likely to skip. A linter checking
  whether `.dist-info/sboms/` is *present* passes it; only one checking whether the documents *cover the bundled
  components* fails it.

  PEP 770 puts the SBOM documents in `.dist-info/`, and that directory does not exist until the backend writes it. The
  fixture build injects them after the wheel is built. Across both additions, `MIRI-PY` coverage rose from 18/43 checks
  to 21/43 and from 50 to 60 weight; untested weight across all families fell from 187 to 177.

  The grader also rejected its own reference answer: `_honest()` seeded only the default control, and the reference
  submission was silent on `native-sbom-1.1.0`, an arm the goldens require a linter to have analysed.

### Fixed

- **Twenty-one PEPs were named in check prose and absent from that check's `references`**, across 18 checks. Reported by
  miri-py, whose fix cards render `type: external` references as a failed check's authority line. Their report embedded
  46 links, and none reached a PEP it cited by number. The standout is **PEP 702**, the document behind the entire
  deprecation-coherence group, cited by nine checks and linked from one. Every number was verified against this tree
  before accepting: 21 pairs, 18 checks, 11 distinct PEPs.

  **`check_references.py` now gates the rule**: if a check's prose names a PEP, that PEP must be reachable from its
  `references`. The gate is mechanical on purpose. The alternative, editorial judgment about which documents deserve a
  link, cannot be gated and gets a different answer from every editor. The gate is mutation-tested: removing any one
  reference fails it and names the entry to restore.

  One reference's title was the bare number `700`, and a renderer showing titles printed `700` where every sibling
  printed `PEP 700`.

- **The same gap outside the PEPs: RFCs, CycloneDX, SPDX and SLSA.** Ten more references were missing across nine
  checks. `MIRI-PY-026` requires a `vex` URL to serve "an OpenVEX document **or** a CycloneDX document containing a
  `vulnerabilities[]` analysis" and referenced only OpenVEX. A producer whose VEX is CycloneDX had no link to the
  specification they were being judged against. `MIRI-PY-024` names both SBOM formats it accepts and cited neither. Six
  checks named an RFC (9457, 9745, 822, 3339, 8259) without linking it. The gate now covers RFCs too.

  **It does not cover named bodies, deliberately.** 23 checks mention `purl` and 11 mention OSV, but most of those are
  our own field names (`identity.purl`) or an ecosystem aside rather than a citation of a specification. Gating them
  would add 34 references nobody asked for and dilute the trail the rule exists to keep. Numbered documents are gateable
  because naming the number *is* the citation, and the URL follows from the number. Named bodies stay editorial.

  The gate's first draft matched only `rfc-editor.org/rfc/rfcNNNN` and reported two RFCs on `MIRI-CLI-032` as unlinked.
  They had been linked all along as `/info/rfcNNNN/`, the spelling this repository uses.

- **`MIRI-PY-005` says what it does not reach.** It checks that an index publishes PEP 740 attestations, the
  distribution mechanism. The attestation's payload is an in-toto statement whose predicate is typically SLSA build
  provenance (`https://slsa.dev/provenance/v1`). That predicate carries `buildDefinition`, `runDetails`, and the
  `builder.id` that SLSA calls the sole determiner of the build level. **This check asks whether provenance is published
  and does not read what it says.** An attestation whose predicate asserts nothing useful about the build still
  satisfies it. Verifying the payload is a separate check that does not exist yet. The standard required provenance and
  shipped provenance without ever naming its format: SLSA and in-toto appeared nowhere in 123 definitions.

### Changed

- **RFC links moved from `rfc-editor.org` to `datatracker.ietf.org`.** CI's link check failed on RFC 9745 and RFC 8594
  with socket timeouts, on links this release did not touch. Eight rapid requests to `www.rfc-editor.org/info/rfcNNNN/`
  all timed out at 25 seconds; the identical burst against `datatracker.ietf.org/doc/html/rfcNNNN` returned in ~0.15s
  every time. The host stalls under bursts, and CI requests the same RFC from several documents in quick succession.
  Fifteen links across nine files moved, and `check_references.py` now suggests the datatracker form.
- **`make check` now runs what it claims to.** Its help said "run everything CI runs locally" and omitted `consistency`,
  `envelope` and `references`, all three CI steps in their own right. A local green could still fail CI. The reference
  gate added this release ran in CI and in nothing a contributor runs.
- **`docs/glossary.md` gains SBOM, VEX, Provenance, and Attestation versus self-consistency.** All four appear in check
  prose and in shipped feedback documents, and the glossary is where the specs' vocabulary is settled. The fourth states
  the boundary between what a conformance report may conclude from inside an artifact and what needs a root outside it.
- **`MIRI-PY-001` states the limit of a pass.** The check verifies that the archive matches `RECORD`: every file listed,
  every sha256 recomputed. It still has value, because pip has never enforced it at install time. It is **not**
  tamper-evidence. `RECORD` is carried inside the archive it describes, and whatever rewrites a file rewrites `RECORD`
  in the same motion. A report rendering a pass as "verified" or "untampered" states a verdict its evidence cannot
  support, the integrity form of the vulnerability claim this standard forbids everywhere else. Level (MUST) and weight
  (0) are unchanged and no `fires_when` clause moved; a linter implementing the check correctly today stays correct. The
  boundary now travels inside the definitions wheel.

  **`MIRI-PY-005` was considered for promotion to MUST and deliberately left at SHOULD.** PEP 740 attestations became
  automatic only under Trusted Publishing, and a MUST would mark a large share of the ecosystem non-conforming for a
  configuration choice. This standard's own definitions wheel is not on PyPI, and our only artifact could not satisfy
  that MUST. The bar is that a linter can decide it *and* near-universal non-compliance is not the expected result; it
  fails the second half today. The decision is recorded in [`standards/feedback/`](standards/feedback/README.md), and
  revisiting it needs a number.

## 0.7.1 (2026-09-22)

**For implementers:** No check, schema or specification sentence changed. `content_sha256` changed (**BREAKING** for
0.7.0 digests): verify with `verify_content()`, and read `families` instead of summing a directory.

This release fixes four blockers miri-py found by vendoring the 0.7.0 wheel and nothing else. None was visible from
inside this repository, because every tool here has the repository.

**A patch rather than a minor, deliberately.** Nothing normative moved: no check definition, no schema, no
specification sentence. The changes are to how the standard is *packaged*: a digest that described the wrong tree, a
manifest that could not name the checklist revision it implements, a directory holding two families with nothing to
tell them apart, and a corpus of fixtures that existed only in a clone. The additions are to the artifact, and the
standard is still 0.7. The **BREAKING** `content_sha256` change below is to the artifact too. The policy above allows a
breaking change in a minor while the major version is 0 and limits a patch to fixes and clarifications; this release
ships the change in a patch because no normative text moved.

### Added

- **The fixture pack, `miri-standard-fixtures-<version>.tar.gz`, attached to each release.** The wheel ships the rules
  for four check families and nothing to run them against, and a vendor could read all four and exercise two. The pack
  carries all three suites (11 consumption variants, 4 CLI arms, 9 greetlib wheels, 40 goldens) with the build recipes,
  the validators, and the attribution graders. It ships recipes instead of built artifacts, because each suite derives
  its arms from one template and asserts byte-identity across them. It carries no check definitions; outside a checkout,
  the validators resolve them from the installed wheel. The pack is byte-reproducible, with gzip's header mtime pinned:
  two builds of one tree produce one sha256.
- **`families` in the wheel's manifest**: one row per check family carrying `checklist_version`, `governing_document`,
  `directory`, `id_prefix`, `active_checks` and `weight_total`. It answers two of miri-py's four blockers. A vendor
  could report "standard 0.7.0, checks at 41aa2682" but not which checklist revision those checks implement, because the
  checklists are prose and are not packaged. The table is keyed by **family** instead of target. The four revisions are
  four values (`0.3-draft`, `0.2-draft`, `0.3.1-draft`, `0.5.0-draft`), and `checks/consumption/` holds MIRI-SURFACE and
  MIRI-CONSUMER on two separate 100-point scales. A consumer reading one directory per family sums 200 and fails a
  weight invariant. The id prefix, the only discriminator, is now declared instead of known out of band. `max(added_in)`
  gives the newest check's release, a different question.
- **`checks(family=...)`** gives the per-directory read that sums 200 an alternative that cannot.
- **`families()`, `checklist_version()`, `verify_content()` and `content_digest()` in the installed package.** A
  consumer calls the algorithm instead of reconstructing it from prose.

### Fixed

- **BREAKING: `content_sha256` did not describe the installed package, and could not be reproduced from any reading of
  its own description.** miri-py tried 36 combinations (three file sets, six length encodings, two path spellings), and
  none matched. The digest was computed over the **staging tree**. That tree carries `_agent_examples.json.src`, a build
  intermediate that `inject_dist_info()` moves into `.dist-info/` and deletes from the wheel. The field hashed one file
  the consumer never receives, and no encoding could have matched. The description's "every file in the installed
  package" was false.

  Both halves are closed. The digest now covers the installed files and nothing else, and the two length prefixes are
  both 8 bytes where they were 4 and 8, an asymmetry no reader would guess and the prose never stated.
  `verify_shipped_digest()` now recomputes the value from the **finished wheel** and fails the build if it disagrees. It
  had agreed with itself for two releases because only one computation of it existed.

  The shipped `docs/api_reference.md` now carries a worked example over two files. The same function that hashes the
  package computes it at build time, and it cannot go stale against the algorithm it documents.

  Every 0.7.0 `content_sha256` is unverifiable and stays that way. Verify that wheel against the release's SHA256SUMS or
  its build attestation; neither is affected.

### Known and open

- **`pip install miri-standard-checks` 404s.** `pkg:pypi/miri-standard-checks` is unclaimed and nothing has been
  published to PyPI. Every consumer hardcodes a versioned release URL, and an upgrade is a text edit. The published
  index works today and resolves by name and version:
  `pip install --index-url https://miri-whl.github.io/simple/ miri-standard-checks`. Publishing to PyPI proper needs the
  name claimed and trusted publishing configured.

## 0.7.0 (2026-09-21)

**For implementers:** **BREAKING.** `scoring-v2.json` renormalizes over the tiers a check declares, and every tiered
score moves; rescore. `MIRI-PY-009` gains an anti-vacuity clause, and report outcomes gain `evidence`.

`scoring-v2.json` withdraws v1's rule that a parked T2's share is parked in T1. The rest of the release is coverage. The
`MIRI-PY` family had 43 checks, 100 weight and no artifact that falsified any of them; it was the founding family and
the only one with nothing to test against. It now has nine wheels and seven goldens.

### Changed

- **BREAKING: `scoring-v2.json` supersedes `scoring-v1.json` for the tier arithmetic.** A check now earns
  `weight × (shares of its live tiers up to tier_earned) ÷ (shares of ALL its live tiers)`, renormalized over what the
  check *declares*, minus a parked T2. Under v1, `MIRI-PY-007` at weight 5 declaring only T0 and T1 earned
  `5 × (0.2 + 0.6) = 4.0`; it now earns 5.0. A check that declares only T0 and T1 has no higher tier to earn, and
  docking it for absent tiers scores it against a schedule it never claimed.

  **This is a withdrawal of a real rule.** v1's `shares` description said a parked T2's share is parked in T1, a
  complete rule producing different numbers. When the reference implementation scored a wheel 47/48 against this
  standard's 45.6/48, **45.6 was what v1 specified and 47 was the implementation diverging from it.** The draft that
  introduced the v2 field deleted the v1 sentence and asserted that no prior rule had existed. A panel caught it against
  `origin/main`.

  `scoring-v1.json` stays published and frozen at its 0.6.0 bytes. Anything that scored under it scored under a real
  rule and must still be able to cite it. v2 also states two things v1 left to the implementation: rounding is half-up,
  applied once at the end, and a **failing** tiered check contributes zero instead of its earned tier share.

### Added

- **[`examples/fixtures/python/`](examples/fixtures/python/README.md): the greetlib wheel fixtures.** Nine arms built
  from one package source: two conforming releases and seven adversarial. `conforming-1.0.0` gives `MIRI-PY-030`
  something to compare. That check compares the public surface across releases, and nothing in this repository had ever
  shipped two wheel releases of one package. It fires now, for the first time. Counting every active check named by a
  golden in any of the three suites, untested weight fell from 237 of 400 to 187, and `MIRI-PY` went from 0/43 checks
  with material to 18/43, 0 weight to 50. (Earlier drafts of this entry said 234 → 195 and 13/43, from a scan that did
  not count a golden's `also_expected` checks.)

  One arm was removed: `support-1.1.0` was written for `MIRI-PY-023` and `033`, and every way of violating those two is
  also `lifecycle-v1`-invalid. `MIRI-PY-018` fires first, and their 4 weight is not independently reachable. The suite's
  README records this, because a reader could otherwise take that weight as measuring something.
- **The definitions wheel conforms, and the release gate enforces it.** `miri-standard-checks` now ships its own
  `agent-metadata/`: `sdk-manifest.json`, `lifecycle.json`, `changelog.json`, `usage-patterns.json`, and a first-release
  `migration-guide.json` omission that is correct rather than missing. `tools/build_checks_wheel.py` writes them at
  build time from the definitions it carries, never by hand. The wheel scores 98 of an effective 53.0 with zero MUST
  failures. `publish-checks.yml` fails the release if that regresses, pinned to a fixed `MIRI_PY_REF` so the gate cannot
  move under the artifact. Dogfooding the standard on the only wheel this repository publishes found six things to tell
  miri-py, written up in [`standards/feedback/`](standards/feedback/README.md). One was a report that told the reader a
  file was *still owed* in the same run that scored its absence as correct.
- **`tools/validate_python_fixtures.py`** asserts that each arm still carries its defect and that the control carries
  none of them, the condition for a finding to be attributable. It checks against the built wheel's own metadata instead
  of a linter's opinion, and the gate holds with no linter installed. The validator is mutation-tested.
- **`tools/score_python_fixtures.py`** grades a linter against the goldens on attribution: a finding counts only if it
  names the check *and* points at the declared evidence. Its self-test rejects nine ways of gaming it, and the grader
  itself first failed two of them: evidence pooled across a case (a shotgun report scored 6/6), and findings credited
  without checking which arm they came from.

### Fixed

- **`changelog-v1.json` rejected the example this specification publishes.** It closed `additionalProperties` without
  listing `$schema`, and the *conforming* fixture arm failed `MIRI-PY-041` on a document written from §4.7 verbatim.
  `lifecycle-v1` and `api-graph-v1` already allowed the pointer; the newer schemas did not. A new schema inherits that
  drift when a convention lives in the examples instead of the schemas. Found on the fixtures' first run.
- **`MIRI-PY-009` had no anti-vacuity clause.** An all-zeros migration guide validates, and presence and schema validity
  passed a document describing no migration at all. `MIRI-PY-008` was given such a clause in the vacuous-conformance
  round, and `009` never got the equivalent. It keys on a *measured* delta: a release that changed nothing is a
  legitimate all-zeros case.
- The doc linters were scanning generated fixture arms (79 → 114 files); build trees are now excluded and gitignored.
  `opensource.org` 403s every non-browser request, and the README's MIT link joins `gnu.org` in the link-check ignore
  list, with the reason stated.

- **`lint-report-v1` outcomes gain `evidence`**, an array of `<document>:<field>` strings naming what a finding
  points at. A report recorded *which* checks failed and nothing about *why*. Attribution could not be graded from a
  conforming report, and both golden harnesses invented a submission shape; nobody runs a harness that needs
  non-standard input. The reference linter already emits this form for its best cases.
  `score_python_fixtures.py --reports` now grades conforming reports directly and falls back to
  `violation_detail[].location` for linters that predate the field.

  Run against the fixtures, miri-py 0.6.0 reports every case correctly (right checks, right arms, nothing on the
  control) and satisfies **two goldens of six**. Both are cases where the evidence is the document itself, and the
  document-only form is what the check's own `violation_unit` names. Detection and attribution are different properties,
  and until this field existed the standard could ask only for the first.

## 0.6.0 (never tagged; first published inside 0.7.0)

0.6.0 was merged to `main` and never tagged. No artifact carries it on its own and nothing could install it; its content
first reaches a consumer inside the 0.7.0 wheel. The heading carries no merge date because a date here is a claim that
something was published.

**BREAKING.** The check schema is bumped to `check-v3.json`: `weight` changes meaning for any definition that declares
`tiers`, and every score moves once the substance-bearing checks are tiered. The schema foundation landed first, and the
check definitions followed.

### Changed

- **BREAKING: `check-v3.json` supersedes `check-v2.json`.** It makes two changes of meaning. First, a substance-bearing
  check may declare [`tiers`](schemas/check-v3.json) and a `conformance_tier`, under which its `weight` is a ceiling
  earned as a cumulative schedule (T0 exists, T1 true, T2 covers, T3 current) instead of a bit. Second, every
  `fires_when` and tier clause must be a pure function of the artifact. Definitions without `tiers` mean what they
  meant under v2. All 123 definitions now declare `$schema: …/check-v3.json`. `check-v2.json` is retained frozen at its
  0.5.0 bytes. Its closed `additionalProperties` makes a v2-pinned linter handed a tiered definition fail loudly
  instead of scoring it as binary. The design was settled with the miri-py team
  (`substance-and-freshness-answers-1.md`, Q1): pass/fail is derived as `tier_earned >= conformance_tier`, default
  **T1**. The MUST boundary sits at the *lie* and not at thinness. No currently conforming wheel becomes non-conforming
  for being thin on the day tiers ship, and one shipping filler does.
- **`scoring-v1.json` gains `conformance.tiers`.** The four tier shares (`0.2 / 0.3 / 0.3 / 0.2`, provisional committee
  numbers) and the T2 activation trigger (**25 wheels from 10 independent publishers**) live here once, as schema
  defaults, never per check. T2 ships defined but weightless, with its share parked in T1. The only corpus available was
  seven wheels, three with an `api_index` and two of those the proposer's own; percentiles over that set would reflect
  habits back and calibrate nothing. The trigger is a count and carries no date.
- **Driver semantics stated normatively in `scoring-v1.json` `conformance.coverage`.** It has five clauses, each
  `const: true` so a scoring configuration cannot opt out: every defined check reports an outcome; a check the
  implementation does not verify is *forfeited*, never passed and never excluded; a forfeited MUST withdraws the grade;
  a verification that cannot run fails loudly; coverage is reported per family with a named blocker per uncovered check.
  0.5.0 defined forfeiting for capability gaps. Extending it to implementation-coverage gaps makes a coverage percentage
  comparable between two linters. `lint-report-v1.json` gains the skip reason `not_implemented` and a required `blocker`
  beside it. Proposed by miri-py from running their kernel. The third clause was added in our response: without it, an
  implementation covering 24 of 43 CLI checks reported `24 pass / 0 fail` instead of `undetermined`.
- **The conformance kernel recorded as a reference artifact.** `reference/conformance-kernel/` holds `rule-v1.json`
  and `operators-v1.json` unmodified from miri-py (pinned at `afc51324`), with the promotion test that would make
  them normative. The 51-file rule corpus is not vendored: a snapshot goes stale on their next commit, and a pinned
  pointer does not.
- **The fixture recipe is normative and its inputs are checksummed.** `examples/fixtures/checksums.json` hashes every
  file under `src/_template/` and `metadata/`, and `validate_fixtures.py` fails on drift. Wheel bytes are deliberately
  not asserted, because the build is not reproducible. The guarantee is the one the recipe can keep: matching inputs
  plus `build_fixtures.py` give the same fixture. The repository ships no fixture binaries.
- **`lint-report-v1.json` outcomes gain `tier_earned`**, the highest tier whose every clause held. It explains a status
  and never replaces it; the verdict vocabulary stays pass / fail / forfeit / exclude.
- **`MIRI-PY-016` withdrawn** (`withdrawn_in: 0.6.0-draft`). Its both-ways index/file join is `014`'s T3 clause, and
  its 2 weight moved there: both halves in one change, per the rule that an ID leaves only by withdrawal. The file and
  ID remain. "Absorbed" was the proposal's word, and it was wrong.
- **Twelve weight changes keep the target summing to exactly 100 with four new checks.** They are `007` 6→5, `008` 5→4,
  `012` 3→2, `019` 4→3, `021` 3→2, `028` 4→3, `029` 4→3, `030` 5→4, `033` 3→2, `038` 2→1; `014` and `015` 4→5 each,
  taking `016`'s weight. Categories: B 24 (unchanged, `041` inside), C 12 (unchanged), D 25→**23**, E 25→**28**, F
  10→**9**. Every published score moves, and the BREAKING line at the top rests on this change as well as on the schema.
- **The checklist's category summary was stale and ungated.** It still read A 10 / B 20 / C 10 against actual 4 / 24
  / 12, and it survived because its wrong rows totalled 100. It is rewritten to the real numbers with the
  gate-checked headings. Checklist stamp `0.2-draft` → `0.3-draft`: 43 active checks.

### Added

- **Four checks, `MIRI-PY-041` through `044`**: the freshness contract's three staleness classes made decidable, plus
  the document they read. `041` *changelog.json valid* (B, 3, conditional on a previous release, the `009` pattern).
  `042` *version silence* (E, 3): `releases[0].version` equals the wheel's version, the single rule that would have
  caught the originating incident. `043` *uncovered delta* (E, 2, `previous-release`): every interface in the measured
  `api_index` delta is named in an entry. `044` *dangling claim* (E, 2): every named symbol resolves in the current or
  previous `api_index`. All four are MUST. Stamp drift, the fourth class, was already `MIRI-PY-011`.
- **Tier tables on the five substance-bearing checks**: `007`, `014`, `015`, `017`, `037`, all at
  `conformance_tier: T1`. Presence is now T0 and earns a fraction of the weight, never all of it. `007`'s T1 requires
  every `common_imports` line to parse *and resolve*. `from _version.py import WheelContext` is schema-valid text and an
  invalid import, and it now fails a MUST, including in the proposer's own flagship (they asked for that). The
  Deprecation & Lifecycle checks `028` through `034` are deliberately **not** tiered. That family is already decomposed
  into discrete joins (subject existed / replacement resolves / delta covered / versions monotonic), the tier ladder
  expressed as separate checks. Tiering them would score the same join twice.
- **Spec §4.7** in the Agent Metadata specification defines `changelog.json`; §8.1 lists it among the required files
  from the second release.
- **The definitions as a data-only wheel, `miri-standard-checks`.** `tools/build_checks_wheel.py` stages the 123
  definitions and 16 schemas at build time, and the repository stays the source of truth. `publish-checks.yml` attaches
  the wheel to the GitHub Release at every release tag, after `make validate` and `make consistency` gate the tree it is
  built from. `manifest.json` pins the release, the full commit sha and a content hash; a report scored from the wheel
  still carries the `checks_commit_sha` it must. Provenance is attested and `SHA256SUMS` published beside it, because a
  definitions package is a supply-chain root. This answers miri-py's 2026-08-18 note: PyPI later, other registries
  declined until a consumer exists. It is a derived output, like the site, and takes no version bump. The reference
  linter scores the wheel in the same job, through the one gate `score_sample.py` already has. That score stays advisory
  until two structural failures close: `MIRI-PY-020` has no vocabulary for an artifact hosted outside an index, and the
  package ships no `agent-metadata/` yet.
- **[`changelog-v1.json`](schemas/changelog-v1.json): machine-readable release history, `changelog.json`.** It mirrors
  the CLI family's `changelog --since` payload (`MIRI-CLI-029`), and both targets share one shape. It is conditional on
  a previous release existing (the `030`/`034` pattern). It makes three staleness classes decidable: *version silence*
  (`releases[0].version` equals the wheel's version, the single rule that would have caught the incident behind this
  proposal), *uncovered delta* (every removal in the measured API delta has an entry), and *dangling claim* (every named
  symbol resolves in the current or previous `api_index`). The wheel metadata set had seven schemas and none was a
  changelog, and a record of fixes had nowhere to live.

- **A check verdict MUST be a pure function of the artifact.** `fires_when` in [`check-v3.json`](schemas/check-v3.json)
  now requires every clause to be decidable from the artifact under test and, where the check declares `requirements`,
  from the capabilities those name (a previous release, the network, execution). No clause may depend on model
  inference, on a judgment of style or quality, or on any other nondeterministic input. Two conformant linters given the
  same artifact reach the same verdict bit for bit. Only that makes a score comparable between implementations.

  **This is an addition, and the first draft of this entry filed it as a clarification.** All 122 active definitions
  already satisfy it and no score moves; both are true and neither is sufficient. The rule introduces a MUST that
  narrows what a check definition may be. A `fires_when` clause resting on model judgment would have validated before
  and is non-conforming now. A rule forbidding something previously permitted is new even when nobody has done it yet.

  Raised by the miri-py team, who argued for settling it before the rest of their proposal. The place a future editor
  would reach for a language model is a check about whether documentation is any good, and the prohibition should exist
  before the checks that would tempt it.

  There is no schema bump. JSON Schema cannot enforce this rule: it binds the check author and the linter and is
  verified by review. A consumer holding the previous reading of `check-v2.json` computes identical verdicts and
  identical numbers for every definition that declares no `tiers`.

### Fixed

- **The site stopped publishing on changelog-only and spec-only merges.** `publish-site.yml` triggered on checks,
  schemas, `docs/`, `website/` and the generator. It did not trigger on `CHANGELOG.md` or `standards/*/*.md`, though the
  generator renders both. Both paths are added. This release would have published; the next small edit would not have.
- **The Agent Metadata specification gained §4.7 without a header bump** in the commit that added it. The header moves
  from `0.2-draft` to `0.3-draft`. The omission was ours.

### Deferred by design

Every ask of the substance-and-freshness proposal is now decided and built: the four staleness classes, the document,
the tier schedule, and the calibration policy. **T2's weight** is deliberately not live. The covers tier is defined on
four checks and moves no score until the corpus of published conformant wheels reaches **25 wheels from 10 independent
publishers** (`scoring-v1.json` `t2_activation`). The only corpus available was seven wheels, three with an `api_index`
and two of those the proposer's own; percentiles over that set would reflect habits back and calibrate nothing. The
trigger is a count with no date, and until it fires T2's share sits in T1.

The reference implementation still owes two things, neither blocking the release: tier tables for the `cli`, `surface`
and `consumer` families under the same schedule, and the multi-invocation comparison operator. That operator is the
first of the three operator classes whose absence keeps `rule-v1`/`operators-v1` a reference artifact instead of a
normative one.

## 0.5.0 (2026-09-10)

**BREAKING.** This is the first release to carry that label. Two changes alter every conformance score, and both affect
anything vendoring the check schema: `conditional` reverses meaning, and three checks move out of the score. See
**Changed** below for what breaks and what to do about it.

It began as 0.4.1 (four fixes from the first binding) and grew through the Production Maps, an executable CLI
fixture suite, six adversarial review panels, and an implementation report that arrived while the panel findings
were being closed. All of it ships as one release because none of it was ever published. The last tag-equivalent is
0.4.0 on `main`, the version the reference linter pinned.

### Changed

- **BREAKING: `conditional` semantics reversed, and three checks now gate instead of scoring.** Both change every
  conformance score and affect anything vendoring the check schema. That schema is now
  [`check-v2.json`](schemas/check-v2.json), bumped for this reason.

  `conditional: true` previously meant a check *"scores its full weight automatically when the condition does not
  apply"*. It now means the check is **excluded from both the numerator and the denominator**. Not-applicable is not a
  pass: awarding weight for an absence let an artifact collect points for having nothing to declare. Twenty-four checks
  across three targets are affected. A linter that implemented the old reading produces different numbers for every
  artifact after re-syncing.

  `MIRI-PY-001`, `002` and `003` gain `scoring: gate` and weight 0. They remain MUSTs and still make an artifact
  non-conforming when they fail; they are no longer measured. Six points moved to `MIRI-PY-007` and `008` (+2 each) and
  `014` and `015` (+1 each). `check-v2.json` gains the `scoring` field because weight 0 already meant "extension check",
  and one value cannot mean two things.

  Reported by the miri-py team from scoring five unrelated wheels that returned an identical 8/10 in
  the Packaging Baseline. Renormalizing shrinks the denominator, and a constant numerator becomes a
  **larger** share: the Baseline went from 8% of a fixed 100 to about 14% of a typical
  applicable 58. Shipping the renormalization alone would have nearly doubled the fraction of a score carrying
  no information. Gating brings it to ~4%.

  Reports MUST now carry `effective_denominator`, `excluded` and `forfeited` beside a conformance score, and a forfeited
  MUST yields the new `undetermined` grade instead of a claim of conformance.

#### To upgrade

The algorithm is **not** in this entry. It is in
[`standards/python/linter-checklist.md`](standards/python/linter-checklist.md) and its
[CLI twin](standards/cli/linter-checklist.md), under **Scoring Model**: excluded vs forfeited, the precedence rule for
checks that are both conditional and capability-gated, `undetermined`, and the no-coverage-floor prohibition. Read those
documents for the algorithm; this entry lists the steps. An earlier version of this section named the changes and linked
to nothing, and a reader had to diff against 0.4.0 to reconstruct their own upgrade.

1. **Re-pin.** [`checks_commit_sha`](schemas/lint-report-v1.json) now requires a full 40-character lowercase sha. A
   short sha or a tag is a hard validation failure: if you pin `cc5d0a4` today, your reports stop validating. The
   release name goes in the new `checklist.standard_version` instead.
2. **Re-point at [`check-v2.json`](schemas/check-v2.json), and re-sync the corpus.** `conditional` reversed meaning
   without one byte of validating *content* changing, and the schema is now versioned for that reason: a schema is an
   interpretation contract, and this one's contract changed. Every definition declares `$schema: …/check-v2.json`,
   and v2 requires it. A v2 corpus **fails** against a vendored v1, and a v1 corpus **fails** against v2. The pairing
   that used to validate and score wrongly now breaks on both sides. [`check-v1.json`](schemas/check-v1.json) is
   retained frozen and still describes 0.4.0 semantics; a consumer pinned there is outdated but correct, and stays
   internally consistent.
3. **Change the scorer**, in this order: exclusion leaves both sides of the ratio; the precedence rule decides which of
   exclusion or forfeit applies to the ten dual-flagged checks (five python-wheel, five CLI); a forfeited MUST yields
   `undetermined`; `scoring: gate` checks are in neither sum, and a failing one is non-conformance, representable
   **only** through `must_failures`.
4. **Change the report.** [`lint-report-v1.json`](schemas/lint-report-v1.json) now requires
   `scores.effective_denominator`, `scores.excluded`, `scores.forfeited` and `must_failures`. A non-empty
   `must_failures` forces `grade: non-conforming` and caps `conformance` at 74; a `skipped` outcome must name its
   `skip_reason`; `grade` gained `undetermined`; `conformance` is bounded 0–100.
5. **Decide about already-published scores.** Every conformance number computed under 0.4.0 semantics is wrong
   under these. The standard does not tell you whether to retract or restate them; it tells you they changed.

**Expected results that look wrong.** `MIRI-PY-015`, `036` and `040` are MUST-level, require `execution`, and are
not conditional. A run without execution therefore forfeits three MUSTs, and every artifact reports
`grade: undetermined` instead of a band. That is the correct answer, because a wheel's runtime behavior cannot be
verified without running it. Do not "fix" it by suppressing forfeits in grading; run with `execution` available, or
accept that a static-only run reports a score and no verdict.

**Skipped work that will not fail loudly.** The three newly required `scores` fields catch a linter that did not update
its *serializer*. Nothing in any schema relates `scores.excluded` to the `outcomes` that were excluded. A linter that
adds the fields and leaves its *arithmetic* unchanged validates clean and reports wrong numbers. The guard against that
is the [`check-v2.json`](schemas/check-v2.json) bump itself, together with the `$schema` each definition now declares.
A linter still applying v1 arithmetic is reading a corpus that says v2, and the mismatch fails in both directions. It
is a tripwire. Nothing can prove your arithmetic changed. (An earlier draft of this entry named a `semantics_version`
field here. That field was proposed and rejected during this release, because a single global fact copied into 119
files becomes 119 statements that can each go stale. The schema bump replaced it. It does not exist; do not look for
it.)

### Added

- **`package.replaced`: a seventh trigger kind**, with
  [Lifecycle and Security Metadata §9.6](standards/python/lifecycle-security-metadata.md) and `MIRI-CONSUMER-052`
  behind it.

  A purl identifies a name and a version and says nothing about the byte stream. Uninstall a distribution and install
  different bytes at the same version, and nothing a consumer would compare has moved. §9.1's adversary (a package
  trustworthy when adopted and malicious later) already covered this, but every delivery mechanism it named was a
  *publication* event. This one publishes nothing.

  Raised from a maintainer's own workflow: developing a wheel means reinstalling at the same version many times an hour,
  because nobody bumps a version on every edit. It is a cache-invalidation problem *and* a trust problem, and the
  standard owed an answer to the trust half. §9.4 already says structured metadata is more dangerous than plain
  documentation because it invites a consumer to lower its guard. Miri therefore raises the value of this attack.

  The exposure is worst where §9.5's foundation is absent. PEP 740 attestation is the only field tying an artifact to
  an independent identity. `MIRI-PY-005` is network-gated and conditional, and a locally built wheel correctly carries
  no attestation. `MIRI-CONSUMER-052` carries the resulting prohibition: **no trust determination survives a
  replacement**. The trigger is *not* a verification. Where no attestation exists, re-reading a hostile artifact yields
  fresher hostile metadata.

- **CLI conformance goldens and a scoring harness.** `examples/fixtures/cli/expected/C1` through `C11` state which check
  a linter must report, on which arm, and (since the harness was rebuilt) pointing at which evidence.
  `make score-cli-linter` rejects seven ways of gaming it.

- **`scoring: gate`** is added to [`check-v2.json`](schemas/check-v2.json), with an invariant coupling it to weight 0
  and MUST level. The schema itself enforces the invariant. A repo-local script also checks it, and vendors do not run
  that script.

- **[Production Map](standards/python/production-map.md)**, the producer counterpart to the Consumption Map. The
  consumer side had an ordered model; the producer side had a checklist and no statement of what an author does first.
  Reported by a team implementing both halves: *"the consumer side was straightforward because the Map told us the
  order; the author side we had to invent an order for, and nothing checks whether we invented a good one."*

  The map has five stages, and **every ordering is derived from an existing check** instead of asserted. A stage with no
  check behind it would be advice. The version must be settled first because `MIRI-PY-019` and `MIRI-PY-012` check
  documents against `METADATA`. The manifest precedes the migration guide because `MIRI-PY-031` requires replacements to
  name interfaces in the *new* manifest. The guide is last because it depends on all three.

  It also states what a checklist cannot: **two checks require a previous release and are not evaluable on a first
  one**. A first release is scored over what could be evaluated and cannot legitimately show 100.

  It is explicitly not a conformance surface. No check scores an author on following it, because the checklist grades
  the artifact and not the process.

- **[CLI Production Map](standards/cli/production-map.md)**, the same document for what was then the largest target in
  the standard. `MIRI-CLI` carried forty-three checks, more than any other suite, and had no ordered model at all.

  It has six stages, and every ordering derives from a check. `--version` is settled first because `MIRI-CLI-017`
  compares `identity.version` against what the binary actually prints. The JSON envelope precedes `--describe` because
  `MIRI-CLI-010` fires when the two disagree, and `--describe` is one of the payloads it governs. The deprecation blocks
  are last because `MIRI-CLI-038` resolves every replacement against the current `--describe` *and* `MIRI-CLI-036`
  requires every deprecation to appear in `changelog --since`. They are the only surface depending on every other one,
  the same reason `migration-guide.json` is last on the wheel side.

  §3 records that **five CLI checks require a previous release**, carrying fourteen of the hundred weight, against two
  on the wheel side. A CLI's deprecation contract is a claim about what the binary used to do, and one release contains
  no evidence of it.

  §4 names the one conformance requirement that is normative and **ungraded**. CLI Lifecycle Specification §9 item 6
  requires `--help` and `--describe` to derive from one schema-as-data source, and no check can verify it. When all a
  linter may do is run the binary, two hand-maintained outputs that agree are indistinguishable from two derived ones.
  An author looking for the check that enforces item 6 has not missed one. One observable shadow of it *is* decidable
  and currently unchecked, and §4 records it.

- **[`agent-findings-v1.json`](schemas/agent-findings-v1.json) and the event-trace goldens.** Nothing pinned down the
  response the Agent Integration Contract defined, the envelope plus a `findings` key. There was no schema for the
  response, no rule mapping check IDs to `findings[].level`, and no goldens. The first binding was left implementing
  against prose and blocked on acceptance criteria it could not write for itself.

  The schema enforces the coupling §3.3 states normatively, in both directions: `present: true` requires `findings`,
  `present: false` forbids it and requires a `reason`, and **an empty `findings` array is rejected**. A binding cannot
  satisfy the silence obligation by emitting one. `task` is closed to the six map sections. `level` is closed to
  `must`/`should`, the conformance vocabulary instead of the check-severity one. A publisher's `priority: "critical"`
  cannot reach it even if a consumer passed it through unexamined. The schema cannot enforce that `level` was *derived*
  from the profile instead of copied, and the schema's own text states that limit.

  Eight goldens, `E1` through `E8`, were authored from the specification instead of captured from an implementation. A
  binding's author therefore cannot also be the author of its acceptance criteria. Every event validates against
  `agent-event-v1` and every response against `agent-findings-v1` under `make validate-fixtures`; the gate is
  mutation-tested.

  `E6` is the only trace driving the **conforming** arm: it asks whether a consumer uses what metadata declares, and
  every other trace asks whether it resists what metadata claims. Adversarial traces alone cannot tell a careful
  consumer from an inert one, the defect `MIRI-CONSUMER-041` itself carried. `E3` makes the trigger-forcing case
  discriminating. `A13` alone asserts only that output does not echo the bid, and a consumer that never reads satisfies
  that. `E3` requires a *response* on both arms: findings where the bid is, and §4.1's absent envelope where it is not.
  The discriminator is **absent envelope versus silence**, because a consumer that reads only when summoned produces
  nothing on the control arm.

- **[CLI conformance fixtures](examples/fixtures/cli/README.md)**: `greetctl`, four arms, and the first executable thing
  a CLI linter can be driven against. Every fixture in the repository was a Python wheel, and `make validate-fixtures`
  could not touch a CLI. The three vacuous-pass defects found in `MIRI-CLI-013`, `034` and `022` were all found by hand
  across four review rounds, because no fixture could find them.

  Unlike the wheel fixtures, it ships a **release history** (`miri-1.0.0` and `miri-1.1.0`) because the five
  previous-release checks cannot be exercised without one. `--shout` is deprecated in 1.0.0 and removed in 1.1.0.
  Invoking it against the current release yields the structured teaching error of `MIRI-CLI-033`, and the
  replacement it names resolves. `legacy-greet` is deprecated in 1.1.0, and that deprecation reaches
  `changelog --since 1.0.0` as `MIRI-CLI-036` requires. Nothing could test that before.

  One implementation file is copied byte-identically into all four arms, and any observed difference is therefore
  metadata-attributable. Eleven attacks (C1–C11) are each asserted live by `tools/validate_cli_fixtures.py` and
  mutation-tested: disarming any one of them fails the validator. `make check` runs the validator via
  `make validate-cli-fixtures`.

### Fixed

- **§4.3 of the Agent Integration Contract was unsatisfiable.** It defined trigger behavior as four things a publisher
  may not influence. Two of them, *whether* findings are carried and *how many*, are necessarily determined by the
  metadata: every finding derives from a shipped field. `MIRI-CONSUMER-051` fired on the behavior the `E3` golden
  mandates, and an implementation passing the golden failed the check. The regulated quantity is whether the **read
  happens**, never what the read finds, and the evidence that a trigger fired is §4.1's absent envelope. The fix also
  dissolved a finding tracked separately as needing a third fixture arm. `E3` could not discriminate because the rule
  pointed at the wrong observable, and the fixture's size was never the cause.

- **`MIRI-PY-008` and `MIRI-PY-007` admitted empty content arrays.** Reported by the miri-py team from scoring five
  real wheels. Verifying the report found the second instance, in the check the report assumed was safe. This is the
  fifth instance of one defect class, and the first found by running checks against real artifacts instead of
  reading them. See `standards/feedback/`.

- **Four gates that had never run, or ran wrong.** `.githooks/pre-commit` is the file `CLAUDE.md` tells a fresh clone to
  enable first. It had a `NameError` and a row regex that read 32 of 40 rows, and it had never completed. The `--since`
  validator was defeated by its own regex. `changelog --since` emitted records where CLI Spec §5.2 wants string arrays.
  §6.1 mapped `dependency.add` to a moment the contract's own footnote says has nothing to read.

- **The CLI linter harness graded a set of strings.** Six independent cheats reached a perfect score. One emitted every
  golden's check ID under the hostile arm's name without opening a fixture. Grading now requires attribution: the right
  check *and* the evidence that golden declares.

The fixes below cover four defects the miri-py team found building the first binding, one process failure of ours that
let two of them ship, one vacuous check they found implementing `test.author`, and one latent bug in the site generator
that adding the second Production Map exposed.

- **The schemas index listed 7 of 13 schemas.** `cli-describe-v1`, `discovery-envelope-v1`, `agent-event-v1`,
  `scoring-v1` and `lint-report-v1` were never added to `schemas/README.md`. Five schemas the specs depend on were
  discoverable only by listing the directory. All thirteen are now indexed, and `make consistency` now fails if a schema
  lacks an index entry. An earlier draft called the index "verified complete" when nothing verified it.

- **The site generator silently overwrote pages whose sources shared a basename.** Output names came from the source
  filename alone. `standards/python/production-map.md` and `standards/cli/production-map.md` both rendered to
  `production-map.html`, and one page vanished from the site with no error. Specs may now set a `slug:`, and a collision
  is a hard failure naming both sources.

- **Two fixes described as committed were not in the release.** They were committed to a branch that was never pushed,
  and a search of every remote branch correctly found nothing. The work existed on one machine and was reported as done.
  Both are now in: §3.3's `lifecycle` step and the event schema's `phase` rule.

- **Consumption Map §3.3 had no `lifecycle` step.** A consumer following the upgrade task as written could upgrade a
  package that is deprecated and names a successor in a foreign purl namespace, and never be told. That is the producer
  standard's highest-severity documented attack, reachable through correct adherence. The namespace prohibition was
  already in §3.3's must-not block, and no read-step supplied its evidence. **A prohibition whose input the read-order
  does not fetch is unenforceable.** 0.4.0 made this worse by making §3.3 REQUIRED.

- **`agent-event-v1.json` could not express a real dependency.** `subject.package` required an import name, but a
  manifest contains **distribution** names. The mapping between them lives in the installed distribution's own metadata,
  unavailable for a package that is not yet installed. `miri-py`, `python-dateutil`, `ruamel.yaml` and our own
  `greet-adversarial` fixture were all rejected. `subject.package_kind` now says which kind of name is carried, with PEP
  503 grammar for the distribution case.

- **`dependency.add` is demoted from REQUIRED to SHOULD.** At the moment a dependency is added it is not installed. It
  ships nothing a local surface can read, and §3.5 has no subject. The trigger fired correctly and found nothing, every
  time, for the case that motivated requiring it. Requiring a structurally silent kind buys a conformance obligation and
  no safety. It becomes REQUIRED when a registry-side surface exists; the kind stays in the vocabulary so that surface
  has somewhere to plug in. **`dependency.version_change` is now the only REQUIRED trigger**, because it is the one
  where the change is both observable and checkable: the old version is installed.

- **§4.1 required the behavior it forbids, in Claude Code.** A hook's stdout enters the agent's context. An adapter
  printing the absent envelope on every manifest edit announces *checked, nothing found* in JSON. Obeying the letter of
  the section produced the context tax §4.1 exists to prevent. The contract answer and what a host emits are now
  explicitly two layers: the absent envelope is what a golden asserts against, and a Claude Code adapter emits nothing.

- **`MIRI-CONSUMER-041` was satisfiable only by abstention.** No producer check requires any package to ship
  `test-patterns.json`. A consumer could be driven against a conforming wheel that ships none, or (as this project's own
  reference fixture did) one that ships it with an empty `supported_test_doubles`. In either state the only conforming
  behavior is to present no double. An inert consumer does the same, and the check could not tell a careful consumer
  from one that never looked.

  It is now **conditional**: scored where a double is declared, excluded from both numerator and denominator otherwise.
  The `miri` fixture declares `FakeGreeter` and gives the affirmative path something to exercise. `MIRI-CONSUMER-020`'s
  test-pattern clause is scoped the same way. Its other clauses are independent, and that check stays scorable for
  every package.

  **This is the fourth instance of one defect class this month**, after `MIRI-CLI-013`, `034` and `022`: a check that
  tests the *form* of a behavior without testing that the behavior *occurs*. The miri-py team found it while
  implementing `test.author`, when no fixture could exercise either MUST's affirmative path.

- **Four tasks could act without knowing a package was deprecated.** §3.3's missing `lifecycle` step was not a one-off:
  §3.1, §3.2, §3.4 and §3.6 omit it too. Instead of patching four read-orders, §4 gains a normative rule: **every task
  establishes the lifecycle facts**, whatever its read-order says. A task author writes the read-order for the question
  the task asks. "Is this package deprecated, and is its successor someone else's" qualifies every answer without being
  any single task's subject.

- **That rule's same-session exemption is now keyed on bytes instead of on the session.** As first written, a consumer
  that had already established the lifecycle facts "in the same session" need not re-fetch them. On a `package.replaced`
  notice the consumer *does* hold them, for the previous artifact's bytes, and the exemption licensed the very reuse
  that [`MIRI-CONSUMER-052`](standards/consumption/checks/MIRI-CONSUMER-052.yaml) forbids. **Consumer implementers:** if
  you cache these facts per session, a replacement must invalidate that cache.

- **The conformance gate no longer reads a field no schema defines.** `tools/score_sample.py` gated on `is_conforming`.
  That field appears in no schema and no specification, and it survived on `additionalProperties: true`. The gate now
  derives the verdict from schema-defined fields (`must_failures` empty, and `grade` outside
  `{non-conforming, undetermined}`), a coupling [`lint-report-v1.json`](schemas/lint-report-v1.json) already enforces.
  It also validates each report against that schema and **warns instead of failing**. 0.5.0 newly requires
  `effective_denominator`, `excluded` and `forfeited`, and gating would fail a linter whose 0.5.0 support is
  legitimately still in progress.

### Specified

- **Batching.** One observable action produces one event per package, and the binding coalesces *output* so a caller
  sees one report about one decision. This was settled from implementation data instead of by adding a plural
  `subjects`, because a subject is what an event is about.

- **Release tags carry no `v` prefix**: `0.5.0` and never `v0.5.0` ([CONTRIBUTING.md](CONTRIBUTING.md)). The tag is for
  humans and GitHub releases only. The machine-readable pin is `checks_commit_sha`. It requires a 40-character sha and
  rejects a tag outright. A tag identical to `standard_version` makes a report's version a usable git ref.

- **Per-check revision history stays editorial** ([schemas/README.md](schemas/README.md)). `added_in` records birth and
  nothing records revision, by decision. Git is the revision record, and `checks_commit_sha` makes it addressable. The
  difference between two reports is therefore a diff instead of a claim. A hand-maintained `changed_in` would fail the
  way `semantics_version` did: one global fact copied into 119 files becomes 119 statements that can each go stale.

## 0.4.0 (2026-09-06)

A **minor** version, because it adds. The Agent Integration Contract is new and two consumer checks are added. Every
consumer score computed before this release shifts as a result. A minor version exists for that, and none of it could be
back-ported to 0.3.1.

The specifications remain **draft** (`0.4.0-draft` in their headers). The contract is specified but the reference
binding does not exist yet. Two review findings are open against it: no schema governs the `findings` array, and no rule
maps Consumer Conformance check IDs to `findings[].level`.

### Added

- **[Agent Integration Contract](standards/consumption/agent-integration-contract.md): the missing *when*.** The
  standard specified what an artifact ships, how a surface serves it, and what a consumer reads; nothing specified what
  causes the reading to start. A conformant producer, surface and consumer could coexist with metadata that was never
  read, and every score stayed green.

  Six **triggers**, one per Consumption Map task, name the observable moment at which each becomes actionable. Two were
  REQUIRED at 0.4.0: a dependency being added, and a version changing. **0.5.0 demotes the first to SHOULD** (the
  release that began as 0.4.1); see that entry for why.

  *Hook* is deliberately not part of the vocabulary. A hook is a host's mechanism, and the word appears elsewhere in
  this standard seven times, every one describing git or setuptools. The sentence that has to keep working is *"Claude
  Code delivers a trigger via a hook; CI delivers the same trigger via a step"*. It parses only if hook is theirs and
  trigger is ours.

- **[`agent-event-v1.json`](schemas/agent-event-v1.json): the event a host sends.** It **closes**
  `additionalProperties`, the opposite of the response envelope's open root, and does so deliberately. The envelope is
  open so a new operation can add a payload key. The event is closed so a host **cannot send a file path, a diff, or the
  user's source**. A prohibition that was prose is now a validation failure.

- **Two consumer checks**, `MIRI-CONSUMER-050` (a trigger with nothing to report answers absent, never empty) and
  `MIRI-CONSUMER-051` (trigger behavior is independent of what the publisher ships). Both are **conditional**. A
  consumer with no binding has no trigger to answer, and by the not-applicable-is-not-a-pass rule they leave both the
  numerator and the denominator. The consumer family is now 17 checks, still summing to exactly 100. Six points came
  from one point off each of six large MUSTs, and no category absorbs the change.

- **Attack A13**: a shipped field bidding for the agent's attention, planted in the adversarial twin and nowhere else.
  Every `.py` stays byte-identical across the fixture variants. Driving the same trigger against `adversarial` and
  `miri` isolates the metadata as the only possible cause.

### Changed

- The **Agent Metadata threat model** gains the axis it was missing. Every item in it concerned what the metadata
  *says*: narrative files inject, `api_index` can lie, execution is not sandboxed. This is the first item concerning
  what the metadata *makes happen*. A package that can force a trigger has a denial-of-context channel. A threat model
  covering only content cannot see attacks that work through control.

- **Consumption Map §3** gains a trigger column. It belongs there rather than in a binding document because it completes
  the map's own sentence: task answers *what*, vehicle answers *how*, trigger answers *when*. The column holds whether
  or not any binding is ever written.

### Fixed

- **An IPv6 hole in the SSRF guard.** Link-local was written as `169.254.0.0/16` and `fd00::/8`. `fd00::/8` is
  unique-local. `fe80::/10`, the actual IPv6 link-local range, was **missing**, and an IPv6 link-local address passed
  the guard. The ranges are now split into private, loopback, link-local and cloud-metadata.

- **A cross-document contradiction** introduced in the same session. The integration contract made `reason`
  machine-meaningful, and the Discovery Contract forbids that outright. The claim was dropped and the rule kept: a
  consumer wanting to know what a package ships asks `list`, the operation whose answer that is.

### Verification

- `tools/check_consistency.py` gains the section-opener count rule it had missed for two rounds. It also loses a
  bug: it counted an escaped pipe as a table-cell separator and reported a defect markdownlint correctly accepts. A
  first attempt at the wider count rule produced **twelve false positives** on this corpus and was replaced with a
  precise one.

## 0.3.1 (2026-09-01)

This release contains bug fixes and clarifications and **no additions to the standard**. Every change either corrects
something that was wrong or makes an existing rule mechanically checkable.

Four of the six defects below were found by the miri-py team building an implementation against the text, and one by
scoring a real CLI. Re-reading our own documents had found none of them.

### Fixed

- **`MIRI-SURFACE-012` required surfaces to refuse documents that six goldens require them to serve.** A clause added
  during 0.3's review demanded `METADATA_UNREADABLE` for any document that parses but fails its schema, while the
  adversarial fixtures expect those same documents served. Ten of the fifteen consumer checks are driven *through* the
  surface, and enforcing the clause would have disabled most of the consumer profile. The check is now scoped to
  readability, as its own examples, its rationale and §3.2's verbatim rule already said. Reported by the miri-py team.
- **All 33 consumption checks advertised a `urls.html` that returns 404.** Linter reports link findings to that address,
  and every consumption finding pointed at a missing page. The 83 producer checks were correct; the consumption suite
  copied the wrong pattern when it was authored.
- **`cli-describe-v1.json` forbade the `advisory_coverage` field that `MIRI-CLI-022` requires.** The schema closes
  `additionalProperties` and never declared the field. A CLI doing what the standard tells it failed the standard's own
  schema, and arghos had been failing validation since adopting it.
- **`schema_version` was unconstrained in three schemas, and three surfaces had diverged.** Two emitted `"1.0"`, one
  `"1"`, and all three validated. The integer-string convention lived only in prose and examples. It is now pinned to
  `^[0-9]+$` in `cli-describe-v1`, `lint-report-v1` and `discovery-envelope-v1`. The `lint-report` pin matters most,
  because it governs the report every `miri score` emits.
- **Five check citations pointed at sections that do not exist, or at the wrong one.** `MIRI-CLI-014` and `MIRI-CLI-034`
  cited a section with no such number; `MIRI-PY-019` used a notation that reads as a subsection; and `MIRI-CLI-013`, a
  check about the general error envelope, cited only §6 *Deprecation Metadata*.
- **The `MIRI-CONSUMER-032` namespace rule failed to detect the attack it targets.** PyPI has no namespace component,
  and `pkg:pypi/a` redirecting to `pkg:pypi/b` compared as the same namespace. The comparison now falls back to the PEP
  503-normalized package name where the type has no namespace.

### Verification made mechanical

Every gate below is new, and each exists because a defect of its shape shipped. The standard has four kinds of normative
artifact (check `fires_when`, spec prose, schemas, and goldens), and each pair that can disagree now has a cross-check.

- **`tools/check_consistency.py`** checks count claims against what is enumerated, sets declared complete against every
  member used, local section references, list numbering, table integrity, and check-demanded fields against every
  schema property. That last sweep found `advisory_coverage`.
- **`tools/check_references.py`** gates that every check's spec citation resolves to a real document and section, and
  **reports** the semantic half as a check-to-section list for a person. The split is deliberate: a falsely confident
  gate is worse than none, because nobody looks behind a green tick.
- **`tools/validate_fixtures.py`** gains a check-versus-golden cross-check. No check can now demand refusing a document
  the goldens require served.
- **These validators had never run in CI.** None of them, and none of the fixture invariants, gated anything until
  this release.

### Contributed

- **`schemas/discovery-envelope-v1.json`** and **`tools/validate_envelope_schema.py`** came from the miri-py
  implementation team, derived from a working surface instead of from this specification a second time. The envelope was
  the one normative wire format with no schema: every `MIRI-SURFACE` check validated a shape that existed only in prose.

  *Present on `main` but **not** part of the 0.3.1 release surface.* By the policy above, a schema is a
  backward-compatible addition and therefore 0.4 material.

## 0.3.0 (2026-08-28)

This release adds the consumption suite, the half of the standard that says how an artifact is **read**. Versions 0.1
and 0.2 specified what an artifact ships; this one specifies how an agent consumes it, and what a conformant consumer
and a conformant metadata surface are.

### Added

- **[Discovery Contract](standards/consumption/discovery-contract.md)**, the transport-agnostic wire contract: eight
  operations in three kinds, the surface-owned envelope, absence-versus-error, caps and continuation, and MCP and
  loopback bindings.

  Its central mechanism nests publisher bytes under a payload key. A hostile package writing `ok: false` into its own
  document cannot forge a served, absent or failed signal. The surface still relays the bytes intact and does not edit
  what a publisher wrote; they sit one level down, as data.

- **[Consumption Map](standards/consumption/consumption-map.md)**: six tasks, each a read-order plus a set of
  prohibitions, with a vehicle label recording what a consumer must possess to perform each step.
- **[Consumer Conformance](standards/consumption/consumer-conformance.md)**: 15 `MIRI-CONSUMER` checks. A consumer is
  *driven* instead of inspected, and every check is written against observable output.
- **[Surface Conformance](standards/consumption/surface-conformance.md)**: 18 `MIRI-SURFACE` checks in six categories,
  ordered as the path a request takes through a surface.
- **Fixtures**: ten variants built from one template, with every `.py` verified byte-identical across the
  source-sharing ones. Any difference in a consumer's behavior is therefore attributable to the metadata alone. Fifteen
  goldens cover attacks A1–A12.
- **The site renders the specifications**, with diagrams, sticky outlines, and per-target check pages for all
  four targets.

### Changed

- **Not-applicable is not a pass.** A conditional check whose condition does not apply is excluded from both the
  numerator and the denominator instead of being credited. Under the old model a CLI could earn 20 points for never
  deprecating anything.
- **Conformance is a gate instead of a band.** A failing MUST makes an artifact non-conforming and no grade is reported.
  The report shows only the score, capped, to show distance.
