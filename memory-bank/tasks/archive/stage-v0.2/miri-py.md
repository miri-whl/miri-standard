# Stage v0.2 — miri-py (conform to the standard)

Two kinds of miri-py work: **(A)** make the `miri` CLI itself pass the MIRI-CLI rules the standard publishes
(dogfooding — the CLI panel found it fails 10 of 17 sampled MUST checks), and **(B)** fix the linter's check
implementations so they enforce the standard correctly. These belong in the `miri-py` repo; recorded here because
they conform to _our_ rules and several coordinate with `standard.md`.

## A. CLI self-conformance to MIRI-CLI (dogfooding)

The `miri` command must pass the checklist it enforces. Current sampled failures, all MUST:

- [ ] Implement `--describe` introspection (MIRI-CLI-015) — also unblocks MIRI-CLI-017 (version coherence). _(needs
      the describe schema from `standard.md`)_
- [ ] Add a `check-update` subcommand (MIRI-CLI-025).
- [ ] Add a `changelog --since` subcommand (MIRI-CLI-029) in the shape `standard.md` settles.
- [ ] Single-line, parseable `--version` (MIRI-CLI-003); fix the `version` **subcommand** exit-1 result-callback
      bug.
- [ ] One root output flag / JSON everywhere (MIRI-CLI-008/009): add JSON mode to `validate`, `version`, `doctor`,
      `check`, `init`.
- [ ] Stamp `schema_version` on all JSON output (MIRI-CLI-010).
- [ ] Clean payload channel (MIRI-CLI-011): `lint --format json` must emit only JSON — no Rich banner, spinner
      residue, or emoji prose on stdout.
- [ ] Structured error envelopes with `error.code` / `ok:false` (MIRI-CLI-013) instead of prose failures.
- [ ] Document the exit-code table (referenced by MIRI-CLI-030/042).

## A′. Functional CLI bugs found while probing (fix before public)

- [ ] `lint --format json <valid-pkg>` crashes (`'str' object has no attribute 'value'`) — the lint JSON path is
      never exercised.
- [ ] `except ImportError: pass` in `cli/main.py:222` silently amputates 12 of 14 commands (incl. `score`) when one
      import is missing, while help still advertises them — fail loudly. (Ironic against MIRI-CLI-037 "no silent
      removals".)
- [ ] `miri lint -o results.json` writes nothing, silently.
- [ ] `validate` failure guidance recommends a `--fix-auto` flag that does not exist.

## B. Linter check-implementation fixes (enforce the standard correctly)

- [ ] Align to the `sdk-manifest-v1.json` version-pattern fix so MIRI-PY-007 and MIRI-PY-012 can both pass a `2.1`
      wheel. _(coordinates with `standard.md` release blocker)_
- [ ] MIRI-PY-011: implement all four `fires_when` clauses — currently only postdating is checked, so the
      committee's own "predates by three weeks" violation example passes; UTC-normalize timestamps and have the
      generator emit `datetime.now(timezone.utc)`.
- [ ] MIRI-PY-005: consult `identity.registry` or skip for `distribution: private` — stop hardcoding pypi.org.
- [ ] MIRI-PY-035 sandbox probe: fix `module.Class.method` name resolution (`rpartition` → `ModuleNotFoundError` →
      false "unresolvable" violation) and move the `getattr` inside `warnings.catch_warnings`.
- [ ] MIRI-PY-009: declares `requirements: [network]` but never uses the network — remove the decorative requirement
      or implement the check.
- [ ] MIRI-PY-001: exclude `RECORD.jws` / `RECORD.p` from the unrecorded-member sweep so it does not flag signed
      wheels.
- [ ] Add the manifest↔surface verification check once `standard.md` defines MIRI-PY-041 — the ingredients (sandbox
      import + AST parser + manifest reader) already exist.

## B′. Generator correctness (it currently fabricates metadata)

- [ ] Stop fabricating in `manifest_builder.py`: `_build_configuration` invents `{PKG}_API_KEY`/`{PKG}_BASE_URL` env
      vars from the package name; `_build_error_handling` invents "common_causes". Emit only evidenced values (env
      vars actually read via AST; exceptions actually raised) or omit the section. _("a trust standard whose
      reference generator invents `FOO_API_KEY` is self-refuting")_
- [ ] Fix `generate_agent_readme` against the real schema (flat-dict `api_index`, `agent-metadata/` path, real
      `quick_reference` keys, drop the unconditional "Complete API reference"/"Comprehensive" claims) or stop
      generating it — it KeyErrors against its own manifest.
- [ ] Implement or drop `generate_api_graph` (currently a stub writing empty nodes/edges → api-graph.json is
      decorative).

## B″. Legacy `lint` path and vendored mirror

- [ ] Fix the legacy `lint` path or delete it: `validators/standard_whl.py:425` looks for `.dist-info/` **directory**
      zip entries pip never writes, so it false-positives on every pip-built wheel (verified against `requests`).
      Match `.dist-info/` as a path-prefix component; also fix the schema-validation crash that still prints
      "Validation complete". Then rewrite the README around `miri score` (which it never mentions) and deprecate the
      6-layer path.
- [ ] Re-sync the vendored check mirror: all 40 `checks/data/*.yaml` have drifted from upstream; the vendored
      `check-v1.json` is missing `rationale`/`fires_when`/`remediation`/`urls`. Regenerate, widen `checks/models.py`,
      and make CI fail on content-hash mismatch (the PROVENANCE mechanism exists — wire it to reality).

## B‴. Enhancer and network safety

- [ ] Wheel enhancer: warn/refuse when re-enhancing an already-signed/attested wheel (it silently invalidates the
      provenance MIRI-PY-005 rewards); add a decompression-bomb size cap; stop stamping wall-clock timestamps that
      break SOURCE_DATE_EPOCH-reproducible wheels.
- [ ] `--network`: block RFC1918/link-local/metadata IPs, enforce HTTPS, and re-validate redirect targets — it is
      currently an unguarded SSRF-GET primitive (MIRI-PY-026/027 fetch package-declared URLs).
- [ ] Rename the "sandbox"; make `--execute` help state plainly that it runs untrusted wheel code with the caller's
      privileges and that the network block is best-effort/bypassable; recommend a disposable container; ideally
      gate behind an explicit confirmation. _(off by default — fixable, not catastrophic)_

## B⁗. Dogfood the wheel

- [ ] Make miri-py's own wheel conforming: add `agent-metadata/`, a quickstart, and a PEP 621 `[project]` table
      (currently legacy `[tool.poetry]`); drop `anthropic` from runtime deps of a linter; fix the classifier vs
      `requires-python` mismatch; resolve the self-declared `[tool.miri] compliance = "partial"`.
