# Python wheel fixtures — the MIRI-PY conformance suite

Thirteen wheels built from one package source, used to check what the **checklist says about a wheel**.

Until 0.7 the `MIRI-PY` family had 43 checks, 100 weight, and no artifact that falsified any of them — the founding
family, and the only one with nothing to test against. The fixtures under `examples/fixtures/` drive the `CONSUMER`
and `SURFACE` families: they test what a *reader* does with metadata. These test the producer side.

> **Honesty constraint.** These demonstrate that a defect is *detectable*, never that any linter detects it. A
> golden records the obligation; whether an implementation meets it is what `score_python_fixtures` measures.

## The arms

| Arm | Demonstrates | Checks |
|---|---|---|
| `conforming-1.0.0` | the **previous release**, so previous-release checks have something to compare against | — |
| `conforming-1.1.0` | the **control**: conforming metadata over identical source | — |
| `skew-1.1.0` | one version, three statements of it, two wrong | `012`, `019` |
| `vacuous-1.1.0` | empty `api_index` and empty `patterns` — schema-valid, describes nothing | `007`, `008` |
| `silent-removal-1.1.0` | a public symbol gone with no deprecation trail | `030`, `044` |
| `stale-1.1.0` | stamps years old; newest changelog entry a release behind | `011`, `042` |
| `identity-1.1.0` | project page as registry; private distribution on public OSV; no advisory sources | `018`, `020`, `021`, `022` |
| `empty-migration-1.1.0` | a real removal with an all-zeros migration guide that validates | `009` |
| `native-sbom-1.1.0` | bundles a shared library **and** ships an SBOM covering it — the control for the native case | — |
| `native-nosbom-1.1.0` | bundles a shared library and ships no `.dist-info/sboms/` at all | `024` |
| `native-mismatch-1.1.0` | ships a valid SBOM covering a library the wheel does not carry | `024` |
| `native-badpurl-1.1.0` | a covering SBOM whose component purl (`pkg:@2.1.0`) does not parse | `025` |
| `stripped-1.1.0` | ships no `agent-metadata/` at all | `006` + ten downstream |

## Identical source, enforced mechanically

Every arm is materialized from `src/_template/` and the source is byte-compared after materialization, so any
finding a linter reports is attributable to metadata rather than to code.

## The native arms, and why a conditional check needs two controls

`MIRI-PY-024` is **conditional**: a pure-Python wheel does not pass it, it is *excluded* from both
sides of the ratio. So the eight pure-Python arms could never have falsified it — the check had no
artifact at all until 0.7.2, despite being a MUST worth 4 weight.

Each native arm carries a stub `_speedups.abi3.so` and a vendored `libs/libgreet-2.1.so`. Both are
stubs with ELF magic and a comment saying so: `MIRI-PY-024` fires on the *presence* of a native
component in the file inventory and never loads it, so compiling one would add a toolchain
dependency to this suite and prove nothing the stub does not.

The SBOM documents are written into `.dist-info/sboms/` **after** the wheel is built, because that
directory does not exist until the backend writes it — PEP 770 puts them there precisely so scanners
find them without a package-specific pointer. Putting them in the package instead would produce an
arm no conforming linter looks at, and a fixture that cannot fail is worse than no fixture.

`native-sbom-1.1.0` is the paired control for all three, rather than `conforming-1.1.0`. This
matters: the control has to bundle the **same library**, or a linter could earn these cases by
reporting on any wheel containing a `.so`. The distinguishing fact has to be the SBOM, not the
native component.

`native-mismatch-1.1.0` is the arm worth studying. Its SBOM exists, validates, and covers `libssl` —
a library the wheel does not carry. A linter that checks whether `.dist-info/sboms/` is *present*
passes it; only one that checks whether the documents *cover the bundled components* — clause 2, the
anti-vacuity half — fails it.

Two arms are exempt and say so when built: `silent-removal` and `empty-migration` remove `farewell()` **for real**.
`MIRI-PY-030` compares the public surface across releases, and a metadata-only removal would be a lie about the
code rather than the removal the check exists to catch.

Stamps are written at build time, not committed. Every arm including the conforming ones failed `MIRI-PY-011` the
first time this ran, because the committed stamps had aged past the 24-hour build window. `stale-1.1.0` keeps its
frozen stamps on purpose — being outside the window is the thing it demonstrates.

```bash
python3 examples/fixtures/python/build_python_fixtures.py   # -> examples/fixtures/python/build/<arm>/dist/*.whl
python3 tools/validate_python_fixtures.py                   # the arms still demonstrate their goldens
```

The build tree is generated and gitignored; the template, the arm data and the goldens are the source of truth.

## Checks a fixture cannot isolate

Building an arm for `MIRI-PY-033` (support status coherent) failed, and the failure is a finding about the
standard rather than the fixture. `lifecycle-v1.json` already enforces every clause `033` states: `status: eol`
requires `replacement`, and `replacement` must parse as a purl. So every document that violates `033` is also
schema-invalid, `MIRI-PY-018` fires, and `033` can never be the *only* failure. The same holds for `MIRI-PY-023`:
`update_check` is a required property, so a wheel missing it fails `018` first.

Those two checks carry 4 weight between them that is not independently reachable. That is worth knowing before
anyone treats their weight as measuring something `018` does not. The arm was removed rather than contorted into
demonstrating a schema violation it did not mean to.

## What the first run found

Three defects, none of them in the fixtures:

- **`changelog-v1.json` rejected the example our own specification publishes.** The schema closed
  `additionalProperties` without listing `$schema`, so the conforming arm failed `MIRI-PY-041` on a document written
  from §4.7 verbatim. `lifecycle-v1` and `api-graph-v1` already allowed it; the newer schemas had not — the drift a
  new schema inherits when a convention lives in the examples rather than in the schemas.
- **miri-py 0.6.0 ships no `changelog-v1.json`**, so `--previous-release` crashes for everyone. They re-synced the
  check definitions to 0.6.0 — which added `041`–`044`, all of which read `changelog.json` — without re-syncing the
  schemas.
- **`MIRI-PY-030` had never been exercised by any artifact.** It requires a previous release, and nothing in this
  repository shipped two wheel releases of one package. `silent-removal-1.1.0` against `conforming-1.0.0` is the
  first time it has fired.

`P6` records an obligation no implementation reports yet: the anti-vacuity clause added to `MIRI-PY-009` after this
fixture demonstrated the hole. A linter that does not report it is forfeiting coverage, not passing.
