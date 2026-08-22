# Stage v0.2 Step 2 — miri-py (SEPARATE REPO — captured, not our branch)

These land in `/Users/bishop/work/patitur/code/miri/miri-py` (`phase-0.2`), not in this repo. Listed so nothing from
Round 3 is lost. Cited to the panelist(s) who raised each.

## P0 — the flagship number

- [ ] **`miri build --generate-metadata` must regenerate `generated_at`.** Today it injects `AGENT_EXAMPLES.json` but
      leaves the committed stale timestamps, so the reference wheel cannot reach its claimed grade. Make a clean
      `miri build && miri score` deterministically reach Silver/Core-conforming, and pin it in a test. _(CLI,
      Security, Packaging, Agent-Tooling)_
- [ ] **Correct the dogfood number in `memory-bank/progress.md:7-8`** ("89 Silver / Health 100"). Reproduced value is
      ~73/non-conforming/Health-89; the "89" is most likely Health mislabeled as conformance. State the exact recipe
      that yields the claimed grade, or the real number. _(all four rebuilders)_
- [ ] **Fix the generator `$schema` domain.** `generator.py:146,422`, `patterns_builder.py:19-25`, migration builder
      stamp `$schema` at `miri-standard.org/schemas/…`; the standard reconciled all `$id`s to `miri-whl.github.io`
      (commit `4e854e0`). A consumer resolving `$schema` hits the wrong/nonexistent domain. _(Agent-Tooling)_

## P1 — CLI conformance (miri-py's own CLI fails its own MUST checks)

- [ ] **CLI-013** — route argument-validation failures through the JSON envelope. `miri score /nope.whl --json`
      currently prints Click prose to stderr + exit 2, no `error.code`. _(CLI Author)_
- [ ] **CLI-027** — `check-update` must degrade honestly: unreachable/offline → `{update_available: null, …}` + exit
      0, not an error object + exit 1. Reserve non-zero for real faults. _(CLI Author)_
- [ ] **CLI-040/041** — add a machine-readable `danger`/`mutates`/`reads_only` field per command in `--describe`;
      mark `score --execute` destructive structurally, not in prose. _(CLI Author)_

## P1 — security

- [ ] **Close the `--execute` CI fail-open** (`score_cmd.py:332-337`): on a non-TTY, `--execute` proceeds after only a
      stderr warning. Require explicit `--yes`/`MIRI_EXECUTE=1` and abort otherwise. _(Security)_
- [ ] **Add a regression test for the confirmation gate** (decline → exit 2; `--yes` → proceeds; non-TTY behavior).
      The security control currently has no test. _(Security)_
- [ ] Optional: a real isolation backend (bubblewrap/nsjail/container) behind `--execute`, or drop the in-process
      egress monkeypatch and rely solely on "use a container." _(Security)_

## P2 — packaging / hygiene

- [ ] **Publish to PyPI** (even `0.2.0rc`) so `pip install miri-py` works — unblocks the standard's CI gate.
      _(OSS, CLI)_
- [ ] **MIRI-PY-011 tolerance**: change `constants.py:120` from 26h to **24h** to match the canonical check YAML.
      _(Packaging)_
- [ ] Drop the redundant `report_version` from the report (schema requires only `schema_version`). _(CLI)_
- [ ] `miri build` "Next Steps" banner still advertises the deprecated `miri lint` and globs `*-miri-*.whl` (matches
      nothing; `--miri-suffix` off by default). _(CLI)_
- [ ] **examples-index.json orphan** — the generator emits it with a `$schema` to a nonexistent schema. Coordinate
      with the standard's decision (see `standard.md`): either it becomes a real spec'd+checked format, or delete
      `generate_examples_index` and standardize on the dist-info `AGENT_EXAMPLES.json`. _(Agent-Tooling)_

## P2 — internal docs / honesty

- [ ] Finish or delete `memory-bank/phase-status-summary.md` — the "+3.1" headline is struck/RETRACTED but the same
      file still asserts "Proven quality gains" (`:132`), "Statistical evidence" (`:116`), "Clear improvements"
      (`:44`). Git-untracked so it won't publish, but it self-contradicts. _(AI Researcher)_
- [ ] Fix the kill-or-validate harness README module map (`experiments/kill-or-validate/README.md:14-23` lists files
      that don't exist; functionality is in `runner_support.py`). _(AI Researcher)_
- [ ] Reconcile task-tracker checkboxes with reality (quarantine work already done via `.gitignore` still shows open).
      _(AI Researcher)_

## P1 — generator bugs found while making the sample conform (2026-08-21)

- [ ] **`miri generate --output-dir <path>` crashes** — `unsupported operand type(s) for /: 'str' and 'str'`
      (a `str / str` path join; needs `Path`). Blocks generating metadata into a chosen location.
- [ ] **`miri generate` writes to `src/agent-metadata/`** for a src-layout package, not `src/<pkg>/agent-metadata/`
      (the packaged location). The output never enters the wheel; it also recreates the stale-duplicate dir the
      standard repo just removed.
- [ ] **`miri build --generate-metadata` is a no-op** on the sample — the build report shows "Generate Metadata: No"
      and the built wheel keeps the committed `generated_at` stamps (so MIRI-PY-011 still fires). The flag does not
      regenerate.
- [ ] **`miri generate` produces only 4/5 files and omits `migration-guide.json`** (not derivable from a single
      version's source) — a regenerate-from-scratch flow would drop the hand-authored migration guide.

_Consequence for the standard:_ until these are fixed, the sample-conformance CI gate re-stamps `generated_at` to
build time (see `tools/score_sample.py`) rather than regenerating from source. Once `miri generate` can target the
packaged path, switch the gate to a true generate-from-source step.
