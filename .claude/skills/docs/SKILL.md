---
name: docs
description: "Use when writing or reviewing prose in this repo — specs under standards/, READMEs, docs/, proposals/, the origin story, governance files. Enforces the Miri Standard house style and the markdownlint/cspell/link rules CI gates on. Triggers: 'documentation', 'README', 'spec', 'write up', 'proposal', 'whitepaper'."
---

# Documentation — Miri Standard house style

This is a **documentation and specification repo**: the deliverables are markdown specs, JSON Schemas, YAML
check definitions, and a generated site. There is no application to run. "Correct" here means *accurate, precise,
and CI-green*, not merely readable. Load this skill before writing or editing any prose file.

## The rules CI actually enforces (get these right or the build is red)

Three CI jobs gate every `*.md` change (`.github/workflows/ci.yml`): markdownlint, cspell, and a link check.

- **Hard-wrap prose at 120 columns** (MD013). Tables and fenced code blocks are exempt. Do not reflow a whole
  paragraph onto one line "because it's cleaner" — CI fails it.
- **Every code fence needs a language** (```` ```json ````, ```` ```python ````, ```` ```text ```` for plain output).
  A bare ```` ``` ```` fails markdownlint.
- **No emphasis-only line as a heading** — write `## Heading`, never a bare `**Heading**` on its own line.
- **Never link to a file that does not exist yet.** Planned documents are listed as **plain text** with a
  *(Planned)* marker — a markdown link to a missing file fails the link checker. This is the single most common
  break; when in doubt, plain-text it.
- **Spelling**: cspell runs against `.cspell.json`. New legitimate jargon or proper nouns go in that file's
  `words` list — add the term rather than rephrasing around it, but only for real terms, not typos.
- Relative links must resolve. Verify before committing (the snippet is in `CLAUDE.md`).

Run all three locally before you hand anything back:

```bash
npx -y markdownlint-cli2@0.13 "**/*.md" --config .markdownlint.json
npx -y cspell@8 "**/*.md" --no-progress
```

## Writing standards for specs

The check pages and the lifecycle/security spec are the quality bar for this repo — match them, not the older
`miri-agent-metadata-specification.md`-era prose.

- **Lead with the claim, then the mechanism, then the evidence.** A good check `rationale` names the harm, gives
  a concrete real-world incident, and says why no existing tool catches it (see `MIRI-PY-030`: kubectl `--export`).
- **Every normative statement is testable.** If a linter cannot mechanically decide whether an artifact satisfies
  a sentence, either make it decidable or move it out of the normative section. "SHOULD be well-documented" is not
  a spec clause; "the first line of `--version` output is `<name> <version>`" is.
- **Examples are complete and correct.** A violation example and a compliant example, both runnable/parseable, both
  actually demonstrating the rule. Wrong examples in a standard are worse than no examples — they get copied.
- **Cite the trail.** Reference the PEP, POSIX/GNU section, RFC, or incident by name and link. Distinguish a `spec`
  reference (another Miri doc) from an `external` one (an upstream standard).
- **Say what the boundary is.** Scope statements ("this standard is POSIX-only", "open-source vs private
  distribution") belong up front, not discovered by a reader who hits an edge case.

## Consistency traps specific to this repo (reviewers have hit all of these)

- **One name per artifact.** It is `AGENT_EXAMPLES.json` and `get_agent_metadata` — never `AI_EXAMPLES.json` /
  `get_ai_metadata`. When you touch a doc that uses the old names, fix them.
- **One definition per concept.** "Minimum compliance" must not be defined three different ways across three files.
  If a concept is defined normatively, other docs reference that definition — they do not restate it differently.
- **The checklist and the check YAMLs are the same facts.** Check counts, MUST/SHOULD splits, and weights in prose
  must match the YAML source of truth. If you change one, change both (see the `check-authoring` and
  `schema-governance` skills).
- **Keep citations current.** PEP 491 is Deferred — cite the living Binary Distribution Format spec instead. Verify
  a PEP's status before citing it as authority.
- **Domains and URLs**: canonical org is `miri-whl` on GitHub, site is `miri-whl.github.io`. Do not introduce
  `miri-standard.org` or other placeholder domains into prose.

## Review checklist

When reviewing a doc change, check in this order: (1) does it pass the three CI linters; (2) is every normative
sentence testable; (3) are the examples correct; (4) do names/definitions/counts match the rest of the repo;
(5) are all citations real and current; (6) planned items plain-text, not linked. Report findings grouped by
"CI-breaking" vs "accuracy" vs "style".
