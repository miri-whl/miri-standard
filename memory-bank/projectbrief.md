# Project Brief: Miri Standard

## What this is

The Miri Standard defines how software artifacts — Python wheels and command-line tools first, Go modules and Rust
crates as later sketches — carry structured, machine-readable metadata that makes them legible to autonomous agents:
pre-parsed API/usage metadata, identity and vulnerability signaling, and lifecycle/deprecation contracts.

This repository is the **standard itself**: the normative specifications, the JSON Schemas, the per-check YAML
definitions (the machine-readable source of truth linters consume), a sample SDK, and a generated documentation
site. It is a documentation and specification repo — there is no application code, build, or test suite of its own
beyond a thin Python site generator and verification one-liners.

## What this is not

- Not the linter. The reference Python implementation is the separate `miri-py` repo.
- Not a multi-language implementation. Other-language tooling lives in its own repos.
- Not a package host or a runtime agent.

## Deliverables

- Normative specs under `standards/` (Python wheel extensions, agent metadata, lifecycle/security, CLI).
- JSON Schemas under `schemas/` governing every metadata file and the check-definition format itself.
- Per-check definitions under `standards/<target>/checks/*.yaml` — one file per check, the source of truth.
- Linter checklists under `standards/<target>/linter-checklist.md` — weighted, summing to exactly 100 per target.
- A sample SDK under `examples/` demonstrating a conforming artifact.
- A generated site (`tools/generate_site.py` → published to the Pages repo by CI).

## Goals

- Make the standard precise enough that two independent implementers build interoperable linters from it.
- Keep the machine-readable sources (schemas, check YAMLs) authoritative; derive prose and site from them.
- Ground every check in a real standard or incident and keep it mechanically decidable.
- Build the standard so its most defensible parts (lifecycle/deprecation/identity signaling) can stand on their own.

## Non-goals for now

- Multi-language rollout beyond Python and CLI (Go/Rust remain scope sketches).
- Any claim of measured agent-performance benefit that has not actually been measured.

## Success criteria

- The check set is internally consistent: weights sum to 100, examples are correct, no check contradicts another.
- The spec and its reference implementation agree; where they diverge, the spec is updated to match reality.
- An outside developer can read a check page and know exactly what to change.
- Governance, provenance, and status claims on the site match what the project actually is.
