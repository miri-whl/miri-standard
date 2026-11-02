# Substance and freshness: graduated scoring for the documents a consumer trusts

*Version: 0.2 — expanded to a full 0.5.1 proposal: graduated (ranged) scoring joins the freshness contract*
*Status: Proposal — targeting 0.5.1*
*Created: 2026-09-18*
*From: the miri-py implementation team*
*Pinned at: `6f4493c38fc36557845c13a41d78567d5ee80d1f` (0.5.0)*

## Summary

Two defects in the current checklist, both measured on our own
artifacts, both invisible to every existing check:

1. **Stale is a state the standard cannot see.** We shipped bug fixes
   with a silent changelog; the downstream project that reported those
   bugs installed the fix and never learned it. Every shipped document
   was present, schema-valid, and stamped in the build window.
2. **Presence scores as substance.** A document earns its full weight
   by existing and validating. Our flagship wheel scores 100% while its
   examples exercise **1%** of its declared 394-symbol surface, its
   docs mention **1%** of it, it ships **one** usage pattern, and its
   generated `quick_reference` contains `from _version.py import
   WheelContext` — schema-valid text that is not valid Python. An
   agent trusting that line fails on its first import.

We propose two coupled changes for 0.5.1:

- **A freshness contract**: four deterministic staleness classes,
  verified as cross-artifact joins, plus one new machine-readable
  document (`changelog.json`) so "what was fixed" has a home a
  consumer's tooling can read.
- **Graduated (ranged) scoring**: substance-bearing checks stop being
  binary. A document's weight is earned in **tiers** — exists, is
  true, covers, is current — so an empty-but-valid file earns a
  fraction of its weight, never all of it.

Everything below is deterministic and shrink-wrapped: **no LLM in any
verification path**, stated as a normative property. Every verdict is
a pure function of the artifact (and, where declared, the previous
release), so independent implementations agree bit-for-bit.

## 1. The freshness contract

**A document is fresh when its claims join against the artifact's
measured surface — in both directions — at build time.** This is the
discipline the checklist already trusts (MIRI-PY-016
examples↔manifest, MIRI-PY-036 manifest↔surface), extended to the
narrative documents. Four staleness classes, each mechanically
decidable:

| Class | Definition | Example |
|---|---|---|
| **Dangling claim** | The document names a symbol, document, or version the artifact does not carry | docs referencing a renamed class; an example calling a removed function |
| **Uncovered delta** | The artifact measurably changed and the owning document is silent | API removed, migration guide silent; API changed, changelog silent |
| **Stamp drift** | The generation stamp falls outside the build window | already normative (MIRI-PY-011) — cited as the pattern |
| **Version silence** | The release-describing document has no entry for the version it ships in | a changelog whose newest entry is two releases old |

The measured delta comes from a previous-release compare — machinery
0.5.0 already requires for MIRI-PY-030, and for which a maintained
off-the-shelf implementation exists (griffe emits typed breakage
objects between two versions; Appendix A).

## 2. One new document: `changelog.json`

The wheel metadata set records breaking changes
(`migration-guide.json`) but has no machine-readable changelog, so
"what was fixed" cannot reach a consumer's tooling. Proposed shape
(mirrors the CLI family's proven `changelog --since` payload,
MIRI-CLI-029):

```json
{ "schema_version": "1",
  "releases": [
    { "version": "0.3.0",
      "added":   [ {"summary": "...", "symbols": ["Client.batch"]} ],
      "changed": [ {"summary": "...", "symbols": ["Client.fetch"]} ],
      "fixed":   [ {"summary": "...", "refs": ["#412"]} ],
      "removed": [ {"symbol": "Client.legacy_fetch"} ] } ] }
```

What it makes decidable:

- `releases[0].version == wheel version`, or the check fires
  (**version silence** — this single rule would have caught our
  incident).
- Every symbol in the measured API delta appears in this release's
  entries (**uncovered delta** — set difference against the
  previous-release compare).
- Every named symbol resolves in the current or previous api_index
  (**dangling claim**, both directions).
- A consumer's `dependency.version_change` trigger can finally answer
  "what changed since X" for a library — the downstream project in
  our incident would have been told its bugs were fixed by machinery
  the contract already ships.

Producer-side, we recommend (non-normatively) the fragment discipline
the ecosystem already uses: a change lands with a news fragment or CI
fails; the release assembles the document (towncrier-class tooling,
Appendix A). The standard owns the artifact-side joins; fragments are
how a producer meets them without heroics.

## 3. Graduated scoring: weight is earned in tiers

Today a substance-bearing check awards its full weight on
present-and-valid. That prices an empty document identically to a
taught one, and our own 100%-at-1%-coverage flagship is the proof the
pricing is wrong. We propose that for the substance-bearing checks,
**weight is a schedule, not a bit**:

| Tier | Name | The question | Typical share |
|---|---|---|---|
| T0 | **Exists** | present, parses, schema-valid | 20% |
| T1 | **True** | its claims join: named symbols resolve; embedded code parses and executes against this wheel | 30% |
| T2 | **Covers** | it addresses a measured floor of the surface or delta it owns | 30% |
| T3 | **Current** | freshness holds: stamps in window, current version described, no dangling claims against the previous release | 20% |

Tiers are cumulative (T2 cannot be earned without T1) and every tier
is a join or an execution — never a word count, never a style opinion,
never a model's judgment. Per-document tier tables:

**Examples (014/015/016/017 family, plus new substance tiers)**
- T0: `examples/` present; every file parses (exists).
- T1: every example executes against this wheel; every API name an
  example uses resolves in api_index (an example demonstrating a
  removed API is stale documentation that still runs).
- T2: examples exercise ≥ the calibrated floor of the declared
  api_index (see §4 for how floors are set — NOT chosen by taste).
- T3: `AGENT_EXAMPLES.json` ↔ files both ways (016, absorbed here) and
  no example references symbols absent from the current release.

**Docs (037 family)**
- T0: the required documents exist with parseable structure.
- T1: **every fenced code block parses and executes** against the
  installed wheel (Sybil-class tooling — this rule alone catches
  `from _version.py import …` filler); identifier-shaped references
  resolve in api_index.
- T2: documented-symbol coverage ≥ the calibrated floor; docstring↔
  signature coherence on the public surface (pydoclint-class — Args/
  Returns/Raises match the live signature).
- T3: stamps and version references current.

**Migration guide (028–034 family, completed)**
- T0: exists and validates when required (non-initial release).
- T1: every entry's subject existed in the previous release; every
  `replacement` resolves in this one (anti-phantom, both directions).
- T2: every removal and PEP 702 marker in the measured delta has an
  entry (uncovered delta).
- T3: version ordering monotonic; entries dated within their release's
  window.

**Changelog (new)**
- T0: `changelog.json` exists and validates.
- T1: every named symbol resolves (current or previous release).
- T2: the measured API delta is fully covered by entries.
- T3: `releases[0].version` equals the wheel version.

Under this schedule our own flagship would earn roughly T0+T1 on docs
and examples and fail T2 outright — **a score we consider correct and
accept publicly.** A proposal that did not demote its own authors'
artifact would deserve suspicion.

## 4. Floors are calibrated, never chosen

The T2 coverage floors are the one place a number enters, and numbers
invite gaming and taste. Both are addressed the same way:

- **Calibration**: floors are set from corpus percentiles measured
  across published conformant wheels (we volunteer our five-wheel
  corpus plus both of our own wheels, probed and published), adopted
  per-release by the committee, and revisited with the corpus — the
  same posture as the complexity thresholds decision.
- **Anti-gaming**: every countable feeding a floor must ALSO clear T1
  — an example only counts if it executes and its symbols resolve; a
  doc mention only counts inside a document whose code blocks run. A
  generated call-everything script or symbol glossary must therefore
  actually work against the wheel, at which point it has become
  documentation.
- **Caps**: T2 award saturates at the floor. There is no incentive to
  chase 100% — the schedule pays for "taught", not "enumerated".

## 5. Normative property: verdicts are pure functions

Every check verdict MUST be computable as a pure function of the
artifact under test and, where the check declares it, the previous
release — no network beyond declared capabilities, no model inference,
no nondeterminism. Two independent implementations MUST agree
bit-for-bit on every tier award. This is true of all 119 definitions
today and written down nowhere; 0.5.1 should say it, because this
proposal is exactly the place a future editor might be tempted to
reach for a language model, and the answer must already be no.

## The ask

1. Adopt the four staleness classes and the join principle as 0.5.1
   checklist material.
2. Add `changelog.json` to the wheel metadata set (or a `releases[]`
   block in lifecycle.json — no strong preference).
3. Adopt graduated tier scoring for the substance-bearing checks, with
   the tier tables of §3 as the starting text and shares as committee
   numbers.
4. Set T2 floors by corpus calibration (§4); we will deliver the
   measured corpus data with our implementation report.
5. State the pure-function/no-LLM property of verdicts normatively.

## Appendix A — implementation evidence (all deterministic, all maintained)

| Contract element | Off-the-shelf tool | Notes |
|---|---|---|
| Previous-release API delta | **griffe** (`griffe check pkg --against <ref>`) | typed breakage objects; CLI + library; powers uncovered-delta joins |
| Changelog format + version presence | **python-kacl** | Keep-a-Changelog validation; exit-code/JSON CI integration; human-readable twin of `changelog.json` |
| No change without an entry (producer side) | **towncrier check** (+ scientific-python action, pre-commit wrappers) | used by pip/pylint/setuptools |
| Docs' code blocks execute | **Sybil** (v10, 2026-06 release) | fenced blocks in md/rst/docstrings run as pytest tests |
| Docstring↔signature coherence | **pydoclint** | Google/numpy/Sphinx styles; fast |
| Docstring coverage + git-based staleness | **docvet** (2026) | independently converged on freshness-by-blame — ecosystem tailwind for this proposal |
| Example complexity ceiling | **radon** | already integrated in our linter |
| agent-metadata joins (api_index ↔ docs/examples/patterns) | first-party (~100 lines, AST + set joins) | nothing off-the-shelf knows MIRI's documents; we ship it |

Our linter wraps external tools behind a degrade-gracefully
integration layer already (flake8, radon, twine, pyroma…); every tool
above slots into that pattern, and absence of a tool forfeits the
affected tier rather than silently passing it.
