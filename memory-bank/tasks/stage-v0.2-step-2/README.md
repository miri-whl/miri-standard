# Stage v0.2 — Step 2 (post-Round-3)

This workstream parses the **Round 3 panel review** (`.generated/miri-panel-review-2026-08-21-1200-round3.pdf`)
into actionable items. Round 3 re-scored the project with miri-py finished and a real dogfooding report in evidence.

**Outcome:** every panelist raised their score — median **5 → 7**, mean **5.0 → 6.7**, spread **2–7 → 5–8**
(OSS 5→6, CLI 5→7, Security 5→7, Agent-Tooling 6→7, Packaging 7→8, AI Researcher 2→5). The panel credited the
finished, honest, dogfooded linter and the cleared spec debt, and converged on three unflattering, reproduced facts:

1. The flagship "89 Silver" does **not** reproduce — the checked-in sample SDK scores **71–74/non-conforming** under
   the standard's own linter (stale `generated_at` trips MIRI-PY-011), and the standard repo's CI never builds/scores it.
2. The **published contract now lags the honest implementation** — the spec + `api-graph-v1.json` still advertise
   fabricated fields the linter refuses to emit; the sample ships an orphan `examples-index.json`; some metadata still
   points `$schema` at the old `miri-standard.org` domain.
3. The core "agents do measurably better" claim still has **zero data** (experiment built but unrun), and the
   governance/authorship "committee" framing persists.

## Files

- `standard.md` — **our side** (the `miri-standard` repo): the primary list to burn down on the next branch.
- `miri-py.md` — items for the separate `miri-py` repo, captured so nothing is lost (not our branch).
- `other-issues.md` — cross-cutting / user-gated (governance decision, the experiment, adoption).

## How to work it

The next branch is cut off `stage-0.2` after the PR merges. Match the house invariants: when a check YAML or schema
changes, move the checklist prose and any example in the **same commit** and re-run the `schema-governance` and
`check-authoring` skill invariants (weights sum to 100; every example validates against its schema; check IDs never
renumbered). Every item below is cited to the panelist(s) who raised it and to a verified `file:line`.
