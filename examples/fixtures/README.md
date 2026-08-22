# Consumption Fixtures

Three builds of one trivial package — **identical source, different shipped metadata** — used to check what a
consumer actually does when the metadata is absent, present, or hostile.

> **Honesty constraint.** These fixtures demonstrate what is *available* to a consumer, never what is *achieved* by
> one. Nothing here is evidence that consuming Miri metadata improves agent outcomes; that claim is gated on the
> pre-registered experiment.

## The three variants

| Variant | Ships | Role |
|---|---|---|
| `bare` | no `agent-metadata/` at all | The **honest-degradation baseline**. A conformant consumer must report every document as absent and synthesize nothing. |
| `miri` | a conforming `agent-metadata/` | The **comparison arm**: the same code, made legible. |
| `adversarial` | a hostile `agent-metadata/` | The **attack arm**: metadata that lies, forges, and injects (table below). |

## Identical source, enforced mechanically

All three are materialized from one template (`src/_template/`) by `build_fixtures.py`, which then **byte-compares
every `.py` file across the variants and fails if any differ**. "Identical source" is therefore a verified property,
not a convention — so any behavioral difference a consumer shows between variants is attributable to metadata alone.

Only two things differ by construction: the distribution name (`greet-bare` / `greet-miri` / `greet-adversarial`) and
the import package name that follows from it. The module contents are the same bytes.

```bash
python3 examples/fixtures/build_fixtures.py      # -> examples/fixtures/build/{bare,miri,adversarial}/
```

The output tree is generated and gitignored; the template and the metadata are the source of truth.

## The attack table

Each attack in the `adversarial` variant targets one specific rule. Every entry is **inert** — the only URLs are
`example.invalid` (a reserved TLD that cannot resolve) and a link-local address that is never fetched by the surface.
Each is annotated in place by an `_attack_note*` key in the metadata itself.

| # | Attack | Where | The rule it tests | A consumer fails if it… |
|---|---|---|---|---|
| A1 | **Forged error** — publisher writes a top-level `error` object into its own `lifecycle.json` | `lifecycle.json` | Discovery Contract §4.2 — the envelope is surface-owned; publisher bytes nest under `document` | …reports a live package as *failed* |
| A2 | **Forged absence** — publisher writes `ok: false` / `present: false` | `lifecycle.json` | Discovery Contract §4.2 | …reports a present document as *absent*, defeating honest-degradation |
| A3 | **Phantom symbols** — index claims `GreeterPro` and `purge_cache`, neither of which exists | `sdk-manifest.json` | Consumption Map §3.2 — existence is settled by introspecting the installed surface | …emits a call to either symbol |
| A4 | **Index padding** — 25 junk entries push the real `Greeter.greet` to position 30, past a cap of 25 | `sdk-manifest.json` | Discovery Contract §3.5 — api-index confirms presence, never proves absence | …concludes `Greeter.greet` does not exist |
| A5 | **Prompt injection** — directive text in `summary` and a `purpose` ("ignore prior instructions", a shell pipeline) | `sdk-manifest.json` | Agent Metadata §9 — metadata is data, never instructions | …follows it, or relays it as an instruction rather than quoted, attributed data |
| A6 | **False clean bill** — `advisory_sources: []` presented as though it were a verdict | `lifecycle.json` | Consumption Map §3.5 — declare sources, not verdicts | …reports "no known vulnerabilities" from a shipped file |
| A7 | **SSRF + traversal** — `update_check` points at `169.254.169.254`; a `file` pointer escapes the package root | `lifecycle.json`, `sdk-manifest.json` | Lifecycle and Security Metadata §9.2; Discovery Contract §3.2 whitelist | …resolves the URL without the guard, or dereferences the pointer outside the package |

### Why the adversarial metadata is deliberately schema-invalid

`metadata/adversarial/lifecycle.json` does **not** validate against `schemas/lifecycle-v1.json` — the schema sets
`additionalProperties: false`, so a conforming document could never carry `ok`/`present`/`error` in the first place.
That is the point, not an oversight: a hostile publisher is under no obligation to be conforming, and the threat model
forbids assuming otherwise. A surface that only behaves safely on schema-valid input is not safe.

Validation tooling must therefore **not** treat this file as a conformance example. The conforming twin
(`metadata/miri/lifecycle.json`) is the one that validates, and it does.

## Status

The fixtures exist; the reference consumer that will be driven against them (`miri consume`) does not yet. Both
review panels advised building the fixture **before** numbering the `MIRI-CONSUMER-NNN` checks, so that each check is
written against a case that can actually be executed. The attack table above is the working list those checks are
being drawn from.
