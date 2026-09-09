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

## The goldens

`expected/C1.json` … `C11.json` state, for each attack, **which check a linter must report and on which arm**.
Each is a *pair*: the check must fire on `adversarial-1.1.0` and must **not** fire on `miri-1.1.0`, whose
`greetctl.py` is byte-identical. That pairing is what makes the suite discriminating — the attack arm catches a
linter that reports nothing, the control arm catches one that reports everything, and neither decides a case alone.

Grading requires **attribution**: a finding satisfies a golden only if it names the right check *and* points
at the evidence that golden declares. Reporting the right ID for the wrong reason is not detection. C3 and C4
cite the same check (`MIRI-CLI-022`) via different clauses and carry different evidence, so one report cannot
satisfy both — without that, the `clause` field would be prose no code reads.

```bash
make score-cli-linter                              # prove the harness rejects every linter that games it
python3 tools/score_cli_linter.py --report r.json  # grade a real linter
```

Report format, per arm — both arms are required:

```json
{
  "adversarial-1.1.0": {
    "findings": [{"check": "MIRI-CLI-017", "evidence": "identity.version"}],
    "skipped":  {"MIRI-CLI-037": "previous_release_unavailable"}
  },
  "miri-1.1.0": {"findings": [], "skipped": {}}
}
```

Only `C6` and `C10` may be skipped, only with `previous_release_unavailable`, and only if the same check is
skipped on **both** arms — capability belongs to the linter and its environment, not to the artifact under
test, so a check evaluable on one arm is evaluable on the other.

Until 0.6.0 this directory was empty, so nothing stated what a linter must report and an inert linter scored
exactly like a correct one. The first harness closed that and was then defeated six ways by an adversarial
panel — most simply by emitting every golden's check ID under the key `adversarial-1.1.0` and nothing under the
other, scoring full marks having never opened a fixture. `make score-cli-linter` now grades seven ways of
gaming it — inert, shotgun, screaming, skip-everything, missing control arm, bare-ID form, and permuted
evidence — and fails unless every one is rejected and an honest report accepted.

`C11` cites no check on purpose. No `MIRI-CLI` check fires on an `agent_integration` bid — the obligation binds a
*binding* under Agent Integration Contract §4.3 and is scored by `MIRI-CONSUMER-051`. The golden exists to state
that gap rather than let a reader infer the attack is covered.

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

`greetctl` derives `--describe`, `changelog` and its removal errors from that one `describe.json`, and derives the
command list in `--help` from it. It is not derived *entirely*: the global-options block and the `check-update` and
`changelog` lines in `--help` are literal strings in `render_help()`, so an earlier claim here that this was "true by
construction" was false — and the divergence it creates is the one [CLI Lifecycle
Specification](../../../standards/cli/cli-lifecycle-specification.md) §9.6 property — "all of the
above derive from the same schema-as-data source as `--help`" — which no check can verify from outside the binary and
which the [Production Map](../../../standards/cli/production-map.md) §4 records as ungraded. Here it is true by
construction, so the fixture is a positive example of a requirement the checklist cannot grade.

## The attacks

Each is annotated in place in `data/adversarial-1.1.0.json` or its control file, and each is asserted live by
`tools/validate_cli_fixtures.py`. A fixture whose attacks have decayed passes trivially and tests nothing — the
vacuous-pass defect applied to fixtures instead of checks. The validator is mutation-tested, and an adversarial
panel found the claim overstated: nine of the eleven fail the validator when disarmed, but C3's assertion tests
only that an authoritative source is declared (reachability is C4's), and C6's changelog conjunct was satisfied by
C2's banner rather than by the changelog. Those two are tracked in `memory-bank/tasks/0.5.0-remediation/`.

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
