# Glossary

Every term this standard defines, and a few it deliberately does not. Where a term has a normative definition, the
entry says where that definition lives — this page explains, it does not define, and a disagreement between the two
is a defect in this page.

The vocabulary grew across four documents and two years, so several terms have close neighbors that mean different
things. Those pairs are the ones worth reading: **absent and error**, **task and trigger**, **binding and hook**,
**level and severity**, **not-applicable and forfeited**.

## The three actors

**Producer** ([Python checklist](../standards/python/linter-checklist.md); [CLI
checklist](../standards/cli/linter-checklist.md)) — whatever builds the artifact and ships its metadata. A wheel's build
backend, a CLI's release
process. Scored by `MIRI-PY` and `MIRI-CLI`.

**Surface** — a program that *serves* metadata in answer to queries, without deciding anything about it. It reads
in-wheel bytes and relays them; it never fetches, never executes, and never repairs. Scored by `MIRI-SURFACE`.
Defined in [Discovery Contract §3](../standards/consumption/discovery-contract.md).

**Consumer** ([Consumer Conformance](../standards/consumption/consumer-conformance.md)) — a program that *asks* and then
decides what to believe. An agent, a linter, a CLI. Scored by
`MIRI-CONSUMER`, and driven rather than inspected, because a consumer's conformance is a property of what it does.

A fourth actor exists and is currently unscored: the **generator**, which reads a project's `[tool.miri.consume]`
declaration and emits harness configuration. Four rules bind it and no profile checks them; that gap is recorded in
[Consumer Conformance §4](../standards/consumption/consumer-conformance.md) rather than left to be discovered.

## Asking and answering

**Operation** — one of the eight things a surface can be asked ([Discovery Contract
§3](../standards/consumption/discovery-contract.md)). `list`, `document`, `lifecycle`,
`migration-guide`, `api-index`, `resolve`, `patterns`, `graph`. The set is closed; a surface exposing a ninth is
non-conforming.

They fall into three kinds, and the kind decides what an *absent* answer licenses:

- **Retrieval** — `document` and its two shorthands. Serves a named document verbatim. Absence means the package
  does not ship that file.
- **Derived view** — `api-index`, `patterns`, `graph`. A bounded selection from a larger document. Absence means
  **nothing**, because the answer is capped and the thing may be past the cap.
- **Determination** — `list`, `resolve`. Answers a question rather than serving a document. Absence *is* the answer.

**Envelope** ([Discovery Contract §4](../standards/consumption/discovery-contract.md);
[`discovery-envelope-v1.json`](../schemas/discovery-envelope-v1.json)) — the JSON object wrapping every response. Its
top level is owned entirely by the **surface**; the
publisher's bytes appear only nested under a payload key. That is the whole anti-forgery mechanism: a package can
write `"ok": false` into its own `lifecycle.json`, and those bytes are still served intact — one level down, where
they are data rather than signal. The standard does not sanitize the payload; it denies the payload the position
from which it could be believed. Governed by
[`discovery-envelope-v1.json`](../schemas/discovery-envelope-v1.json).

**Payload key** — the field carrying the answer ([Discovery Contract
§4.1](../standards/consumption/discovery-contract.md)): `packages`, `document`, `entries`, `resolution`, `patterns`,
`graph`, and `findings` for a trigger response. Exactly one appears, and only when `present` is true.

**Absent versus error** ([Discovery Contract §4.2](../standards/consumption/discovery-contract.md)) — two independent
booleans, and the distinction the
whole contract rests on.

| | `ok` | `present` | Means |
|---|---|---|---|
| **served** | `true` | `true` | here it is |
| **absent** | `true` | `false` | the surface answered; the thing does not exist |
| **error** | `false` | *omitted* | the surface could not answer |

Collapsing absent into error makes a consumer retry something that will never succeed. Collapsing it into served
with an empty payload makes a consumer report "no advisories" when it means "no advisory file". Three outcomes,
never two.

**`reason`** ([Discovery Contract §4.1](../standards/consumption/discovery-contract.md)) — free text explaining an
absence, **for humans only**. A consumer branches on `ok` and `present` and
never on `reason`; a surface never copies publisher bytes into it. It is omitted entirely when `ok` is `false`,
because a failure is the response a consumer scrutinizes least and free text there is an injection channel wearing a
helpful label.

**Cap, `truncated`, cursor** ([Discovery Contract §3.5.1](../standards/consumption/discovery-contract.md)) — a derived
view is bounded. `cap` is the bound in force, `truncated` says whether
anything was dropped, and a cursor continues the same ordering. `truncated: true` with **no** `next_cursor` is
valid and means *there is more and I cannot reach it* — the honest answer from a surface that keeps no cursor state.

## Reading

**Task** — one of six jobs a consumer does: first use, scaffolding, upgrading, diagnosing, security, writing tests.
Each is a read-order plus a set of prohibitions. Defined in
[Consumption Map §3](../standards/consumption/consumption-map.md).

**Vehicle** ([Consumption Map §1.1](../standards/consumption/consumption-map.md)) — *how* a read-step's data arrives,
and therefore what a consumer must possess to perform it.

| | Vehicle | Needs |
|---|---|---|
| **(S)** | Served by an operation | only a connection |
| **(S?)** | Served, but the surface may decline — the document is provisional | only a connection; absence is expected |
| **(F)** | Filesystem, read from the installed tree | read access to site-packages |
| **(X)** | External, obtained by executing something | the ability to run installed code |
| **(C)** | The consumer's own workspace | nothing; it already has it |

**Trigger** ([Agent Integration §3.1](../standards/consumption/agent-integration-contract.md)) — *when* a task becomes
actionable. The third column of a table that already had *what* (task) and
*how* (vehicle), and the one this standard was missing until 0.4. Six of them, named for observable actions:
`dependency.add`, `dependency.version_change`, `package.first_reference`, `integration.begin`, `runtime.error`,
`test.author`.

**Event** — the message a host sends when a trigger fires. Governed by
[`agent-event-v1.json`](../schemas/agent-event-v1.json), whose root is **closed** so a host cannot smuggle a file
path, a diff, or the user's source into it.

**Binding** — one host's implementation of a contract ([Discovery Contract
§6](../standards/consumption/discovery-contract.md) binds MCP;
[Agent Integration §5–6](../standards/consumption/agent-integration-contract.md) binds Claude Code). MCP is a binding of
the Discovery Contract; a Claude Code
plugin is a binding of the Agent Integration Contract. A binding names its host, maps the contract's vocabulary onto
that host's mechanisms, and **says which parts it cannot support** rather than approximating them.

**Hook** — *not a term of this standard* (the reasoning is [Agent Integration
§1](../standards/consumption/agent-integration-contract.md)). It is what one host calls its delivery mechanism, and it
appears in these
documents only when describing git or setuptools. The sentence that has to keep working is *"Claude Code delivers a
trigger via a hook; CI delivers the same trigger via a step"* — which only parses if hook is theirs and trigger is
ours. Naming the mechanism in a specification is how a standard acquires one vendor's vocabulary permanently.

**Skip reason** ([Consumption Map §4](../standards/consumption/consumption-map.md)) — why a read-step produced no
answer. A closed set of four, and the distinctions matter:
`absent` (the vehicle worked; the artifact does not exist), `unavailable-vehicle` (the consumer lacks the vehicle),
`error` (the vehicle was available and failed), `not-applicable` (the step's stated condition does not hold).
`absent` and `error` are kept apart because one is a fact about the package and the other a fact about the attempt.

## Checking

**Check** — one numbered, mechanically decidable requirement, governed by
[`check-v1.json`](../schemas/check-v1.json). Its authoritative form is a YAML file under
`standards/<target>/checks/`; the tables in the profiles are a derived rendering. IDs are **never renumbered**, and
the numbering is **sparse** — `MIRI-CONSUMER` runs 001–051 across seventeen checks, so an ID range is an address
space and never a count.

**`fires_when`** ([`check-v1.json`](../schemas/check-v1.json)) — the operative content of a check: the concrete
conditions under which a conforming linter raises
it. Everything else in a check file is explanation; this is the part an implementer implements.

**Level** ([Consumer Conformance §3](../standards/consumption/consumer-conformance.md)) — `MUST` or `SHOULD`. A failing
MUST makes an artifact **non-conforming**, and a non-conforming result
carries no grade at all — only the score, capped, to show distance. Distinct from **severity** (`LOW` … `CRITICAL`),
which is about how bad one violation is for health scoring. Level answers *may I proceed*; severity answers *how
bad is this*.

**Weight** ([Consumer Conformance §3](../standards/consumption/consumer-conformance.md)) — a check's share of 100. Every
target's active weights sum to exactly 100, which is why adding a check
means redistributing rather than appending.

**Conditional** ([Consumer Conformance §3](../standards/consumption/consumer-conformance.md)) — a check whose obligation
only applies in some circumstances. **Not-applicable is not a pass**: a
conditional check whose condition does not hold is removed from *both* the numerator and the denominator, never
credited. The earlier model awarded a CLI twenty points for never deprecating anything.

**Forfeited** ([Consumer Conformance §3](../standards/consumption/consumer-conformance.md)) — a check the suite could
not drive. Also excluded from both sides, and **reported**, because a
coverage gap silently omitted becomes a coverage claim. A forfeited MUST leaves conformance **undetermined** — a
third outcome, not a shade of pass or fail — and no grade is emitted.

## Verifying

**Fixture** ([`examples/fixtures/`](../examples/fixtures/README.md)) — one of ten variants of a single trivial
package, built from one template. Every `.py` is verified
**byte-identical** across the source-sharing variants, so any difference in a consumer's behavior is attributable to
the metadata and nothing else. That property is what makes the whole suite evidential rather than anecdotal.

**Adversarial twin** ([`examples/fixtures/`](../examples/fixtures/README.md)) — the variant whose metadata lies: forged
envelope keys, phantom symbols, a padded index, a
prompt injection, an SSRF payload, a cross-namespace replacement, and a field bidding for the agent's attention.

**Golden** ([`examples/fixtures/expected/`](../examples/fixtures/README.md)) — a file stating what a conformant
surface must return and what a conformant consumer must not do, for
one attack. Authored from the specification, never captured from an implementation — because a golden captured from
the tool it grades is the tool grading itself.

**Paired control** ([Consumer Conformance §5](../standards/consumption/consumer-conformance.md)) — an attack fixture and
its innocent twin, scored as one check over two runs. A consumer that
refuses both has not detected the attack; it has disabled the feature. Either arm wrong fails the whole check,
because half credit is exactly what a blanket refusal would earn.

**Circularity firewall** ([Consumer Conformance §6](../standards/consumption/consumer-conformance.md)) — the rule that a
reference consumer and a reference surface must not share the code under
test. Where they do, the suite drives the consumer against **recorded** responses so the surface's code never runs.

## Identity and trust

**purl** ([Discovery Contract §4.1](../standards/consumption/discovery-contract.md); [purl
specification](https://github.com/package-url/purl-spec)) — the
package URL that joins an artifact to advisory data. A **surface-derived** field: the surface reads
it from the installed distribution's own record and never from a served document, because a package that could
declare its own purl could inherit any namespace's trust by saying so.

**`advisory_coverage`** ([CLI Spec §4.1](../standards/cli/cli-lifecycle-specification.md)) — whether any listed advisory
source is authoritative for the artifact *itself* rather than
its dependency tree. `none` declares honestly that no machine-queryable source covers this artifact — the true state
for a git-installed binary in no package ecosystem — and requires a published security policy in exchange. A
consumer reading it reports *"no advisory source covers this artifact"*, never *"no known vulnerabilities"*.

**Content versus control** ([Agent Metadata §9](../standards/python/miri-agent-metadata-specification.md); [Agent
Integration §4.3](../standards/consumption/agent-integration-contract.md)) — the axis the threat
model gained in 0.4. Every earlier item concerned what metadata
*says*: narrative files inject, an index can lie, provenance anchors trust. A shipped field that determines whether
an integration fires concerns what metadata *makes happen* — a denial-of-context channel rather than a false
statement, and closed by a different rule.
