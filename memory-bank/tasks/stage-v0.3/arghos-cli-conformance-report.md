# arghos vs MIRI-CLI: 39/100, 23 MUST failures, non-conforming

**Tool:** arghos (`~/work/patitur/code/arghos`), assessed 2026-08-23
**Verdict:** **NON-CONFORMING.** 23 of 36 MUST checks fail. Raw score 39/100, reported capped at 74.
**Purpose:** arghos is ours. The goal is that an agent can drive it fully and know when its surfaces change.
This measures the distance to that, and the distance is large.
**Method:** manual — the CLI linter does not exist. Every check evaluated by reading source and running the binary.

## The score, strictly

| Category | Score | |
|---|---|---|
| Baseline Conventions | **12/12** | Click and rich did most of this |
| Machine Output | **2/18** | |
| Identity & Introspection | **3/22** | |
| Update & Changelog | **2/14** | |
| Deprecation Coherence | **20/22** | **vacuous — see below** |
| Safety | **0/12** | |
| **Raw total** | **39/100** | 23 MUST failures ⇒ non-conforming regardless |

**Failing MUSTs** (each links to its published definition):
[008](https://miri-whl.github.io/checks/cli/MIRI-CLI-008.html),
[009](https://miri-whl.github.io/checks/cli/MIRI-CLI-009.html),
[010](https://miri-whl.github.io/checks/cli/MIRI-CLI-010.html),
[011](https://miri-whl.github.io/checks/cli/MIRI-CLI-011.html),
[013](https://miri-whl.github.io/checks/cli/MIRI-CLI-013.html),
[015](https://miri-whl.github.io/checks/cli/MIRI-CLI-015.html),
[016](https://miri-whl.github.io/checks/cli/MIRI-CLI-016.html),
[017](https://miri-whl.github.io/checks/cli/MIRI-CLI-017.html),
[018](https://miri-whl.github.io/checks/cli/MIRI-CLI-018.html),
[019](https://miri-whl.github.io/checks/cli/MIRI-CLI-019.html),
[020](https://miri-whl.github.io/checks/cli/MIRI-CLI-020.html),
[021](https://miri-whl.github.io/checks/cli/MIRI-CLI-021.html),
[022](https://miri-whl.github.io/checks/cli/MIRI-CLI-022.html),
[023](https://miri-whl.github.io/checks/cli/MIRI-CLI-023.html),
[025](https://miri-whl.github.io/checks/cli/MIRI-CLI-025.html),
[027](https://miri-whl.github.io/checks/cli/MIRI-CLI-027.html),
[028](https://miri-whl.github.io/checks/cli/MIRI-CLI-028.html),
[029](https://miri-whl.github.io/checks/cli/MIRI-CLI-029.html),
[030](https://miri-whl.github.io/checks/cli/MIRI-CLI-030.html),
[038](https://miri-whl.github.io/checks/cli/MIRI-CLI-038.html),
[039](https://miri-whl.github.io/checks/cli/MIRI-CLI-039.html),
[040](https://miri-whl.github.io/checks/cli/MIRI-CLI-040.html),
[041](https://miri-whl.github.io/checks/cli/MIRI-CLI-041.html).

## The 39 is flattering, and here is why

Twenty of the thirty-nine points come from **Deprecation Coherence, awarded for never having deprecated anything.**
arghos has no `lifecycle` blocks because it has no deprecations; the checks pass by absence of opportunity.

Strip those and arghos scores **19 out of 78 on things it actually does — 24%.**

Another 12 of the remaining 19 are Baseline Conventions, which Click and rich provide without anyone deciding
anything. **Deliberate, arghos-specific conformance work to date: roughly 7 points.**

That 20-point vacuous award is a defect in **our standard**, not in arghos. A scoring model that hands out a fifth of
the total for having shipped nothing worth deprecating is measuring project age, not quality. It goes on our backlog,
not theirs.

## What an agent cannot do with arghos today

**Choose a command.** Sixteen commands. Four read as "run the thing": `all`, `run`, `evaluate`, `critique`. The
distinctions are real and recoverable only from prose written for someone who already holds the model. An agent picks
by string similarity and picks wrong.

**Know what a command costs.** `critique` spends real money and writes a run directory. `config` does neither.
Nothing declares it. `--max-cost` exists — so the danger is known and simply not discoverable by anything that did
not read the source. An agent asked to "see what the panel would say" picks `all` instead of `plan` and spends the
budget.

**Know that anything changed.** No `changelog --since`, no `check-update`. `review` and `review-compare` were added
recently; an agent that learned arghos last month has no mechanism to find out. This is the "know the changes" half
of the goal and it scores 2/14.

**Recover from an error.** A bad argument yields a Python traceback on stderr and empty stdout. No code, no
`retryable`. An agent cannot distinguish "retry" from "this will never work".

**Simulate anything.** `--dry-run` exists on one command. Safety scores **0/12** — every check in the category fails.

## Two defects wrong on their own terms

**`--version` says 0.1.0. The package is 0.1.5.** Hardcoded, drifted five releases. Beyond
[MIRI-CLI-017](https://miri-whl.github.io/checks/cli/MIRI-CLI-017.html), this
poisons `meta.json`: every run recorded to date carries a version that has not existed for five releases, and any
run-over-run comparison across that boundary is silently comparing mislabelled data. One line —
`importlib.metadata.version("arghos")`.

**Unhandled traceback as the error path.** `arghos analyze --json nonexistent-run` → exit 1, traceback, empty stdout.

## Order, by what it buys an agent

1. **`--describe`** — 22 points, and the only thing that turns sixteen ambiguous commands into a menu with declared
   cost and mutation. `arghos config` already enumerates knobs with resolved values, so identity is half-assembled.
   What needs writing is per-command `mutating` / `destructive`.
2. **The two bugs.** One is a one-liner.
3. **JSON envelope** — `schema_version` on every payload, structured errors with `code` and `retryable`. arghos
   already does exactly this internally: `CritiqueJudgment` is a Pydantic model validated server-side. The CLI
   surface has not caught up with the internal one.
4. **`--json` everywhere**, same flag. Currently 2 of 16 commands.
5. **`changelog --since`.** Cheap to emit as you go, expensive to reconstruct from git later — and the review
   scenario is about to churn its surface repeatedly.
6. **Deprecation blocks**, adopted now while free.

## The decision that is cheapest today and never again

`review` and `review-compare` exist and the review scenario family is being built. That surface will change shape
several times before it settles.

If `--describe` and `changelog --since` land **first**, every change is discoverable as it happens. If they land
after, the churn is invisible and has to be reconstructed. This is the cheapest this decision will ever be.

## What the standard learns

arghos is the first CLI outside the standard's own authorship measured against MIRI-CLI, and it has already found a
real defect in our scoring model — 20 points for shipping nothing. Every further place the checklist demands
something arghos has no reason to provide is a finding about **the standard**.

When the CLI linter exists, arghos is its first target.

---

## Where to read the checks

- **All 43 CLI checks, published:** <https://miri-whl.github.io/checks/cli/index.html> — each check page carries its
  rationale, the exact `fires_when` triggers a linter uses, ordered remediation steps, and a violating/compliant
  example pair. That is the page to work from, not this report.
- **The checklist and scoring model:**
  <https://github.com/miri-whl/miri-standard/blob/main/standards/cli/linter-checklist.md>
- **The CLI specification** — what `--describe`, `check-update` and `changelog --since` must actually emit, with
  worked JSON:
  <https://github.com/miri-whl/miri-standard/blob/main/standards/cli/cli-lifecycle-specification.md>
- **Canonical YAML for any single check** (what a linter consumes, and the source of truth if a page disagrees):
  `https://github.com/miri-whl/miri-standard/blob/main/standards/cli/checks/MIRI-CLI-NNN.yaml`

The four highest-value pages for the work below, in order:
[015 `--describe`](https://miri-whl.github.io/checks/cli/MIRI-CLI-015.html) ·
[040 destructive flagged](https://miri-whl.github.io/checks/cli/MIRI-CLI-040.html) ·
[013 structured errors](https://miri-whl.github.io/checks/cli/MIRI-CLI-013.html) ·
[029 `changelog --since`](https://miri-whl.github.io/checks/cli/MIRI-CLI-029.html)
