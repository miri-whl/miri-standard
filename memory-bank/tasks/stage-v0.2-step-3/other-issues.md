# Stage v0.2 Step 3 — Decision / funding (the real path to 9)

Neither a spec edit nor a linter fix. Round 4 was unanimous: after the mini step-3, **these are what stand between the
standard and a 9** — and none of them is documentation work. Prioritized by leverage.

## The experiment (the only thing that moves the AI Researcher off 5)

- [ ] **Freeze the pre-registration.** Add the frozen-status line + date to
      `miri-py/docs/validation/kill-or-validate-preregistration.md` — a five-minute integrity gate that must precede
      any run. _(AI Researcher)_
- [ ] **Fund and run the experiment as written** (~$2–5k, ~2 weeks): ≥2 real tool-use harnesses, ≥3 packages, ≥3
      seeds/cell, all 7 conditions, executable pytest ground truth, **every cell published regardless of sign**. This
      is the load-bearing item — nothing else touches the empirical score. _(AI Researcher)_
- [ ] **Honor the pre-registered decision rule and its kill branch.** Adopt-worthy only if condition 4/5 beats the
      stubs+docstrings baseline by ≥10pp pass rate (or ≥30% tokens at equal pass), replicated across both harnesses,
      with the stale-metadata arm showing no regression vs package-only. A cleanly-published **negative** that the
      maintainer then acts on is still a real result (~7, "finally an answer"); a positive clearing the rule is the 9.
      _(AI Researcher)_

## Adoption (the ceiling on the whole standard's credibility)

- [ ] **Land one genuinely independent external adopter** — a wheel maintained by someone who is not the maintainer,
      that reaches Core-conforming because its author chose to, with the diff published. Until this exists, the project
      is "a well-specified one-person proposal," not an adopted standard. Gets most of the way to 8 on its own. _(OSS,
      Packaging)_

## Then

- [ ] **Move to the 0.3 consumption-spec RFC** (`proposals/20260821-consumption-specification.md`) — but _after_ the
      experiment reads out. Building more spec before then "just widens the gap between what's asserted and what's
      shown." The RFC already carries the security work (Ask 4 reshape, adversarial fixture) correctly scoped and
      deferred. _(AI Researcher; whole panel)_

## Reference (not action items)

- **75/Silver is the project scoring its own artifact — not agent-benefit evidence.** The new CI gate makes that
  self-scoring continuous; keep it framed as _conformance_, never as validation of the benefit claim, whenever the
  number is cited externally. _(AI Researcher)_
- The only data that ever existed (the retired pilot) trended **negative** (−0.44). The experiment is as likely to
  kill the claim as confirm it — which is exactly why running it is the honest move. _(AI Researcher)_
