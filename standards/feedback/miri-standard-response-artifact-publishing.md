# Response: Publish the Definitions as a Versioned Artifact

*Response Version: 0.1*
*Status: miri-standard maintainers' response*
*Created: 2026-09-19*
*In reply to: [upstream-artifact-publishing-feedback.md](upstream-artifact-publishing-feedback.md)*

Filed 2026-08-18 and left unanswered for a month while the thing it asked for became more necessary. Answered now
because the 0.6.0 bump made the cost of *not* having it concrete: every consumer re-implements the pin, and the one
that had done so correctly still found a stale copy of the validator in our own workflow. Your three tiers, in order.

## 1. Tag releases — yes, and it is the load-bearing one

Accepted. A published artifact needs a ref that cannot move, and a version number is exactly such a ref. This is
also why it has been the recurring loose end: `0.5.0` and `0.6.0` are both merged and both untagged, and two frozen
schemas now carry a `git diff <tag>` self-check that cannot run. Tags are bare (`0.6.0`, no `v`), per
`CONTRIBUTING.md`, so that `standard_version` in a report is usable as a git ref with no mapping.

One thing your note got right that we want on record: **`checks_commit_sha` stays a sha.** A tag is a movable label.
The artifact carries the tag as its *version* and the commit as its *pin*, and a report cites the pin.

## 2. Release assets — yes, built and gated, not attached by hand

Accepted, as a **data-only wheel**, `miri-standard-checks`, attached to the GitHub Release at every release tag.
The repository stays the source of truth: `tools/build_checks_wheel.py` stages `standards/*/checks/*.yaml` and
`schemas/*.json` at build time, and CI runs `make validate` and `make consistency` *before* building, so the wheel
never carries anything the gates did not pass. Inside it, `manifest.json` pins the release, the full commit sha, and
a content sha256 over every staged file — the same shape your `sync_checks.py` computes — so a consumer can confirm
the wheel it installed is the tree it names.

Built anywhere but exactly at a release tag, the version becomes `<release>.dev0+g<sha>`: a PEP 440 local version
that cannot be mistaken for a release and cannot be uploaded to an index by accident.

**This artifact is a supply-chain root.** A poisoned definitions package weakens every linter that installs it —
reweight one MUST to zero and every wheel passes. So the job attests build provenance and publishes `SHA256SUMS`
beside the wheel. This is the standard asking of its own artifact what `MIRI-PY-005` asks of producers.

## 3. Registries — PyPI later; npm and crates declined

GitHub Releases first, deliberately. PyPI with trusted publishing is the natural next step and this workflow is the
one that grows it; it waits on the tags existing and one release cycle of the attached wheel being consumed.

npm and crates are declined until a second implementation in another language exists to consume them. Three
artifacts kept byte-identical for zero consumers is maintenance with no reader.

## 4. The wheel is scored by the reference linter, and the first run is a finding

The definitions wheel is a wheel, so `miri score` runs on it in the publish job — the standard's own artifact held to
the standard it carries. Before the first run, two things it will fail are already known, and both are true
statements about the artifact rather than defects in the linter:

- **`MIRI-PY-020` has no vocabulary for an artifact distributed outside an index.** `identity.registry` must be an
  installable index, and a GitHub Release is a project page. A wheel hosted this way cannot declare a registry
  honestly, so it fails a MUST until it is on PyPI. That is the argument for tier 3 stated by the checklist itself.
- **A data-only package still owes `agent-metadata/`** (`006`), a quickstart (`014`) and a manifest whose
  `api_index` is not empty (`007`). It has an honest two-function surface — `root()` and `manifest()` — so the
  documents can be generated rather than faked; they are not generated yet.

Until both are closed the score is reported in the job log and does not gate the release. Gating a release on a
rule the artifact structurally cannot meet without PyPI would block the artifact that is supposed to get it there.

## What we ask of you

1. Consume the wheel in place of the SHA clone once the first tagged build exists, and tell us what the manifest
   is missing — you are its first reader.
2. Confirm `content_sha256` matches what `sync_checks.py` computes for the same tree, or tell us where the shapes
   differ so one of them moves.
