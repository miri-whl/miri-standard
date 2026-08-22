# Response: Count Normalization Proposal

*Response Version: 0.1-draft*
*Status: Draft — miri-standard maintainers' response*
*Created: 2026-08-18*
*In reply to: [count-normalization-proposal.md](count-normalization-proposal.md)*

## Summary

**Accepted, with one amendment.** Raw counts stay in the baseline health score; population and violation density become
report-level data that never enter the number. This is our "declare sources, not verdicts" principle applied to
normalization, and your §2.2 argument — that every population definition is a surface where conforming linters can
diverge — is the same argument that produced the canonical check definitions. You applied our own reasoning
correctly, and we adopt the conclusion.

The amendment closes a hole in the proposal's own terms: as drafted, `population` is a SHOULD-optional,
implementation-computed field — which demotes the divergence problem from the score to the report rather than
eliminating it. Two linters counting "total examples" differently produce non-comparable `violation_density` for the
same wheel, and density is precisely the field registries will rank on. The fix is the same move that resolved
severity: **population definitions belong in the check definition files.** See §2.

## 1. What Is Accepted As Proposed

- **Baseline counts are raw** — no scaling, caps, or population adjustment inside the score. Implementations MUST NOT
  normalize the baseline. The Wheel A/B anchor numbers (95.6 / 17.6 under `balanced@1`) stand as the baseline's
  reproduction target.
- **Health is magnitude.** Forty broken examples are forty traps and forty repair items regardless of how many healthy
  ones sit beside them; size-adjusted comparison is a different question and gets a different, defined field.
- **Saturation is signal.** A diagnostic magnitude that reaches 0 when the surface is broken end to end is behaving
  correctly; consumers wanting asymptotic degradation declare the exponential-decay annex method — no-naked-scores
  makes that safe.
- **Caps stay an annex method.** No central cap table in the baseline.
- **The promotion path** (§3.4): a future density-based method enters as a *new named method* in a minor version,
  leaving the baseline untouched. This is the correct additive use of the no-naked-scores rule, and we endorse it
  explicitly.

## 2. The Amendment: Standard-Defined Population Units

The standard's check definitions (`standards/<target>/checks/`, [check-v1.json](../../schemas/check-v1.json)) now
carry an optional **`severity.population_unit`** alongside `violation_unit`: the canonical countable
population for per-instance checks. Examples now shipped:

- `MIRI-PY-015` — violation unit: "each example that fails to compile or execute"; population unit: "all example
  files listed in AGENT_EXAMPLES.json".
- `MIRI-PY-030` — population unit: "all public interfaces removed since the previous release".
- `MIRI-CLI-008` — population unit: "all commands in --describe".

Note that these denominators are deliberately defined in terms of **Miri metadata itself** (the example index, the
sdk-manifest, `--describe`) wherever possible — that is what makes them crisp enough to be normative. Per-artifact
singleton checks ("the wheel archive", "the update_check declaration") define no population unit, exactly matching
your observation that normalization is a question about a minority of checks.

Binding rules for your `lint-report-v1.json` draft:

1. Where a check defines a `population_unit`, a conforming report **MUST** carry `population` for that check's
   outcome (your draft said SHOULD).
2. Where no `population_unit` is defined, `population` MUST be omitted — implementations do not invent denominators.
3. `violation_density = count / population` remains a derived, score-free report field as you specified.

With this, both numbers in your §4 worked example are fully standard-defined: Wheel B and Wheel C share a health score
because their brokenness is identical in magnitude, and their densities (1.0 vs 0.10) are comparable because the
denominator is canonical, not linter-chosen.

## 3. One Note on the Evidence

The 400-wheel scan is persuasive motivation — 3.5 orders of magnitude across populations is the empirical kill-shot
for any fixed normalization constant — but a scan of one developer machine's caches cannot be cited as a normative
basis. We would welcome the measurement script as a contribution (a `tools/` or `research/` home can be arranged) so
the number is reproducible against any cache, and future population-unit decisions can lean on it honestly.

## 4. State of the Open Items

| Item | Owner | State |
|---|---|---|
| Severity vocabulary + violation units | standard | Shipped (`checks/`) |
| Population units | standard | Shipped with this response (§2) |
| Count semantics (raw, unnormalized baseline) | standard decision, lands in `scoring-v1.json` | Decided here |
| `scoring-v1.json` / `lint-report-v1.json` drafts (cross-language, versioned profiles) | miri-py | Awaited |
| Blended-aggregate question (response §5 to the two-score proposal) | open | Awaiting your production view |

---

*miri-standard maintainers. Discussion: open an issue or thread on the
[miri-standard discussions board](https://github.com/miri-whl/miri-standard/discussions).*
