# Stage v0.2 Step 3 — miri-py (SEPARATE REPO — carried forward)

These land in `/Users/bishop/work/patitur/code/miri/miri-py`, not this repo. Consolidated from Round 4 and the
step-1/step-2 archives so nothing is lost. Several of these directly unblock standard-repo items (`standard.md`) and the
CI gate. Cited to the panelist(s) who raised each.

## STATUS — handoff resolved (miri-py `37664a4`)

Per the miri-py side: **everything in this file except PyPI has landed**, pre-flighted against our actual
`stage-0.2-step-3` branch. Notables: the danger/mutates fields were renamed to **`destructive`/`mutating`** to match
our §6.4 (both repos now agree); `api_index` already ships zero `cli/` symbols and no console-script `main`, so the
new MIRI-PY-036 clause passes as-is; the api-graph emitted doc already validates against the closed-root schema; and
the `--describe` light-up was rehearsed end-to-end (validates with `destructive`/`mutating` set). Gates: 1157 pass /
0 fail, ruff clean. **Still open:** PyPI (deferred to end-of-project) and the post-merge sync ritual (bump
`PINNED_SHA`, run `sync_checks` → brings the extended schema + `checklist_version: 0.2-draft`, verify dogfood pins) —
~10 min, runs once step-3 merges to our main.

## P0 — publish + re-pin (unblocks the standard's CI gate and the honesty of tool output)

- [ ] **Publish miri-py to PyPI** (even a `0.2.0rc`). Fixes `pip install miri-py`, turns the standard's
      `sample-conformance` gate from skip-guarded to real, and is the panel's #1 cross-repo lever. _(OSS, CLI,
      Packaging)_
- [x] **Re-pin the vendored checks mirror to ≥ `4e51dd6`.** `PROVENANCE.json` pins a commit that predates the standard's
      fixes, so `miri score`/`describe` output still shows the retired "executes in sandbox" wording
      (`MIRI-PY-015.yaml`, 5 occurrences) and "committee-defined" — undercutting the honest posture in the output users
      actually see. _(Security N1, N3)_
- [x] **Purge "committee" from miri-py code** — `score_cmd.py:301` ("40 committee-defined checks"), `execution.py`,
      `runner.py`. Match the standard's single-maintainer honesty. _(Security N3)_

## P1 — the generate bugs (block the standard's generate→diff gate)

- [x] **`miri generate --output-dir <path>` crashes** (`unsupported operand type(s) for /: 'str' and 'str'` — needs
      `Path`). _(found while building the step-2 sample gate)_
- [x] **`miri generate` writes to `src/agent-metadata/`** for a src-layout package, not `src/<pkg>/agent-metadata/`
      (the packaged location); the output never enters the wheel and recreates the stale-duplicate dir. _(same)_
- [x] **`miri build --generate-metadata` is a no-op** — the build report shows "Generate Metadata: No"; the wheel keeps
      the committed stamps, so MIRI-PY-011 still fires. _(same)_
- [x] **`miri generate` omits `migration-guide.json`** (not derivable from a single version's source) — a
      regenerate-from-scratch flow would drop the hand-authored migration guide. _(same)_

Fixing these lets the standard switch its sample gate from re-stamp to true generate→build→`git diff`→score.

## P1 — CLI conformance (miri-py's own CLI still fails MUST checks)

- [x] **CLI-013** — argument-parse errors bypass the JSON envelope. `miri --json score --bogus` → exit 2, prose on
      stderr, no `error.code`. Root cause: Click runs `standalone_mode=True` (`cli/main.py:275`), so `UsageError`
      raises `SystemExit(2)` which the `except Exception` handler never catches. Fix: run non-standalone and catch
      `UsageError`/`NoSuchOption`/`BadParameter`/`MissingParameter`, emitting the envelope in machine mode. _(CLI
      Author)_
- [x] **CLI-040 producer half** — miri-py already builds `danger`/`mutates` in `describe.py` but strips them unless
      `_schema_declares_safety_fields()` returns true, and that detector reads `$defs` while the Draft-07 schema uses
      `definitions` — so it returns false forever. Fix it to read `definitions`, then re-vendor the updated
      `cli-describe-v1.json` (after the standard adds the fields — see `standard.md`). _(CLI Author)_
- [x] **§5.4 CLI-exclusion violation** — `sdk-manifest.json` `api_index` contains the console-script target `main`
      plus 47 `cli/` symbols; §5.4 says the CLI surface MUST be excluded from `api_index`. Drop them from the
      extractor. _(Agent-Tooling)_

## P2 — hygiene (carried from the step-2 archive)

- [x] **MIRI-PY-011 tolerance**: change `constants.py` from 26h to **24h** to match the canonical check YAML.
      _(Packaging)_
- [x] Drop the redundant `report_version` from the report (schema requires only `schema_version`). _(CLI)_
- [x] `miri build` "Next Steps" banner still advertises the deprecated `miri lint` and globs `*-miri-*.whl` (matches
      nothing). _(CLI)_
- [x] **examples-index.json orphan** — the generator emits it with a `$schema` to a nonexistent schema; delete
      `generate_examples_index` and standardize on the dist-info `AGENT_EXAMPLES.json`, or spec+check it. _(Agent-Tooling)_
- [x] Fix the generator `$schema` domain (`generator.py`, `patterns_builder.py`) from `miri-standard.org` to
      `miri-whl.github.io`. _(Agent-Tooling)_
- [x] Correct/retire `memory-bank/phase-status-summary.md` (struck "+3.1" headline but still asserts "Proven quality
      gains" elsewhere) and fix the kill-or-validate harness README module map. _(AI Researcher)_

## P2 — version sync (added this session)

- [ ] **Re-sync `checklist_version` to `0.2-draft`.** The standard bumped its current version from `0.1-draft` to
      `0.2-draft` (spec headers, README, `site.yaml`); miri-py's reports still pin `checklist_version: 0.1-draft`.
      Re-vendor the checks and bump the reported checklist version so a report's version matches the standard it
      scored against. Note: check `added_in` fields stay `0.1-draft` (historical) — only the current/checklist
      version moves. _(version bump)_
