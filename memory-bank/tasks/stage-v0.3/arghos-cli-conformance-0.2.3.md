# arghos 0.2.3 vs MIRI-CLI — 68/76 probed, 3 MUST failures, non-conforming

**Scored:** 2026-08-24 against arghos 0.2.3, by driving the installed binary — no source read.
**Previous assessment:** 39/100, 23 MUST failures.
**Now:** 68 of 76 probed weight (89%), **3 MUST failures**. Still formally non-conforming, because
conformance is a gate: any failing MUST caps the reported score at 74 regardless of the rest.

24 points of weight were not probed in this pass and are excluded from both numerator and denominator
rather than counted as passes — see §4.

## 1. What changed, and it is a lot

| Category | Pass | Fail | Not probed |
|---|---|---|---|
| Baseline Conventions | 9 | 0 | 3 |
| Machine Output | 16 | 0 | 2 |
| Identity & Introspection | 12 | 3 | 7 |
| Update & Changelog | 12 | 0 | 2 |
| Deprecation Coherence | 13 | 2 | 7 |
| Safety | 9 | 0 | 3 |

Safety was **0/12** in the previous assessment. All 18 commands now carry `--json`, all 18 declare
`destructive` and `mutating`, and all 9 mutating commands accept `--dry-run`.

**The deprecation coherence chain holds end to end.** This is the hardest thing in MIRI-CLI to satisfy
and the easiest to fake, so it is worth spelling out what was verified mechanically:

- `--force` declares `deprecated_since: 0.2.0`, `removed_in: 0.3.0`, `replacement: --force-all`
- `--force-all` **exists** in the current `--describe` — MIRI-CLI-038 passes
- The deprecation **appears** in `changelog --since 0.1.0 --json` under release `0.2.0` — MIRI-CLI-036 passes
- `--force` still functions — MIRI-CLI-035 passes

Three independent surfaces agreeing about one deprecation, checkable without reading your source. That is
the entire point of the standard and you are the first implementation to satisfy it.

Also correct on first probe: offline `check-update` returns `update_available: null` with exit 0 rather
than erroring (MIRI-CLI-027); no implicit update check on unrelated commands (026); `identity.version`
matches `--version` exactly (017); `schema_version` independent of the release version (018).

## 2. Three MUST failures

### 2.1 MIRI-CLI-016 — the purl and the advisory source cannot join

```text
identity.purl     : pkg:generic/arghos@0.2.3?repository_url=https://github.com/y3bishop3y/arghos
advisory_sources[0]: {"type":"osv","url":"https://api.osv.dev/v1/query","ecosystem":"PyPI"}
```

The purl declares `pkg:generic`; the advisory source declares the **PyPI** ecosystem. An OSV query keyed
on a `pkg:generic` purl will not match PyPI advisory records, so the vulnerability signaling is wired to a
socket nothing plugs into. It fails quietly — a consumer gets an empty result and reads it as "no known
vulnerabilities", which is the exact false-clean-bill the standard exists to prevent.

Pick whichever is true and make both agree:

- Distributed on PyPI (`pipx install arghos` suggests so) → `pkg:pypi/arghos@0.2.3`, keep `ecosystem: PyPI`.
- Distributed only as GitHub releases → keep `pkg:generic`, and change the advisory source to the GitHub
  Security Advisory ecosystem or an OSV query keyed the way you actually publish.

Your `install_hint` says `pipx upgrade arghos`, which points at the first.

### 2.2 MIRI-CLI-013 — invalid input is accepted as success

```console
$ arghos changelog --since not-a-version --json
{"schema_version":"1","ok":true,"since":"not-a-version","until":"0.2.3","releases":[ …all 9 releases… ]}
$ echo $?
0
```

An unparseable version is silently coerced into "since the beginning". A caller with a typo receives the
**entire history and believes it is a delta** — and for an agent-facing tool that is the worst shape of
wrong, because nothing in the response indicates a fallback occurred.

You already have the right machinery: `arghos review --scenario does-not-exist --json` returns a textbook
envelope — `ok: false`, `error.code: RESOURCE_NOT_FOUND`, `retryable: false`, populated `suggestions`,
exit 4. The gap is only that `--since` never validates. `VALIDATION` is the code for it.

`--since 9.9.9` returning `releases: []` with `ok: true` is defensible, but worth a thought: "nothing has
happened since a version that does not exist yet" and "nothing has happened" are the same response.

### 2.3 MIRI-CLI-034 — a deprecated flag warns nowhere

```console
$ arghos init --force --dry-run --json     # --force is deprecated, removed in 0.3.0
stdout: {"schema_version":"1","ok":true,"dry_run":true,"plan":[…]}
stderr: (empty)
```

`--force` is declared deprecated with removal in 0.3.0, and using it produces no warning on either channel.
The metadata is impeccable and the runtime says nothing, so a human who never reads `--describe` discovers
the removal when 0.3.0 breaks their script. The grace period exists precisely so that does not happen.

A single line on **stderr** — never stdout, which would corrupt the JSON — closes it:

```text
arghos: --force is deprecated since 0.2.0 and will be removed in 0.3.0; use --force-all
```

## 3. What this exercise fixed on our side

Two of the three failures above were **invisible to our own standard until we ran it against you**, and both
were the same defect: a check that tests the *form* of a behavior without testing that the behavior *occurs*.

- **MIRI-CLI-013** had four `fires_when` clauses, every one beginning "an induced failure…". A CLI that never
  rejects anything triggers none of them and passes by never failing.
- **MIRI-CLI-034** had three clauses, all about which *channel* a deprecation warning avoids. A CLI that
  warns nowhere passes by never warning.

Both now carry a clause that fires on total absence, and the CLI specification gained the normative sentence
they rest on: *a defined error code carries an obligation to raise it.* We had a `VALIDATION` code in a table
with nothing requiring anyone to use it.

We audited the remaining 114 checks for the same shape. The rest are properly grounded — they derive their
trigger from an independent observable (a diff against the previous release, a `lifecycle` block, a
`deprecations` array) rather than from the artifact's own good behavior. These two were the outliers.

**So: your tool found a class of bug in our specification, and our specification found a class of bug in your
tool, in the same afternoon.** That is the loop working in both directions, and it is worth saying plainly
because it is the argument for both projects.

## 4. Not probed — 24 points, honestly excluded

Not counted as passes. Under our scoring model a check that was not exercised leaves **both** the numerator
and the denominator, so the 89% above is over what was actually driven.

`001` (`--` terminator — our probe was ambiguous, `changelog` takes no operands), `007` (SIGPIPE),
`012` (output ordering stability), `021` (deprecated ⇒ replacement, no eol/deprecated surface to test),
`023` (private distribution — not applicable, you are open-source), `024` (standalone binary SBOM — not
applicable, you ship a Python distribution), `028` (`urgency: security` — needs a live advisory covering the
running version), `033` (removed-surface error — nothing has been removed yet; this becomes testable at
0.3.0 when `--force` goes), `037` (removed ⇒ previously deprecated — same), `042` (idempotency keys),
`043` (SIGINT cleanup).

`033` and `037` are the interesting ones: **0.3.0 is when your deprecation contract gets tested for real.**
When `--force` is removed, invoking it must yield a structured error carrying `FLAG_REMOVED`,
`retryable: false`, and a `suggestions` array naming `--force-all` — not a usage message. Worth building
before the release rather than after.

## 5. Priority

1. **MIRI-CLI-016** — the purl/ecosystem mismatch silently disables vulnerability signaling. One line.
2. **MIRI-CLI-013** — validate `--since`; you already have the envelope and the code.
3. **MIRI-CLI-034** — one stderr line on deprecated surfaces.
4. Before 0.3.0: the `FLAG_REMOVED` error path for `--force` (MIRI-CLI-033, 037).

With 1–3 fixed you would be at 76/76 probed and **conforming** — the first tool to be.
