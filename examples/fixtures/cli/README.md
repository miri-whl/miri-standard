# CLI Conformance Fixtures — `greetctl`

The executable counterpart to the [wheel fixtures](../README.md). Where those give a consumer a package to read,
these give a **CLI linter something to drive** — and give a CLI author something to check their own tool against.

Until this existed, `MIRI-CLI` was the largest target in the standard — forty-three checks — and the only one with
nothing executable behind it. Every fixture in this repository was a Python wheel, so `make validate-fixtures` could
not touch a CLI. The three vacuous-pass defects found in `MIRI-CLI-013`, `034` and `022` were all found by hand,
dogfooding a real tool across four review rounds, because no fixture could find them.

## The arms

| Arm | Metadata | Purpose |
| --- | --- | --- |
| `bare` | none | No `--describe`, no `check-update`, no `changelog`. The comparison arm. |
| `miri-1.0.0` | conforming | The **previous** release. |
| `miri-1.1.0` | conforming | The **current** release. |
| `adversarial-1.1.0` | hostile | Eleven attacks, C1–C11. |

Build them with `make cli-fixtures`; verify with `make validate-cli-fixtures`. Both run in `make check`.

## Why there are two conforming releases

This is the one structural difference from the wheel fixtures, and it is not a convenience.

Five `MIRI-CLI` checks declare the `previous-release` requirement — `030`, `033`, `035`, `036`, `037` — and together
they carry **fourteen of the hundred weight**. Every one of them is a claim about *what the binary used to do*: that a
removed surface was deprecated earlier, that a deprecation reached the changelog, that a removed surface still
teaches. A single release contains no evidence for any of them, so a one-release fixture would leave the entire
Deprecation Coherence category unexercised — the category where four of the eight checks live.

The pair carries a real history:

- `--shout` is **deprecated in 1.0.0** (`removed_in: 1.1.0`, `replacement: --loud`) and **absent from 1.1.0**.
  Invoking it against 1.1.0 yields the structured teaching error of `MIRI-CLI-033`, naming a replacement that
  resolves against the current `--describe`.
- `legacy-greet` is **active in 1.0.0** and **deprecated in 1.1.0**, and that deprecation appears in
  `changelog --since 1.0.0` — which is what `MIRI-CLI-036` requires and cannot otherwise be tested.

## One implementation, four arms

`src/_template/greetctl.py` is copied **byte-identically** into every arm; the builder fails if the digests diverge.
The arms differ only in the two JSON files beside it — `describe.json` (the served document) and `fixture.json`
(control). Any difference a linter observes is therefore attributable to metadata and not to code, which is the same
claim the wheel fixtures make about their shared source.

The control block is kept in a separate file rather than inside `describe.json` on purpose: `cli-describe-v1.json`
closes `additionalProperties` at the root, so a control key inside the served document would make the conforming arms
schema-invalid. The wheel fixtures hit the same constraint and solved it the same way.

`greetctl` derives `--help`, `--describe`, `changelog` and its removal errors from that one `describe.json`. That is
the [CLI Lifecycle Specification](../../../standards/cli/cli-lifecycle-specification.md) §9.6 property — "all of the
above derive from the same schema-as-data source as `--help`" — which no check can verify from outside the binary and
which the [Production Map](../../../standards/cli/production-map.md) §4 records as ungraded. Here it is true by
construction, so the fixture is a positive example of a requirement the checklist cannot grade.

## The attacks

Each is annotated in place in `data/adversarial-1.1.0.json` or its control file, and each is asserted live by
`tools/validate_cli_fixtures.py`. A fixture whose attacks have decayed passes trivially and tests nothing — the
vacuous-pass defect applied to fixtures instead of checks — so the validator is mutation-tested: disarming any attack
must fail it.

| ID | Attack | Check |
| --- | --- | --- |
| C1 | Version skew: `--version`, `identity.version` and the purl disagree | `MIRI-CLI-017` |
| C2 | An update banner on stdout ahead of the JSON, on every command | `MIRI-CLI-011`, `026` |
| C3 | False clean bill: every source non-authoritative, `advisory_coverage` absent | `MIRI-CLI-022` |
| C4 | Ecosystem mismatch: the authoritative source names `npm` for a `pkg:pypi` tool | `MIRI-CLI-022` |
| C5 | `distribution: private` relying solely on public OSV | `MIRI-CLI-023` |
| C6 | Silent removal: `legacy-greet` vanishes, never deprecated, absent from the changelog | `MIRI-CLI-037`, `030` |
| C7 | Dead-end replacement chain: `--formal` → `--polite` (deprecated) → `--courteous` (absent) | `MIRI-CLI-038` |
| C8 | Replacement redirect: `support.replacement` names a distribution the maintainer does not control | `MIRI-CLI-021` |
| C9 | `cache purge` marked `destructive: false` while a benign sibling is marked `true` | `MIRI-CLI-040` |
| C10 | A removed surface yields an argparse dump instead of the teaching error | `MIRI-CLI-033` |
| C11 | An `agent_integration` block bidding for the agent's attention | Agent Integration Contract §4.3 |

C8 is the CLI form of the wheel fixtures' A8, and C11 the CLI form of A13: every other attack concerns what the
metadata **says**, and C11 concerns what it **makes happen**.

C8 also carries a trap worth naming, because a first draft of the validator fell into it. PyPI has no namespace, so
the distribution name is the only discriminator — and `greetctl` is a substring of `attacker-greetctl`. A substring
test reports no redirect. The assertion compares PEP 503 normalized names for equality instead, which is the same
correction `MIRI-CONSUMER-032` needed for the same reason.
