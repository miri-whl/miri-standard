# Proposal: A Consumption Specification for the MIRI Standard

**Status:** DRAFT for panel discussion — not submitted upstream, nothing implemented.
**From:** miri-py (reference implementation)
**Date:** 2026-08-21

## Problem statement

The MIRI Standard v0.2 is a producer-side specification. Its 40 checks define, precisely and
verifiably, what an agent-ready wheel must *ship*. It defines nothing about how an agent
*consumes* what was shipped: no reading order, no discovery contract, no definition of a
conformant consumer, no way for an agent to verify its own integration.

The consequence shows up in every review round to date:

- Round 2 and Round 3 panels: "the adoption and agent-benefit claims remain asserted, not shown."
- Agent-tooling reviewer (R3): the trust-making semantic rules live in the reference
  implementation's code comments, not in spec text — "an author who builds strictly to the
  documents writes dead code."
- Pre-registration H5: whether agents ever open `agent-metadata/` unprompted is an open question;
  if they never do, "the wheel is the wrong delivery vehicle and the standard should say so."
- The report-DX review: even a perfect artifact fails its purpose when the consumer-facing
  surface makes the reader do the triage.

A wheel can be Gold-graded and help no agent. Compliance of the artifact is necessary but not
sufficient; the standard should also specify the consumption contract that makes the artifact
worth producing.

## Design principles

1. **Mechanisms, not benefits.** The spec defines how consumption works. Whether it helps is an
   empirical question with a pre-registered experiment attached; no normative text may assert
   effectiveness before that reads out.
2. **Verifiable or absent.** Every contract below must be checkable the way the 40 artifact
   checks are checkable. If a clause cannot be verified mechanically, it does not go in.
3. **Pointers, not dumps.** Consumption is context-budgeted. The spec should encode restraint
   (caps, routing, deep links) as a requirement, not a courtesy.
4. **Metadata is untrusted input** (§9.4 already): every consumption rule inherits that posture.

## Ask 1 — A normative task-to-document consumption map

A new spec section ("Consuming MIRI metadata") defining, per task type, what a consumer SHOULD
read and in what order:

| Agent task | Read, in order | Must not |
| --- | --- | --- |
| First use of a package | quickstart example → `usage-patterns.json` → api-index (routing only) → embedded docs | Dump the full manifest into context |
| Upgrading a dependency | `migration-guide.json` + deprecation inventory → cross-reference against the consumer codebase's own call sites → only then propose edits | Apply changelog items the codebase never touches |
| Runtime failure in the package | error-handling patterns → troubleshooting doc → api-index for the failing surface | Guess at surfaces not present in the index |
| Security / trust question | `lifecycle.json` advisory sources (as hints, not authorities — §9.1) → update check | Forward credentials; treat advisories as verdicts |

The table is the teach-the-agent artifact: it is what a harness author embeds in a system prompt,
what a context server implements, and what the experiment's treatment arms operationalize.
(Two rules the reference implementation already enforces belong here as precedent: omit
config/error sections when there is no source evidence; CLI surfaces are excluded from
`api_index`. Both are currently code-only — same disease, one level down.)

### 1b. Element-by-element: what each document is FOR

The task map says when to read; this companion table says what each element buys the agent and
what goes wrong without it. Every element the standard defines gets a row — an element that
cannot articulate its consumption value is a candidate for removal, which makes this table a
useful audit of the standard itself.

| Element | What it answers | How it helps the agent | Failure mode without it |
| --- | --- | --- | --- |
| `sdk-manifest.json` (api_index + caller params) | "What exists, where, and what does it take?" | Routing (name → purpose → file) and surface verification BEFORE writing a call — the anti-hallucination check | Agent greps serially, or invents plausible symbols that don't exist |
| `usage-patterns.json` | "How do calls compose in practice?" | Idiomatic sequences extracted from real examples/tests, with complexity labels — pick the pattern matching the task instead of deriving one from signatures | Agent chains calls in orders the package never intended; subtle misuse that type-checks |
| `api-graph.json` | "What relates to what?" | The map where api_index is the phone book: extends/relation edges let the agent reason about blast radius (what else is touched by changing X), navigate inheritance, and plan multi-file changes without loading the whole source into context | Structure discovered by reading files one by one — context burned on archaeology, relationships guessed |
| `lifecycle.json` | "Is this alive, and whom do I ask about it?" | Decision-time trust: support status, advisory sources (hints, not authorities), update check — before the agent builds on the package | Agent assumes health; integrates against an abandoned or advisory-laden dependency |
| `migration-guide.json` + deprecation inventory | "What changed, and what replaces what?" | Structured {surface, removed_in, replacement} → mechanical cross-reference against the consumer's own call sites; upgrade plans become "affected at N sites," not changelog paraphrase | Upgrades by prose changelog or trial-and-error; deprecated surfaces linger until removal breaks them |
| `AGENT_EXAMPLES.json` + `examples/` (quickstart) | "Show me working code" | A verified-runnable learning path (015 gates it) — lessons taught at machine speed are TRUE; quickstart is the first-contact entry point | Agent learns from README snippets that may never have run |
| Embedded docs (`api_reference`, `troubleshooting`) | "Depth, offline" | The runtime-failure path: symptom → cause without leaving the environment | Failure debugging falls back to web search or source spelunking |
| `prompt-templates.md` | "How does the author want agents framed?" | Package-author-curated task scaffolds — the author's own consumption guidance | Every harness re-derives framing per package |
| `templates/` | "Scaffold me a correct integration" | Code templates coherent with package idiom (038 gates coherence) | Boilerplate invented per-agent, drifting from idiom |
| `_miri` discovery APIs | "Programmatic access, in-process" | Runtime self-description with graceful degradation (040) — agent code can introspect instead of path-guessing | Hard-coded paths that break when metadata is stripped |
| `agent-metadata/README.md` | "What's in this directory?" | The generated inventory — the entry point an agent that knows nothing else can read first | Directory contents must be inferred by listing and opening each file |

## Ask 2 — A discovery contract

Normative enumeration of how consumers find the metadata at all:

1. **In-wheel** (exists): `agent-metadata/` + dist-info `AGENT_EXAMPLES.json`.
2. **In-process** (exists, §6.1): the `_miri` discovery APIs with graceful degradation.
3. **Context server** (new): a minimal MCP tool surface (list / lifecycle / migration-guide /
   api-index) so metadata reaches the agent at decision time without file spelunking. The
   reference implementation ships this today (`miri mcp`).
4. **Project declaration** (new): a `[tool.miri]` table in the consuming project's
   `pyproject.toml` declaring the context server, from which tooling can generate harness config
   (e.g., `.mcp.json`) — making agent-readiness a declared property of a project rather than
   per-machine setup.

H5's invocation-log data adjudicates between vehicles; the spec names them now and retires the
losers on evidence.

## Ask 3 — A consumer conformance profile

Symmetric to the MIRI-CLI tool profile: define what a **conformant consumer** is, as checkable
requirements (MIRI-CONSUMER-00x):

- Respects context budgets: routing responses capped (the api-index 25-entry cap as precedent);
  never inlines a document when a pointer suffices.
- Treats all metadata as untrusted data (§9.4); never executes or forwards credentials on its
  say-so.
- Verifies claimed surfaces against the installed package (import/`inspect` resolution) before
  relying on them — the MIRI-PY-035/036 discipline applied consumer-side.
- Degrades honestly: absent documents are reported absent, never synthesized.
- When acting on migration data, cross-references against the consumer codebase's actual usage
  before proposing changes (no changelog-cargo-culting).

The reference consumer (`miri brief`, planned) implements this profile the way `miri score`
implements the linter contract.

## Ask 4 — A verification contract

"Understand how to test the wheel" is currently only half-specified: examples must be runnable
(015), but nothing tells an agent how to close the loop on its *own* integration. Ask: a
declared verification recipe in the metadata (e.g., a `verification` object in the manifest or
lifecycle: smoke-check entry point, test command, expected signal) so a consumer's plan can end
with "run this, expect that" — mechanically checkable (the declared command exists and is
runnable under the execution capability) and honest (absent = "no declared verification").

## Ask 5 — A paired miri / non-miri reference fixture with a demonstration harness

The standard should ship ONE trivial package built twice from identical source: a bare wheel and
its MIRI twin (full `agent-metadata/`, dist-info `AGENT_EXAMPLES.json`, discovery APIs). Plus a
small harness that runs the Ask-1 consumption map against both and prints, side by side, exactly
what a consumer sees in each case: the twin answers routing/lifecycle/migration/example queries;
the bare wheel yields honest "absent" on every one.

Three jobs, one fixture:

1. **Demonstration** — the five-minute artifact for any skeptic or adopter: same code, here is
   what the agent gets with and without the standard. (Mechanism made visible, NOT proof of
   benefit — see below.)
2. **Consumer conformance fixture** — the bare twin is the test bed for the MIRI-CONSUMER
   honest-degradation checks (Ask 3): a conformant consumer must report absence, never
   synthesize. The twin pair makes those checks executable in CI.
3. **Experiment substrate** — the kill-or-validate conditions need exactly this pairing
   (package-only vs full-miri arms, pre-registration §3); a committee-owned fixture pair means
   the experiment and the standard test against the same artifacts.

The upstream sample SDK is halfway there (the compliant build exists); the ask is the bare twin
built from the same source in the same CI, plus the comparison harness — gated in CI so both
stay green (the round-3 lesson: an ungated sample rots).

**Honesty constraint:** the harness demonstrates what is *available*, never what is *achieved*.
Its output must carry that line verbatim; agent-benefit claims remain gated on the experiment.

## What we are NOT asking

- No effectiveness claims in spec text; the kill-or-validate experiment (frozen decision rule,
  publish-regardless) remains the only path to those.
- No new mandatory artifact for producers in v0.x: asks 1–3 constrain consumers and tooling;
  ask 4 is the only producer-side addition and should enter as SHOULD; ask 5 is a
  standard-repo fixture, not a producer requirement.

## Evidence base for the panel

Three review rounds (R1–R3), the report-DX review, the H5 instrument (`miri mcp --log`
JSONL), and the pre-registration's task taxonomy — which this proposal makes well-formed by
fixing what "correct consumption" means for each task type.

## Requested feedback

1. Is the task-to-document map the right normative core, or should it stay guidance (SHOULD vs
   informative annex)?
2. Which discovery vehicles deserve blessing now vs after H5 data?
3. Is a consumer conformance profile enforceable enough to be worth numbering, given consumers
   are heterogeneous harnesses?
4. Where should the verification recipe live (manifest vs lifecycle), and is SHOULD the right
   level?
5. Sequencing: does any of this belong in v0.2.x, or is it all v0.3 material?
6. The element-by-element table (1b) doubles as an audit: should an element that cannot state
   its consumption value be marked reserved or removed? (api-graph survived its round-3 scare
   by becoming real — the table is how the next such element gets caught earlier.)
7. Fixture ownership (Ask 5): does the bare/miri twin pair live in the standard repo's CI (our
   preference — one source of truth for demonstration, consumer conformance, and the
   experiment's substrate), or does each implementation build its own?
