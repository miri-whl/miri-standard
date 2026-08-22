# Stage v0.2 — Step 3 (post-Round-4)

This workstream is the **mini step-3** the panel prescribed in Round 4
(`.generated/miri-panel-review-2026-08-21-1955-round4.pdf`). Round 4 re-scored the standard after the step-2 fixes:

**Median 7 → 8; every panelist held or rose** (OSS 6→7, CLI 7→8, Security 7→8, Agent-Tooling 7→8, Packaging 8→8.5,
AI Researcher 5→5). Nobody reached 9. The panel was unanimous on why: **the standard repo's internal work is essentially
done; the gap to 9 is a short set of standard-repo cleanups plus cross-repo and decision work that no spec edit can
substitute for.**

So step-3 is deliberately small. Do the standard-repo cleanups here, then move to the 0.3 consumption-spec RFC and the
cross-repo/decision work (publish miri-py, one external adopter, run the experiment).

## Files

- `standard.md` — **our side** (the `miri-standard` repo): the mini step-3 to burn down on this branch
  (`stage-0.2-step-3`).
- `miri-py.md` — items for the separate `miri-py` repo, carried forward from Round 4 (and the step-2 archive).
- `other-issues.md` — the decision/funding items that are the real path to 9 (adopter, experiment) — not repo work.

The step-1 and step-2 backlogs are in `memory-bank/tasks/archive/`; their still-open cross-repo items are consolidated
into `miri-py.md` / `other-issues.md` here so nothing is lost.

## The one-paragraph verdict to keep in view

The standard is, in the panel's words, "a well-specified one-person proposal" that now needs **contact with the outside
world**, not another internal round. A clean 9-across-the-board is gated on the experiment reading out (the AI
Researcher is structurally capped at 5 until then) and on an independent adopter (OSS/Packaging reserve 8+ for it) —
neither of which is a documentation task. Finish the mini step-3, then spend effort outward.
