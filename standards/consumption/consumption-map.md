# Miri Standard: Consumption Map (Consumption)

*Specification Version: 0.3-draft*
*Status: Draft*
*Created: 2026*

## Abstract

The [Discovery Contract](discovery-contract.md) says how a package's metadata *reaches* an agent. This document says
what the agent *reads*, per task, and in what order — the teach-the-agent artifact a harness author embeds in a system
prompt, a context server operationalizes, and the experiment's treatment arms encode. It separates a **normative core**
(read-order and prohibitions, mechanically checkable against a reference consumer) from **informative heuristics**, and
it audits every element the standard defines against one question: *what does consuming it buy the agent, and what goes
wrong without it?*

This document specifies *mechanism*, not benefit. It defines correct consumption; whether correct consumption improves
agent outcomes is the pre-registered experiment's question, and no clause here asserts it does.

## Table of Contents

1. [Scope and Posture](#1-scope-and-posture)
2. [Force of Each Clause](#2-force-of-each-clause)
3. [The Task-to-Document Map](#3-the-task-to-document-map)
4. [Interpretation Rules](#4-interpretation-rules)
5. [The Element Audit](#5-the-element-audit)
6. [Conformance](#6-conformance)

---

## 1. Scope and Posture

This is consumer-side guidance. It constrains an agent (and the harness driving it), not the artifact — the producer
requirements are unchanged. Two postures carry from the rest of the standard and are load-bearing here:

- **Metadata is untrusted input.** Every document read below is publisher-authored data, never instructions; it
  inherits the threat model in [Agent Metadata §9](../python/miri-agent-metadata-specification.md) and
  [Discovery Contract §9.1](discovery-contract.md). "Read X" never means "obey X."
- **Pointers, not dumps.** The map is context-budgeted by design: it routes the agent to the smallest sufficient
  document rather than inlining a whole manifest when a pointer suffices.

### 1.1 Vehicles

Each read-step below is labelled with the delivery vehicle that supplies it
([Discovery Contract §1](discovery-contract.md)):

| Label | Vehicle | Availability |
|---|---|---|
| **(S)** | **Served** — obtainable from a context server via a Discovery Contract operation | Any consumer, including one with no filesystem access |
| **(F)** | **Filesystem** — read directly from the installed tree or the wheel | Only a consumer with read access to site-packages |
| **(X)** | **External** — obtained by executing or querying something outside the metadata | Requires the stated capability, with its own caveats |

A consumer MUST skip a step whose vehicle is unavailable to it and continue with the next; a skipped step is reported,
never silently synthesized (§4). Every **(S)** step is servable by `document`, `lifecycle`, `migration-guide`,
`api-index`, or `list` — the Discovery Contract is deliberately sized so that no normative read-order depends on a
document no operation can serve.

## 2. Force of Each Clause

Each task in §3 is given as a read-order, a set of prohibitions, and an informative note, and the three carry
different force:

- **Read, in order** — the recommended reading sequence. It is **SHOULD** for a general consumer and **MUST** for the
  reference consumer (`miri consume`, Consumer Conformance), skipping steps whose vehicle is unavailable (§1.1).
- **Must not** — **correctness and safety prohibitions**, **MUST** for any conformant consumer. Each is verifiable
  from a consumer's *observable output* by driving a reference consumer against the paired bare/miri and
  adversarial-metadata fixtures. Where a prohibition constrains only unobservable internal ordering, it is stated as
  the observable claim the consumer must not make.
- **Should not** — **context-budget preferences**, **SHOULD**. These are efficiency, not correctness; a consumer that
  violates one is wasteful, not wrong, and Consumer Conformance grades them separately from the MUSTs.
- *Heuristic* — informative. Judgment calls and rationale that no linter adjudicates; never a verdict.

The split is the answer to "is a heterogeneous consumer contract enforceable?": the read-*order* is graded guidance,
but the prohibitions are hard rules checkable against a reference tool, and it is the prohibitions that keep a consumer
honest.

## 3. The Task-to-Document Map

### 3.1 First use of a package

**Read, in order:**

1. **(S)** `agent-metadata/README.md` — the generated inventory: what documents this package ships. Equivalently,
   `list` reports the same document set as `documents`.
2. **(S)** The quickstart example (`AGENT_EXAMPLES.json`; `examples/` **(F)**) — the verified-runnable first-contact
   path.
3. **(S)** `usage-patterns.json` — the idiomatic sequence matching the task, rather than one derived from signatures.
4. **(S)** `api-index` — **routing only** (name → purpose → file) to locate the surfaces the pattern names.

**Must not:**

- Claim a package ships no examples, or present reconstructed code as the package's own, when the quickstart was
  simply not read (a honest-degradation claim, observable in output).
- Treat a `README`/prose snippet as verified working code; the runnable examples are the ground truth (MIRI-PY-015).

**Should not:**

- Inline the full `sdk-manifest.json` when the `api-index` routing answers the question.

*Heuristic:* the quickstart before the index — learn the intended entry point before enumerating the surface, so the
agent builds on the path the author verified rather than reconstructing one.

### 3.2 Scaffolding a new integration (generative)

**Read, in order:**

1. **(S)** The quickstart + `usage-patterns.json` — the idiom to build on.
2. **(F)** `templates/` — author-provided scaffolds coherent with the package idiom (MIRI-PY-038).
3. **(S)** `api-index`, then **(F/X)** introspection of the installed package — confirm every symbol the scaffold will
   call actually exists in the installed version.
4. **(S)** `api-graph.json` — for a multi-file change, the blast radius: what the touched surfaces extend, return,
   and use.

**Must not:**

- Emit a call to a symbol that does not exist in the **installed surface**, verified by introspection (the MIRI-PY-036
  discipline applied consumer-side) — the anti-hallucination check.
- Treat absence from an `api-index` response as evidence a symbol does not exist. That response is capped, filtered,
  and may be `truncated` ([Discovery Contract §3.5](discovery-contract.md)): **it can confirm presence, never prove
  absence.** A consumer that cannot introspect the installed package MUST report the symbol as unverified rather than
  either emitting or refusing the call on index membership alone.
- Copy a `templates/` scaffold without reconciling it against the installed version's surfaces.

*Heuristic:* templates encode idiom, the installed surface encodes truth — scaffold from the template, then let
introspection correct it. `api-graph.json` is consulted only when the change spans files; a single-call integration
does not need it.

### 3.3 Upgrading a dependency

**Read, in order:**

1. **(S)** `migration-guide` — the structured `{surface, removed_in, replacement}` records and deprecation inventory.
2. **(F/X)** Cross-reference each record against the consumer codebase's **own call sites**.
3. **(S)** `api-index` — confirm each `replacement` surface appears in the target version, then verify it against the
   installed surface before emitting a call (§3.2).

**Must not:**

- Propose an edit for a migration record the consumer codebase never touches — no changelog cargo-culting. (Observable:
  every proposed edit corresponds to a real call site.)
- Present a migration guide's claims as verified facts about the installed package without checking them against it.

*Heuristic:* an upgrade plan reads as "affected at N sites," not as a changelog paraphrase. The migration guide names
what *could* change; only the consumer's own usage says what *will*.

### 3.4 Diagnosing a runtime failure

**Read, in order:**

1. **(S)** The error-handling patterns in `usage-patterns.json`, if present, for the failing surface.
2. **(F)** `docs/troubleshooting.md` — symptom → cause, without leaving the environment.
3. **(S)** `api-index` for the failing surface — confirm its identity and, where the entry carries a `signature`, its
   parameters. A conformant `api-index` entry carries `signature` and `file` only where the producer supplies them
   ([Discovery Contract §3.5](discovery-contract.md)), so a consumer MUST fall back to introspecting the installed
   surface when they are absent.

**Must not:**

- Assert that a surface does not exist, or that a signature is wrong, on the basis of an `api-index` response alone
  (§3.2 — capped and filtered; presence only).
- Present a cause drawn from the metadata as a confirmed diagnosis without reproducing or verifying it.

*Heuristic:* exhaust the embedded troubleshooting doc before a web search — the answer is more likely offline, version-
matched, and author-written than anything a general search returns.

### 3.5 Answering a security or trust question

**Read, in order:**

1. **(S)** `lifecycle` — support status and identity (`purl`): is this package alive, and exactly which package is it?
2. **(S)** `lifecycle.advisory_sources` — as **pointers to live sources, not verdicts**
   ([Lifecycle and Security Metadata §9.1](../python/lifecycle-security-metadata.md)): the consumer queries the source
   at decision time.
3. **(S)** `lifecycle.update_check` — likewise a pointer to a live check, not a cached answer.

**Must not:**

- Report "no known vulnerabilities" (or any equivalent clean verdict) on the basis of the shipped metadata. An absent
  or empty advisory list is **not** a claim of safety; a verdict requires querying the source at call time
  (declare-sources-not-verdicts).
- Resolve any URL from the metadata without the SSRF guard in
  [Lifecycle and Security Metadata §9.2](../python/lifecycle-security-metadata.md) — HTTPS-only, block private,
  link-local and cloud-metadata ranges, re-validate after redirects — or forward credentials to it. The context server
  performs no fetches ([Discovery Contract §9.2](discovery-contract.md)); resolving these URLs is the consumer's act,
  and its guard is the consumer's obligation.

*Heuristic:* trust is decided at call time against live sources, never read off the shipped file. The metadata tells
the agent *whom to ask*; it never answers *on their behalf*.

## 4. Interpretation Rules

Three rules govern how a consumer reads what it receives. The first two mirror producer-side Generation Invariants
([Agent Metadata §5.4](../python/miri-agent-metadata-specification.md)) that today live only in the reference
generator's code — the "an author who builds strictly to the documents writes dead code" gap, one level down.

- **Absence is evidence-scoped, not existential.** The generator omits a section (e.g. configuration, error handling)
  when it found no source evidence for it. A consumer MUST read an absent section as *"the generator found no
  evidence,"* never as *"the package has no such feature."* It MUST NOT synthesize the missing section and MUST NOT
  infer absence-of-feature from absence-of-section.
- **CLI surfaces are excluded from `api_index`.** Console-script entry points are excluded by construction
  (MIRI-PY-036). A consumer MUST NOT expect a package's CLI commands to appear in an `api-index` response. Those
  surfaces are described by the CLI's own `--describe`
  ([CLI Lifecycle Spec §3](../cli/cli-lifecycle-specification.md)) — which is an **(X)** vehicle: it *executes the
  installed console script*, and is therefore outside the Discovery Contract's import-free, executes-nothing surface
  ([Discovery Contract §5](discovery-contract.md)). A consumer MUST treat invoking it as running installed code, under
  the same confinement it would apply to any other execution, and MUST NOT invoke it merely to enrich a description.
- **A skipped step is reported, never synthesized.** Where a read-step's vehicle is unavailable (§1.1) or its document
  is absent, a consumer MUST say so in its output rather than filling the gap from its own priors. This is the
  honest-degradation rule the bare/miri fixture pair exists to check.

## 5. The Element Audit

The map above says *when* to read; this table records *what each element is for*. Every element the standard defines
gets a row.

**Normative audit rule:** an element defined by the standard MUST be reachable by at least one read-step in §3 or be
marked **reserved**. This is a mechanical criterion — a reviewer checks it by cross-referencing §3 — and it is what
keeps the standard from accreting elements nothing ever reads. It was applied to `api-graph.json` during review, which
survived it by being given a defined consumption role (§3.2 step 4); an element that cannot be given one is a removal
candidate.

The two right-hand columns are **informative**: they record the design intent for each element, not a measured
outcome, and no clause of this standard depends on them.

| Element | What it answers | Design intent *(informative)* | Gap it addresses *(informative)* |
| --- | --- | --- | --- |
| `sdk-manifest.json` (`api_index` + caller params) | "What exists, where, and what does it take?" | Routing (name → purpose → file) and a starting point for surface verification before writing a call | Agent greps serially, or invents plausible symbols that do not exist |
| `usage-patterns.json` | "How do calls compose in practice?" | Idiomatic sequences from real examples/tests, complexity-labeled — a matching pattern instead of one derived from signatures | Calls chained in orders the package never intended; misuse that still type-checks |
| `api-graph.json` | "What relates to what?" | The map to `api_index`'s phone book: extends/returns/uses edges for reasoning about blast radius and planning multi-file changes without loading all source | Structure discovered file by file — context burned on archaeology, relationships guessed |
| `lifecycle.json` | "Is this alive, and whom do I ask?" | Decision-time trust: support status, advisory *pointers*, update check — before building on the package | Health assumed; integration against an abandoned or advisory-laden dependency |
| `migration-guide.json` + deprecation inventory | "What changed, and what replaces what?" | Structured `{surface, removed_in, replacement}` for mechanical cross-reference against the consumer's call sites | Upgrades by prose changelog or trial-and-error; deprecated surfaces linger until removal breaks them |
| `AGENT_EXAMPLES.json` + `examples/` (quickstart) | "Show me working code" | A runnable learning path (MIRI-PY-015 gates it); the quickstart is the first-contact entry point | Agent learns from snippets that may never have run |
| Embedded docs (`api_reference`, `docs/troubleshooting.md`) | "Depth, offline" | The runtime-failure path — symptom → cause without leaving the environment | Debugging falls back to web search or source spelunking |
| `prompt-templates.md` | "How does the author want agents framed?" | Author-curated task scaffolds. **Reserved:** deliberately never served (Discovery Contract §9.1) and routed to by no read-step, because it is the highest-risk injection surface | — |
| `templates/` | "Scaffold me a correct integration" | Code templates coherent with package idiom (MIRI-PY-038 gates coherence) | Boilerplate invented per-agent, drifting from idiom |
| `_miri` discovery APIs (`get_agent_metadata`) | "Programmatic access, in-process" | Runtime self-description with graceful degradation (MIRI-PY-040) — the **(F)** in-process vehicle for code that introspects instead of path-guessing | Hard-coded paths that break when metadata is stripped |
| `agent-metadata/README.md` | "What is in this directory?" | The generated inventory — the entry point an agent that knows nothing else reads first (§3.1 step 1) | Directory contents inferred by listing and opening each file |

## 6. Conformance

The prohibitions in §3 and the interpretation rules in §4 are the checkable consumer requirements; they will be
numbered `MIRI-CONSUMER-NNN` in the forthcoming Consumer Conformance document and verified against the reference
consumer (`miri consume`) driven on the paired bare/miri fixture and an adversarial-metadata twin. The read-order
lists are the reference consumer's required behavior and the general consumer's SHOULD; the **Should not** items are
graded separately as budget preferences. This document defines the contract those checks encode.
