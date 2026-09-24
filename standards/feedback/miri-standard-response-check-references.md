# Response: the incomplete standards trail where checks cite a PEP in prose

*Responding to: `standards-contribution/check-references-completeness.md` (miri-py)*
*Status: Accepted in full and gated. One change asked of you in return.*
*Created: 2026*

## Disposition

Accepted, all 21 pairs, shipping in 0.7.2. Your count reproduces exactly against this tree:

```text
pairs 21   checks 18   distinct PEPs 11
by PEP: {387:2, 427:1, 440:2, 503:2, 517:1, 565:1, 632:1, 691:1, 702:8, 740:1, 792:1}
PEP 702 — missing on 8 checks, linked on 1
```

And your rule is now **gated**, not merely applied: `tools/check_references.py` fails the build when a
check's prose names a PEP its `references` omit, printing the exact entry to add. That is the part that
matters — applying it once fixes 0.7.1, gating it means 0.7.3 cannot quietly reopen it. Mutation-tested by
removing each reference and confirming the gate names it.

We took the mechanical rule for the reason you gave: the alternative is editorial judgment about which
documents are "important enough", which nothing can gate and every editor answers differently.

One correction to your numbers, immaterial to the ask: "already used by 15 MIRI-PY checks and 21 references
in total" — 21 is the MIRI-PY count. Across all four families it is 37.

Found while implementing: one existing reference carried `title: 700` rather than `PEP 700`, so any renderer
showing the title alone printed a bare number. Fixed in the same change.

## What we are asking of you: relabel the card

Your fix card renders this line as **"Defined by: PEP 770"**. For 17 of the 21 that is exactly right. For
four it is false, and the falseness is the kind that teaches a producer something untrue about where a rule
comes from:

| Pair | How the prose actually cites it |
|---|---|
| `MIRI-PY-001` / PEP 517 | remediation: *"Rebuild the wheel with a standard PEP 517 backend via `python -m build`"* — a tooling instruction. The check's authority is PEP 427 plus the living binary-distribution-format spec, **both already in its references**. PEP 517 does not make RECORD a rule. |
| `MIRI-PY-031` / PEP 632 | rationale: *"PEP 632's migration advice leaves `distutils.util.strtobool` … with no successor"* — cited as evidence of the harm the check exists to prevent. The check is not defined by it; it is defined against it. |
| `MIRI-CLI-021` / PEP 702 | *"PEP 702's `@deprecated` message, Rust's `#[deprecated(note)]`, RFC 9745's deprecation link relation"* — comparative prior art. A CLI check is not governed by a Python typing PEP. |
| `MIRI-CLI-032` / PEP 702 | *"`replacement` follows PEP 702's `@deprecated`, GraphQL's `@deprecated(reason:)`, Java's `@Deprecated`"* — same shape. |

So: **"References: PEP 702"** rather than **"Defined by: PEP 702"**. True for all 21, still gets a producer
to the document in one click, and smaller than the change you asked of us.

We considered the alternative — a `defines` versus `cites` distinction in the reference object — and rejected
it. It is a schema change, it requires a judgment call on all 123 checks, and the judgment is exactly the
thing your rule was designed to avoid needing. A label that is true of every entry is better than a taxonomy
that has to be maintained.

## Two notes on your audit script

`PEP[\s-]?(\d{3})` captures three digits, so a four-digit PEP becomes a wrong three-digit pair rather than no
pair. No such PEP exists yet, so this is latent rather than live; ours uses `\d{3,4}` on both sides. The set
arithmetic is right — `MIRI-PY-032` cites both 440 and 702, already links 440, and correctly appears once in
your table.

Your field list is the right one. We kept it identical rather than adding `name` or `category`, because a PEP
named in a check's *name* and nowhere else would be a naming problem, not a citation problem.

## What this closes, and what it does not

It closes the gap between "this MUST failed" and "here is the document that makes it a rule rather than this
tool's opinion", for every implementation at once rather than each hard-coding a PEP-number-to-URL map the
standard already knows. That framing is right and is why this was worth doing at the source.

We extended it to RFCs in the same change rather than waiting to be asked, and found six checks naming
RFC 9457, 9745, 822, 3339 and 8259 without linking them. Ten more references went in alongside: `MIRI-PY-026`
requires a `vex` URL to serve *"an OpenVEX document or a CycloneDX document containing a `vulnerabilities[]`
analysis"* and referenced only OpenVEX, so a producer whose VEX is CycloneDX had no link to the specification
they were being judged against; `MIRI-PY-024` names both SBOM formats it accepts and cited neither.

**The gate stops at numbered documents, and that boundary is deliberate.** "PEP 702" and "RFC 9745" name one
document, and the URL is arithmetic — naming the number *is* the citation. Named bodies are not the same:
23 checks mention `purl` and 11 mention OSV, but most are our own field names (`identity.purl`) or an
ecosystem aside, not a citation of a specification. Gating those would have added 34 references nobody asked
for and diluted the trail the rule exists to keep honest. So they stay editorial, and the audit for them is a
person reading prose. If you disagree, the argument we would want is a case where a named-body mention left
you unable to reach a document you needed.

Our own first draft of the gate made the opposite error and is worth recording: it matched only
`rfc-editor.org/rfc/rfcNNNN` and reported two RFCs on `MIRI-CLI-032` as unlinked when they had been linked
all along as `/info/rfcNNNN/`, the spelling this repository uses. A gate that cannot read its own
repository's convention manufactures work rather than finding it — worth knowing if you run the audit your
side against a tree whose URLs differ from your pattern.

## One more, from the same thread: SLSA

Unprompted by your report, but found by pulling the same thread. `MIRI-PY-005` checks that an index publishes
PEP 740 attestations. The payload of one is an in-toto statement whose predicate is typically
`https://slsa.dev/provenance/v1`. **SLSA and in-toto appeared nowhere in 123 definitions** — the standard
required provenance, ships provenance on its own releases via `actions/attest-build-provenance`, and never
named the format its provenance is in.

`MIRI-PY-005` now carries the SLSA reference and states the boundary in its rationale: PEP 740 is the
*distribution mechanism* — how an index receives, verifies and republishes an attestation — while SLSA
provenance is the *content*, carrying `buildDefinition`, `runDetails`, and the `builder.id` that SLSA calls
the sole determiner of the build level. The check asks whether provenance is published, not what it says. An
attestation whose predicate asserts nothing useful about the build satisfies it today.

That gap is real and we are not closing it by widening `MIRI-PY-005`: verifying a payload is a different
check with a different failure mode, and it would need the same MUST-bar argument that kept `005` at SHOULD.
If you have a view on whether a predicate-type-and-builder check is worth its weight, we would rather hear it
before writing it than after.
