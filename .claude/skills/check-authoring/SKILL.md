---
name: check-authoring
description: "Use when adding, editing, withdrawing, or reviewing a MIRI check definition — the per-check YAML files in standards/<target>/checks/ that are the machine-readable source of truth linters consume. Triggers: 'add a check', 'MIRI-PY-', 'MIRI-CLI-', 'check definition', 'new alert', 'edit a check', 'withdraw a check', 'checks/*.yaml'."
---

# Authoring MIRI check definitions

Each file in `standards/python/checks/` and `standards/cli/checks/` is one canonical check: the
machine-readable source of truth a linter implements by ID. The generated site and the linter both consume these
files, so a mistake here propagates to every downstream tool. The governing schema is `schemas/check-v1.json`
(JSON Schema draft-07) — read it before authoring, and validate against it after (see the `schema-governance` skill
for the weight/coverage invariants that span the whole set).

## Anatomy of a check (all fields are required unless noted)

- `id` — `^MIRI-(PY|CLI|PYX|CLIX)-\d{3}$`. **Stable forever; never renumbered.** The `PYX`/`CLIX` namespaces are
  extension (health-only) checks and carry `weight: 0`.
- `name` — short human name, ≤ 80 chars.
- `target` — `python-wheel` or `cli` (must match the directory).
- `status` — `active` or `withdrawn`. A withdrawn check keeps its file and ID and requires `withdrawn_in`; its
  weight is redistributed in a minor version (never leave a hole in the sum — see `schema-governance`).
- `added_in` / `withdrawn_in` — checklist version strings (e.g. `0.1-draft`).
- `level` — `MUST` or `SHOULD`. A MUST failure makes the artifact non-conforming (score capped at 74). Do not make
  a check MUST unless a linter can decide it and near-universal non-compliance is not the expected result.
- `category` — the checklist category; must be spelled identically to the checklist table and the other checks in
  that category.
- `weight` — integer 0–10. All `active` weights **per target sum to exactly 100**. Extension checks are 0.
- `conditional` — if true, the check scores full weight automatically when its condition does not apply.
- `severity` — canonical, for health scoring; implementations MUST use these, not their own:
  - `default` — one of `LOW MINOR MEDIUM HIGH CRITICAL` (ordered 1–5; note the nonstandard `LOW < MINOR`).
  - `violation_unit` — the countable thing that is one violation. Make it unambiguous across linters
    ("each silently removed interface"), never "each schema violation" (validators disagree on granularity).
  - `population_unit` (optional) — the denominator for per-instance density. Include only where a natural
    population exists; if present, reports MUST carry the count, and MUST omit it otherwise.
- `short_description` / `long_description` — one-liner, then rationale + full definition.
- `rationale` — ≥ 40 chars, the editorial case: the harm, ideally a real incident, and why no existing tool catches
  it. This is what makes a check page persuasive; write it like the best existing checks.
- `fires_when` — ≥ 1 concrete trigger conditions. These are the linter's spec — each must be mechanically decidable
  from the artifact plus the check's declared `requirements`. Do not write a `fires_when` clause that needs source
  access or a judgment call the runtime cannot make.
- `remediation` — ≥ 1 ordered fix steps. `suggested_fix` is the one-line summary of these.
- `requirements` (optional) — capabilities beyond the baseline (`network`, `previous-release`, `execution`). A
  linter lacking one MUST skip (forfeited, reported); a linter with it MUST NOT skip. Baseline is static inspection
  for wheels, local invocation for CLIs — so a plain static check omits this field. **Declare exactly what the
  `fires_when` clauses actually use**: a decorative `requirements: [network]` on a check that never touches the
  network is a real bug reviewers catch.
- `references` — the standards trail; each `{title, url, type}` with `type` ∈ `spec` | `external`.
- `urls` — canonical `definition` (GitHub blob on main) and `html` (published page). Follow the exact pattern of a
  sibling file; the site generator does not derive these.

## The consistency rules that bite

- **The example must demonstrate the exact rule and both states must be correct.** A compliant example that
  actually violates another check (wrong `schema_version` placement, a purl/OSV pair that can never join, a version
  string the schema rejects) is a shipped contradiction. Cross-check your example against related checks.
- **Do not contradict a sibling check.** If two checks constrain the same field (e.g. a version's equality
  semantics, or an error code's `retryable` value), their examples must agree. Grep the neighbours before writing.
- **`fires_when` must be decidable within `requirements`.** If a clause needs the previous release, declare
  `previous-release`; if it needs to run the artifact, declare `execution`. A clause that needs static source
  analysis of a wheel's code is outside the model — rewrite it.
- **Keep the prose and the YAML in lockstep.** Adding, withdrawing, or reweighting a check means editing the
  checklist table in the same change so the counts and the weight sum still hold (that verification lives in the
  `schema-governance` skill and `CLAUDE.md`).

## Workflow for a change

1. Read `schemas/check-v1.json` and two or three sibling checks in the same category for tone and field patterns.
2. Write or edit the YAML. Keep `id` stable; pick the next free number for a new check.
3. Validate the single file against the schema, then run the whole-set invariants (weights sum to 100, IDs
   contiguous, categories consistent) — the `schema-governance` skill has the exact commands.
4. Update the checklist table (`standards/<target>/linter-checklist.md`) so counts and weights match.
5. Regenerate the site locally (`make site`) and confirm the new/changed page renders.
6. Run the doc linters (see the `docs` skill) — the YAML `long_description`/`rationale` are prose too.
