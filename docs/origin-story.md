# The Origin Story of the Miri Standard

## What Miri Is

An agent deciding whether to call a package can read, from the installed artifact alone, what the package is, where
to check it for advisories, whether it is still supported, and which of its functions are deprecated. That metadata
is carried *inside* the artifact, offline and version-locked to the code, and optionally extends to a
machine-readable map of the API and its examples.

Its most defensible layer is small and hand-authorable: **Miri Core**, the identity, security, and lifecycle signaling
a well-maintained package can adopt in a day. A `lifecycle.json` that ships in the wheel looks like this:

```json
{
  "identity": {
    "purl": "pkg:pypi/weather-sdk@1.2.0",
    "registry": "https://pypi.org/simple/"
  },
  "advisory_sources": [
    { "type": "osv", "ecosystem": "PyPI", "url": "https://api.osv.dev/v1/query" }
  ],
  "support": { "status": "active", "supported_versions": [">=1.0,<2.0"] }
}
```

An agent — or a security scanner — reads identity and advisory pointers straight from the installed artifact instead of
guessing the package's name, re-deriving its version, or hard-coding where to look for vulnerabilities. The standard's
rule is *declare sources, not verdicts*: the artifact points at live sources, and the consumer computes the answer at
call time. On top of Core, the **Full** profile adds the richer agent-facing surface — a structured API index, usage
examples, and deprecation-coherence machinery so that a removal is never silent.

## Where the Name Comes From

The standard is named after Miranda Serena Sharifi — "Miri" — from Nancy Kress's *Beggars in Spain*, first published as
a 1991 novella that won both the Hugo and Nebula Awards and later expanded into a 1993 novel. In the story, Miri and
the other genetically enhanced "Supers" think in *thought-strings*: dense, non-linear structures that carry far more
than speech can. But those structures have gaps "where information ought to go." The enhancement is real; the missing
pieces hold it back.

Packages have the same flaw. A wheel carries the code an agent needs but not the machine-readable context around it —
its stable identity, its advisory sources, whether a function is deprecated and what replaced it. The Miri Standard
puts that context inside the wheel: a `lifecycle.json` an agent reads without a network call, a migration guide
derived from the code's own deprecation markers. The name stands for one claim and no more — an artifact that
completes its own missing information.

## A Note on the Name

Rust's toolchain includes a well-known interpreter also called **MIRI** (the MIR Interpreter, which detects undefined
behavior). It is unrelated to this project. Where the two could be confused — most obviously any future Rust support —
this standard disambiguates explicitly; see `standards/rust/README.md`.

## Status

Miri is an early, unratified draft (version 0.1). The specifications, JSON Schemas, and machine-readable checks exist
today; the reference linter and some profiles are still in progress. The README's "Project Status" section is the
authoritative account of what is real versus planned — this page is only the story behind the name.
