# Product Context: Miri Standard

## The problem it addresses

Autonomous agents increasingly install and use software packages, but packages carry almost nothing an agent can
rely on beyond human-oriented docs: no machine-readable statement of which interfaces are deprecated and what
replaces them, no pinned advisory sources, no support/lifecycle status, no pre-parsed API surface that travels with
the installed artifact. Agents fall back on reading source, guessing, and working from stale training knowledge.

The Miri Standard proposes that this metadata ship *inside the artifact* (the wheel, the CLI's introspection
surface) so it is version-locked and available offline, and that a weighted conformance checklist make "is this
package legible to agents?" a measurable, gateable question.

## Who consumes the standard

- **Package and CLI maintainers** — adopt the standard by generating and shipping the metadata; judged by the
  checklist.
- **Linter implementers** — build tools that read the per-check YAML definitions and score artifacts.
- **Agent/harness builders** — the end consumers of the metadata; the standard must earn its place against their
  existing options (reading source, type stubs, docstrings, llms.txt, MCP).
- **Security/supply-chain tooling** — consumers of the identity and lifecycle signaling (purl, OSV, SBOM links).

## What "good" looks like for each

- A maintainer can reach a meaningful conformance tier without heroic effort — an on-ramp exists, not just a wall of
  MUSTs.
- A linter implementer never has to guess: field names, shapes, and firing conditions are pinned in the schema and
  the check YAMLs, and no two checks contradict each other.
- An agent builder gets facts they cannot derive from the installed code — deprecation timelines, advisory sources,
  migration diffs — rather than a redundant re-description of the API surface.

## Honesty posture

The standard is early (0.1-draft, Incubation). Claims on the site and in specs must match reality: what exists
versus what is planned, what is measured versus hypothesized, and who maintains it. Overclaiming (unproven
performance numbers, plural-committee framing for a small team) is treated as a defect, not marketing.

## The defensible core

The parts of the standard that encode facts an agent genuinely cannot get by reading installed code — the
lifecycle/deprecation/migration layer and identity/vulnerability signaling — are the strongest contribution. The
pre-parsed API-surface layer competes with introspection and type stubs and must justify itself on verifiability
and token/version-locking grounds, or be demoted.
