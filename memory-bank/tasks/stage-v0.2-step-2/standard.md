# Stage v0.2 Step 2 — The Standard (miri-standard repo) — OUR SIDE

Spec text, check YAMLs, JSON Schemas, checklists, sample SDK, CI, governance docs. All items verified against
`stage-0.2` @ `3f698ca`. Each is cited to the panelist(s) who raised it. When a check/schema changes, move the
checklist prose in the same commit and re-run the `schema-governance` / `check-authoring` invariants.

## P0 — flagship credibility (verified regressions from stage-v0.2)

> The stage-v0.2 list marked "sample SDK conforming + gated in CI" as done. The Round-3 panel reproduced that it is
> **not** — four panelists rebuilt it and got 71–74/non-conforming. This is the single most damaging thing a skeptic
> can run (`python -m build && miri score`). Carry it forward and actually close it.

- [x] **Make the sample SDK pass its own linter.** The packaged metadata
      `examples/sample-sdk/src/weather_sdk/agent-metadata/{sdk-manifest,usage-patterns,lifecycle,migration-guide}.json`
      carries stale hardcoded `generated_at` (`2025-08-30`, `2026-08-18`) → trips **MIRI-PY-011** (build-window
      freshness; three stamps spread ~353 days). Fix: generate the metadata at build time with one coherent build
      clock (wire `miri generate` into the sample's build), or commit values that a fresh build keeps in-window.
      _(OSS, CLI, Security, Packaging, Agent-Tooling)_
- [x] **Resolve the MIRI-PY-016 gap for the sample.** `AGENT_EXAMPLES.json` in dist-info is injected by miri-py's
      wheel enhancer, not by `python -m build`. Decide the sample's canonical "conforming" build path uses
      `miri build` (enhancer on), and document it — otherwise a bare `python -m build` will always fail 016.
      _(CLI, Packaging)_
- [x] **Gate the sample in the standard's CI.** Add a job to `.github/workflows/` that builds the sample and runs
      `miri score` (fail on non-conformance, or at minimum on `core_conforming: false`). Today CI is doc-lint / spell
      / structure only. Depends on miri-py being invokable in CI (see `miri-py.md` → PyPI/rc). _(Packaging: "a
      showcase that fails the standard's own linter is the most damaging thing a skeptic can run")_
- [x] **Delete the tracked sample-SDK cruft.** `examples/sample-sdk/src/agent-metadata/` is a **stale duplicate**
      (not packaged; `pyproject.toml` package-data points only at `weather_sdk/agent-metadata/*`). It still points
      `$schema` at `miri-standard.org` and holds the orphan `examples-index.json`. `git rm` the whole `src/agent-metadata/`
      dir, plus the stray `src/_miri.py`; reconcile `src/__init__.py`. **This one cleanup resolves both the
      "$schema wrong domain in our repo" and the "examples-index orphan" findings.** _(Agent-Tooling)_

## P1 — spec ↔ implementation contradictions (fix before implementers encode them)

- [x] **api-graph contract lies — make the spec + schema tell the truth.** The reference builder refuses to emit
      scored/derived fields, but both `schemas/api-graph-v1.json` and the spec example still advertise them. Remove,
      or normatively mark "reserved — not emitted": on `graph_node` → `centrality`, `dependencies`, `dependents`,
      `common_with`, `complexity`; on `graph_edge` → `pattern`, `frequency`; and the top-level `workflows` block.
      Update both `schemas/api-graph-v1.json` (lines ~28, 44, 50, 55, 60, 98, 124) and
      `standards/python/miri-agent-metadata-specification.md:§4.5` (lines ~428–457), then re-run schema-governance so
      the trimmed example still validates. _(Agent-Tooling — his single gate to 8/10: "the contract advertises
      fabrication the code correctly refuses")_
- [x] **Resolve the CLI-018 self-contradiction.** `standards/cli/checks/MIRI-CLI-018.yaml` (lines 14, 24) and the CLI
      checklist demand `identity.schema_version`, but `standards/cli/cli-lifecycle-specification.md:143` says
      `schema_version` is a **top-level field, not inside `identity`**. A spec-conforming CLI therefore fails 018.
      Decide canonical: fold 018's "independent-of-release-version" intent onto the top-level `schema_version` (and
      dedupe vs MIRI-CLI-010), or give `identity` its own declared block-version. Align the check YAML, the checklist,
      and `schemas/cli-describe-v1.json`. _(CLI Author)_

## P2 — coherence / wording

- [x] **Fix the Core profile off-by-one.** `standards/python/linter-checklist.md:39` calls Core a "15-check set" but
      the enumeration (001–005, 013, 018–023, 033, 040) is **14**, matching miri-py's `CORE_PROFILE_CHECK_IDS` (14).
      Change the prose to "14-check", or deliberately add a 15th check and update miri-py in lockstep. (CLI checklist
      Core section has no count claim — no change there.) _(OSS, Packaging)_
- [x] **Purge misleading "sandbox" wording.** The example runner is not a security boundary (Security engineer's
      two-round finding, now honest in miri-py's code). Reword `standards/python/checks/MIRI-PY-015.yaml` (5 refs:
      lines 17, 19, 32, 37, 41) and `standards/python/linter-checklist.md:76`. **Leave** `MIRI-PY-037.yaml:18` — its
      "agent sandbox or air-gapped network" describes the deployment environment, a different and legitimate use.
      _(Security)_
- [x] **Lift code-only semantic rules into spec text.** Rules that make the generators trustworthy live only in
      miri-py docstrings/comments: "emit `configuration`/`error_handling` only from source evidence, omit when
      absent"; "CLI entry points are excluded from `api_index`"; api-graph edge-derivation. Add them to
      `standards/python/miri-agent-metadata-specification.md` so tool authors build to the same contract the linter
      enforces. _(Agent-Tooling)_

## P3 — governance (USER DECISION — verify remnants, do not pre-decide)

- [ ] **Governance honesty.** stage-v0.2 marked "de-committee the framing" and "reframe standards/feedback" as done,
      but the Round-3 panel verified remnants on `stage-0.2`: `GOVERNANCE.md:50-88` still describes a Steering
      Committee + elections with unfilled `[TERM LENGTH]`/`[TIME PERIOD]` placeholders; `README.md:207` "Steering
      Committee: [To be established]"; "committee-defined" survives in `MIRI-PY-011.yaml`; `standards/feedback/` still
      reads as a plural body. Decide the posture (honest "single maintainer, drafts open for review" vs committee) and
      finish the sweep. Includes the **y3bishop3y authorship re-attribution** the miri-py log calls "the deliberate
      last step." → **Emiliano's call.** _(OSS Maintainer: "the one dishonesty a reviewer can prove from git shortlog";
      would move his score most, at zero engineering cost)_

## Coordination note (no our-side code change)

- **MIRI-PY-011 tolerance** — our check YAML is canonical at **24h** (`MIRI-PY-011.yaml:25-26`); miri-py's
  `constants.py` uses **26h**. Keep 24h; miri-py conforms down. Tracked in `miri-py.md`. _(Packaging)_

## Not a repo task

- The evidence-pack prose errors the panel caught (the Core-MUST list; the unfootnoted "89") were in the reviewers'
  briefing doc, not in the repo — no repo change needed.
