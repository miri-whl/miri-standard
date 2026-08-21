# Task: <name>

_Status: planned | active | blocked | done — <date>._

## Goal

One or two sentences: what this task delivers and why. Tie it to a `projectbrief.md` goal or a `progress.md` item.

## Scope

- In scope: <what this task covers>
- Out of scope: <explicitly excluded, especially anything that belongs to the linter repo>

## Approach

Ordered steps. For spec/check work, note which sources change (schema, check YAMLs, checklist, prose) and remember
they move together.

1. <step>
2. <step>

## Definition of done

- [ ] Change made at the authoritative source (schema / check YAML), not only in prose.
- [ ] Invariants hold: weights sum to 100, check YAMLs validate, examples correct and non-contradictory.
- [ ] Prose counts/definitions match the YAML.
- [ ] Doc linters pass (markdownlint, cspell, links).
- [ ] Site regenerates cleanly (`make site`) and the affected pages render.
- [ ] Downstream note recorded if a schema change affects the vendored linter mirror.

## Notes / decisions

Record decisions and their rationale here as the task progresses; promote durable ones to `activeContext.md` or the
relevant core file when done.
