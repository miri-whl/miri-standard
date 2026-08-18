# CLI Interfaces for Agent Consumers: Landscape, Prior Art, and Open Gaps

*Prepared as background input for **Miri**. Current as of August 2026.*

---

## 0. Summary

There is no standard for making a CLI legible to an AI agent. There are:

- **Two genuine standards** covering command-line *syntax* (POSIX XBD §12.2, GNU Coding Standards §4.7). Both predate
  agents and say nothing about machine-readable output.
- **One de-facto style guide** (clig.dev) that is widely cited but has no normative authority.
- **A cluster of 2026-vintage manifestos** — at least six independent efforts — that converge on nearly identical advice
  but have no shared schema, no conformance test, and no cross-adoption.
- **One adjacent standard with real adoption** (Agent Skills / `SKILL.md`), which solves discovery via filesystem
  convention rather than via the CLI itself.

The convergence across the manifestos is a good sign for eventual consolidation. The unaddressed area — and the largest
opening for a new standard — is **change over time**: versioning, deprecation, migration, and the fact that a meaningful
fraction of an agent CLI's consumers are frozen model weights that can never read a changelog.

---

## 1. What Is Actually Standardized Today

### 1.1 POSIX Utility Syntax Guidelines

IEEE Std 1003.1 (XBD §12.2) defines what an option looks like: the `-` delimiter, single-alphanumeric short option
names, `-abc` bundling for options that take no argument, `-o foo` and `-ofoo` equivalence, the `--` terminator, and
options-before-operands ordering.

It also defines the SYNOPSIS grammar used in both man pages and help text: bold for literal text, italic for replaceable
arguments, `[ ]` for optional, `|` for alternatives, `...` for repeatable.

**Scope:** syntax only. Nothing about output format, exit codes beyond 0/non-zero, or help content.

### 1.2 GNU Coding Standards §4.7

Requires that `--help` print brief invocation documentation to **stdout** and exit **successfully**, ignoring all other
options once seen. Requires long-form options as synonyms for short ones, and maintains a "Table of Long Options" so
that `--verbose` means the same thing across every GNU program.

**Scope:** behavior of the `--help` flag itself, plus naming consistency. Nothing about structure, sections, examples,
or machine parsing.

### 1.3 clig.dev — Command Line Interface Guidelines

Community document (originating with people from Heroku/Stripe). Recommends `-h`/`--help`, per-subcommand help, worked
examples, `NO_COLOR` support, TTY detection, and standard environment variable names.

**Status:** widely cited, no normative authority, no conformance mechanism. Functions as the shared vocabulary rather
than a spec.

### 1.4 Adjacent prior art: tldr-pages JSON schemas

The [tldr-json-schemas](https://github.com/tldr-pages/tldr-json-schemas) project predates the agent wave and shares its
core motivation: man pages are unreliable as a parsing source because they are written for humans, so a
language-independent schema is needed to describe command syntax. It also resolves the classic ambiguity of whether
`-ab` is two bundled short options or one option with an attached value.

Worth reviewing before designing anything from scratch — the ambiguity cases they enumerate are the same ones any
introspection schema must handle.

---

## 2. Emerging Work (2026)

None of the following is a standard. All are one-organization or one-author efforts. Listed roughly in order of how
spec-like they are.

### 2.1 Agent-First CLI — `agentfirstcli.github.io`

The closest thing to a written spec. Sixteen principles across six categories, published with a machine-readable `principles.json`.

| # | Principle | Tagline |
|---|---|---|
| 01 | Structured Output | Data over decoration |
| 02 | Token Efficiency | Signal over noise |
| 03 | Deterministic Ordering | Predictable over pretty |
| 04 | Structured Progress | Events over animations |
| 05 | Partial Failure Output | Partial truth over total silence |
| 06 | Semantic Exit Codes | Meaning over convention |
| 07 | Parseable Errors | Codes over prose |
| 08 | Non-Interactive Default | Automation over assumption |
| 09 | Idempotent Operations | Convergence over sequence |
| 10 | Faithful Dry Run | Simulation over approximation |
| 11 | Graceful Cancellation | Cleanup over corruption |
| 12 | Stable Schema | Contract over convenience |
| 13 | Stable Flags | Contract over changelog |
| 14 | Capability Negotiation | Query over guess |
| 15 | Machine-Readable Help | Introspection over documentation |
| 16 | Signal Danger | Guardrails over good luck |

**Principle 15** is the direct answer to "is there a standard for `--help`. " Its argument: agents learn flags either
from training data scraped before the model's cutoff, or by parsing `--help` at runtime. Training data goes stale — a
flag added last release is invisible to an agent working from weights. Runtime parsing is brittle; `git log --help` on
macOS opens a man page in a pager, which in a non-interactive context may block, emit terminal control codes, or vary by
`PAGER`.

Proposed shape is `<cmd> --help --output json` returning typed data: aliases collapsed into one entry with multiple
names, enum members enumerated, optional-value flags marked explicitly, and inter-flag constraints expressed as
structured rules rather than prose.

The most important implementation note, and one worth carrying into Miri verbatim in spirit: **do not generate the
machine-readable form by parsing your own help text.** Write the schema as data and derive both the human help and the
machine output from it. This keeps them in sync by construction and eliminates the bug class where `--help` documents a
flag removed two versions ago.

### 2.2 anc.dev — "The Agent-Native CLI Standard"

Six MUST-level requirements, shipped with a linter (`anc`) and an MCP server. Notable requirements:

- Non-interactive by default — a tool that blocks on a prompt is invisible to an agent; the agent hangs and the
  operation times out silently.
- Separate data from diagnostics; offer machine-readable output.
- `--dry-run` on every write operation.
- The read-vs-write distinction must be visible from the command name and `--help` alone.
- Composability: handle SIGPIPE, detect TTY, accept stdin.

Also argues that a skill bundle (`AGENTS.md` / `SKILL.md`) beats `--help` for discovery, because it is found through
filesystem convention and loaded once rather than re-parsed per session.

### 2.3 Practitioner writeups

Independent, converge sharply.

- **Justin Poehnelt** (built the Google Workspace CLI agent-first) — gives a retrofit order of operations: add
  `--output json`; validate all inputs assuming adversarial input; add `--describe` or schema introspection; support
  `--fields` masks so agents can limit response size and protect their context window; add `--dry-run`.
- **Ezequiel Aceto** — same two pillars: structured output via `--json`, and runtime introspection exposing the command
  tree, parameters, types, and required scope as JSON.
- **Terry Li** (`mtor`) — argues only four things are genuinely agent-specific and the rest is just good CLI design. His
  envelope: `ok`, `result`, `error`, `fix`, `next_actions`, `version`. The envelope shape *is* the API, and it is
  versioned.
- **`desk`** — `--capabilities` returning version plus, per service, the command list, which commands support batching,
  which support dry-run, and which are destructive. Errors carry `suggestions` (dynamically generated next actions) and
  a `retryable` boolean. Mutations accept `--idempotency-key` so a retried command is a safe no-op returning the
  original result.
- **Trevin Chow** — adds a point the others miss: pick *one* output flag and use it everywhere. Always `--json`, never
  `--format=json` on some commands and `--output json` on others. Inconsistency at that layer is its own category of
  brokenness. Also proposes a `feedback` subcommand so agents have a channel to report friction, since otherwise the
  agent retries, eventually succeeds, and the maintainer never learns.
- **Propel Code** — ties CLI output to review policy: emit stable artifacts (dry-run record, diff summary, provenance)
  so merges can be gated on their presence rather than on a human reverse-engineering the run.

### 2.4 Commercial implementations

- **Speakeasy** (OpenAPI → CLI generator) — ships `--agent-mode` to disable interactivity, JSON Schema definitions for
  all commands and responses, and capability exposure via `llms.txt` and `skills.md`. Notably outputs **TOON** rather
  than JSON in agent mode, which is a useful signal that even the serialization format is unsettled.
- **Docker Agent CLI** — every subcommand accepts `--json`; success documents carry a top-level `"schema_version": "1"`
  marker with stable snake_case keys and no prose or ANSI mixed in. Mutations require either `--expected-version <n>`
  (optimistic lock; version conflict exits 3) or an explicit `--force`.
- **env0 Agent CLI** — generates a **version-matched** usage guide into the coding agent's config, so the agent works
  from the command surface actually installed rather than one half-remembered from training. The guide is a committed
  file in the repo, extensible with local policy.
- **Google `agents-cli`** — ships CLI + skills together; includes an `upgrade` command that performs a three-way merge
  between old template, new template, and the user's project.

### 2.5 The thing with actual adoption: Agent Skills

`SKILL.md` / `AGENTS.md`. Released as an open standard in December 2025; adopted across Codex CLI, Microsoft Agent
Framework, Cursor, and Copilot. Deliberately minimal schema — name, description, markdown body — which is credited with
enabling the breadth of adoption.

**The division of responsibility that works:**

> The installed CLI is the source of truth for **syntax**. The skill is the source of truth for **workflow**.

Do not copy the manual into `SKILL.md`. Instruct the agent to run `<cli> --help` before first use in a session and to
treat the installed binary's help as authoritative over skill examples, because help text changes as versions change.

---

## 3. The Gap: Everything Above Assumes a Static CLI

This is the largest unaddressed area, and it is not an oversight — it is deliberate avoidance.

Agent-First CLI's principle 13 is titled **"Stable Flags — Contract over changelog."** Principle 12 is **"Stable Schema
— Contract over convenience."** The movement's answer to change is *don't change*. That is a freeze, not a migration
story. It is reasonable advice for `ls`; it is unusable for any product whose command surface will churn through its
first several years.

### 3.1 Why change is structurally harder with agent consumers

An agent's knowledge of a CLI comes from three sources that go stale at three different rates and cannot be invalidated
the same way:

| Source | Freshness | Can be notified? |
|---|---|---|
| Model weights | Frozen at training cutoff | **No — ever** |
| Skill file (`SKILL.md`) | Whenever someone re-syncs | Only if regenerated |
| Live `--help` / `--describe` | Always current | Only if consulted |

The middle row is a process problem. The top row is genuinely new. With human users, a breaking change costs each user
one read of the changelog. With agents, part of the consumer population is *structurally incapable* of reading it. You
cannot reach them. You can only make the failure recoverable at call time.

The failure mode is also silent. An agent constructs a command from weights, gets an error, retries with a hallucinated
variant, eventually stumbles into something that works. No bug report is filed. The maintainer never learns the
interface degraded.

### 3.2 The canonical cautionary tale

`kubectl get --export`: deprecated in v1.14, removed in v1.18. Broke Helm chart template generation and CI/CD pipelines
doing resource backup. The deprecation was well-documented — so it was not a communication failure. The failure was not
recognizing that **CLI output formats are contracts, and contracts have dependencies.**

That happened with human consumers who could at least read release notes. The blast radius with agent consumers is
strictly larger.

### 3.3 Mechanisms that exist in the wild

Assembled from shipped tools rather than from any spec:

1. **Version the wire schema separately from the product.** Docker's `"schema_version": "1"` on every payload; Terry
   Li's versioned envelope. The product can go to 2.0 without the contract moving, and the contract can break at 1.4
   with an honest signal.
2. **Deprecation metadata inside the introspection output.** Not in `CHANGELOG.md`. A `--describe` entry carrying
   `deprecated_since`, `removed_in`, and `replacement` is read at call time by an agent that will never read release
   notes. Agent-First CLI's principle 15 mentions this in passing; nobody has specified its shape.
3. **Removal errors that teach.** `error: unrecognized arguments: --foo` is a dead end. A structured error carrying
   `retryable: false` plus `suggestions: ["use --bar instead"]` converts a hard failure into a one-turn recovery.
4. **Regenerate the skill file from the installed binary.** The env0 pattern, and the only shipped answer to
   weight-staleness. `<cli> agent-context --write` regenerating the repo's `SKILL.md` from the same schema struct that
   produces `--help` means an upgrade automatically re-teaches every agent in the repo — and the diff surfaces in code
   review.
5. **Deprecation warnings on stderr, never stdout.** A notice printed to stdout corrupts the JSON payload and every
   downstream parser fails simultaneously.
6. **Schema pinning.** `--describe --schema-version 1` keeps serving the old shape after shipping 2.

### 3.4 The missing artifact: an explicit stability contract

SemVer for a CLI is ambiguous because **nothing defines the public API**. A bump to 2.0 is meaningless if consumers were
never told which surfaces were covered.

The missing document is a one-page stability contract, committed to the repo, that states explicitly:

**Covered by SemVer:**

- flag names and their accepted types
- JSON keys and value types under `--json`
- `schema_version`
- exit code meanings
- subcommand paths

**Not covered:**

- human-readable text and its wording
- log message phrasing
- field ordering within JSON objects
- stderr formatting
- anything behind `--debug`

Write it once and both directions get easier: the maintainer knows what they are allowed to break, and the consumer
knows what is safe to depend on.

---

## 4. Candidate Scope for Miri

Where a new standard has room to be additive rather than the seventh restatement of "emit JSON":

1. **A normative introspection schema.** The manifestos describe the *idea* of `--describe` output; none publishes a
   schema with a version, a JSON Schema document, and a conformance test. That artifact does not exist and is the
   obvious first deliverable.
2. **Lifecycle as a first-class concern.** Deprecation states, removal timelines, schema pinning, and negotiation — the
   entire area principle 13 declines to address.
3. **The stability contract as a required artifact**, with a defined vocabulary for what SemVer covers.
4. **A machine-readable changelog.** No tool ships `<cli> changelog --since <version> --json`. An agent that has been
   away for three releases has no way to ask what moved. This is a clean, small, obviously-useful primitive nobody has
   claimed.
5. **Skill-file regeneration as a specified command**, not a vendor pattern — so the CLI can re-teach its own consumers
   on upgrade.
6. **Flag-name convergence.** GNU's Table of Long Options solved this for `--verbose`. The agent-era equivalent
   (`--json` vs `--output json` vs `--format json`; `--dry-run` vs `--plan`; `--yes` vs `--auto-approve` vs `--force`)
   is unsolved and actively fragmenting.

Item 4 is probably the highest ratio of usefulness to effort, and item 2 is the one with no incumbent.

---

## 5. Multi-Clock Versioning Note

For any CLI fronting a versioned service API, there are **three independent clocks**:

- the CLI's own release version
- the CLI's wire schema version (what `--json` emits)
- the backing service API version

Collapse any two and you lose the ability to ship a change to one without a major bump in the other. Three version
fields is more bookkeeping than it looks, but the coupling is otherwise discovered at the worst possible moment.

---

## References

**Standards and guidelines.**

- POSIX / IEEE Std 1003.1, XBD §12.2 Utility Syntax Guidelines — <https://posix.opengroup.org>
- GNU Coding Standards, `--help` — <https://www.gnu.org/prep/standards/html_node/_002d_002dhelp.html>
- GNU Coding Standards, Command-Line Interfaces — <https://www.gnu.org/prep/standards/html_node/Command_002dLine-Interfaces.html>
- Command Line Interface Guidelines — <https://clig.dev/>
- tldr-pages JSON schemas — <https://github.com/tldr-pages/tldr-json-schemas>

**Emerging agent-CLI work.**

- Agent-First CLI (16 principles) — <https://agentfirstcli.github.io/>
- Agent-First CLI, Machine-Readable Help — <https://agentfirstcli.github.io/principles/machine-readable-help/>
- anc.dev, Agent-Native CLI Standard — <https://anc.dev/>
- Poehnelt, *You Need to Rewrite Your CLI for AI Agents* — <https://justin.poehnelt.com/posts/rewrite-your-cli-for-ai-agents/>
- Aceto, *Effective CLI Tools for the AI Era* — <https://www.kimi.blog/blog/effective-cli-tools-for-the-ai-era>
- Li, *4 Principles for Agent-Facing CLI Design* — <https://terryli.ai/posts/4-principles-for-agent-facing-cli-design/>
- Chow, *10 Principles for Agent-Native CLIs* — <https://trevinsays.com/p/10-principles-for-agent-native-clis>
- *Agent-first CLIs are about reducing turns, not JSON* — <https://keyboardsdown.com/posts/01-agent-first-clis/>
- *Writing CLI Tools That AI Agents Actually Want to Use* — <https://dev.to/uenyioha/writing-cli-tools-that-ai-agents-actually-want-to-use-39no>
- Propel Code, *Agent-First CLI Design* — <https://www.propelcode.ai/blog/agent-first-cli-design-coding-agents>
- InfoQ, *Keep the Terminal Relevant* (the `--export` case study) — <https://www.infoq.com/articles/ai-agent-cli/>

**Implementations.**

- Speakeasy CLI generation — <https://www.speakeasy.com/product/cli-generation>
- Docker Agent CLI reference — <https://docker.github.io/docker-agent/features/cli/>
- env0 Agent CLI — <https://www.env0.com/blog/announcing-the-env-zero-agentic-experience-point-your-coding-agent-at-your-infrastructure>
- Google `agents-cli` — <https://github.com/google/agents-cli>
- CLI skill design practices — <https://agent-layer.dev/cli-skill-design/>
