# Feedback: Publish the Alert Definitions as a Versioned Artifact

*Feedback Version: 0.1-draft*
*Status: Draft — submitted for miri-standard discussion*
*Created: 2026-08-18*
*From: the miri-py implementation team*
*Follows: [Scoring Model Proposal](miri-py-scoring-model-proposal.md) and the maintainers' response*

## Abstract

The new `standards/python/alerts/` and `standards/cli/alerts/` directories are exactly what we asked for and more: the
committee-owned, machine-readable source of truth, with severity and violation units fixed by the standard. One gap
remains, and it is distribution, not content: the normative rule says implementations **MUST consume these definitions**,
but the only way to consume them today is a git checkout of `main` — an unpinned moving target. We ask the standard to
publish the alert definitions as a **versioned, released artifact**, so that "one source of truth" is enforced by the
packaging ecosystem rather than by each implementation's vendoring discipline.

## 1. The Consumption Problem

- **`main` moves; scores must not.** Weights and severities change legitimately (withdrawal, redistribution,
  `added_in`/`withdrawn_in`), but on the standard's clock, in minor versions. An implementation reading an unpinned
  checkout can produce different scores for the same wheel on different days with no change on its side — the exact
  comparability failure the alert files were created to prevent.
- **Linters ship the data.** A conforming linter must work offline and in air-gapped environments (the standard's own
  private-package story depends on this), so the definitions must be embedded in each implementation's release
  artifact. Every implementation therefore needs a *sync-and-pin* mechanism; today each must invent its own.
- **Reports must declare their basis.** A lint report should say which checklist version it scored against. That
  declaration is only meaningful if the version names a released, immutable artifact.

## 2. Precedent

This is a solved problem in every mature ecosystem — standards-owned data, published as a versioned artifact,
pinned by consumers:

| Data | Publisher → artifact | Consumers |
|---|---|---|
| Trove classifiers | PyPA → `trove-classifiers` on PyPI, auto-released from the repo | pip, twine, build backends |
| IANA time zones | IANA → `tzdata` on PyPI (repackaged by CPython core) | the standard library, pytz successors |
| SPDX license list | SPDX → tagged `license-list-data` releases | license tooling across languages |
| Browser support data | caniuse → `caniuse-lite` on npm | browserslist, autoprefixer, every bundler |

The consumer side has equally strong precedent: **ruff** vendors typeshed into its binary via an automated,
pinned-commit sync job — a scheduled workflow updates the vendored copy, CI validates it, and the pin is explicit in
the tree. That is precisely the bridge mechanism miri-py will run until a released artifact exists (§5). Notably,
typeshed's consumers each had to build that machinery themselves; `trove-classifiers` consumers just declare a
dependency. The difference is the publisher shipping a versioned artifact.

## 3. The Ask, in Three Tiers

Ordered by cost; each tier is useful without the next:

1. **Tag releases** of the miri-standard repository whenever a checklist version changes (e.g. `checklist/0.1.0`).
   Cost: near zero. Effect: implementations pin a named, immutable ref instead of a commit SHA, and "checklist
   version" becomes a resolvable identifier.
2. **Attach generated aggregates as release assets.** The aggregated `checklist.json` per target is already planned as
   a generated convenience artifact; generating it (and, ideally, a single archive of the alert YAMLs) in CI and
   attaching it to the release makes each release self-contained — consumers fetch one validated file per target
   rather than forty.
3. **Publish data packages** to the language registries — a `miri-standard-alerts` package on PyPI (and its npm/crates
   siblings as target suites mature), containing the alert definitions and schemas, versioned in lockstep with the
   checklist. Given the maintainers' own cross-language stance on the scoring schemas, one package per registry
   carrying *all* targets' definitions seems right — implementations consume the subset for their target. This is the
   `trove-classifiers` end state: consuming the standard becomes `pip install`, and pinning becomes a lockfile entry.

## 4. Versioning Semantics

- Artifact version = checklist version, on the checklist's own clock — consistent with the standard's stated
  "the contract moves on its own clock, explicitly" principle for profiles and schemas.
- A release is immutable; weight redistribution or withdrawal is a new minor version, exactly as the checklist already
  specifies.
- Lint reports (a field for `lint-report-v1.json`, which we are drafting per the maintainers' response §3.2) declare
  the checklist version they scored against.

## 5. What miri-py Does Meanwhile

Until tier 1–2 exist, miri-py will run the ruff/typeshed pattern as a bridge: a vendored mirror of
`standards/python/alerts/` inside the package, written only by a sync command pinned to an upstream commit SHA, with
schema validation, the 100-point-sum invariant check, and a provenance record (upstream SHA, checklist version, date,
content hash) committed alongside. When releases exist, the sync's source changes from a raw commit to the release
artifact and nothing else moves. We are happy to contribute the CI workflow for tier 2 (generate, validate, attach) to
the miri-standard repository — it is the same generator the schema-as-data rule already calls for.

---

*Prepared by the miri-py team, following the maintainers' response on the two-score architecture.*
