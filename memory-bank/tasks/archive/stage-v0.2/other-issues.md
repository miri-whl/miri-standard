# Stage v0.2 — Other issues

Everything the panel raised that is neither a standard edit nor a linter-conformance fix: miri-py pre-publication
blockers, the evidence/validation problem, and repo hygiene. Most of these are about **making miri-py safe and
honest to publish**.

## P0 — miri-py pre-publication blockers (before the repo goes public)

- [ ] **Scrub git history.** All 20 commits are authored as `emiliano.berenbaum@cielara.ai` and
      `emiliano@medlista.com`, linking the author's identity across cielara.ai, medlista.com, and patitur. Use
      `git filter-repo` or squash to fresh history before the public push — or accept the linkage deliberately.
      _(security)_
- [ ] Scrub the local path leak `/Users/bishop/work/patitur/...` (in `memory-bank/techContext.md`). _(security)_
- [ ] Publish miri-py to PyPI at the same time the repo goes public — every doc's first command is
      `pip install miri-py`, which currently fails ("No matching distribution found"). _(skeptic)_

## P0 — evidence and honesty (highest urgency per the AI researcher)

- [ ] **Quarantine the invalid experiment.** `validation-frameworks/exports/` holds a one-day pilot whose "MIRI"
      condition scored a _negative_ mean quality delta (−0.44) on metadata-free wheels, with a hardcoded fake stub
      (`# For now, simulate MIRI metadata`) and canned rows logged as real API calls (including a "claude-5-sonnet"
      that did not exist in Sept 2025). Delete it or clearly label it an invalid pilot. _(AI researcher)_
- [ ] Correct `memory-bank/phase-status-summary.md`: the "Proven MIRI Value: +3.1 quality improvement" /
      "statistical evidence" claims are one cherry-picked cell from data whose mean is negative. Publishing the repo
      ships this claim next to the CSVs that refute it. _(AI researcher)_
- [ ] Drop `budget/`, `rich-analysis.json`, and `memory-bank/` from the public repo — internal ops telemetry and a
      dev diary that also discloses unreviewed AI-generated commits on `main` and frames the "committee" as one
      person driving an agent. _(security and AI researcher, independently — the single most publication-dangerous
      content)_
- [ ] Fix or remove the `compare-agents` CLI stub ("TODO … coming soon!") while `miri --help` advertises it as a
      working quality command. _(AI researcher)_

## P1 — CI and repo hygiene (miri-py)

- [ ] CI: add `permissions: contents: read`; SHA-pin `actions/checkout`, `setup-python`, `cache`. _(security)_
- [ ] Shrink the ruff ignore list (19 rule classes including F821 undefined-names); raise the 50% coverage floor.
      _(skeptic)_
- [ ] Quarantine or delete the legacy engine so a public reader does not find two parallel lint systems:
      `linter/main.py` (48 KB), `validators/` (70 KB), `validation-frameworks/`, the retired 134-rule engine, and
      the abandoned `standards-contribution/` design docs. _(agent-tooling, skeptic)_
- [ ] Remove committed working dirs (`.claude/`, `.cursor/`); commit or generate the missing test-fixture wheel so
      `tests/.../test_standard_whl.py` actually runs (it currently skips itself and would pass on the false
      positive anyway). _(skeptic)_
- [ ] Add the `CONTRIBUTING.md` that `QUICKSTART.md` references. _(skeptic)_

## P2 — make the claims true (validation)

- [ ] Run the kill-or-validate experiment before any adoption ask: 3 packages (real, post-cutoff or
      API-perturbed), 30–50 executable-ground-truth tasks, 7 conditions **including a stale-metadata harm
      condition** and an organic-discovery condition, metrics = task pass rate + hallucinated-symbol rate +
      deprecated-API-use rate + tokens. Pre-registered decision rule: adopt-worthy only if Miri beats
      docstrings/stubs by ≥ 10pp pass rate or ≥ 30% tokens at equal pass rate, replicated, with no stale-condition
      regression. ~$2–5K, ~2 weeks. Publish results regardless of sign; until then the public posture is
      "unvalidated design." _(AI researcher)_
- [ ] Rebuild the eval harness honestly if kept: real metadata physically in the wheels, symmetric prompts (no
      "Enhanced with MIRI: Yes" framing), executable pass/fail plus hallucinated-symbol rate, no LOC-as-improvement
      metric, statistics or no claims. _(AI researcher)_
- [ ] Prototype one harness-side consumer — an MCP / context-provider that surfaces `lifecycle.json` at agent
      decision time — and measure whether agents ever open `agent-metadata/` unprompted. If not, the wheel is the
      wrong delivery vehicle and the standard should say so. _(AI researcher, agent-tooling)_
