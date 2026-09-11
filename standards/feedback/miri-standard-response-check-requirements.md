# Response: Check Execution Requirements Proposal

*Response Version: 0.1-draft*
*Status: Draft — miri-standard maintainers' response*
*Created: 2026-08-19*
*In reply to: [check-requirements-proposal.md](check-requirements-proposal.md)*

## Summary

**Accepted, and your correction is taken.** Skip semantics were indeed the last implementation-inferred decision left
in the conformance path, and the argument is the one the standard has now settled three times: any place where two
conforming linters can legitimately diverge must be closed by data in the check definitions. The `requirements` field
ships with this response — schema, Python values per your §3 (with the confirmations below), and the CLI suite's
values assigned alongside. Your §4 reconciliation is correct: our implementer note overclaimed — `MIRI-PY-029` and
`MIRI-PY-031` are computable from the current wheel alone, only `MIRI-PY-030` needs the prior release. The note is
corrected rather than the definitions; thank you for reading our files more carefully than our notes.

We also accept the scoping restraint in §1: no declarative condition triggers for conditional checks, no derivable
data. The field covers skip semantics alone.

## 1. What Shipped

`check-v1.json` gains an optional top-level **`requirements`** array, enum `network` / `previous-release` /
`execution`, with your three semantics adopted verbatim:

1. Missing capability ⇒ MUST skip with the fixed reason (`network_unavailable` / `previous_release_unavailable` /
   `execution_disabled`); satisfied capability ⇒ MUST NOT skip. Skips stay forfeited-and-reported; conditional
   non-applicability remains a separate, full-weight concept.
2. Absent/empty `requirements` means computable from the artifact alone; skipping such a check is non-conforming.
3. One definitional refinement, needed the moment the field crosses targets: requirements are declared **relative to
   the target's baseline analysis mode** — static file inspection for wheels, *local invocation of the tool* for
   CLIs. A CLI linter that cannot run the binary cannot analyze it at all, so "execution" is the CLI baseline, not a
   requirement; the field marks only capabilities beyond the baseline. This keeps the field meaningful instead of
   decorating all 43 CLI checks with `[execution]`.

## 2. Python Values: Adopted with Two Confirmations

Your §3 table is adopted as proposed. On the two flagged items:

- **`MIRI-PY-021`/`023` are static, as you inferred.** The intent is on record in the lifecycle specification's
  conformance section: sources must be "reachable-by-construction (a well-formed URL or path, not a placeholder)" —
  deliberately not live reachability, for exactly the offline-determinism reason your proposal is built on. Live
  probing of declared endpoints is a health-side concern for an extension check (`MIRI-PYX-`), if anyone wants it.
- **`MIRI-PY-009` is `network`, with your fallback adopted as normative**: an offline linter treats an absent
  migration guide as condition-not-applicable. The asymmetry is intentional — offline, a missing file cannot be
  distinguished from a first release, and conformance must not depend on a guess.

  **Correction, 0.5.0.** This bullet originally said condition-not-applicable meant *"full weight"*, taking that
  wording from `check-v1.json`, whose own description said exactly that. As of 0.5.0 the rule is reversed: a check
  whose condition does not apply is **excluded from both the numerator and the denominator**, never awarded its
  weight — stated now in `check-v2.json` and in both producer checklists. `check-v1.json` still reads "full weight",
  because it is the frozen pre-0.5.0 record and a linter pinned there is internally consistent rather than wrong;
  that a reversal of meaning left the shape untouched is precisely why the schema was bumped instead of edited. For
  `MIRI-PY-009` the practical effect is that an offline linter's score is computed over a denominator three points
  smaller, rather than over 100 with three points granted.

  **Second correction, same release.** Offline, `MIRI-PY-009` is a **forfeit**, not an exclusion. Both leave the
  denominator so the score is identical, but the precedence rule now in both producer checklists says that where
  *whether the condition applies* cannot itself be settled, the check is forfeited — and offline a missing migration
  guide genuinely cannot be distinguished from a first release, which is the reason this bullet gave in the first
  place. The consequence is that an offline lint reports conformance for that check as `undetermined` rather than met.
  That is stricter than the answer we first gave you, and we think it is the honest one: "we could not tell" is not the
  same claim as "the obligation did not apply".

## 3. CLI Values

Assigned with this response, under the §1-3 baseline rule (local invocation is the CLI baseline):

| Requirement | Checks |
|---|---|
| *(none — baseline)* | 001–027, 029, 031, 032, 034, 038–043 |
| `network` | 028 (verifying `urgency: security` requires knowing which advisories cover the running version) |
| `previous-release` | 030 (changelog coverage), 033 (identifying removed surfaces), 035 (grace period), 036 (changelog coherence), 037 (silent removals) |

Note `MIRI-CLI-027` (offline degradation) requires *denying* the tool network access, which any runner can do; it is
baseline, not a capability.

## 4. Bookkeeping

- The Python implementer note now names `MIRI-PY-030` alone for previous-release fetching; the CLI note (036/037 plus
  030/033/035) is superseded by the field itself — both notes now defer to `requirements` as the authoritative list.
- The three `skip_reason` values are confirmed as the report-format vocabulary; encode them in the
  `lint-report-v1.json` draft as proposed.
- Your commitment to drop miri-py's hardcoded skip decisions in favor of the field, in the release that picks up the
  new sync, is noted and welcomed.

---

*miri-standard maintainers. Discussion: open an issue or thread on the
[miri-standard discussions board](https://github.com/miri-whl/miri-standard/discussions).*
