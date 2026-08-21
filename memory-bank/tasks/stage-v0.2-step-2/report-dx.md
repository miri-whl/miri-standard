# Stage v0.2 Step 2 — The dev-facing report (`miri score --format pdf`)

Goal: make the conformance **report a developer receives** great — not just correct. Assessed by reading the real
artifact `patitur-sdk-api-client-0.10.7-miri-report.pdf` (miri-py 0.2.0), the run against a real un-adopted Patitur
wheel (47/100, non-conforming, 11 MUST failures).

**Split of ownership.** The PDF *template and aggregation* are miri-py (`miri score --format pdf`). The per-check
*"Why it matters" / "Fix" / "Target state"* copy is rendered from **our** check YAMLs (`standards/python/checks/*.yaml`
→ `rationale` / `remediation` / example fields). So a great report is a shared job; items below are tagged **[ours]**
or **[miri-py]**.

## What the report already does well (keep)

Clean Conformance + Health score cards; per-section bar chart; a prominent red MUST-failures box; a full check table
(every check with LVL / WT / RESULT / DETAIL); and per-failure "Violations & Suggested Fixes" cards carrying *Why it
matters*, the exact violation + location, a **Fix:** line, a concrete **Target state:** JSON, a docs link, and a
provenance footer (checklist SHA + linter version + profile + timestamp). Strong skeleton — the gaps are about turning
a scary number into an obvious next action.

## P0 — the actionability wins

- [ ] **[miri-py] Surface the leverage: one file clears seven failures.** 7 of the 11 MUST failures (018–023, 033)
      are all "lifecycle.json missing". The report lists them as seven separate cards and never says they collapse to
      a single fix. Add an up-front "Fastest path" summary: *"Add one file — `agent-metadata/lifecycle.json` — and you
      clear 7 of 11 MUST failures."* Group violations by shared root cause (missing file / missing dir) before listing
      them individually. This is the single highest-impact change.
- [ ] **[miri-py] Fill "Target state" with the developer's real identity.** Every target-state snippet uses a stranger's
      package — `example-sdk@1.2.0`, `Example_SDK 2.1.1`, `pkg:pypi/acme-billing`, `weather-sdk-ng`. The dev has to
      mentally translate each one. Substitute the scored artifact's real name / version / purl
      (`patitur-sdk-api-client`, `0.10.7`, `pkg:pypi/patitur-sdk-api-client@0.10.7`) into the rendered examples so a
      dev can copy-paste. (Requires the check YAML target-state to be a template with clear substitution slots — see
      the [ours] item below.)
- [ ] **[miri-py] Show the path to Core-conforming.** The report leads with a scary Full-profile 47 and never mentions
      that Core is the recommended on-ramp. Add: *"You are N MUST checks away from **Core-conforming**"* with just the
      Core-set failures highlighted. Reframes adoption as achievable.

## P1 — clarity

- [ ] **[miri-py] Explain forfeits as recoverable, not failures.** The header says "9 check(s) forfeited" with no
      guidance. Add a short line per skip reason: *"5 checks need `--network`; 3 need `--execute`; 1 needs a previous
      release — re-run with those enabled to evaluate them."* A dev shouldn't read a forfeit as a fault.
- [ ] **[miri-py] Fix the duplicated grade string.** The header renders "NON-CONFORMING · NON-CONFORMING · 9 check(s)
      forfeited" — the grade and the band both emit the same token. Show one, or show grade + numeric band.
- [ ] **[miri-py] De-duplicate "Why it matters".** Every check in a section repeats the same rationale paragraph
      verbatim (e.g. all six Identity & Security cards). State it once per section, then per-check specifics only.
- [ ] **[miri-py] Add grade-band context to the score cards.** Show the Bronze/Silver/Gold thresholds and where 47
      lands, and a one-line gloss of Health vs Conformance (a dev won't know `weighted_linear / balanced@1` means).

## P1 — [ours] check-YAML copy that feeds the report

- [ ] **Make `remediation` / target-state examples template-ready.** So miri-py can substitute the real identity
      (above), the check YAML examples must use unambiguous placeholders (a single convention, e.g. `<PACKAGE_PURL>`,
      `<NAME>`, `<VERSION>`) instead of ad-hoc stand-ins (`example-sdk`, `acme-billing`, `weather-sdk-ng`). Audit the
      `standards/python/checks/*.yaml` `remediation`/example fields for consistency. Coordinate the placeholder
      convention with miri-py's renderer.
- [ ] **Tighten remediation to one imperative line where possible.** The best cards (e.g. MIRI-PY-021 "Declare at
      least one OSV-compatible advisory endpoint.") are crisp; some are wordier. A dev scanning 11 failures wants the
      verb-first fix first, detail second. Review the `remediation` field across the checks a typical wheel fails.
- [ ] **Ensure every check's docs link resolves.** The cards link `https://miri-whl.github.io/checks/python/miri-py-006.html`
      etc.; confirm the site generator publishes a page per check ID so no card links to a 404 (tie-in with the site
      build).

## Optional — deeper review

- [ ] If desired, run a focused 2-reviewer **report-DX panel** (a developer *receiving* a 47 and trying to fix it; a
      docs/DX writer) on this exact PDF, for a timestamped report like the other rounds. The list above is my direct
      read; a panel would pressure-test it.
