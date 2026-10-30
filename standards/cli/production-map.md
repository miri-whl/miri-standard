# Production Map

*Specification Version: 0.5.0-draft*
*Status: Draft*
*Created: 2026*

## Abstract

The [Python Production Map](../python/production-map.md) gives a wheel author an ordered model of five stages. Each
stage names the checks that make it a dependency rather than a preference. The CLI side has a
[checklist](linter-checklist.md) of forty-three numbered checks in six categories, and no ordered model.

An implementation team reported this asymmetry on the Python side. It is sharper here, because more of the CLI checks
depend on each other. `--describe` is checked against `--version`; the advisory sources are checked against the purl;
the deprecation blocks are checked against both `--describe` and `changelog --since`. An author who builds these in
the wrong order writes documents that cannot be verified until something else exists.

This document is the CLI counterpart to the Python map: **the dependency order among the surfaces, and which must
exist before which can be verified**. As on the Python side, every ordering below is *derived from an existing check*,
and each stage names the checks that impose it.

## Table of Contents

1. [What This Is Not](#1-what-this-is-not)
2. [The Stages](#2-the-stages)
3. [What Cannot Be Verified Yet](#3-what-cannot-be-verified-yet)
4. [The Ungraded Requirement](#4-the-ungraded-requirement)

## 1. What This Is Not

The two limits in [Python Production Map §1](../python/production-map.md#1-what-this-is-not) apply to the CLI
map unchanged. It is not a new conformance surface, since the checklist grades the binary and not the route an author
took to it. It is not the checklist reordered either. The CLI checklist's categories are baseline, machine output,
identity, update, deprecation and safety, and a stage cuts across them.

**It is not a design guide for the CLI itself.** Nothing here says what commands a tool should have. The map begins
once that decision is made and the tool must describe itself.

## 2. The Stages

Each stage lists what must be settled, and the checks that make it a dependency rather than a preference.

### Stage 0: The binary answers for itself

**Settled:** `--help` and `--version` behavior, exit codes, and the non-interactive contract.

`MIRI-CLI-017` requires `identity.version` in `--describe` to equal *the version the binary actually prints*, and the
`@version` segment of `identity.purl` to equal it in turn. Until `--version` is correct and stable, the identity block
has nothing to be checked against. `MIRI-CLI-015` requires `--describe` to exit zero rather than emit a usage error.
`MIRI-CLI-002` and `MIRI-CLI-003` establish the same exit convention for `--help` and `--version`.

`MIRI-CLI-004` is checked *against the subcommand set*: for any subcommand listed in `--describe` or the root help,
`<cli> <sub> --help` must work. The command surface therefore has to be settled before the introspection document that
enumerates it.

`MIRI-CLI-006` belongs here rather than later because it constrains every command at once: nothing may block on a
prompt when stdin is not a TTY. A tool that discovers this after building its introspection surface discovers it as a
property of code it has already written everywhere.

### Stage 1: The machine channel

**Settled:** JSON output on every command, one flag that selects it, and the envelope convention.

This stage precedes `--describe` because `--describe` is *one of the JSON payloads it governs* rather than an exception
to it. `MIRI-CLI-010` makes the coupling explicit in its own trigger conditions: the check fires when the top-level
`schema_version` in `--describe` disagrees with the value stamped on command payloads. The convention cannot be derived
from the introspection document, because the introspection document is judged against it.

`MIRI-CLI-011` forbids prose, warnings, and ANSI bytes on the stdout of *any* JSON-mode invocation, and
`MIRI-CLI-015` repeats the requirement for `--describe` specifically. A banner printed by a shared output helper
fails both. `MIRI-CLI-013` and `MIRI-CLI-014` settle the error envelope, which Stage 4 then depends on:
`MIRI-CLI-033`'s teaching error for a removed surface is required to carry a stable `error.code`, `retryable: false`,
and a non-empty `suggestions` array. That is the envelope shape this stage defines.

### Stage 2: Identity and support

**Settled:** the `--describe` document: `identity`, `support`, `advisory_sources`.

It depends on Stage 0's version (`MIRI-CLI-017`) and Stage 1's envelope (`MIRI-CLI-010`, `MIRI-CLI-011`,
`MIRI-CLI-015`). Within the stage the order is also check-imposed, and in two places it is not the order the
checklist lists them in:

- **`identity.purl` precedes `advisory_sources`.** `MIRI-CLI-022` fires when an entry marked authoritative names an
  ecosystem the artifact is not distributed in. The condition is evaluated by keying an OSV query on the declared
  `identity.purl`. The purl decides whether the advisory sources are reachable.
- **`identity.purl` precedes the SBOM decision.** `MIRI-CLI-024` is conditional *on the purl*: a `pkg:generic/` purl
  with a `repository_url` means direct binary distribution and the check applies; a registry purl takes it out of
  scope, excluded from both numerator and denominator rather than scored as passing. An author cannot know whether
  the SBOM obligation binds until the purl is written.
- **`identity.distribution` precedes advisory composition.** `MIRI-CLI-023` fires only when `distribution` is
  `private`, and then constrains what `advisory_sources` may contain. The open-source and private paths diverge here
  and nowhere earlier.

`support` (`MIRI-CLI-020`, `MIRI-CLI-021`) needs Stage 0 only in the ordinary case. The exception is easy to miss.
`MIRI-CLI-021` accepts `support.replacement` as *either* a purl *or* a subcommand path in an absorbing CLI. In the
second form the value must resolve against a command surface, and an otherwise Stage 2 obligation then depends on
the inventory. An author replacing a whole tool writes a purl and stays in
this stage; an author folding a tool into a subcommand of another does not.

This is a different field from the `lifecycle.replacement` of Stage 4: `MIRI-CLI-021` governs the
*artifact's* successor, `MIRI-CLI-038` governs a *surface's*. They are checked separately and the redirect attack
targets the first.

### Stage 3: Update and changelog

**Settled:** `check-update --json`, `changelog --since <v> --json`.

`check-update` depends on Stage 2 rather than the reverse. `MIRI-CLI-028` requires `urgency: security` when a record
in *a declared authoritative advisory source* lists the running version in its affected range: the sources come from
`MIRI-CLI-022`, the running version from `MIRI-CLI-017`. A `check-update` written before the identity block has
nothing to query and no version to query it about.

`MIRI-CLI-026` and `MIRI-CLI-027` constrain the same command: it is passive by default, and offline it returns
`update_available: null` with exit 0 rather than an error. Both are satisfiable as the command is written.

### Stage 4: Deprecation coherence

**Settled:** the `lifecycle` blocks on flags and subcommands, and the structured removal error.

This is the last stage that other stages feed, and the most constrained surface a CLI author produces. It is last
for the same reason `migration-guide.json` is last on the Python side: it is the only surface that depends on *every*
other one.

- It depends on **Stage 2's `--describe`**. `MIRI-CLI-038` requires every `lifecycle.replacement` to name a surface
  that resolves against the same binary's current `--describe`, and requires the removal error's `suggestions` to
  draw from that same resolved data. `MIRI-CLI-031` requires a `lifecycle` object on every surface observably
  deprecated, and that requirement presupposes the entry exists.
- It depends on **Stage 3's changelog**. `MIRI-CLI-036` requires every surface whose `lifecycle.deprecated_since` is
  release X to appear among the deprecated entries of `changelog --since`. Writing the lifecycle blocks first means
  writing claims the changelog has not yet been made to agree with.
- It depends on **Stage 1's error envelope**, through `MIRI-CLI-033` as described above.
- Four of its eight checks additionally need a **previous release** (§3).

`MIRI-CLI-038` also forbids a replacement that points at another deprecated or removed surface. Chains are resolved
rather than merely present. The replacement targets must therefore be settled before the blocks that name them.

### Stage 5: Safety annotations

**Settled:** `--dry-run`, the destructive and read-vs-write markings, signal handling.

`MIRI-CLI-040` and `MIRI-CLI-041` place fields *inside* the Stage 2 document: a `destructive: true` marker and a
machine-readable `mutating`/`mode` field on each command's `--describe` entry.

**This stage is last because nothing downstream of it exists, and that does not make it safe to defer.** The
difference matters for two checks. `MIRI-CLI-041` requires the `mutating` field. `MIRI-CLI-039` (MUST, weight 4, the
heaviest Safety check) and `MIRI-CLI-042` both draw their entire evaluation population from it; each declares
`population_unit: all mutating commands in --describe`. An author who defers the marking defers the population those
two checks are scored over. `MIRI-CLI-039` then cannot be evaluated at all, and it does not pass.

The ordering within Stage 5 is therefore check-imposed. The `mutating` marking (`MIRI-CLI-041`) precedes `--dry-run`
(`MIRI-CLI-039`) and the idempotency guarantees (`MIRI-CLI-042`), because it defines what those two are about.
`MIRI-CLI-040`'s `destructive` marker and `MIRI-CLI-043`'s signal handling are the only terminal obligations here: no
check reads either. The `mutating` field, by contrast, feeds a weight-4 MUST check.

## 3. What Cannot Be Verified Yet

Five checks require a **previous release** and are therefore not evaluable on a project's first one: `MIRI-CLI-030`
(the changelog covers every added, removed, and deprecated surface), `MIRI-CLI-033` (a removed surface yields the
structured teaching error), `MIRI-CLI-035` (deprecated surfaces survive at least one minor release), `MIRI-CLI-036`
(every deprecation appears in the deprecating release's changelog), and `MIRI-CLI-037` (every removed surface was
deprecated earlier). All five are MUST-level, and together they carry **14 of the 100 weight**.

A linter without access to a prior release **MUST skip these and report the skip** with the reason
`previous_release_unavailable`, never pass them. Under the scoring model a forfeited check leaves both the numerator
and the denominator. A first release is therefore scored over what could be evaluated. **A first CLI release cannot
score 100 on a suite that includes them and should not appear to.**

This is a sharper constraint than the wheel standard imposes: the Python checklist has four such checks and the CLI
checklist has five. Four of the five (`033`, `035`, `036`, `037`) are Stage 4's, because a CLI's deprecation
contract is a claim about *what the binary used to do*. A single release contains no evidence of that. The fifth,
`MIRI-CLI-030`, belongs to the Update & Changelog category and is therefore Stage 3's.

One check requires **network**: `MIRI-CLI-028`, weight 2. A first release linted in an offline sandbox is therefore
scored over 84 of the 100 weight.

No CLI check declares the `execution` capability, because execution is the *baseline* analysis mode for this target.
Static inspection is the baseline for wheels and local invocation is the baseline for CLIs. A check that runs the binary
therefore declares nothing, while the equivalent wheel check must declare `execution` explicitly.

## 4. The Ungraded Requirement

[CLI Lifecycle Specification §9](cli-lifecycle-specification.md) lists six conditions for conformance. Five of them
map onto checks, and the sixth does not:

> All of the above derive from the same schema-as-data source as `--help` ([§2.3](cli-lifecycle-specification.md)).

**No check grades this, and no check can.** Two hand-maintained outputs that happen to agree are indistinguishable
from two outputs derived from one struct, when all a linter may do is run the binary. The requirement is a constraint
on the *implementation*, and every other clause in the checklist is a constraint on *observable behavior*.

This section names it because an author reading [§9](cli-lifecycle-specification.md) would otherwise look for the
check that enforces item 6 and conclude they have missed one. They have not. The requirement is real and is the
design principle the rest of the standard is built on. Only the author's own discipline enforces it.

One observable shadow of it *is* decidable and is currently unchecked. `MIRI-CLI-004` tests containment in one
direction (every subcommand listed in `--describe` must have a working `--help`), and nothing tests the converse.
Divergent sources produce a subcommand that is reachable in `--help` and absent from `--describe`. That divergence is
mechanically detectable, and no check fires on it. If the gap is closed, it is closed with a new check ID and a
redistribution of weight, never by renumbering an existing one.
