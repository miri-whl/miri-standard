# Tech Context: Miri Standard

## Nature of the repo

Documentation and specification. No application code, build, or test suite of its own. The only executable pieces
are `tools/generate_site.py` (the site generator) and Python one-liners used for verification.

## Layout

- `standards/` — normative specs, per-target `checks/*.yaml`, and `linter-checklist.md` files. Targets: `python`,
  `cli`; `go` and `rust` hold scope sketches.
- `schemas/` — JSON Schemas (draft-07) for each metadata file and for the check-definition format.
- `examples/sample-sdk/` — a sample artifact meant to demonstrate conformance.
- `website/` — `site.yaml` (structure), `templates/` (Jinja2), `static/css/` (design tokens + components).
- `tools/generate_site.py` — thin renderer; outputs to `.generated/site` (gitignored).
- `docs/` — origin story and supporting docs.
- `proposals/`, `community/`, governance files at root.

## Local verification (mirror of CI)

A pre-commit hook ships in `.githooks/` — enable with `git config core.hooksPath .githooks` in a fresh clone.
CI (`.github/workflows/ci.yml`) runs three doc jobs plus structure checks; all must pass.

- Markdown lint: `npx -y markdownlint-cli2@0.13 "**/*.md" --config .markdownlint.json`
- Spell check: `npx -y cspell@8 "**/*.md" --no-progress` (add real new jargon to `.cspell.json` `words`)
- Link check runs in CI; locally verify relative links resolve (snippet in `CLAUDE.md`).
- Schema + example validation and checklist-weight sums: snippets in `CLAUDE.md` and the `schema-governance` skill.

The `Makefile` wraps the site workflow: `make site` (validate + generate), `make serve`, `make validate`,
`make check` (validate + lint + spell).

## Writing conventions the linters enforce

- Prose hard-wrapped at 120 columns (MD013); tables and code blocks exempt.
- Every code fence declares a language; `text` for plain output.
- No emphasis-only line as a heading.
- Planned documents are listed as **plain text** with a *(Planned)* marker — never a link to a file that does not
  exist (the link checker fails on it).
- `gnu.org` URLs are in the link-checker ignore list (they 403 CI crawlers).

## Internal working docs are excluded from the doc linters

`memory-bank/` and `.claude/` are listed in `.markdownlintignore` and `.cspell.json` `ignorePaths` so internal
notes and skill files do not have to satisfy the published-prose rules. Keep cross-references in these files as
plain backticked paths, not markdown links, so the link checker has nothing to resolve.

## Canonical names and URLs

- GitHub org: `miri-whl`; standard repo: `miri-whl/miri-standard`; linter: `miri-whl/miri-py`.
- Site: `https://miri-whl.github.io/`.
- One name per artifact (`AGENT_EXAMPLES.json`, `get_agent_metadata`); do not reintroduce the `AI_EXAMPLES` /
  `get_ai_metadata` / `miri-standard.org` variants.

## Constraints

- The site HTML is never committed here; it is derived and published by CI to the Pages repo.
- Check IDs are permanent; weights per target sum to 100 at all times.
- Version labels are early: `0.1-draft`, status Incubation. Keep them consistent across files.
