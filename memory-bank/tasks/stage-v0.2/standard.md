# Stage v0.2 — The Standard (miri-standard repo)

Spec text, check YAMLs, JSON Schemas, checklists, site, governance, sample SDK. When a check YAML or schema changes,
move the checklist and prose in the same commit and re-run the `schema-governance` invariants.

## P0 — honesty, governance, blockers

- [x] Replace "committee-owned" / "committee-assigned" framing everywhere (check-page status lines, both index
      ledes, site footers, QUICKSTART) with honest small-team/BDFL governance language. _(all panelists; skeptic
      "false provenance claim")_
- [x] Fill or remove placeholders: `GOVERNANCE.md` ("[To be established]"), `SECURITY.md`
      ("[SECURITY_EMAIL_TO_BE_ADDED]", "[TO_BE_ASSIGNED]"). _(security, skeptic)_
- [x] `README.md`: replace "[QUICK START GUIDE TO BE ADDED]", delete stale "Planned: Q2 2025" roadmap, add a real
      getting-started path and a pointer to the linter once it is public. _(skeptic, CLI, packaging)_
- [x] Reframe `standards/feedback/` self-authored proposal/response dialogue as design notes, or disclose single
      authorship. _(skeptic)_
- [x] Add an honest status section/page: what exists (specs, schemas, 83 checks, site), what is planned (linter
      public, CLI describe schema), what is missing. _(skeptic, AI researcher)_
- [x] Sample SDK: make `examples/sample-sdk` buildable and checklist-passing — restore `pyproject.toml`, add
      `examples/quickstart.py` and `AGENT_EXAMPLES.json`, add a migration guide, fix the 1.2.0/1.0.0 version
      incoherence — then gate it with `miri score` in CI. _(all; it currently fails MIRI-PY-014/016 at the front
      door)_
- [ ] Fix the cross-links broken by the `standards/python` file renames (the stashed rename work): every reference
      to the old filenames in `linter-checklist.md` and the check YAMLs. _(carried over from the rebase)_
- [x] Strip unvalidated performance claims from normative text ("30–60 seconds", "instant consumption", "eliminate
      re-parsing") — restate as labeled hypotheses; reframe the pitch around version-locking and offline
      availability. _(AI researcher, agent-tooling)_

## P1 — fix shipped contradictions and check bugs (before implementers encode them)

CLI track:

- [x] Pick one `retryable` value for `CONFIRMATION_REQUIRED` (MIRI-CLI-006 `true` vs MIRI-CLI-040 `false`) and add
      the missing error-code table to the CLI spec §6. _(CLI author)_
- [x] Pick one `changelog --since` shape (MIRI-CLI-029 array vs MIRI-CLI-036 object-keyed) and make both examples
      agree. _(CLI author)_
- [x] Make every spec example satisfy MIRI-CLI-010 (top-level `schema_version`): 8 error-envelope example files omit
      it and the `--describe` example nests it. _(CLI author)_
- [x] Rewrite MIRI-CLI-003 to require a parseable first line (`<name> <version>`) per GNU §4.7, or stop citing GNU —
      the current compliant example contradicts the cited authority. _(CLI author)_
- [x] Replace the dead `pkg:brew` / `Homebrew` OSV join in MIRI-CLI-015/016 examples and fix MIRI-CLI-016's false
      "joins directly against OSV records" claim. _(CLI author)_
- [x] Reconcile the sixth contradiction: the lint-report format stamps `report_version` while MIRI-CLI-010 mandates
      `schema_version` — rename the field or define/exempt the report envelope in 010. _(CLI author)_

Python track:

- [x] **Release blocker:** `schemas/sdk-manifest-v1.json` version pattern `^\d+\.\d+\.\d+.*$` rejects valid PEP 440
      (`2.1`, CalVer) — a `2.1` wheel cannot pass MIRI-PY-007 and MIRI-PY-012 simultaneously. Fix the pattern (or
      parse via `packaging.Version`). Coordinates with `miri-py.md`. _(packaging, proven by probe)_
- [x] Fix MIRI-PY-012's garbled `fires_when` bullet ("1.2.0 vs 1.2" describes canonical agreement as a violation)
      and state whether 012/019 equality is textual or canonical. _(packaging)_
- [x] `schemas/lifecycle-v1.json`: `{status: eol, replacement: null}` validates despite MIRI-PY-033's
      "schema-enforced" claim — narrow `replacement` to `type: string` under the `then`; fix the "and a successor
      exists" hedge that contradicts 033. _(security, packaging; proven by fuzzing)_
- [x] Define a normative mechanism for deprecating module-level attributes (PEP 702 `@deprecated` can't mark them) —
      resolve the MIRI-PY-028 vs 035 gap. _(packaging)_
- [x] MIRI-PY-011: keep all four `fires_when` clauses; pin the build-window tolerance centrally (not "the linter's")
      and specify SOURCE_DATE_EPOCH interplay. _(packaging, agent-tooling)_
- [x] MIRI-PY-005: make conditional on `distribution: open-source` / derive the endpoint from `identity.registry`
      instead of hardcoding pypi.org in `fires_when`. _(packaging)_
- [x] Define stable counting rules for `violation_unit: "each schema violation"` (007–010) — validators disagree on
      granularity, so scores are not comparable. _(packaging)_

## P1 — schema-enforces-the-spec and missing schemas

- [x] Push the linter's URL enforcement into the published schema: require `^https://` for all signal URLs
      (registry, advisory, `update_check`, `vex`, `security_policy`); reject `http://`, `javascript:`, `file:`.
      _(security)_
- [x] `lifecycle-v1.json`: `osv` source ⇒ `ecosystem` required; define `osv-local` base-path resolution; define
      `authoritative` default and list-order semantics. _(security)_
- [x] Ship the CLI `--describe` introspection JSON Schema — 33 of 43 CLI checks depend on it. _(CLI author; the
      single biggest CLI-track blocker)_
- [ ] Ship or de-reference the missing schemas: `agent-examples-v1.json` (aka `ai-examples`), `templates-v1.json`,
      `api-reference-v1.json`; specify or delete `performance-hints.json`; add `examples-index-v1.json`. _(agent-
      tooling, packaging, security)_
- [ ] Add `scoring-v1.json` / `lint-report-v1.json` to `schemas/` (the report format the linter emits). _(CLI
      author)_

## P1 — producer-spec reconciliation

- [x] Excise or respec "Enhanced METADATA" (`miri-wheel-extensions.md` §4.2) — unimplementable (no PEP 517 backend
      injects custom core-metadata fields; the example puts fields in the Description body); §7.2.1 mandates it for
      Minimum Compliance. _(packaging, security)_
- [x] Collapse the three conflicting "Minimum Compliance" definitions into the checklist as sole authority; delete
      the `Miri-Compliance: full|partial|none` vocabulary. _(packaging, agent-tooling)_
- [x] Rename all `AI_EXAMPLES.json` → `AGENT_EXAMPLES.json` and `get_ai_metadata` → `get_agent_metadata` across the
      specs. _(agent-tooling, security)_
- [x] Fix or regenerate `implementation-guide.md` — broken `importlib` loader, invalid JSON example, `build_hooks`
      import mismatch, naive timestamp; it is superseded by a working implementation it does not reference.
      _(packaging, agent-tooling)_
- [x] Amend MIRI-PY-001 remediation to sanction RECORD-coherent post-processing (the enhancer does this
      legitimately) and exclude `RECORD.jws`/`RECORD.p` from the unrecorded-member sweep. _(packaging)_
- [x] Purge PEP 491 citations (Deferred) → cite the living Binary Distribution Format spec; add PEP 639
      License-Expression coverage (nothing checks it today). _(packaging)_
- [ ] Reconcile `$schema` URLs (`miri-standard.org`) against canonical `miri-whl.github.io`; align version labels
      (`1.0-draft` vs `0.1-draft`). _(security, agent-tooling)_

## P1 — threat model and trust (standard-side)

- [x] Write the Threat Model / Security Considerations section in both specs: metadata is attacker-controlled once a
      package is compromised; all natural-language metadata is untrusted **data**, never instructions; auto-actions
      (migrate to `replacement`, apply `vex`, follow a fix) require out-of-band verification or human confirmation.
      _(security, agent-tooling, AI researcher, packaging — four panelists)_
- [x] Invert the trust anchor: artifact-declared `advisory_sources`/`update_check` are hints; authoritative source
      selection comes from consumer-side policy keyed by purl namespace. Add: HTTPS-only, no credential forwarding
      to package-declared URLs, SSRF guidance. _(security)_
- [x] Fix the redirect primitive: consumers MUST verify `support.replacement` provenance (same publisher via PEP 740
      identity) before acting; agents MUST NOT auto-install a replacement. _(security)_
- [x] Make MIRI-PY-039 enforce something real (length caps / no-imperative heuristics) plus normative "treat as
      data" text — a "has ≥ 1 heading" check is not content safety. _(agent-tooling, security)_
- [x] Promote PEP 740 attestations (MIRI-PY-005) from SHOULD/2pts toward MUST or Gold-gating for public wheels; stop
      calling `generated_at` an "audit trail." _(security)_
- [x] Define the currency algorithm (exclude yanked/pre-releases, respect `Requires-Python`, consult PEP 792 before
      trusting local `support.status`). _(security)_

## P2 — scope and adoption

- [x] Define a "Core" conformance profile (~15 checks) an ordinary well-maintained project can pass in a day — an
      on-ramp, not just a wall of MUSTs. _(every panelist, both rounds; `requests` scores 40/100)_
- [x] Fix the scoring model: Gold is arithmetically unreachable for first releases (previous-release forfeiture caps
      at 86); define skipped-MUST score semantics; make grades measure the wheel, not the linter's capabilities
      (report a capability profile). _(CLI author, packaging)_
- [x] Declare the POSIX platform scope explicitly in `standards/cli/README.md` (Windows appendix later). _(CLI
      author)_
- [x] Split the standard: promote the lifecycle/deprecation/identity layer as "Miri Core"; demote
      sdk-manifest/usage-patterns/api-graph to experimental / optional-derived. _(agent-tooling, AI researcher;
      four-panelist convergence)_
- [x] Add MIRI-PY-041 (or fold into 036): manifest↔code verification — every `api_index` symbol must exist in the
      importable surface. Would make Miri the only _verified_ API-summary format. Coordinates with `miri-py.md`.
      _(agent-tooling)_
