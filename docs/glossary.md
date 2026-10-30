# Glossary

This page explains every term the standard defines, and a few it deliberately leaves undefined. `purl`, SBOM and OSV are
used here as their own specifications define them. Where a term has a normative definition, the entry links to it. The
definitions themselves live in the specifications, and where this page disagrees with one, the defect is in this page.

Several terms have close neighbors that mean different things. These pairs are the easiest to confuse: **absent and
error**, **task and trigger**, **binding and hook**, **level and severity**, **not-applicable and forfeited**.

## The three actors

**Producer** ([Python checklist](../standards/python/linter-checklist.md); [CLI
checklist](../standards/cli/linter-checklist.md)): whatever builds the artifact and ships its metadata, such as a
wheel's build backend or a CLI's release process. `MIRI-PY` and `MIRI-CLI` score it.

**Surface** ([Discovery Contract §3](../standards/consumption/discovery-contract.md)): a program that *serves* metadata
in answer to queries, without deciding anything about it. It reads in-wheel bytes and relays them. It never fetches,
never executes, and never repairs. `MIRI-SURFACE` scores it.

**Consumer** ([Consumer Conformance](../standards/consumption/consumer-conformance.md)): a program that *asks* and then
decides what to believe, such as an agent, a linter or a CLI. `MIRI-CONSUMER` scores it. The suite drives a consumer
rather than inspecting it, because a consumer's conformance is a property of what it does.

The standard also has a fourth actor that no profile scores. The **generator** reads a project's `[tool.miri.consume]`
declaration and emits harness configuration. Four rules bind it, and [Consumer Conformance
§4](../standards/consumption/consumer-conformance.md) records that no profile checks them.

## Asking and answering

**Operation** ([Discovery Contract §3](../standards/consumption/discovery-contract.md)): one of the eight things a
surface can be asked. The eight are `list`, `document`, `lifecycle`, `migration-guide`, `api-index`, `resolve`,
`patterns` and `graph`. The set is closed, and a surface exposing a ninth is non-conforming.

Operations fall into three kinds, and the kind decides what an *absent* answer licenses:

- **Retrieval** (`document` and its two shorthands) serves a named document verbatim. Absence means the package does
  not ship that file.
- **Derived view** (`api-index`, `patterns`, `graph`) returns a bounded selection from a larger document. Absence
  means **nothing**, because the answer is capped and the thing may be past the cap.
- **Determination** (`list`, `resolve`) answers a question rather than serving a document. Absence *is* the answer.

**Envelope** ([Discovery Contract §4](../standards/consumption/discovery-contract.md)): the JSON object wrapping
every response. The **surface** owns all of its top level, and the publisher's bytes appear only nested under a
payload key. This separation is what stops a package from forging the signals a consumer branches on. A package can
write `"ok": false` into its own `lifecycle.json`, and the surface still serves those bytes intact. They sit one level
down, as data rather than signal. The standard does not sanitize the payload; it denies the payload the position from
which it could be believed. The envelope's schema is
[`discovery-envelope-v1.json`](../schemas/discovery-envelope-v1.json).

**Payload key** ([Discovery Contract §4.1](../standards/consumption/discovery-contract.md)): the field carrying
the answer. The keys are `packages`, `document`, `entries`, `resolution`, `patterns`, `graph`, and `findings` for a
trigger response. Exactly one appears, and only when `present` is true.

**Absent versus error** ([Discovery Contract §4.2](../standards/consumption/discovery-contract.md)): the distinction the
whole contract rests on, carried by two independent booleans.

| | `ok` | `present` | Means |
|---|---|---|---|
| **served** | `true` | `true` | here it is |
| **absent** | `true` | `false` | the surface answered; the thing does not exist |
| **error** | `false` | *omitted* | the surface could not answer |

Collapsing absent into error makes a consumer retry something that will never succeed. Collapsing it into served with an
empty payload makes a consumer report "no advisories" when it means "no advisory file". Each response has one of three
outcomes, and a consumer has to keep all three apart.

**`reason`** ([Discovery Contract §4.1](../standards/consumption/discovery-contract.md)): free text explaining an
absence, **for humans only**. A consumer branches on `ok` and `present` and never on `reason`. A surface never copies
publisher bytes into it. The field is left out when `ok` is `false`. A failure is the response a consumer scrutinizes
least, and free text there would be an injection channel.

**Cap, `truncated`, cursor** ([Discovery Contract §3.5.1](../standards/consumption/discovery-contract.md)): the bounds
on a derived view. `cap` is the bound in force. `truncated` says whether anything was dropped. A cursor continues the
same ordering. `truncated: true` with **no** `next_cursor` is valid, and it means *there is more and I cannot reach it*.
This is the correct answer from a surface that keeps no cursor state.

## Reading

**Task** ([Consumption Map §3](../standards/consumption/consumption-map.md)): one of the six jobs a consumer does. The
six are first use, scaffolding, upgrading, diagnosing, security, and writing tests. Each is a read-order plus a set
of prohibitions.

**Vehicle** ([Consumption Map §1.1](../standards/consumption/consumption-map.md)): *how* a read-step's data arrives, and
therefore what a consumer must possess to perform it.

| | Vehicle | Needs |
|---|---|---|
| **(S)** | Served by an operation | only a connection |
| **(S?)** | Served, but the surface may decline (the document is provisional) | only a connection; absence is expected |
| **(F)** | Filesystem, read from the installed tree | read access to site-packages |
| **(X)** | External, obtained by executing something | the ability to run installed code |
| **(C)** | The consumer's own workspace | nothing; it already has it |

**Trigger** ([Agent Integration §3.1](../standards/consumption/agent-integration-contract.md)): *when* a task
becomes actionable. It is the third column beside *what* (the task) and *how* (the vehicle), and the standard added it
in 0.4. There are seven, each named for an observable action: `dependency.add`, `dependency.version_change`,
`package.replaced`, `package.first_reference`, `integration.begin`, `runtime.error`, `test.author`.

`package.replaced` differs from the others. It fires when an installed artifact is replaced **without its
version changing**. A purl cannot see that case, because a purl identifies a name and a version, never a byte stream
([Lifecycle and Security Metadata §9.6](../standards/python/lifecycle-security-metadata.md)). It is the only trigger
that routes to two tasks. A replaced artifact raises two questions: what the surface is now, and whether it may still
be trusted. Answering one does not answer the other.

**Event** ([`agent-event-v1.json`](../schemas/agent-event-v1.json)): the message a host sends when a trigger fires. The
schema's root is **closed**. A host therefore cannot smuggle a file path, a diff, or the user's source into an event.

**Binding** ([Discovery Contract §6](../standards/consumption/discovery-contract.md) binds MCP; [Agent Integration
§5–6](../standards/consumption/agent-integration-contract.md) binds Claude Code): one host's implementation of
a contract. MCP is a binding of the Discovery Contract, and a Claude Code plugin is a binding of
the Agent Integration Contract. A binding names its host and maps the contract's vocabulary onto the
mechanisms of that host. It also **states which parts it cannot support** and does not approximate them.

**Hook** ([Agent Integration §1](../standards/consumption/agent-integration-contract.md) gives the reasoning): *not a
term of this standard*. It is what one host calls its delivery mechanism, and these documents use it only when
describing git or setuptools. The sentence that has to keep working is *"Claude Code delivers a trigger via a hook; CI
delivers the same trigger via a step"*. It parses only if hook is theirs and trigger is ours. Naming the mechanism in a
specification is how a standard acquires one vendor's vocabulary permanently.

**Skip reason** ([Consumption Map §4](../standards/consumption/consumption-map.md)): why a read-step produced no answer.
The set is closed and has four members: `absent` (the vehicle worked; the artifact does not exist),
`unavailable-vehicle` (the consumer lacks the vehicle), `error` (the vehicle was available and failed), `not-applicable`
(the step's stated condition does not hold). `absent` and `error` are kept apart because one is a fact about the package
and the other a fact about the attempt.

**Honest degradation** ([Consumer Conformance §5, category
A](../standards/consumption/consumer-conformance.md#a-honest-degradation-22-points)): what a consumer does when metadata
is **absent**. It reports an absent document as absent and never synthesizes content for one. It branches on `ok` and
`present`, never on `reason` text. These are checks `MIRI-CONSUMER-001` to `003`, category A of the consumer profile at
22 points, and the `bare` fixture exists for this category. The specs use the same term wherever the rule recurs, for
example in the Consumption Map's handling of a skipped read-step
([§4](../standards/consumption/consumption-map.md#4-interpretation-rules)). Its near neighbor, **absent versus
error**, is the surface's half of the rule. A consumer's honest degradation can be checked only if the surface
itself tells absent from failed ([Discovery Contract
§4.2](../standards/consumption/discovery-contract.md#42-absence-is-not-error)).

**Blast radius** ([Consumption Map
§3.2](../standards/consumption/consumption-map.md#32-scaffolding-a-new-integration-generative), step 4): the symbols
reachable from a symbol by the edges `graph` returns, which are what it extends, returns and uses. A truncated `graph`
neighborhood is not the complete blast radius ([Discovery Contract
§3.8](../standards/consumption/discovery-contract.md#38-graph)).

## Checking

**Gate** ([Python checklist](../standards/python/linter-checklist.md); `scoring: gate` in
[check-v3](../schemas/check-v3.json)): a check that is a **precondition rather than a measurement**. It carries weight 0
and enters neither side of the conformance ratio. Failing it makes the artifact non-conforming. There are three,
`MIRI-PY-001`, `002` and `003`. They are the wheel-structure and metadata checks an index enforces at upload. Every
correctly built wheel passed them, and as measurements they separated nothing. A gate can only be a `MUST`. Its sole
declared effect is non-conformance, and a SHOULD cannot cause non-conformance. A SHOULD gate would therefore be inert.

Because a gate has weight 0, a failing gate leaves **no arithmetic trace**. A scorer that computes conformance from
weights alone cannot see it. Its only representation is `must_failures` in
[lint-report-v1](../schemas/lint-report-v1.json). That field is coupled to the grade and the 74 cap.

**Effective denominator** ([Python checklist](../standards/python/linter-checklist.md)): the sum of the weights of the
checks that **applied and could be evaluated**. A conformance score is a percentage of this sum. It is at most 100 and
is often less. A report MUST carry it. A score of 80 out of 100 and one of 80 out of 58 are different claims, and the
number alone cannot distinguish them. The denominator deliberately has **no floor**, because a small one usually means a
simpler artifact rather than a worse one.

**Undetermined** ([lint-report-v1](../schemas/lint-report-v1.json) `grade`): the grade when a **forfeited** MUST leaves
conformance unknowable. It is not non-conformance. The obligation applied and went unassessed, and the artifact is
neither known to conform nor known to fail. An **excluded** MUST never produces it, because that obligation did not
exist for this artifact. The [conditional](../standards/python/linter-checklist.md#scoring-model) and
[forfeited](../standards/consumption/consumer-conformance.md#3-scoring-model) rules decide which of the two applies.
Both have entries later in this section.

**Check** ([`check-v3.json`](../schemas/check-v3.json)): one numbered, mechanically decidable requirement. Its
authoritative form is a YAML file under `standards/<target>/checks/`. The tables in the profiles are a
derived rendering. IDs are **never renumbered**, and the numbering is **sparse**. For example, `MIRI-CONSUMER` runs
001–052 across eighteen checks. An ID range is an address space and never a count.

**`fires_when`** ([`check-v3.json`](../schemas/check-v3.json)): the operative content of a check, meaning the concrete
conditions under which a conforming linter raises it. Everything else in a check file is explanation. This is the part
an implementer implements.

**Level** ([Consumer Conformance §3](../standards/consumption/consumer-conformance.md)): `MUST` or `SHOULD`. A failing
MUST makes an artifact **non-conforming**. A non-conforming result carries no grade at all. It carries only the score,
capped, to show its distance from conformance. Level is distinct from **severity** (`LOW` … `CRITICAL`). Severity
measures how bad one violation is for health scoring. Level answers *may I proceed*; severity answers *how bad is this*.

**Weight** ([Consumer Conformance §3](../standards/consumption/consumer-conformance.md)): a check's share of 100. Every
target's active weights sum to exactly 100. Adding a check therefore means redistributing weight rather than
appending it.

**Tiers** ([`check-v3.json`](../schemas/check-v3.json)): for a substance-bearing check, the cumulative schedule by which
its weight is earned instead of awarded as a bit. The tiers are **T0** *exists* (present, parses, schema-valid), **T1**
*true* (named symbols resolve, embedded code runs against this artifact), **T2** *covers* (a calibrated floor of the
surface it owns) and **T3** *current* (stamps in window, current version described, no dangling claim against the
previous release). Every tier clause is a join or an execution, never a word count or a judgment. T2 ships defined but
weightless until the corpus trigger in [`scoring-v1.json`](../schemas/scoring-v1.json) is met.

**Conformance tier** ([`check-v3.json`](../schemas/check-v3.json)): the tier at which a tiered check's *obligation*
is satisfied. Tiers above it price weight only. Pass/fail is derived from it (`tier_earned >= conformance_tier`), and
the verdict vocabulary therefore does not grow. The default is **T1**. At T1 the MUST boundary sits at the *lie* rather
than at thinness. A document whose claims are false fails the MUST and the 74 cap fires; one that is true but thin
passes and earns a thin score.

**Tier earned** ([lint-report-v1](../schemas/lint-report-v1.json)): the highest tier whose every clause held, with all
its predecessors held. A report gives it per outcome for a tiered check. It explains a status and never replaces it. Its
absence on a tiered check means every tier was forfeited.

**Staleness classes** ([Agent Metadata §4.7](../standards/python/miri-agent-metadata-specification.md)): the four ways a
document that is present, schema-valid and stamped in the build window can still be wrong about the artifact it
ships in. Each is a cross-artifact join, decidable without judgment. **Dangling claim** (`MIRI-PY-044`): the document
names a symbol, document or version the artifact does not carry. **Uncovered delta** (`MIRI-PY-043`): the artifact
measurably changed and the owning document is silent. **Version silence** (`MIRI-PY-042`): the release-describing
document has no entry for the version it ships in. **Stamp drift** (`MIRI-PY-011`): the generation stamp falls outside
the build window. The first three read `changelog.json`. The fourth predates it and served as their model.

**Conditional** ([Consumer Conformance §3](../standards/consumption/consumer-conformance.md)): a check whose obligation
applies only in some circumstances. The rule is that **not-applicable is not a pass**. A conditional check whose
condition does not hold is removed from *both* the numerator and the denominator and is never credited. Under the
earlier model, a CLI collected twenty points for never deprecating anything.

**Forfeited** ([Consumer Conformance §3](../standards/consumption/consumer-conformance.md)): a check the suite could
not drive. It is also excluded from both sides of the ratio. It is **reported** as well, because a coverage gap that is
silently omitted becomes a coverage claim. A forfeited MUST leaves conformance **undetermined**, and no grade
is emitted. Undetermined is a third outcome, not a shade of pass or fail. A forfeit has two sources, and both use the
same arithmetic. One is a **capability** the linter lacks (`network_unavailable`,
`previous_release_unavailable`, `execution_disabled`). The other, since 0.6.0, is **implementation coverage**: the
linter ships no verification for the check at all (`not_implemented`, which must name a `blocker`). Neither is ever an
exclusion, because the obligation existed. `scoring-v1.json` `conformance.coverage` gives the five driver clauses.

## Verifying

**Reachable** ([Linter Checklist § Reachability](../standards/python/linter-checklist.md)): the property a path must
have for a check to be satisfied. A path is reachable when the installed import package can open it. In practice that
means `importlib.resources.files(<pkg>).joinpath(<path>)` resolves to a file. The near neighbor is **present**. A member
routed through the PEP 427 `.data` scheme is present in the archive and listed in `RECORD`. It installs to
`<venv>/examples/`, outside the package. Nothing that needs the file can open it there. Six checks depend
on reachability. An absent file and an unreachable one also take opposite remedies. The first needs writing, and the
second needs moving.

**Fixture** ([`examples/fixtures/`](../examples/fixtures/README.md)): one variant of a single trivial artifact, built
from one template. It differs from its siblings **only** in shipped metadata. Every `.py` is verified **byte-identical**
across the source-sharing variants. Any difference in behavior is therefore attributable to the metadata and
nothing else. That property makes a suite evidential rather than anecdotal. Three suites exist: the consumption fixtures
(eleven `greet` wheels, driving a *consumer*), the `greetctl` fixtures (four variants, driving a *CLI linter*), and the
`greetlib` wheel fixtures (nine wheels, driving a *wheel linter*).

**Adversarial twin** ([`examples/fixtures/`](../examples/fixtures/README.md)): the variant whose metadata lies. It
carries forged envelope keys, phantom symbols, a padded index, a prompt injection, an SSRF payload, a cross-namespace
replacement, and a field bidding for the agent's attention.

**Golden** ([`examples/fixtures/expected/`](../examples/fixtures/README.md)): a file stating what a conformant
implementation must produce for one case. For a surface and a consumer, it states what the surface must return and what
the consumer must not do. For a linter, it states which checks the linter must report against which arm. A golden is
authored from the specification and never captured from an implementation. A golden captured from the tool it grades is
the tool grading itself. A golden an implementation does not attempt is **forfeited as unimplemented**. That forfeit is
reported and is never counted as a pass.

**Attribution** ([`examples/fixtures/python/`](../examples/fixtures/README.md)): the property a golden grades
beyond detection. A finding satisfies a golden only if it names the right check **and** points at the evidence declared
for that check. Detection and attribution are different properties. A grader that pools evidence across a case gives
full marks to an indiscriminate report.

**Evidence** ([`lint-report-v1`](../schemas/lint-report-v1.json)): an outcome's array of `<document>:<field>` strings
naming what a finding points at. The document-only form (`changelog.json`, no field) is correct where the check's own
`violation_unit` is the document. The field arrived in 0.7.0. Before it, the standard could ask a linter to be right but
had no way to ask where the problem was.

**Paired control** ([Consumer Conformance §5](../standards/consumption/consumer-conformance.md)): an attack fixture and
its innocent twin, scored as one check over two runs. A consumer that refuses both has not detected the attack; it has
disabled the feature. Getting either arm wrong fails the whole check, because a blanket refusal would otherwise earn
half credit.

**Circularity firewall** ([Consumer Conformance §6](../standards/consumption/consumer-conformance.md)): the rule that a
reference consumer and a reference surface must not share the code under test. Where they do, the suite drives the
consumer against **recorded** responses so the surface's code never runs.

## Identity and trust

**purl** ([Discovery Contract §4.1](../standards/consumption/discovery-contract.md); [purl
specification](https://github.com/package-url/purl-spec)): the package URL that joins an artifact to advisory data. A
purl is **surface-derived**. It comes from the installed distribution's own record and never from a
served document. A package that could declare its own purl could claim any namespace's trust.

**SBOM** ([MIRI-PY-024](../standards/python/checks/MIRI-PY-024.yaml); [PEP 770](https://peps.python.org/pep-0770/)): the
inventory of what an artifact *contains* beyond the code its package manager knows about. A wheel that vendors a native
library has two identities. One is the identity its purl declares. The other is the library linked inside it. No
dependency-graph scan can see the second one. PEP 770 places the documents at `.dist-info/sboms/`. Scanners find them
there without a Miri-specific pointer. An SBOM is required only when the artifact bundles non-Python components, and it
is required to **cover** them. A document that exists but inventories something else satisfies the form and not
the rule.

**VEX** ([MIRI-PY-026](../standards/python/checks/MIRI-PY-026.yaml); [OpenVEX](https://github.com/openvex/spec)): a
vendor-authored statement that a vulnerability in a listed component is or is not exploitable in this artifact. It lets
a consumer suppress a false positive with an auditable record instead of an ignore-list. VEX is a *source*, and the
verdict stays with the consumer. A declared `vex` URL that serves nothing is worse than none. A consumer that planned to
apply suppressions on its authority then either re-raises every finding or fails open.

**Provenance** ([MIRI-PY-005](../standards/python/checks/MIRI-PY-005.yaml); [SLSA build
provenance](https://slsa.dev/spec/v1.2/build-provenance)): a signed statement binding an artifact to the source and the
build that produced it. The **mechanism** and the **content** are separate and often confused. PEP 740 is how an index
receives, verifies and republishes an attestation. SLSA provenance is what the attestation says: its `buildDefinition`,
its `runDetails`, and a `builder.id`. Miri checks the first and not yet the second. An attestation that asserts nothing
useful about the build therefore still satisfies `MIRI-PY-005`.

**Attestation versus self-consistency** ([MIRI-PY-001](../standards/python/checks/MIRI-PY-001.yaml)): the boundary a
conformance report must not blur. Checks computed *inside* an artifact prove that the artifact agrees with itself.
Examples are RECORD matching the archive and a manifest digest matching the files. Such checks detect corruption and an
edit nobody hid. They cannot establish where the artifact came from, because whatever rewrote a file rewrote the
manifest in the same motion. Only a root outside the artifact can establish that, such as an attestation, a digest
published beside the release, or a resolver-enforced lock. A report rendering internal consistency as *"verified"*
states a verdict its evidence cannot support.

**`advisory_coverage`** ([CLI Spec §4.1](../standards/cli/cli-lifecycle-specification.md)): whether any listed advisory
source is authoritative for the artifact *itself* rather than its dependency tree. `none` declares that no
machine-queryable source covers this artifact. That is the true state for a git-installed binary in no package
ecosystem, and `none` requires a published security policy in exchange. A consumer reading it reports *"no advisory
source covers this artifact"*, never *"no known vulnerabilities"*.

**Content versus control** ([Agent Metadata §9](../standards/python/miri-agent-metadata-specification.md); [Agent
Integration §4.3](../standards/consumption/agent-integration-contract.md)): the axis the threat model gained in 0.4.
Every earlier item concerned what metadata *says*: narrative files inject, an index can lie, provenance anchors trust. A
shipped field that determines whether an integration fires concerns what metadata *makes happen*. It is a
denial-of-context channel rather than a false statement, and a different rule closes it.
