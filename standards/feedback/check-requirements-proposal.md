# Proposal: Machine-Readable Execution Requirements in Check Definitions

*Proposal Version: 0.1-draft*
*Status: Draft — submitted for miri-standard discussion*
*Created: 2026-08-18*
*From: the miri-py implementation team*

## Abstract

Implementing the first eleven checks surfaced the last place where conforming linters must invent semantics the
standard doesn't define: **which checks may legitimately be skipped under which operating constraints**. Whether a
check needs the network, the previous release, or code execution lives today only in prose — so two conforming linters
running offline can skip *different* check sets for the same wheel, forfeit different weights, and report different
conformance scores. That is the same divergence surface the standard has now closed twice, for severity and for
population denominators, by moving the decision into the check definitions. We propose closing it the same way: an
optional **`requirements`** field in `check-v1.json`, with canonical values. This document includes the
proposed values for all 40 Python checks, and one reconciliation question the audit surfaced.

## 1. Completeness Audit: What an Implementation Consumes

Building miri-py's check runner, everything an implementation needs comes from the definition files — with one gap:

| Implementations need | At the source today? |
|---|---|
| Identity, level, weight, category | ✅ `id`, `level`, `weight`, `category` |
| Severity + counting unit | ✅ `severity.default`, `severity.violation_unit` |
| Density denominator | ✅ `severity.population_unit` (added with the count-normalization response) |
| Conditionality flag | ✅ `conditional` |
| Human guidance (descriptions, fix, examples, references) | ✅ all present |
| Versioning | ✅ `added_in` / `withdrawn_in` / `status` |
| **Which operating constraints justify a skip** | ❌ prose only — implementation-inferred |

We do **not** propose machine-readable *condition triggers* for conditional checks (the trigger logic — e.g.
"bundles non-Python components" — must live in implementation code regardless; a declarative encoding buys nothing),
nor any derivable data. The gap is the skip semantics alone.

## 2. The Proposed Field

In `check-v1.json`, under the top level of a definition:

```yaml
requirements: []                    # default: pure static analysis of the artifact
# or any of:
requirements: [network]             # live external endpoints (index APIs, URL resolution)
requirements: [previous-release]    # the prior release's artifact or metadata
requirements: [execution]           # executing artifact code (sandboxed)
```

Semantics:

1. A linter operating without a listed capability MUST skip the check with the corresponding reason — and MUST NOT
   skip a check whose requirements it satisfies. Skips remain *forfeited and reported* per the checklist's existing
   rule (conditional-not-applicable is unrelated and keeps full weight).
2. Reason mapping is fixed: `network` → `network_unavailable`; `previous-release` → `previous_release_unavailable`;
   `execution` → `execution_disabled`. These are exactly the `skip_reason` values already serialized by the
   `lint-report-v1.json` draft — the field completes a loop the report format exposes.
3. An empty/omitted `requirements` means the check is computable from the artifact alone; skipping it is
   non-conforming behavior.

With this, "same wheel, same constraints, same score" holds for offline and sandboxed runs, not just full-capability
runs.

## 3. Proposed Values for the 40 Python Checks

Committee homework included — assignments derived from each check's own description:

| Requirement | Checks |
|---|---|
| *(none — static)* | 001, 002, 003, 004, 006, 007, 008, 010, 011, 012, 013, 014, 016, 017, 018, 019, 020, 021, 022, 023, 024, 025, 028, 029, 031, 032, 033, 037, 038, 039 |
| `network` | 005 (index attestations), 009 (determining "non-initial release" needs release history; validation itself is static), 026 (the VEX URL must *serve* a document), 027 (security policy "resolvable") |
| `previous-release` | 030 (removals since prior release), 034 (≥2-release grace period) |
| `execution` | 015 (examples run in sandbox), 035 (DeprecationWarning fires), 036 (discovery APIs importable), 040 (graceful degradation under stripped metadata) |

Notes: 021/023 verify *well-formedness* of URLs per their descriptions — static; if the standard intends
reachability, they become `network`. 009's dual nature (network to determine the condition, static to validate) argues
for `network` with the documented fallback that an offline linter treats an absent file as condition-not-applicable —
which is what miri-py ships today.

## 4. A Reconciliation Question the Audit Surfaced

The checklist's implementer notes say checks **029/030/031** require the previous release. Their own definitions
disagree for two of the three: 029 compares PEP 702 markers against `migration-guide.json` — both inside the current
wheel — and 031 resolves `replacement` targets against the current `sdk-manifest.json`. Only 030 (silent removals)
genuinely needs the prior release. We propose `requirements: [previous-release]` on 030 alone, and a correction to the
checklist note — or, if the standard intended cross-release semantics for 029/031, definitions that say so. Either
way, the `requirements` field is what makes such a discrepancy impossible to leave ambiguous in future.

## 5. Cost and Compatibility

- Schema: one optional array field with a three-value enum; `additionalProperties: false` is preserved.
- Data: values on ~10 of 40 Python files (and the CLI suite analogously); the rest omit the field.
- Backward compatible: absence means static, which is today's implicit default for most checks.
- miri-py commits to consuming the field the release it ships (our sync/model layer picks up schema additions
  automatically, as `population_unit` demonstrated) and to removing our hardcoded skip decisions in its favor.

---

*Prepared by the miri-py team, following the check-runner implementation experience. Companion deliverables pending
submission: `scoring-v1.json` and `lint-report-v1.json` drafts, the blended-aggregate answer, and the wheel-population
measurement script.*
