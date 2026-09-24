# Note: what a linter may conclude about a wheel's integrity, and what it may not

*For: miri-py. Prompted by a question about whether the linter should report that an artifact is intact.*
*Status: One check's definition clarified. No level, weight, or rule changed.*
*Created: 2026*

## The short version

`MIRI-PY-001` verifies that the archive matches `RECORD` — every file listed, every sha256 recomputed, no
forbidden algorithms, no file present that `RECORD` omits. That is a real check and it is worth running: pip
has never enforced it at install time ([pypa/pip#2752](https://github.com/pypa/pip/issues/2752), open since
2015), so a wheel modified after build installs without complaint and a conformance run is often the only
place the mismatch surfaces.

**It is not tamper-evidence, and a report must not present it as such.** `RECORD` is carried inside the
archive it describes. Whatever rewrote a file rewrote `RECORD` in the same motion. Passing establishes that
the artifact agrees with itself — which detects corruption, truncation, a caching proxy that mangled a file,
and a post-build edit nobody tried to hide. It does not detect an edit by anyone who read the spec.

This is the same boundary we drew for `verify_content()` on the definitions wheel, and it generalizes: no
property computable from inside an artifact can establish where the artifact came from.

## What this means for report wording

The rule this standard applies everywhere else is *declare sources, never verdicts* — an artifact may not
claim "no known vulnerabilities", it declares where to ask. Integrity works identically. A linter may report:

- `MIRI-PY-001 pass` — the archive is internally consistent with its own manifest.
- `MIRI-PY-005 pass` — the index publishes PEP 740 attestations covering every file of this release.
- `MIRI-PY-005 forfeited (network_unavailable)` — the question could not be asked. Reported, never silent.

A linter must not report, or let a summary line imply:

- "verified", "authentic", "untampered", "integrity OK" as a conclusion about the artifact as a whole
- a green overall badge whose tooltip or docs describe it as a supply-chain guarantee

The distinction is not pedantry about wording. A consumer who reads "verified" stops looking for the
attestation, and the attestation is the only thing that would have caught the case that matters.

## Where provenance actually comes from

Three roots, all outside the artifact, in ascending order of strength:

1. **A digest published beside the release** (`SHA256SUMS`). Answers "are these the bytes that were
   published", provided you trust the channel that served the sums.
2. **A build attestation** — PEP 740 on an index, or `actions/attest-build-provenance` for artifacts
   distributed elsewhere. Binds the file to a source repository and a CI workflow. `MIRI-PY-005` checks for
   the first of these; it is conditional and network-gated, so a wheel outside a public index is excluded
   rather than failed, and a linter without network forfeits rather than passing.
3. **A resolver-enforced lock digest.** The strongest of the three, because the expected hash is fixed
   *before* the bytes are fetched, and the check runs in the installer rather than in a tool the installer
   never consults. Your poetry lock against the definitions wheel is this, and it is why we told you to keep
   it rather than switch to `verify_content()`.

`MIRI-CONSUMER-052` carries the consequence into the consumer profile: no trust determination survives a
`package.replaced` event. A verdict about bytes must not outlive a change in those bytes at the same
identity. And `MIRI-SURFACE-040` is the same principle one layer down — a surface derives `purl` from the
installed distribution and never reads it from a document, because identity is observed, not claimed.

## What changed in the standard

`MIRI-PY-001`'s `long_description` now states the boundary explicitly, so it travels inside the definitions
wheel rather than living in a conversation. Level (MUST) and weight (0, a gate) are unchanged, and no
`fires_when` clause moved — a linter that implements the check correctly today stays correct.

**What we deliberately did not change.** Promoting `MIRI-PY-005` to MUST was considered and rejected. PEP 740
attestations became automatic only under Trusted Publishing, so a MUST would mark a large share of the
ecosystem non-conforming for a configuration choice — and the standard's own definitions wheel is not on
PyPI, so we would be shipping a MUST our only artifact cannot satisfy. The bar for MUST in this standard is
that a linter can decide it *and* near-universal non-compliance is not the expected result. It fails the
second half today. If attestation coverage becomes the norm, that is a decision to revisit with a number
attached rather than a feeling.

## One thing worth building on your side

`MIRI-PY-001` currently passes or fails as a unit. A report that distinguished *which* clause failed — file
missing from the archive, digest mismatch, unlisted file present, forbidden hash algorithm — would be much
more useful, because those four have genuinely different causes. An unlisted file present is the one to
surface loudest: it is how a component inventory gets into a wheel that the manifest does not account for,
and it is exactly the case `MIRI-PY-024` names when it requires SBOM documents to appear in `RECORD`.

The `evidence` field added in 0.7.0 is the place for it: `evidence: ["RECORD:<path>"]` says which entry
disagreed, and that is gradeable.
