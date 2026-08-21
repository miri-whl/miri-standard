# System Patterns: Miri Standard

## Schema-as-data (the central rule)

The machine-readable sources are authoritative; everything human-facing is derived from them.

- `schemas/*.json` — JSON Schemas (draft-07) governing each metadata file and the check-definition format
  (`check-v1.json`).
- `standards/<target>/checks/*.yaml` — one file per check, the committee-owned source of truth linters consume.
- Prose specs, the linter checklists, and the generated site are **downstream** of those two. When a fact changes,
  it changes at the source and flows outward — never the reverse.

## The check pipeline

```text
check-v1.json  (schema: the shape of a check)
      │
      ▼
standards/<target>/checks/MIRI-*.yaml   (the checks themselves — source of truth)
      │                         │
      ▼                         ▼
linter-checklist.md        tools/generate_site.py ──► .generated/site ──► (CI) Pages repo
(weighted table,               (thin renderer:
 sums to 100)                   content from YAML + docs/,
                                structure from website/site.yaml,
                                look from website/static/css/,
                                markup from website/templates/)
```

## Invariants that must always hold

- Active check weights sum to **exactly 100** per target.
- Every check YAML validates against `check-v1.json`; the schema is itself a valid draft-07 schema.
- Check IDs are stable and never renumbered; withdrawn checks keep their file/ID and redistribute weight.
- Counts and MUST/SHOULD splits in prose equal what the YAML files actually contain.
- Examples in each check are correct and do not violate a sibling check.
- The schema enforces what the prose says it enforces (no "schema-enforced" claim the schema does not back).

## Governance model

Checks are committee-owned in intent; severities and weights are assigned centrally so linters use them rather than
inventing their own. In practice the maintainer set is small — governance docs and public framing must describe the
project as it actually is, not as a larger body than exists.

## Relationship to the reference linter (miri-py)

`miri-py` vendors the check YAMLs (pinning a commit and content hash) and implements each check by ID. Consequences
for work in this repo:

- Tightening `check-v1.json` (e.g. adding a required field) breaks the vendored mirror until it re-syncs — flag
  schema changes as downstream-affecting.
- Where the linter has resolved an ambiguity the spec left open (naming, version-equality semantics, skip rules),
  the spec should absorb that resolution so a second implementer does not diverge.
- Where the linter ships a behavior that contradicts the spec, decide which is right and fix the other — do not
  leave them disagreeing.

## Site publishing

`tools/generate_site.py` builds into `.generated/site` (gitignored). A `Makefile` wraps it (`make site`,
`make serve`, `make validate`). CI regenerates and publishes to the `miri-whl.github.io` Pages repo on changes to
checks, schemas, the origin story, the website assets, or the generator. The site HTML is never committed to this
repo — it is a derived artifact.
