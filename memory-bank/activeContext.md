# Active Context

_Last updated: 2026-08-21._

## Current focus

**v0.3 — the Consumption Standard**, on the `phase-0.3` branch. v0.2 is merged; the site and miri-py are caught up.
v0.3 closes the producer→consumer loop the review rounds kept flagging: v0.1/v0.2 say what an artifact _ships_, v0.3
says how an agent _consumes_ it. The maintainer considers this the final step for the core thesis — "the miri-py MCP
implementing that, and teaching the agent how to use the package."

Plan lives in `tasks/stage-v0.3/README.md` (three pillars + guardrails, mapped from the RFC's five asks). **Pillar 1 —
the Discovery Contract — is drafted:** `standards/consumption/discovery-contract.md`, grounded in the real `miri mcp`
(four tools, import-free discovery, api-index cap 25), with the panel's wire discipline made normative (top-level
`schema_version`, an absence-vs-error envelope, a surface version independent of the MCP protocol date, MCP as one
binding). Suite indexed in `standards/README.md`; all three doc linters green.

Next: Pillar 2 (the task-to-document consumption map — the "teach the agent" core), then Pillar 3 (consumer
conformance `MIRI-CONSUMER-NNN` + the reference tool + the paired bare/miri and adversarial fixtures).

## Recent decisions

- **Site hosting**: the site is published to the dedicated `miri-whl/miri-whl.github.io` Pages repo (clean root
  URLs). The generated HTML is never committed to this repo — it is a derived artifact published by CI.
- **Local build**: `.generated/` is the local test-render target (gitignored); `make site` / `make serve` build and
  preview it.
- **Tooling scope**: this repo is docs/specs, so only documentation-relevant skills were brought in; the
  Python-application skills from the linter repo were intentionally not copied. New skills were authored for what
  this repo actually does (check YAML authoring, schema/checklist governance).
- **v0.3 shape**: the consumption work is a new cross-cutting suite (`standards/consumption/`), not a per-language
  addition, since it constrains consumers and tooling rather than any one artifact type. The AI-researcher panelist's
  "no consumer contract exists" objection is treated as the thing v0.3 answers, not a blocker — the mechanism is a
  prerequisite for the experiment that would settle benefit. Spec discipline: mechanisms never benefits; MCP is one
  binding of a transport-agnostic contract, not the contract itself.

## Next steps (roadmap, not yet done)

v0.3 is planned in `memory-bank/tasks/stage-v0.3/README.md` (pillars mapped from `consumption-spec-proposal.md`'s five
asks). Remaining after Pillar 1:

- **Pillar 2 — Consumption Map** (`standards/consumption/consumption-map.md`): the task-to-document reading contract,
  split into a normative column (read-order + prohibitions) and an informative one (heuristics); the element audit
  (every element states its consumption value or is marked reserved); the two code-only rules folded in as precedent.
- **Pillar 3 — Consumer Conformance**: `MIRI-CONSUMER-NNN` checks + `consumer-conformance.md` + reference tool
  `miri brief`, verified on the paired bare/miri fixture and an adversarial-metadata twin. The circularity firewall
  lives here.
- **Guardrails**: Ask 4 (verification recipe) as a minimal producer SHOULD; Ask 5 (paired fixture + comparison
  harness, gated in CI, honesty line verbatim).
- Version bump to 0.3-draft across spec headers / README / site once the suite is coherent.
- Post-merge miri-py: conform `miri mcp` to the §4 wire discipline (schema_version + absence envelope + surface
  version) and re-sync the vendored checks.

Carried-over v0.2 loose ends (deferred, not v0.3-blocking): publish miri-py to PyPI (internal dogfooding first); run
the kill-or-validate experiment; land one external adopter.

## Open questions (v0.3)

- Is the task-to-document map the normative core, or guidance (SHOULD vs informative annex)? Leaning: read-_order_ and
  the prohibitions are normative; the heuristics are informative.
- Which discovery vehicles get blessed now vs after H5 data? The Discovery Contract names all four and lets the
  invocation-log evidence retire losers later.
- Is a consumer conformance profile enforceable enough to number, given consumers are heterogeneous harnesses? Current
  answer: yes, verified against a _reference_ consumer on fixtures, not against arbitrary harnesses.
- Where does the verification recipe live (manifest vs lifecycle), and is SHOULD the right level?

## Working-tree note

Earlier local edits (a set of `standards/python` file renames and related doc changes) are parked in a git stash,
not yet committed. Check `git stash list` before assuming the tree is clean.
