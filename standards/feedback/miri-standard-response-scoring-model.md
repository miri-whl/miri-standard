# Response: Scoring Model Proposal (Two-Score Architecture)

*Response Version: 0.1-draft*
*Status: Draft — miri-standard maintainers' response*
*Created: 2026-08-18*
*In reply to: [miri-py-scoring-model-proposal.md](miri-py-scoring-model-proposal.md)*

## Summary

Accepted in architecture, with amendments. The two-question decomposition — **Conformance** ("does it conform, and how
completely?") vs **Health** ("how bad is what's wrong?") — is correct, and the Wheel A/B example identifies a real hole
in the checklist model: binary checks discard magnitude by design. We also accept your endorsement of the conformance
model unchanged; its comparability across independent implementations is the property the standard exists to protect,
and nothing in this response perturbs it.

One part of your proposal is not just accepted but already implemented: the committee-assigned severity vocabulary now
ships in the standard. See §2.

## 1. Disposition of the Asks

| # | Ask | Disposition |
|---|---|---|
| 1 | Keep the conformance model unchanged | **Accepted** — no changes |
| 2 | Normative Health Score (severity vocabulary, violation binding, baseline method, profiles) | **Accepted with amendments** (§2–§3) — severity layer shipped; scoring layer pending your drafts |
| 3 | Method + profile declaration on any reported health score ("no naked scores") | **Accepted** as proposed — it is our "declare sources, not verdicts" principle applied to scoring |
| 4 | Reserved extension namespace for health-only quality checks | **Accepted, amended** — namespaces reserved, promotion rule added (§3.3) |
| 5 | `checklist.json` + `scoring-v1.json` + `lint-report-v1.json` | **Accepted, amended** — per-check definitions shipped as `alerts/`; scoring/report schemas welcome as drafts, cross-language (§3.2) |

## 2. Already Shipped: Centralized Alert Definitions

Your §3.2-1 and §3.2-2 (severity vocabulary + violation-to-check binding) had a hidden dependency you did not call out:
**if severity assignment is implementation-defined, baseline health scores are not comparable across linters** — the
exact non-comparability you conceded in §2.2 returns through the back door. The formula being fixed is not enough; the
inputs must be fixed too.

The standard therefore now defines severity per check, centrally:

- **`standards/python/alerts/`** and **`standards/cli/alerts/`** — one YAML file per check (`MIRI-PY-001.yaml` …),
  validated against [`alert-v1.json`](../../schemas/alert-v1.json). Each file is the committee-owned definition:
  name, level, category, weight, short/long descriptions, violation and compliant examples, suggested fix, references,
  and versioning (`added_in` / `withdrawn_in`).
- **`severity.default`** — one of `LOW` / `MINOR` / `MEDIUM` / `HIGH` / `CRITICAL` (numeric 1–5), exactly your
  vocabulary.
- **`severity.violation_unit`** — what counts as *one* violation (e.g. MIRI-PY-015: "each example that fails to
  compile or execute"). This is the countable unit that makes your Wheel A/B example computable: 1 MEDIUM vs 40 MEDIUM,
  from the same definition file.
- **Normative rule**: implementations MUST consume these definitions and MUST NOT override severity or violation
  units. Your commitment §4-1 (adopting `MIRI-PY-NNN` as primary finding IDs) should bind to these files rather than
  to the markdown table, which is now the derived human rendering.

This supersedes the `checklist.json` portion of ask 5 in richer form; an aggregated `checklist.json` remains a planned
convenience artifact generated from the same files.

## 3. Amendments Required Before the Health Score Is Normative

### 3.1 Count Normalization Must Be Defined in the Baseline

`max(0, 100 − Σ(wᵢ × countᵢ))` over raw counts penalizes large artifacts: 40 broken examples out of 400 scores the
same as 40 out of 40. Whatever stance the baseline takes — raw counts, proportional scaling for countable populations,
or per-unit caps — it must be *defined in the standard*, or comparability leaks out the same door severity almost did.
We have no fixed position and would welcome a proposal grounded in your production data; we note your own Tiered
Penalty method already contains the per-severity-cap idea.

### 3.2 The Scoring Layer Is Cross-Language

Nothing in the severity vocabulary, baseline method, profiles, or report format is Python-specific. We will adopt:

- `scoring-v1.json` and `lint-report-v1.json` as **shared schemas** (like `lifecycle-v1.json`), serving the CLI
  checklist (`MIRI-CLI-NNN`, 43 checks — alert definitions already shipped) and future Go/Rust suites identically.
- Please generalize your §3.4 drafts accordingly; Python-only schemas will not be accepted.

### 3.3 Extension Namespace: Granted, With a Promotion Rule

`MIRI-PYX-NNN` is reserved (and `MIRI-CLIX-NNN` alongside it; the `alert-v1.json` ID pattern already admits both).
Extension checks carry weight 0 and contribute only to health. One addition: **promotion from an X-namespace into the
conformance namespace is a weight-table change** and follows the same versioned-redistribution rule as withdrawal — no
silent migration, ever. Also note one alignment requirement: any PYX security-scanning check (your pip-audit
dimension) MUST perform its advisory lookup through the artifact's declared `advisory_sources`
([Lifecycle Spec §3](../python/lifecycle-security-metadata.md)), not through a parallel hardcoded path — otherwise
private packages silently scan against the wrong database.

### 3.4 Profiles Are Versioned

"CI gate at health ≥ 80, profile balanced" is only stable if `balanced` cannot change under a pinned reference.
Profiles carry versions (`balanced@1`); changing a profile's weights is a new profile version. Same reasoning as our
`schema_version` clock: the contract moves on its own clock, explicitly.

## 4. What We Ask of miri-py

Your §4 commitments are accepted with thanks — the reference scoring engine and the generalized schema drafts are
exactly the contributions that make "conforming linter" a testable claim. Concretely, in order:

1. Bind your finding IDs to the `alerts/` definitions and report any severity or violation-unit assignment you
   disagree with as an issue against the alert file — that is now the mechanism for severity debate.
2. Draft `scoring-v1.json` / `lint-report-v1.json` as cross-language schemas (§3.2), including versioned profiles
   (§3.4) and a count-normalization stance for the baseline method (§3.1).
3. Validate the Wheel A/B worked example end-to-end against the shipped severity data — MIRI-PY-015 is defined as
   MEDIUM per failing example, so your §5 numbers should reproduce exactly.

## 5. One Open Question Back

Your six-layer dimensional blend (§2.2) includes layers we deliberately keep out of both scores (external tool
findings, code-quality analyzers). The X-namespace gives them a vocabulary, but a question remains: should the
standard define *any* aggregate above the two scores (a "blended" third number), or is that permanently
implementation territory? Our instinct is the latter — two numbers with defined meaning beat three where one is
vendor-defined — but if production experience says operators demand a single dial, we would rather standardize its
declaration format ("no naked blends") than pretend it will not exist.

---

*miri-standard maintainers. Discussion: open an issue or thread on the
[miri-standard discussions board](https://github.com/miri-whl/miri-standard/discussions).*
