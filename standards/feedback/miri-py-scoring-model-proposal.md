# Scoring Model Proposal: One Conformance Score, One Health Score

*Proposal Version: 0.1-draft*
*Status: Draft — submitted for miri-standard discussion*
*Created: 2026-08-18*
*From: the miri-py implementation team*

## Abstract

The new [Linter Checklist](https://github.com/miri-whl/miri-standard/blob/main/standards/python/linter-checklist.md)
(v0.1-draft) gives the Python standard its first scoring model: 40 checks (`MIRI-PY-001`…`040`), fixed weights summing
to 100, MUST/SHOULD levels, and Gold/Silver/Bronze grade bands. Independently, the miri-py reference linter has been
running a different, more granular scoring engine in production: severity-graded violations, four pluggable scoring
methods, configurable strictness profiles, and quality dimensions (code quality, external tooling, security scanning)
that the checklist does not cover. The two models were designed without sight of each other, and each solves a problem
the other cannot.

This proposal argues they answer **different questions** and should both be standardized: the checklist's additive model
as the normative **Conformance Score** ("does this wheel conform, and how completely?"), and a severity-graded penalty
model as the normative-baseline **Health Score** ("how bad is what's wrong?"). One number for interoperability, one for
diagnosis — never conflated into one.

## 1. The Motivating Example

Two wheels both fail `MIRI-PY-015` (*examples runnable*):

- **Wheel A**: 1 of 40 examples fails to execute (a missing optional import).
- **Wheel B**: all 40 examples fail to execute.

Under the checklist model these wheels are **indistinguishable**: both lose the same 3 points, both are capped at 74 as
non-conforming. Under a graded model they are worlds apart: one MEDIUM violation versus forty. An agent deciding whether
to trust the examples directory needs the second signal; a registry deciding whether to award a badge needs the first.

The inverse failure exists too. In miri-py's current blended scoring, a critical structural failure can be *averaged
away* by strong scores in other layers — there is no conformance gate. The checklist's "any failing MUST ⇒
non-conforming, cap at 74" rule is exactly the gate our model lacks.

Neither model is wrong. They are answering different questions, and each currently pretends to answer both.

## 2. The Two Models Today

### 2.1 The Checklist Model (miri-standard, new)

- **Additive reward**: Score = Σ weights of *passing* checks; weights fixed by the standard, summing to exactly 100.
- **Binary checks**: each of the 40 checks passes or fails, with no magnitude.
- **Conformance gating**: any failing MUST check ⇒ non-conforming regardless of score; score still reported, capped
  at 74.
- **Stable IDs**: `MIRI-PY-NNN`, never renumbered; withdrawn checks redistribute weight in a minor version.
- **Grade bands**: 90–100 Gold, 75–89 Silver, 50–74 Bronze, <50 non-conforming.
- **Conditional checks** score full weight when the condition does not apply.

Strengths: deterministic, reproducible, and — critically — **comparable across independent linter implementations**.
Two conforming linters must produce the same score for the same wheel. This is the property a standard must protect.

Limitations: binary checks discard magnitude (§1); fixed weights cannot express an organization's risk posture; a
single number is asked to carry both "conforms" and "is healthy".

### 2.2 The miri-py Model (implemented, production)

- **Penalty-based**: violations are extracted with one of five severities (LOW=1, MINOR=2, MEDIUM=3, HIGH=4,
  CRITICAL=5) and deducted from 100.
- **Four scoring methods**, each with published formula and configuration:
  1. *Weighted Linear Deduction* — `max(0, 100 − Σ(weightᵢ × countᵢ))`; the shape used across compliance frameworks
     (NIST, ISO 27001, SOC 2).
  2. *Exponential Decay* — `100 × e^(−k × Σ(severity² × count))`; smooth degradation, never reaches zero.
  3. *Tiered Penalty with Caps* — escalating per-severity penalties with per-severity maximums, so one violation class
     cannot dominate.
  4. *Risk-Weighted Composite* — `100 / (1 + Σ(severity³ × count × frequency) / threshold)`; actuarial shape with
     frequency weighting.
- **Named strictness profiles**: strict / balanced / lenient severity-weight presets
  (balanced default: 0.2 / 0.8 / 2 / 5 / 10 for LOW→CRITICAL).
- **Dimensional blend**: six validation layers (standard wheel, external tools, Miri compliance, quality assessment,
  best practices, changelog) combined by weight.
- **Coverage beyond conformance**: external packaging tools (`twine check`, `pyroma`, `pydistcheck`,
  `check-wheel-contents`), code-quality analyzers (coverage, type-annotation coverage, docstring coverage, cyclomatic
  complexity), and security scanners (bandit, pip-audit) — none of which appear in the 40 checks, deliberately or not.

Strengths: magnitude-aware, risk-curve-aware, tunable to context.

Limitations, stated honestly: scores are **not comparable** across tools or even across configurations of the same
tool; findings do not yet carry stable IDs; and there is no conformance gate — the blend can hide a MUST-level failure.

## 3. Proposal: Standardize Both, Bind Them Together

### 3.1 Conformance Score (normative — the checklist, unchanged)

Adopt the checklist model exactly as drafted for the conformance number: additive, fixed weights, MUST-gating with the
74 cap, Gold/Silver/Bronze. This is the number that travels — registries, badges, CI gates, cross-linter comparison.
We propose **no changes to its semantics**. It is the right model for its question, and its comparability across
implementations is worth more than any added sophistication.

### 3.2 Health Score (normative baseline, extensible by declaration)

Add a second standardized number answering "how bad is what's wrong?":

1. **Severity vocabulary** (normative): five levels — LOW, MINOR, MEDIUM, HIGH, CRITICAL — with numeric values 1–5.
2. **Violation binding** (normative): every violation a linter emits carries the `MIRI-PY-NNN` check ID it was found
   under, a severity, and a location. A check *fails* for conformance purposes per the checklist's own definition; the
   full violation set, with counts and severities, feeds the health score. This is the bridge between the models: one
   check, many graded violations.
3. **Baseline method** (normative): Weighted Linear Deduction — `max(0, 100 − Σ(wᵢ × countᵢ))` — with a
   standard-published default weight set. Simple, explainable, and the industry-standard shape.
4. **Named profiles** (normative): `strict` / `balanced` / `lenient` weight presets published in the standard, so "CI
   gate at health ≥ 80, profile balanced" means the same thing in every toolchain.
5. **Alternative methods** (informative annex): exponential decay, tiered penalty with caps, and risk-weighted
   composite, with their formulas and configuration schemas — implementations MAY offer them.
6. **No naked scores** (normative): a reported health score MUST be accompanied by its method identifier and profile
   (or full parameter set). A health score without its formula is noise; this rule keeps extensibility from destroying
   comparability.

### 3.3 Extension Checks for Quality Dimensions

The 40 checks deliberately stop at conformance. The quality dimensions miri-py measures today (external tool findings,
code-quality analyzers, security scanning) are valuable but should never gate conformance or perturb the conformance
score. We propose a reserved extension namespace — e.g. `MIRI-PYX-NNN` — for standardized quality checks that
contribute **only to the health score**. This gives the ecosystem one vocabulary for quality findings without
reopening the weight table every time a new analyzer appears.

### 3.4 Machine-Readable Deliverables

The checklist already plans a `checklist.json`. We propose it carry, per check: `id`, `level` (M/S), `weight`,
`category`, `conditional`, and references — and that the standard add two sibling schemas:

- `scoring-v1.json` — the severity vocabulary, method definitions, and named profiles as data.
- `lint-report-v1.json` — the report format: per-check outcomes, violations (check ID + severity + location), both
  scores, grade band, and the health score's method/profile declaration.

With those three files, "conforming linter" becomes a testable claim: same wheel in, same conformance score and same
baseline health score out.

## 4. What miri-py Commits To

This proposal is not only an ask. If the two-score model is adopted, miri-py will:

1. **Adopt `MIRI-PY-NNN` as the primary finding IDs**, mapping its existing internal rules (`PEP427-NNN`, `MIRI-NNN`,
   `FILE-NNN`, …) onto the standard checks and retiring free-text-only findings.
2. **Implement all 40 checks**, including the new Identity & Security (018–027) and Deprecation Coherence (028–035)
   categories, and report the conformance score exactly per the checklist.
3. **Ship both scores** in every report, with the method/profile declaration of §3.2-6.
4. **Contribute the scoring engine as the reference implementation** of the baseline method and the annex methods —
   the four methods, the profile system, and their tests already exist and are extractable.
5. **Contribute drafts** of `scoring-v1.json` and `lint-report-v1.json`, and a generator for `checklist.json` following
   the standard's schema-as-data rule (one source for the markdown table and the JSON).

## 5. Worked Example

A wheel passes 37 of 40 checks, failing `MIRI-PY-015` (examples runnable, M, weight 3), `MIRI-PY-017` (error handling
shown, S, weight 2), and `MIRI-PY-034` (grace period, S, weight 2).

**Conformance**: 100 − 7 = 93, but a MUST check failed ⇒ **non-conforming, reported 74-capped: 74**. Identical for
Wheel A and Wheel B of §1. This is correct — conformance is binary-with-distance, and both wheels are non-conforming.

**Health** (baseline method, balanced profile): Wheel A's violations are 1 MEDIUM + 3 MINOR →
`100 − (1×2 + 3×0.8) = 95.6`. Wheel B's are 40 MEDIUM + 3 MINOR → `100 − (40×2 + 3×0.8) = 17.6`.

The pair (74, 95.6) says: *one small thing blocks conformance — fix it and this is a Gold wheel*. The pair (74, 17.6)
says: *the examples directory is broken end to end*. Today, both the checklist alone and miri-py alone would report
these two wheels as the same number.

## 6. Summary of Asks

| # | Ask | Change to standard |
|---|---|---|
| 1 | Keep the checklist's conformance model unchanged | none — endorsement |
| 2 | Add a normative Health Score: severity vocabulary, violation-to-check binding, baseline weighted-linear method, named profiles | new section in linter-checklist.md |
| 3 | Require method+profile declaration on any reported health score | new conformance rule |
| 4 | Reserve `MIRI-PYX-NNN` extension namespace for quality checks (health-only) | one paragraph |
| 5 | Extend planned `checklist.json` with `scoring-v1.json` and `lint-report-v1.json` | two new schemas (drafts offered) |

---

*Prepared by the miri-py team. Reference implementation of everything in §2.2 is available in the
`miri-py` repository (`src/miri_py/linter/scoring/`; repository not yet public — link withheld).*
