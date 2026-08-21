# Miri Standard Memory Bank

Session-persistent project memory for the **miri-standard** repository. This is the specification/standards repo —
markdown specs, JSON Schemas, YAML check definitions, and a generated site — not the Python linter (that is the
separate `miri-py` repo).

Read `activeContext.md` and `progress.md` at the start of any non-trivial session. The workflow for reading and
updating these files is wired into the repo's `CLAUDE.md`.

## Files

Core (maintain these):

- `projectbrief.md` — scope, goals, what this repo is and is not. Shapes everything else.
- `productContext.md` — why the standard exists, the problem it addresses, who consumes it.
- `systemPatterns.md` — how the repo is structured: schema-as-data, the check/checklist/site pipeline, governance.
- `techContext.md` — tools, CI, local verification, conventions, constraints.
- `activeContext.md` — current focus, recent decisions, next steps. Update most often.
- `progress.md` — what exists, what is planned, known issues and open risks.

Task tracking:

- `tasks/` — one file per active workstream; `tasks/task-template.md` is the starting shape.
- `archive/` — completed workstreams moved out of `tasks/`.

## Scope discipline

This memory bank tracks *the standard*. Facts about the reference linter live in `miri-py`. When a decision spans
both (a spec clause and its enforcement), record the spec side here and note the linter dependency; do not paste
linter internals in.

## Publication note

These files are git-tracked and this is a **public repository**. Keep them free of internal-only notes, unreviewed
speculation, credentials, private paths, and anything that reads as different from the project's public posture.
Write them as if a prospective contributor will read them, because one will.
