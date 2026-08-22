# Proposal (RFC): A Consumption Specification for the MIRI Standard

- **Authors**: MIRI Standard maintainers
- **Status**: Draft — *Request for Comments*; deferred to post-v0.2 (see Sequencing)
- **Created**: 2026-08-21
- **Updated**: 2026-08-21
- **Tracking Issue**: *(to be filed)*
- **Pre-review**: Reviewed by the six-member standing panel on 2026-08-21 (see **Panel Pre-Review** below);
  consolidated report `miri-consumption-spec-review-2026-08-21` in the project's generated-reports set.

## Abstract

The MIRI Standard v0.2 is a *producer-side* specification: its checks define, verifiably, what an agent-ready wheel
must **ship**. It defines nothing about how an agent **consumes** what was shipped — no reading order, no discovery
contract, no definition of a conformant consumer, no way for an agent to verify its own integration. This RFC proposes
a **Consumption Specification** that closes the producer→consumer loop: a task-to-document consumption map, a discovery
contract, a consumer conformance profile, a verification recipe, and a paired reference fixture with a demonstration
harness. It is deliberately disciplined about honesty — it specifies *mechanisms*, never *benefits*; effectiveness
remains gated on the pre-registered kill-or-validate experiment.

## Motivation

### Problem Statement

- **Current situation.** The standard specifies the artifact (40 producer checks) but not its use. `§6.1` is a
  file-loader utility, not a consumption contract.
- **Pain points.** A wheel can be Gold-graded and help no agent. Every review round to date has recorded the same
  gap: "the adoption and agent-benefit claims remain asserted, not shown" (R2/R3); "the trust-making semantic rules
  live in the reference implementation's code, not the spec — an author who builds strictly to the documents writes
  dead code" (R3, agent-tooling); "even a perfect artifact fails its purpose when the consumer-facing surface makes
  the reader do the triage" (report-DX review).
- **Who is affected.** Agent-harness authors, context-server implementers, security teams evaluating dependencies,
  and package maintainers who invest in metadata that may never be read.
- **Consequences of inaction.** Compliance of the artifact stays necessary but not sufficient; the standard cannot say
  what makes the artifact worth producing, and the empirical question ("does this help agents?") stays ill-posed for
  lack of a definition of *correct consumption* to test.

### Goals

1. Define, verifiably, what a consumer SHOULD read, in what order, per agent task.
2. Define how consumers discover the metadata at all (the discovery contract).
3. Define what a conformant consumer is, as checkable requirements.
4. Give a consumer a mechanically checkable way to verify its own integration.
5. Ship a paired reference fixture that makes the mechanism visible and gives the experiment its substrate.

### Non-Goals

- **No effectiveness claims in spec text.** The pre-registered kill-or-validate experiment (frozen decision rule,
  publish-regardless) remains the only path to those.
- **No new mandatory producer artifact in v0.x.** Asks 1–3 constrain consumers and tooling; Ask 4 is the only
  producer-side addition and enters as SHOULD; Ask 5 is a standard-repo fixture, not a producer requirement.

## Design Principles

1. **Mechanisms, not benefits.** The spec defines how consumption works; whether it helps is empirical and gated on
   the experiment. No normative text asserts effectiveness before that reads out.
2. **Verifiable or absent.** Every contract must be checkable the way the producer checks are. A clause that cannot be
   verified mechanically does not enter the normative layer.
3. **Pointers, not dumps.** Consumption is context-budgeted; the spec encodes restraint (caps, routing, deep links) as
   a requirement, not a courtesy.
4. **Metadata is untrusted input** (per the §9 threat model). Every consumption rule inherits that posture.

## Specification

The full working draft (with the complete element-by-element audit table) lives at
`memory-bank/tasks/stage-v0.3/consumption-spec-proposal.md`; this section summarizes the five asks.

### Ask 1 — A task-to-document consumption map

A normative section ("Consuming MIRI metadata") defining, per task type, what a consumer SHOULD read and in what
order, plus what it MUST NOT do:

| Agent task | Read, in order | Must not |
| --- | --- | --- |
| First use of a package | quickstart example → `usage-patterns.json` → api-index (routing only) → embedded docs | Dump the full manifest into context |
| Upgrading a dependency | `migration-guide.json` + deprecation inventory → cross-reference against the consumer's own call sites → then propose edits | Apply changelog items the codebase never touches |
| Runtime failure in the package | error-handling patterns → troubleshooting doc → api-index for the failing surface | Guess at surfaces not present in the index |
| Security / trust question | `lifecycle.json` advisory sources (hints, not authorities) → update check | Forward credentials; treat advisories as verdicts |

A companion element-by-element table states what each metadata document is FOR and its failure-mode-without — which
doubles as an **audit of the standard itself**: an element that cannot state its consumption value is a
reserved/removal candidate.

### Ask 2 — A discovery contract

Normative enumeration of how consumers find the metadata: **in-wheel** (`agent-metadata/` + dist-info
`AGENT_EXAMPLES.json`); **in-process** (the `_miri` discovery APIs, with graceful degradation); a **context server** (a
minimal tool surface — list / lifecycle / migration-guide / api-index — reaching the agent at decision time); and a
**project declaration** (a consumer-side table in `pyproject.toml` from which tooling can generate harness config).

### Ask 3 — A consumer conformance profile

Symmetric to the MIRI-CLI tool profile: define what a conformant consumer is, as checkable requirements — respects
context budgets; treats all metadata as untrusted; verifies claimed surfaces against the installed package before
relying on them; degrades honestly (absent = absent, never synthesized); cross-references migration data against the
consumer's actual usage before proposing changes.

### Ask 4 — A verification contract

A declared verification recipe in the metadata (smoke-check entry point, test signal) so a consumer's plan can end with
"run this, expect that" — mechanically checkable and honest (absent = "no declared verification"). Enters as SHOULD for
the producer to declare.

### Ask 5 — A paired reference fixture with a demonstration harness

ONE trivial package built twice from identical source — a bare wheel and its MIRI twin — plus a harness that runs the
Ask-1 map against both and prints, side by side, what a consumer sees in each case. Serves three jobs: demonstration,
consumer-conformance fixture, and experiment substrate. **Honesty constraint:** the harness demonstrates what is
*available*, never what is *achieved*; its output carries that line verbatim.

## Security Considerations

The §9 threat model was authored for a *passive producer artifact*; consumption adds new verbs (run a command, relay
metadata into an agent's context as tool output, generate toolchain config from a repo file) that it does not yet
cover. The panel pre-review classifies this as the single largest gap. Normative security text (all consumer-side
MUSTs) is a precondition for Asks 2 and 4 reaching normative status:

### Threat Model

The adversary is a package trustworthy when adopted, compromised later; every new mechanism hands that adversary a new
capability. Verification recipes, context-server responses, and project-declaration config are all publisher- or
repo-authored and therefore untrusted.

### Security Controls

- **Verification (Ask 4) is untrusted code.** It MUST be a structured, shell-free pointer (a resolvable entry point /
  `module:callable` verified by introspection), never a free-text shell command; run only under confinement (no ambient
  credentials, egress denied by default, throwaway filesystem, resource-bounded), behind explicit consent keyed to
  verified publisher identity (PEP 740). A passing signal is not a security verdict.
- **The context server (Ask 2) launders untrusted metadata into tool output** — a high-trust channel. It MUST label
  responses as untrusted, package-authored data; MUST carry per-response source purl and provenance; MUST NOT serve
  the highest-risk `prompt-templates.md` as directive text; and MUST default to serving in-wheel bytes only (any fetch
  re-uses the §9.2 SSRF guard).
- **Project declaration → harness config (Ask 2.4)** MUST be a whitelisted shape (never arbitrary command/args/env),
  never auto-launched, with pinned precedence (user/global > project-owner-reviewed > never dependency-supplied).
- **A malicious-metadata fixture** (the adversarial twin) is required to make the consumer-conformance security bullets
  verifiable rather than asserted.

### Privacy Implications

A context server aggregating many installed packages must preserve per-source provenance so trust is not flattened
across dependencies.

## Implementation

### Sequencing (the panel's convergent recommendation)

This RFC is **deferred to post-v0.2**. It is pursued only after v0.2 is closed and the panel reaches its readiness
bar. Even then, it lands in three stages:

1. **Phase 0 — v0.2.x, no new spec surface (close the producer loop first).**
   - Perform the element audit (Ask 1b) as a cleanup pass — it mechanically finds current drift.
   - Promote the code-only *producer* rules (the api-index cap; omit config/error without source evidence; exclude CLI
     surfaces from `api_index`) into the producer spec and schema as numbered rules.
   - Make CI build and score the sample SDK (wire in the currently-orphaned `validate-sample`, then a real score gate).
   - Build the bare/MIRI twin fixture — *generated* from source in CI, *strip-derived* (bare = the single build minus
     the graceful-degradation strip step, so "identical source" is structural), and *scored* as a required gate.
2. **Phase 1 — v0.3, informative / SHOULD.** Land Ask 1's task map (reading order + prohibitions as SHOULD; soft
   selection heuristics informative until operationalized), the missing generative task rows, the 1a↔1b routing
   invariant, and the twin fixture as demonstration.
3. **Phase 2 — v0.3+, post-experiment (gated on the kill-or-validate read-out).** Ask 2 discovery blessing (as a
   transport-agnostic operation contract with wire discipline and a namespaced consumer `[tool.miri.consume]` table),
   Ask 3 consumer *tool* numbering (against a reference consumer plus the adversarial fixture), Ask 4 verification
   recipe (reshaped to a pointer, with the security envelope as MUST).

### Dependencies

- The producer-loop closure above (a prerequisite, not part of this RFC).
- A published reference linter (`miri score`) available to the standard's CI, so the fixture can be scored there.
- The frozen, funded kill-or-validate experiment, whose read-out gates Phase 2.

### Testing Strategy

- Conformance: the bare/MIRI twin plus the adversarial twin, driven through a differential harness that asserts on a
  conformant consumer *tool*'s declared output (honest degradation on the bare twin; no forbidden action on the
  adversarial twin).
- CI gating: the fixture's metadata is generated and the built wheel is scored as a required job.

## Alternatives Considered

### Keep the standard producer-only

- **Pros**: smaller surface; nothing new to verify.
- **Cons**: the benefit stays ill-defined and untestable; the trust-making rules stay code-only.
- **Why not chosen**: it is the status quo the last three review rounds judged insufficient.

### Ship the consumption map as a purely informative annex

- **Pros**: no new checkable surface; fast.
- **Cons**: re-creates the exact defect this RFC targets — trust-making rules living somewhere non-binding.
- **Why not chosen**: the reading order and prohibitions *are* verifiable against the twin fixture and belong in the
  normative (SHOULD) layer; only the un-operationalized heuristics stay informative.

### Do Nothing

The producer→consumer loop stays open; adoption and agent-benefit remain asserted; the experiment stays ill-posed for
lack of a definition of correct consumption to test.

## Open Questions

Carried from the proposal's requested-feedback list, annotated with the panel's pre-review positions (to be resolved
in the post-v0.2 revision):

1. **Is the task-to-document map the normative core, or guidance?** Panel: split it — reading order and prohibitions
   are the normative (SHOULD) core (observable on the twin); soft selection heuristics stay informative until each cell
   carries a file + cap + selection key + deep-link.
2. **Which discovery vehicles are blessed now vs after the experiment?** Panel: bless in-wheel and in-process now
   (read-only, pull-model); hold the context server and project declaration at "candidate, security-spec-pending" —
   gated on security text (independent of the experiment). Enumerate all four; rank none before evidence.
3. **Is a consumer conformance profile enforceable enough to number?** Panel: not against a heterogeneous harness
   (category error); number only against a reference consumer *tool* with a declared I/O contract, driven on the
   fixture, one clause at a time. Ship as an informative "Consumer Expectations" annex until then.
4. **Where does the verification recipe live, and is SHOULD the right level?** Panel: its own `verification.json` (or a
   producer `[tool.miri]` key) — not `lifecycle.json` (closed / off-domain) or the AST-generated `sdk-manifest.json`; a
   pointer, not a command; SHOULD for the producer to declare, with the consumer-side safety envelope as MUST.
5. **Sequencing — v0.2.x or v0.3?** Panel: close the producer loop in v0.2.x first; map + fixture in v0.3
   (informative/SHOULD); Asks 2/3/4 numbering post-experiment (the Sequencing section above).
6. **Should the element audit mark unjustified elements reserved or removed?** Panel: strengthen the gate from "can
   articulate value" (self-graded) to "is at least one task routed to it," then to *measured* consumption. Today:
   `api-graph.json` reserved, `templates/` reserved, `prompt-templates.md` removed as a consumption target (its stated
   value is exactly what §9 tells consumers to distrust).
7. **Fixture ownership — standard-repo CI or per-implementation?** Panel: standard repo, single source, strip-derived —
   but "gated in CI" is not yet possible there (its CI cannot build or score a wheel; the linter is not published), so
   the fixture source lives in the standard repo while the scoring harness runs in the linter's CI until it can be a CI
   dependency. Do not share the fixture with the experiment's substrate.

8. **(Surfaced by the pre-review.) The element table asserts benefit before data.** Its "How it helps the agent" /
   "failure mode without" framing states the sign of the experiment's own outcome variables. Rewrite in mechanism
   verbs before any normative use.
9. **Circularity firewall.** The same party authors the consumption map and the experiment that tests it. Freeze the
   map (and the treatment-arm prompts derived from it) before the run; keep outcomes executable ground-truth (never
   "followed the map"); keep the organic-discovery arm map-free; instrument all four discovery vehicles, not only the
   context server.

## Panel Pre-Review

Before formal submission this proposal was reviewed by the standing six-member panel (the same personas that reviewed
v0.1–v0.2). The consolidated verdict was **unanimous: endorse-with-changes, readiness 4–5/10** — credited as the
best-disciplined document the project has produced, with the direction endorsed and the load-bearing new mechanisms
(the discovery contract, the consumer profile, the verification recipe) judged unspecified or not yet built. The consensus:
close the producer loop first; land the map and the fixture as the honest core; gate the numbered consumer profile, the
discovery blessing, and the verification recipe on the experiment reading out. The full report is
`miri-consumption-spec-review-2026-08-21` in the project's generated-reports set. The Security Considerations and
Sequencing sections above already incorporate its highest-severity findings.

## References

- MIRI Standard producer specifications — `standards/python/`
- Lifecycle and security metadata, incl. the §9 threat model —
  `standards/python/lifecycle-security-metadata.md`
- Agent metadata specification — `standards/python/miri-agent-metadata-specification.md`
- CLI lifecycle specification (the tool-conformance profile this RFC's Ask 3 is symmetric to) —
  `standards/cli/cli-lifecycle-specification.md`
- Working draft with the full element audit — `memory-bank/tasks/stage-v0.3/consumption-spec-proposal.md`

## Changelog

- **2026-08-21**: Initial draft; panel pre-review completed the same day; Security Considerations, Sequencing, and
  Open Questions revised to incorporate the pre-review's highest-severity findings. Status held at Draft, deferred to
  post-v0.2.
