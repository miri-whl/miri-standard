# Stage v0.2 Step 3 — The Standard (miri-standard repo) — OUR SIDE

The mini step-3 from Round 4: close the remaining standard-side residuals. Each item is cited to the panelist(s) who
raised it, with the verified detail. When a check/schema changes, move the checklist prose in the same commit and re-run
the `schema-governance` / `check-authoring` invariants (weights sum to 100; every example validates against its schema).

## P1 — spec/schema self-contradictions (same class as the CLI-018 bug already fixed)

- [x] **Close the api-graph schema root.** `schemas/api-graph-v1.json` has `additionalProperties:false` on the
      node/edge objects but **not the top-level object**, so a document with a top-level `workflows` array still
      validates (0 errors, verified). Add `additionalProperties:false` at the root and whitelist
      `$schema`/`version`/`generated_at`/`nodes`/`edges` in `properties`. Re-validate the real 348-node artifact
      (`miri-py/src/miri_py/agent-metadata/api-graph.json`) after — it has no `$schema` key, so it stays valid.
      _(Agent-Tooling — his remaining gate to 9)_
- [x] **Open `cli-describe-v1.json` for the danger markers, and give CLI-040 a spec home.** CLI-040 (MUST) requires a
      machine-readable `danger`/`mutates`/`destructive` marker in a command's `--describe` entry, but the schema sets
      `additionalProperties:false` on `definitions.flag` and `definitions.command` with no such field — **the schema
      forbids the field the MUST requires** (a conformant CLI cannot satisfy 040 and schema-validate). Fix: add
      `danger` and `mutates` (boolean, default false) to both `definitions.flag.properties` and
      `definitions.command.properties` (keep `additionalProperties:false`); document the two fields in the
      `cli-lifecycle-specification.md` §3.1 field table and `--describe` field list with a normative sentence, and add
      matching example JSON, so CLI-040 cites the spec (not just the landscape doc) and schema + spec + example
      validate together. _(CLI Author — a fresh CLI-018-class contradiction)_

## P2 — dogfood and CI honesty

- [ ] **Pin the miri-py CI install to a tag/SHA.** The `sample-conformance` job now installs miri-py best-effort
      (skip-guard merged in PR #3), but the URL is unpinned, so when it does resolve it scores against miri-py's moving
      HEAD (a miri-py regression could turn the standard red for unrelated reasons; a loosening could pass silently).
      Pin `git+https://github.com/miri-whl/miri-py.git@<tag-or-sha>` (or switch to a pinned PyPI version once
      published). _(Packaging + OSS)_
- [ ] **Ship an `api-graph.json` in the sample SDK** so the standard dogfoods its own trimmed §4.5 contract — today the
      only live proof of the api-graph schema is miri-py's self-scan, not the standard's own sample (the sample ships
      only lifecycle / migration-guide / sdk-manifest / usage-patterns). _(Packaging + Agent-Tooling)_
- [ ] **Add an `--execute --yes` pass over the standard's own trusted sample in CI.** The default gate forfeits 9
      checks — including MUSTs **015** (examples runnable) and **036** (discovery / manifest↔surface) — so "CI green"
      does not mean the executable MUSTs were verified. Add a second score pass with `--execute --yes` over the
      standard's **own** sample only (as miri-py dogfoods its own wheel), which runs trusted code, not untrusted
      third-party code. Depends on the miri-py CI install being available. _(Security — N2)_
- [ ] **Make the committed sample statically conforming, or switch the gate to generate→build→diff→score.** The
      committed sample's `generated_at` is a fixed date, so scoring the committed metadata _directly_ more than 24h
      later trips MIRI-PY-011 (the gate's build-time re-stamp is what rescues it). The real fix is to regenerate the
      metadata from source in CI, `git diff --exit-code` it, then build+score — the loop §5.4 and MIRI-PY-011's own
      compliant example describe. **Blocked** on the miri-py `generate` bugs (see `miri-py.md`); the switch itself is
      standard-repo. _(Packaging)_

## P2 — cleanup

- [ ] **Scrub the two residual "Committee" headings in `standards/feedback/`** — the governance pass missed them:
      `miri-standard-response-count-normalization.md:37` ("Committee-Defined Population Units") and
      `check-requirements-proposal.md:65` ("Committee homework included"). The README device disclaims the pair in
      aggregate, but a reader opening those files directly hits the language the rest of the repo just retired.
      _(OSS — R4 new finding)_
- [ ] **Fix the `alerts` → `checks` doc drift.** `standards/feedback/upstream-artifact-publishing-feedback.md`
      references `standards/python/alerts/`; the actual directory is `standards/python/checks/`. _(Packaging — R4)_

## P3 — bigger / weigh step-3 vs 0.3

- [ ] **Back the §5.4 Generation Invariants with linter checks.** Invariants #1 (evidence-only omission of
      `configuration`/`error_handling`) and #2 (CLI excluded from `api_index`) are prose-only — no check enforces them,
      so a linter cannot catch a violation (miri-py's own builder currently violates #2, emitting `main` + 47 `cli/`
      symbols into `api_index`). Add a new `MIRI-PY-0NN`, or extend `MIRI-PY-036`, so conformance is machine-verified —
      the difference between "the spec says it" and "the linter proves it." _(Agent-Tooling — larger; could be step-3
      or fold into 0.3)_
- [ ] **Add a normative line that the linter does not sandbox example execution** — so the spec text can never be read
      as promising isolation; verifying executable checks requires running trusted code under external confinement.
      _(Security)_

## Deferred to 0.3 (not step-3)

- The **adversarial-metadata fixture** (malicious twin: fabricated `api_index`, prompt-injection `prompt-templates.md`,
  SSRF URLs, credential-exfil `update_check`) already lives in the deferred consumption-spec RFC (Ask 5) and is where
  §9's injection-resistance MUSTs become verifiable. Track it there, not here. _(Security)_
