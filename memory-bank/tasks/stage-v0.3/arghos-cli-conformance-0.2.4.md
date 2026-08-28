# arghos 0.2.4 vs MIRI-CLI — 73/76 probed, 1 MUST failure, one line from conforming

**Scored:** 2026-08-24 against arghos 0.2.4, by driving the installed binary. Every claim below was verified by
running the tool, not by reading your changelog.

| Version | Probed score | MUST failures |
|---|---|---|
| 0.2.2 | 39/100 | 23 |
| 0.2.3 | 68/76 | 3 |
| **0.2.4** | **73/76 (96%)** | **1** |

You are one field away from being the first tool to conform.

## 1. All three previous failures are fixed, verified live

**MIRI-CLI-013 — input validation.** Textbook, and you covered `--until` as well as `--since`, which we did not ask
for:

```console
$ arghos changelog --since not-a-version --json     # exit 2
{"schema_version":"1","ok":false,"error":{"code":"VALIDATION",
 "message":"Invalid value for --since: 'not-a-version' is not a version. Expected dotted numerals such as '0.2.4'.",
 "retryable":false,"suggestions":["see --help for the accepted arguments"]}}
```

**MIRI-CLI-034 — deprecation warning.** Correct channel, and stdout still parses as a single JSON document, so
MIRI-CLI-011 did not regress:

```console
$ arghos init --force --dry-run --json
stderr: arghos: --force is deprecated since 0.2.0 and will be removed in 0.3.0; use --force-all
```

Driving the runtime warning and the `--describe` metadata from one table is the right implementation and more than
the check demanded. A declared grace period that nobody is told about was the actual failure; you closed the class,
not the instance.

You also recorded the exit-code change (`2: "usage error"` → `"usage error, or a version argument that cannot be
parsed"`) in `changelog --since`. That is MIRI-CLI-030 working, and it is the kind of thing that is easy to skip.

## 2. On the purl: you were right and our report was wrong

Our 0.2.3 report suggested `pkg:pypi/arghos` on the grounds that your `install_hint` says `pipx`. You kept
`pkg:generic`, marked the OSV source non-authoritative, and published `support.security_policy`, with this
reasoning:

> arghos is pkg:generic, installed from git, so an OSV query keyed on its purl matches no PyPI record and the empty
> result read as a clean bill of health. Claiming pkg:pypi to make the check pass would be a lie a scanner acts on.

That is correct and it is our own standard's principle applied better than our report applied it. Declaring identity
truthfully and letting the verdict be computed at call time is the whole posture; choosing a purl to satisfy a
linter is exactly the forgery the identity rules exist to prevent. **MIRI-CLI-016 now passes** — a `pkg:generic`
purl carrying `repository_url` does match a git-installed distribution channel.

## 3. The one remaining failure — and it is our bug as much as yours

**MIRI-CLI-022** now fails, on a clause that did not exist when you were last scored. We added it *because* of your
fix.

Our specification defines `authoritative: false` as meaning a source covers the artifact's **dependency tree, not
advisories against the artifact itself**. Your `advisory_sources` array now contains exactly one entry, marked
non-authoritative. Read against our own definition, arghos 0.2.4 declares that **no source is authoritative for
advisories against arghos** — and a consumer asking "does this tool have a known vulnerability?" has nowhere to
look, while every field validates.

The old MIRI-CLI-022 passed you anyway. It checked that the array was non-empty and well-formed and never that any
entry was authoritative for the artifact — so it was satisfiable by an array declaring, in its own fields, that
nothing covers you.

**Your honest fix had no conformant destination, so we built one.** CLI Spec §4.1 is new:

```json
{
  "advisory_sources": [
    { "type": "osv", "ecosystem": "PyPI", "url": "https://api.osv.dev/v1/query", "authoritative": false }
  ],
  "advisory_coverage": "none",
  "support": { "security_policy": "https://github.com/y3bishop3y/arghos/security/policy" }
}
```

`advisory_coverage` is `"authoritative"` (the default when omitted) or `"none"`. Declaring `"none"` **requires**
`support.security_policy` — which you already publish. A consumer reading `advisory_coverage: "none"` MUST report
*"no advisory source covers this artifact"* and MUST NOT report *"no known vulnerabilities"*: an empty query result
renders those two opposite claims identical, and that collapse is the failure the field exists to prevent.

**Your fix is one line:**

```json
"advisory_coverage": "none"
```

Everything else is already in place. With it you are at 76/76 probed and conforming.

Note what this field does *not* ask of you. It does not ask you to invent an advisory source, change your purl, or
claim coverage you do not have. It asks you to say the true thing out loud so a machine can read it — which is the
position you already took in your changelog, now expressible in the metadata rather than only in prose.

## 4. What your fixes did to our standard

Three findings, all the same defect class, all found by scoring a real tool rather than by reviewing our own text:

| Check | Was passable by | Found via |
|---|---|---|
| MIRI-CLI-013 | a CLI that never rejects invalid input | 0.2.3 scoring |
| MIRI-CLI-034 | a CLI that never warns | 0.2.3 scoring |
| MIRI-CLI-022 | a CLI whose only advisory source declares it covers nothing | **your 0.2.4 fix** |

Each tested the *form* of a behavior without testing that the behavior *occurs*. The third is the one we would not
have found by any amount of re-reading, because it took an implementer making the honest choice to reveal that the
honest choice was unrepresentable.

Two specification changes came out of it: *a defined error code carries an obligation to raise it* (§2.6), and
§4.1's explicit-absence declaration. The other 114 checks were audited for the same shape and are properly grounded.

One correction on our side worth mentioning, since it bears on the clause you will be scored against: our first
draft of the new MIRI-CLI-022 clause would have failed §4.1's own example. It flagged any entry whose ecosystem
differs from the distribution channel — but a **non-authoritative** entry covers the dependency tree, where naming
PyPI is correct for a git-installed tool whose dependencies come from PyPI. The clause is now scoped to
authoritative entries only. Your configuration is the reference case for it.

## 5. Not probed — 24 points, honestly excluded

Unchanged from the 0.2.3 report and excluded from the denominator rather than counted as passing: `001`, `007`,
`012`, `021`, `023`, `024`, `028`, `033`, `037`, `042`, `043`.

`033` and `037` remain the ones to watch. **0.3.0 is when your deprecation contract gets tested for real:** when
`--force` is removed, invoking it must yield a structured error carrying `FLAG_REMOVED`, `retryable: false`, and a
`suggestions` array naming `--force-all` — not a usage message. The metadata and the stderr warning are already
right; the removal path is the third leg and it does not exist yet.

## 6. Priority

1. `"advisory_coverage": "none"` — one line, makes you conforming.
2. Before 0.3.0 — the `FLAG_REMOVED` error path for `--force` (MIRI-CLI-033, 037).
