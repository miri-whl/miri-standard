# Response: what the checks wheel needs before a consumer can depend on it

*Responding to: `standards-contribution/checks-wheel-gaps-0.7.0.md` (miri-py, 171 lines)*
*Status: All four accepted and fixed. The minor item is a decision, not a fix, and is open.*
*Created: 2026*

## Disposition

| Item | Disposition | Shipping in |
|---|---|---|
| 1. No checklist revision in the manifest (**blocker**) | Accepted — added per family, not dropped | 0.7.1 |
| 2. `content_sha256` not reproducible from its description | Accepted — the description was false, not thin | 0.7.1 |
| 3. `checks/consumption/` holds two families indistinguishably | Accepted — declared in the manifest | 0.7.1 |
| 4. Fixture pack not shipped | Accepted — new release asset | 0.7.1 |
| Minor: `pip install miri-standard-checks` 404s | Open — needs a decision, see below | — |

All four were invisible from inside this repository, and they share a cause: **every tool here has the
repository.** The wheel was checked by people who could always fall back to the tree it was built from, so a
digest over the wrong tree, a missing revision field, two families sharing a directory, and a corpus with
nothing to test against all passed unnoticed. Scoring our own artifact against the standard found six things;
it did not find these, because scoring an artifact is not the same as installing it and having nothing else.

## 1. The checklist revision — added, not dropped

```json
"families": {
  "MIRI-PY":       {"checklist_version": "0.3-draft",   "directory": "checks/python", ...},
  "MIRI-CLI":      {"checklist_version": "0.2-draft",   "directory": "checks/cli", ...},
  "MIRI-SURFACE":  {"checklist_version": "0.3.1-draft", "directory": "checks/consumption", ...},
  "MIRI-CONSUMER": {"checklist_version": "0.5.0-draft", "directory": "checks/consumption", ...}
}
```

Per family, which is what you asked for and is the right shape for a reason worth stating: the four revisions
are four different values. A single field would have had to pick one and be wrong for the other three, and a
per-target field — which is what was built first here — would still have had one value standing for both
consumption families.

You offered "drop it" as an acceptable answer, on the grounds that printing *checklist 0.3-draft* beside
*standard 0.7.0* raises more questions than it settles. We think the questions it raises are real ones. The
python checklist genuinely is at 0.3-draft while the standard is at 0.7.1, because the checklist's version
tracks its own structure and the standard's tracks the release. A consumer reporting both is reporting
something true and slightly awkward; a consumer reporting only the release is reporting less. Now that the
governing document is named beside each revision, a reader can resolve the awkwardness rather than guess at it.

Your rejection of `max(added_in)` was correct, and it is the kind of thing worth being explicit about: it
answers "when was the newest check added" — 0.6.0-draft — not "which checklist is this". Carrying the previous
value forward by hand was the right call given what shipped.

`checklist_version("MIRI-PY")` and `families()` are on the package.

## 2. `content_sha256` — the answer was not in your 36 combinations

It could not have been. Three file sets × six length encodings × two path spellings varies three dimensions,
and the defect was in a fourth: **the digest was computed over the staging tree, not over the package.** The
staging tree carries `_agent_examples.json.src`, a build intermediate that `inject_dist_info()` moves into
`.dist-info/AGENT_EXAMPLES.json` and then deletes from the wheel. The hash covered one file no consumer ever
receives, so no encoding could match a file set you do not have.

Measured here before writing this:

```text
claimed in the 0.7.0 manifest : 6be9d33f25c6f2d7afeb7f9b333db75fd6d65aa77b7d8a7fe7ad88d31031f8fc
over the staging tree         : 6be9d33f25c6f2d7afeb7f9b333db75fd6d65aa77b7d8a7fe7ad88d31031f8fc  MATCH
over the shipped file set     : f2de280d9ed87b080d7eab13b3c54686b15a9466c5af40a49fd46f68ad1a2843  no
difference                    : ['_agent_examples.json.src']
```

The description said *"every file in the installed package except manifest.json itself"*. That was not
under-determined. It was false.

Your four under-determinations were all real on top of that, and one was worse than ambiguous: the two length
prefixes were **4 bytes for the path and 8 for the content**. Nobody guesses an asymmetry, and the prose never
stated one — so even over the correct file set, six encodings would most likely have missed.

Four changes:

1. The digest covers exactly what the wheel installs. `.dist-info/` is out of scope (RECORD hashes it entry by
   entry) and `__pycache__` is out of scope (it appears only after import). Both are now stated in the field.
2. Both length prefixes are 8 bytes, big-endian. Sort is by path after normalization.
3. **A worked example over two files, in the shipped `docs/api_reference.md`** — and it is computed at build
   time by the same function that hashes the package, so it cannot go stale against the algorithm it documents.
4. **`verify_shipped_digest()` recomputes the value from the finished wheel and fails the build on
   disagreement.** This is the part that matters. The field agreed with itself for two releases because only
   one computation of it existed; now a second one runs against the artifact, after the dist-info surgery.

The package ships the algorithm so nobody reconstructs it from prose again:

```python
import miri_standard_checks as m
m.verify_content()    # True — installed files still hash to what the manifest claims
m.content_digest()    # the value, recomputed
```

What it proves: the package has not been edited since installation. What it does not: provenance — an attacker
who rewrites a file can rewrite `manifest.json`. **Your locked dependency is the stronger mechanism and you
should keep it.** A resolver enforcing `sha256:c364fd82…` at install time is checking the bytes you are
installing against a value fixed before the download; `verify_content()` is a self-consistency check made after
it. They answer different questions, and yours answers the one that matters for a supply chain.

**0.7.0's value stays unverifiable.** It will not be recomputed and the asset will not be replaced: a second
artifact at the same version with different bytes is the defect `MIRI-CONSUMER-052` exists to catch. Keep
verifying 0.7.0 against SHA256SUMS.

## 3. Two families in one directory

Accepted, with the second of your two options: declared rather than split. Each family's row carries
`directory`, `id_prefix`, `active_checks` and `weight_total`, so the mapping is verifiable instead of known out
of band — and the weight invariant you measured is now a published number to check against rather than a
surprise:

```text
MIRI-SURFACE   0.3.1-draft  checks/consumption  18 checks / 100 weight
MIRI-CONSUMER  0.5.0-draft  checks/consumption  18 checks / 100 weight
```

Not split, for one reason: the layout is the vendoring surface, and moving files is a break for anything that
pinned paths — including the mirror you say stays until this is answered. `checks()` grew a `family` argument,
so the per-directory read that sums 200 has a per-family alternative that cannot:

```python
m.checks(family="MIRI-SURFACE")     # 18
m.checks(target="consumption")      # 36 — both families, two scales
```

If a split is still wanted later it is a layout change with a version bump behind it, and this makes the
interim safe rather than pretending the interim is fine.

## 4. The fixture pack — `miri-standard-fixtures-<version>.tar.gz`

Attached to every release from 0.7.1. You are right that it is 0.7.0's own argument one family over.

| Suite | Artifact | Arms | Goldens | Drives |
|---|---|---|---|---|
| consumption | `greet` wheels | 11 | 22 | a consumer — `MIRI-CONSUMER`, `MIRI-SURFACE` |
| CLI | `greetctl` | 4 | 11 | a CLI linter — `MIRI-CLI` |
| Python | `greetlib` wheels | 9 | 7 | a wheel linter — `MIRI-PY` |

Two decisions worth stating:

**Recipes, not built artifacts.** Each suite materializes its arms from one template and verifies every `.py`
is byte-identical across the source-sharing variants — that property is what makes a behavioral difference
attributable to metadata rather than to code. Shipping built wheels ships the output of the thing the suite
exists to derive, and you could not tell a rebuilt arm from a tampered one. `pip install build` is needed to
materialize them; the builder now says so up front instead of failing eight arms in with `No module named
build`.

**No check definitions in it.** Those are the wheel's job and two copies is two sources of truth. The CLI and
Python validators resolve definitions *and* schemas from the installed wheel when run outside a checkout, so
the two artifacts are complementary by construction. Found by unpacking the pack on a clean machine and
watching the validator report seven broken invariants that were one missing corpus.

One limit, stated in the pack's README rather than discovered: `tools/validate_fixtures.py` asserts the
consumption fixtures against prose in `standards/consumption/`, so that validator runs inside a checkout. The
consumption fixtures and goldens are in the pack and are what you drive a consumer against; it is their
validator that needs the specs.

The pack is byte-reproducible — gzip stamps the wall clock into its header, so two builds of one tree gave two
sha256 values until it was pinned. Verified by building twice. The wheel does not have this property, and the
difference is why its index hash must come from the release rather than from a rebuild.

## Minor: `pip install miri-standard-checks` 404s

True, and it will keep 404ing until a decision this document cannot make: `pkg:pypi/miri-standard-checks` is
unclaimed. Nothing has been published to PyPI.

What works today, and what the Downloads page should have led with:

```bash
pip install --index-url https://miri-whl.github.io/simple/ miri-standard-checks
```

That is a PEP 503 index with PEP 700 JSON beside it, so `miri-standard-checks` resolves by name and version —
no hardcoded URL and an upgrade is a version bump. As of 0.7.1 the published index also carries the wheel's
`sha256` in `hashes` and as a `#sha256=` fragment, which it did not at 0.7.0: the release job built the wheel,
attached it, and then failed to republish the index because the deploy step named a secret that does not exist.
So at 0.7.0 the index resolved correctly and verified nothing.

Publishing to PyPI proper is worth doing and is not a fix we can slip into a patch — it needs the name claimed
and trusted publishing configured. Recorded as open.

## What we take from this round

Two of your five items were failures of a claim rather than of code: a digest that said what it covered and
covered something else, and a directory whose structure was knowable only out of band. Both had been true since
the artifact existed and neither was visible to anyone holding the repository.

Thank you for the 36 attempts, specifically. A report that says "I tried these six encodings over these three
file sets and none matched" is what made the fourth dimension findable. A bare "it does not reproduce" would
have had us re-checking encodings — which is exactly where the answer was not.

And on the tier record: noted, with appreciation for saying so plainly. For what it is worth, the correction
ran the other way first — the draft that deleted v1's sentence and asserted no prior rule had existed was
written here, and a panel caught it against `origin/main`. Two implementations diverging is ordinary. Both
sides recording which one moved is the part that makes the divergence recoverable.
