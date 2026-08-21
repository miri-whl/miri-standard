# Stage v0.2 Step 2 — Cross-cutting / user-gated

Items that are neither a spec edit nor a linter fix: they gate the project's *credibility ceiling*, and the panel was
unanimous that these — not more engineering — are what stands between "working tool" and "adopted, validated standard."

## The empirical claim (the score ceiling for the AI Researcher, and the whole thesis)

- [ ] **Freeze, fund, and run the pre-registered kill-or-validate experiment.** The harness is built to spec (7 paired
      conditions incl. a stale-metadata-harm arm, a frozen decision rule, integrity-hardened, 12 passing tests) but
      **unrun** — zero data on whether Miri metadata improves agent outcomes. Until it reads out, "unvalidated design"
      is the only honest posture (which the project now correctly holds). _(AI Researcher: "an instrument that refuses
      to run is not a result" — his hard ceiling at 5 until it runs)_
- [ ] **Honor the kill branch.** If the stale-metadata arm (H4) regresses vs package-only, in-wheel bundling is the
      wrong transport — pause any adoption ask until a freshness mechanism exists. Publish negative results.
      _(AI Researcher)_
- [ ] **Pre-wire governance to execute the pre-registered consequences** (e.g. cut api-index from MUST if lifecycle-only
      ≈ full). A frozen decision rule only matters if someone acts on the negative branch. _(AI Researcher)_

## Adoption (converts "the detector works" into "the standard is adoptable")

- [ ] **Earn one external data point.** Get **one real third-party package** (not miri-py's own wheel or the sample
      SDK) to Core-conforming and publish the diff. Every "will it do what it says" answer split the same way: the
      engineering is demonstrated; adoption and agent-benefit are asserted, not shown, because the only conforming
      artifact is the project's own. _(OSS, Packaging, CLI, Security, Agent-Tooling)_

## Governance decision (also tracked in standard.md P3 — the doc-editing half)

- [ ] **Decide the governance posture** — honest single-maintainer/BDFL vs the current committee framing — and the
      **y3bishop3y authorship re-attribution** ("deliberate last step"). This is the one dishonesty a reviewer can
      prove from `git shortlog`; the OSS Maintainer says fixing it would raise his score most, at zero engineering
      cost. **Emiliano's call**; the doc edits that follow live in `standard.md` P3. _(OSS Maintainer)_

## Reference (not action items)

- The **89-vs-47 spread is not adoption or agent-benefit evidence** — both ends are the project scoring itself, and
  the 89 end doesn't even reproduce. It shows the linter runs end-to-end and emits a legible, provenance-stamped
  negative. Keep this framing whenever the numbers are cited externally. _(all panelists)_
