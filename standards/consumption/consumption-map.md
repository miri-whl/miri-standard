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
| **(C)** | **Consumer's own workspace** — the calling project's source, not the dependency's | Always available to the consumer; nothing to do with the surface |

These four labels are the complete set. A step carries exactly one; there is no compound label.

A consumer MUST skip a step whose vehicle is unavailable to it and continue with the next; a skipped step is reported,
never silently synthesized (§4). Every **(S)** step is servable by `list`, `document`, `lifecycle`,
`migration-guide`, `api-index`, or `resolve` — the Discovery Contract is deliberately sized so that no normative
read-order depends on an answer no operation can give. In particular a **server-only consumer can complete every
task in §3**, including the generative ones: `resolve` is what makes the anti-hallucination rule dischargeable
without filesystem access.

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

1. **(S)** `list` — the inventory: which documents this package ships, composed by the surface from the directory
   listing rather than read from a publisher-authored index
   ([Discovery Contract §3.2.1](discovery-contract.md)).
2. **(S)** `patterns` — the idiomatic sequence matching the task, rather than one derived from signatures. This is
   the served path to working code. Read each returned pattern **whole**: `explanation.key_points`, `security_note`
   and `performance_note` carry the author's best-practice guidance, and `antipatterns` carries the negative half —
   the mistakes the author expects a caller to make.
3. **(F)** The quickstart (`AGENT_EXAMPLES.json`, `examples/`) — the verified-runnable first-contact path
   (MIRI-PY-015). `AGENT_EXAMPLES.json` is a `.dist-info/` file and `examples/` is package source, so **neither is
   servable**; a consumer without filesystem access skips this step and relies on step 2.
4. **(S)** `api-index` — **routing only** (name → purpose, plus `file`/`signature` where the producer supplies them)
   to locate the surfaces the pattern names.

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

1. **(S)** `patterns` — the idiom to build on, read whole (best-practice fields and `antipatterns` included).
2. **(F)** `templates/` — author-provided scaffolds coherent with the package idiom (MIRI-PY-038).
3. **(S)** `resolve` — confirm every symbol the scaffold will call actually exists in the installed package's
   source ([Discovery Contract §3.6](discovery-contract.md)). `api-index` routes; `resolve` settles.
4. **(S)** `graph` — for a multi-file change, the blast radius around each touched symbol: what it extends, returns
   and uses. A truncated neighborhood MUST NOT be read as the complete blast radius
   ([Discovery Contract §3.8](discovery-contract.md)).

**Must not:**

- **Present a call as verified when `resolve` did not confirm the symbol.** A `found: true` result is the only
  positive evidence this contract offers; anything else — `not-in-source`, `module-unreadable`, or no `resolve` call
  at all — leaves the symbol **unverified**, and a consumer that emits it anyway MUST say so rather than presenting
  it as checked. (Observable: a symbol asserted as existing that `resolve` reports `found: false` for.)
- **Refuse a call solely because `resolve` returned `not-in-source`.** That result is weak evidence
  ([§3.6.1](discovery-contract.md)) — dynamically constructed surfaces are invisible to static parsing — so treating
  it as proof of non-existence makes the consumer wrong about every runtime-generated API. Report unverified;
  do not conclude absence.
- Treat absence from an `api-index` response as evidence a symbol does not exist. That response is capped, filtered,
  and may be `truncated` ([Discovery Contract §3.5](discovery-contract.md)): **it can confirm presence, never prove
  absence.** Existence questions go to `resolve`, never to the index.
- Copy a `templates/` scaffold without reconciling it against the installed version's surfaces.
- **Emit code that a returned `antipattern` of severity `correctness` or `security` describes as wrong, without
  surfacing that the author has flagged it.** These are author-declared failure modes for the exact surface being
  called; silently reproducing one is the failure this element exists to prevent. (Observable: emitted code matching
  a `wrong_code` whose severity is `correctness` or `security`, with no mention of the author's warning.)

*Heuristic:* templates encode idiom, the installed surface encodes truth — scaffold from the template, then let
introspection correct it. `graph` is consulted only when the change spans files; a single-call integration does not
need it.

### 3.3 Upgrading a dependency

**Read, in order:**

1. **(S)** `migration-guide` — the structured `{surface, removed_in, replacement}` records and deprecation inventory
   for the transition **into the installed version**. The surface answers only for what is installed
   ([Discovery Contract §6.2.1](discovery-contract.md)); a prospective "what breaks if I move to 1.5.0?" has no
   operation in 0.3 and MUST NOT be answered from the shipped file.
2. **(C)** Cross-reference each record against the consumer codebase's **own call sites**.
3. **(S)** `resolve` — confirm each `replacement` surface exists in the **installed** package before emitting a call
   to it (§3.2). Where the replacement is not yet installed, the record is reported as
   pending verification, not as a confirmed target.

**Must not:**

- Propose an edit for a migration record the consumer codebase never touches — no changelog cargo-culting. (Observable:
  every proposed edit corresponds to a real call site.)
- Present a migration guide's claims as verified facts about the installed package without checking them against it.
- **Automatically install, or migrate code onto, a declared `replacement`**
  ([Lifecycle and Security Metadata §9.3](../python/lifecycle-security-metadata.md)). A `replacement` purl is
  publisher-authored and may point into a namespace the publisher does not control; a compromised release can redirect
  dependents onto an attacker-held successor. The consumer surfaces the claim for a human decision and MUST flag a
  replacement whose purl namespace differs from the deprecated package's.

*Heuristic:* an upgrade plan reads as "affected at N sites," not as a changelog paraphrase. The migration guide names
what *could* change; only the consumer's own usage says what *will*.

### 3.4 Diagnosing a runtime failure

**Read, in order:**

1. **(S)** `patterns` filtered to the failing surface — its error-handling patterns and, in particular, its
   `antipatterns`, which often name the failure directly.
2. **(F)** `docs/troubleshooting.md` — symptom → cause, without leaving the environment.
3. **(S)** `api-index` for the failing surface — confirm its identity and, where the entry carries a `signature`, its
   parameters. A conformant `api-index` entry carries `signature` and `file` only where the producer supplies them
   ([Discovery Contract §3.5](discovery-contract.md)), so a consumer MUST fall back to **(S)** `resolve`, which
   reports `kind`, `file`, `line` and `signature` from the source, when they are absent.

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

### 3.6 Writing tests against a dependency

**Read, in order:**

1. **(S)** `test-patterns.json` — how the package's own suite exercises the surface being integrated, and which test
   doubles the package **ships** for consumers.
2. **(S)** `api-index` — confirm the surface under test, and its `signature` where the producer supplies one.
3. **(S)** `usage-patterns.json` — the idiomatic call sequence the test should exercise, so the test covers real usage
   rather than an invented one.

**Must not:**

- Present a **synthesized mock as the package's supported test double.** Only entries in
  `supported_test_doubles` are supported; anything the consumer invents is its own, and MUST be described as such.
  (Observable: a claimed "official" fake that appears in no `supported_test_doubles` entry.)
- Run a pattern whose `requires_network` or `requires_credentials` is `true` without explicit opt-in, and never
  fabricate or substitute credentials to make one run.
- Report that a package "has no tests" from the absence of `test-patterns.json`. Absence is evidence-scoped (§4): it
  means no test patterns were generated, not that the package is untested.

*Heuristic:* a package's own suite is the most reliable statement of how its surface is meant to be exercised —
including which failures it treats as expected. Prefer extending its idiom over inventing a parallel one.

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
- **A pointer is not a permission.** Several elements carry paths that point into the package — `api_index`'s `file`,
  `api-graph` nodes' `file`/`module`, `test-patterns`' `source_file`. These are **publisher-authored strings**, and a
  consumer that opens one is acting on untrusted input. Before dereferencing any such pointer a consumer MUST resolve
  it against the package's own root, take the fully resolved path, and confirm the result is a regular file
  **physically inside that root** — rejecting symbolic links, absolute paths, and traversal sequences. A pointer that
  escapes the package root MUST be reported as malformed and MUST NOT be opened. This mirrors the obligation the
  Discovery Contract places on a *surface* ([§3.2.2](discovery-contract.md)); the same discipline applies to a
  consumer, because the same string reaches it.

- **A skipped step is reported, never synthesized.** Where a read-step's vehicle is unavailable (§1.1) or its document
  is absent, a consumer MUST say so in its output rather than filling the gap from its own priors. This is the
  honest-degradation rule the bare/miri fixture pair exists to check.

## 5. The Element Audit

The map above says *when* to read; this table records *what each element is for*. Every element the standard defines
gets a row.

**Normative audit rule — both directions.** The audit is bidirectional, and each direction catches a different
failure:

1. **Element → task.** Every element the standard defines MUST be reachable by at least one read-step in §3, or be
   marked **reserved**. This keeps the standard from accreting elements nothing ever reads. It was applied to
   `api-graph.json` during review, which survived by being given a defined consumption role (§3.2 step 4); an element
   that cannot be given one is a removal candidate.
2. **Task → element.** Every task in §3 MUST have at least one element that answers it, and — conversely — **a
   question a developer demonstrably asks, with no element to answer it, is a gap the audit MUST record** as a row
   with no element rather than leaving it invisible.

Direction 2 was added after direction 1 alone failed to catch a real hole. Testing — "how do I test my integration?" —
had no element, so it had no row, so the completeness check passed silently: *a capability that was never defined
cannot fail an elements-only audit.* An audit that only walks the elements it already has can never discover the one
it is missing. `test-patterns.json` (§3.6) closes that specific gap; the rule change is what stops the next one
hiding the same way.

The two right-hand columns are **informative**: they record the design intent for each element, not a measured
outcome, and no clause of this standard depends on them.

| Element | What it answers | Design intent *(informative)* | Gap it addresses *(informative)* |
| --- | --- | --- | --- |
| `sdk-manifest.json` (`api_index` + caller params) | "What exists, where, and what does it take?" | Routing (name → purpose → file) and a starting point for surface verification before writing a call | Agent greps serially, or invents plausible symbols that do not exist |
| `usage-patterns.json` | "How do calls compose in practice?" | Idiomatic sequences from real examples/tests, complexity-labeled — a matching pattern instead of one derived from signatures. Carries **both halves** of usage guidance: `explanation.*` for what to do, `antipatterns` for the author-declared ways to get it wrong | Calls chained in orders the package never intended; misuse that still type-checks |
| `api-graph.json` | "What relates to what?" | The map to `api_index`'s phone book: extends/returns/uses edges for reasoning about blast radius and planning multi-file changes without loading all source | Structure discovered file by file — context burned on archaeology, relationships guessed |
| `lifecycle.json` | "Is this alive, and whom do I ask?" | Decision-time trust: support status, advisory *pointers*, update check — before building on the package | Health assumed; integration against an abandoned or advisory-laden dependency |
| `migration-guide.json` + deprecation inventory | "What changed, and what replaces what?" | Structured `{surface, removed_in, replacement}` for mechanical cross-reference against the consumer's call sites | Upgrades by prose changelog or trial-and-error; deprecated surfaces linger until removal breaks them |
| `AGENT_EXAMPLES.json` + `examples/` (quickstart) | "Show me working code" | A runnable learning path (MIRI-PY-015 gates it). **(F) only** — `AGENT_EXAMPLES.json` lives in `.dist-info/` and `examples/` is package source, so neither is servable; `usage-patterns.json` is the served path to working code | Agent learns from snippets that may never have run |
| Embedded docs (`api_reference`, `docs/troubleshooting.md`) | "Depth, offline" | The runtime-failure path — symptom → cause without leaving the environment | Debugging falls back to web search or source spelunking |
| `test-patterns.json` | "How do I test my integration against this?" | Per-surface unit and integration patterns extracted from the package's own suite, plus the test doubles the package actually ships — so a test exercises the package's real idiom and known-expected failures | Tests written from priors against a guessed surface; consumers inventing mocks that drift from the package's own fidelity assumptions |
| `prompt-templates.md` | "How does the author want agents framed?" | Author-curated task scaffolds. **Reserved:** deliberately never served (Discovery Contract §9.1) and routed to by no read-step, because it is the highest-risk injection surface | — |
| `templates/` | "Scaffold me a correct integration" | Code templates coherent with package idiom (MIRI-PY-038 gates coherence) | Boilerplate invented per-agent, drifting from idiom |
| `_miri` discovery APIs (`get_agent_metadata`) | "Programmatic access, in-process" | Runtime self-description with graceful degradation (MIRI-PY-040) — the **(F)** in-process vehicle for code that introspects instead of path-guessing | Hard-coded paths that break when metadata is stripped |
| `agent-metadata/README.md` | "What is in this directory?" | **Reserved:** superseded as a consumption path by `list`, which composes the same inventory surface-side. Never served (Discovery Contract §3.2.1) — a prose file with no schema is the wrong shape for a first read. It remains a human-facing convenience in the wheel. | — |

## 6. Conformance

The prohibitions in §3 and the interpretation rules in §4 are the checkable consumer requirements; they will be
numbered `MIRI-CONSUMER-NNN` in the forthcoming Consumer Conformance document and verified against the reference
consumer (`miri consume`) driven on the paired bare/miri fixture and an adversarial-metadata twin. The read-order
lists are the reference consumer's required behavior and the general consumer's SHOULD; the **Should not** items are
graded separately as budget preferences. This document defines the contract those checks encode.
