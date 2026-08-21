---
name: schema-governance
description: "Use when editing JSON Schemas in schemas/, changing check weights or the checklist, validating example metadata, or working on the schema-as-data site generator. Covers the invariants that span the whole check set: weights sum to 100, schema enforces what the spec claims, examples validate. Triggers: 'schema', 'schemas/', 'weights', 'checklist', 'validate example', 'generate_site', 'lint-report', 'jsonschema'."
---

# Schema and checklist governance

This repo's central design rule is **schema-as-data**: the JSON Schemas in `schemas/` and the YAML check
definitions are the source of truth; prose, the site, and every linter are derived from them. Governance work is
about keeping those sources internally consistent and making the schema *actually enforce* what the spec claims.

## The invariants (verify all of these before committing a schema/checklist change)

1. **Weights sum to exactly 100 per target.** After editing any check weight or the checklist:

   ```bash
   python3 -c "
   import re
   for f, p in [('standards/python/linter-checklist.md','MIRI-PY'), ('standards/cli/linter-checklist.md','MIRI-CLI')]:
       w = re.findall(r'^\| ' + p + r'-\d+ \|.*\| (\d+) \|$', open(f).read(), re.M)
       print(f, sum(map(int, w)))"
   ```

   The same must hold summing the `weight:` fields across the `active` YAML files for each target. If you withdraw a
   check, redistribute its weight in the same change — never leave the sum below 100.

2. **Every check YAML validates against `schemas/check-v1.json`**, and the schema itself is a valid draft-07
   schema:

   ```bash
   python3 -m venv /tmp/v && /tmp/v/bin/pip -q install jsonschema pyyaml
   /tmp/v/bin/python -c "
   import json, pathlib, yaml, jsonschema
   schema = json.load(open('schemas/check-v1.json'))
   jsonschema.Draft7Validator.check_schema(schema)
   n = 0
   for f in pathlib.Path('standards').glob('*/checks/*.yaml'):
       jsonschema.validate(yaml.safe_load(f.read_text()), schema); n += 1
   print(f'{n} check definitions valid')"
   ```

3. **Example metadata validates against its schema.** Any `schemas/<x>-v1.json` change must be validated together
   with the sample-SDK instance it governs (pattern in `CLAUDE.md` for `lifecycle-v1.json`). A schema change that
   makes the shipped example invalid is a break.

4. **IDs are contiguous and stable.** No renumbering, no gaps in the active range beyond withdrawn placeholders.

5. **Counts in prose match the YAML.** The checklist's stated check count and MUST/SHOULD split must equal what the
   files actually contain. Reviewers verify this by counting; so should you.

## The schema-must-enforce-the-spec rule

A recurring, load-bearing defect: the prose says a constraint is "schema-enforced" but the schema does not enforce
it, so any consumer validating against the published schema alone is fooled. When a spec sentence claims the schema
guarantees something, make the schema actually guarantee it. Known shapes to watch:

- **Conditional requirements that a null satisfies.** `if status in {deprecated, eol} then required: [replacement]`
  is satisfied by `"replacement": null` when `replacement` is nullable. Narrow the type under the `then`
  (`properties: {replacement: {type: string}}`), do not just require the key.
- **URL fields that accept dangerous schemes.** If a field is a fetched or trusted URL, constrain it
  (`"pattern": "^https://"`), rather than accepting `http://`, `javascript:`, or `file:`.
- **Enums/patterns that reject valid real inputs.** A version `pattern` that rejects valid PEP 440 (`2.1`,
  CalVer `2024.6`) will contradict a check that requires exact-match to that version. Test the schema against real
  inputs, not just the happy path.
- **"Required" sub-objects that are only shape-checked.** Requiring a field's presence is not the same as
  verifying its meaning; say which one the schema does, and do not overclaim in prose.

When you cannot express a guarantee in JSON Schema, say so explicitly in the spec ("enforced by the linter, not the
schema") rather than implying the schema covers it.

## The site generator (schema-as-data in practice)

`tools/generate_site.py` renders the site purely from real artifacts: content from the check YAMLs and `docs/`,
structure from `website/site.yaml`, look from `website/static/css/`, markup from `website/templates/`. It invents
nothing. Rules when touching it:

- The generator must stay a thin renderer. If a page needs a fact, that fact comes from a check YAML, a schema, or
  `site.yaml` — never hardcoded in the Python.
- Build locally with `make site` (validates first, then generates into `.generated/site`, which is gitignored) and
  open the result before committing. `make serve` serves it.
- The generated site is never committed here; CI publishes it to the Pages repo. Do not add `site/` output to git.

## Cross-repo consistency

Linters vendor these definitions. If a downstream tool (e.g. miri-py) pins a commit and content-hash of
`standards/*/checks/`, then adding a required field to `check-v1.json` breaks that vendored mirror until it re-syncs.
When you add or tighten a schema field, note it as a downstream-affecting change so the vendored copies can be
regenerated — a silently drifted mirror enforces rules it has never seen.
