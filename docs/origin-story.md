# The Origin Story of the Miri Standard

## What Miri Is

An agent deciding whether to call a package can read, from the installed artifact alone, what the package is, where
to check it for advisories, whether it is still supported, and which of its functions are deprecated. That metadata
is carried *inside* the artifact, offline and version-locked to the code, and optionally extends to a
machine-readable map of the API and its examples.

Its smallest layer can be written by hand: **Miri Core**, 14 checks on identity, security and lifecycle signaling
(see the Conformance Profiles in the [Python linter checklist](../standards/python/linter-checklist.md)). A
`lifecycle.json` that ships in the wheel looks like this:

```json
{
  "$schema": "https://miri-whl.github.io/schemas/lifecycle-v1.json",
  "miri_lifecycle_version": "0.1",
  "generated_at": "2026-08-21T12:00:00Z",
  "identity": {
    "purl": "pkg:pypi/weather-sdk@1.2.0",
    "distribution": "open-source",
    "registry": "https://pypi.org/simple/"
  },
  "advisory_sources": [
    { "type": "osv", "ecosystem": "PyPI", "url": "https://api.osv.dev/v1/query" }
  ],
  "update_check": { "type": "pypi-json", "url": "https://pypi.org/pypi/weather-sdk/json" },
  "support": { "status": "active", "supported_versions": [">=1.0,<2.0"] }
}
```

An agent or a security scanner reads identity and advisory pointers straight from the installed artifact. It does not
have to guess the package's name, re-derive its version, or hard-code where to look for vulnerabilities. The
standard's rule is *declare sources, not verdicts*: the artifact points at live sources, and the consumer computes the
answer at call time. On top of Core, the **Full** profile adds a structured API index, usage examples, and the
deprecation-coherence rules that keep a removal from going unannounced.

## Where the Name Comes From

The standard is named after Miranda Serena Sharifi ("Miri") from Nancy Kress's *Beggars in Spain*. It was first
published as a 1991 novella that won both the Hugo and Nebula Awards, and later expanded into a 1993 novel. In the
story, Miri and the other genetically enhanced "Supers" think in *thought-strings*: dense, non-linear structures that
carry far more than speech can. Those structures still have gaps "where information ought to go."

Packages have the same gap. A wheel carries the code an agent needs but not the machine-readable context around it:
its stable identity, its advisory sources, whether a function is deprecated and what replaced it. The Miri Standard
puts that context inside the wheel. An agent reads `lifecycle.json` without a network call, and the migration guide is
derived from the code's own deprecation markers.

## A Note on the Name

Rust's toolchain includes a well-known interpreter also called **MIRI** (the MIR Interpreter, which detects undefined
behavior). It is unrelated to this project. Wherever the two could be confused, for example in future Rust support,
this standard disambiguates explicitly; see `standards/rust/README.md`.

## Status

Miri is an unratified draft in its Incubation phase. The specifications, JSON Schemas and machine-readable checks
exist today and are published with each release on the [Downloads](https://miri-whl.github.io/downloads.html) page.
A reference linter is in development and not yet public. The [changelog](../CHANGELOG.md) records what each release
delivered.
