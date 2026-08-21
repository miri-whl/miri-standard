# Stage v0.2 — backlog

Three actionable lists derived from the two-round developer panel review (reports archived in
`.generated/miri-panel-review-2026-08-20-1236-round1.pdf` and `...-1333-round2.pdf`). Everything here is the work to
get from 0.1-draft to a defensible 0.2.

## The three lists

- `standard.md` — changes to **this repo**: spec text, check YAMLs, JSON Schemas, checklists, the site, governance
  and honesty docs, the sample SDK.
- `miri-py.md` — changes to the **reference linter** (`miri-py` repo): making the `miri` CLI itself conform to the
  MIRI-CLI rules we publish (dogfooding), and fixing the linter's check implementations so they enforce the standard
  correctly.
- `other-issues.md` — everything else raised: miri-py pre-publication blockers, the evidence/validation problem,
  and repo hygiene.

## Priority key

- **P0** — do before miri-py goes public / before the next tag. Honesty, blockers, release-breakers.
- **P1** — reconcile spec and implementation; fix shipped contradictions; close schema-enforcement gaps.
- **P2** — scope, adoption on-ramp, and the longer-horizon validation work.

Each item cites its source check ID or finding. Items that must move together across repos are cross-referenced
(e.g. the 007↔012 version pattern touches both `standard.md` and `miri-py.md`).
