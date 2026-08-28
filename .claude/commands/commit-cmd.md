---
description: Produce a ready-to-run git commit command for the current changes (no push, no PR)
---

Produce a **commit command for the user to run**. Do not run `git commit` yourself.

## Steps

1. `git status --short` and `git diff HEAD --stat` to see what is uncommitted.
2. If any diff looks larger than the change warrants (e.g. a reformatted JSON file), run a **semantic diff** before
   proposing the commit and say what actually changed. A large diff for a small edit is usually an accidental
   reformat, and the user should know which it is.
3. Confirm the repo's gates are green for whatever was touched — do not claim green without running them:
   - `npx -y markdownlint-cli2@0.13 "**/*.md" "!.generated/**" --config .markdownlint.json`
   - `npx -y cspell@8 "**/*.md" --no-progress`
   - schemas + checks validate, `tools/validate_fixtures.py`, and the weights-sum-to-100 check, when relevant
   If something fails, fix it first rather than committing red.
4. Output a single fenced `bash` block with `git add -A && git commit -m "..."`.

## Message conventions

- Prefix: `feat:` / `fix:` / `chore:` (see `CLAUDE.md`).
- Subject line under ~72 chars, imperative mood.
- Body explains **why**, not just what — the reasoning that would otherwise be lost. Where a panel or review drove the
  change, name the finding it closes.
- State what was verified, with real numbers (checks valid, fixture invariants, weights).
- If a change is a correction of an earlier mistake in this repo, say so plainly in the body.
- End with:

  ```text
  Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
  ```

## Do not

- Do not push, open a PR, or run the commit — the user runs it.
- Do not include `.generated/` output (gitignored) or a generated `build/` tree.
- Do not bundle unrelated work into one commit; propose separate commits if the changes are genuinely separate.
