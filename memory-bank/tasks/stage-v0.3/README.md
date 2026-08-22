# Stage v0.3 — The Consumption Standard

**Branch:** `phase-0.3`
**Goal:** Close the producer to consumer loop. v0.1/v0.2 specify what an artifact *ships*; v0.3 specifies how an agent
*consumes* it — discovery, reading order, and what a conformant consumer is. This is the step the maintainer considers
final for the core thesis: the metadata is only worth producing if there is a specified contract for consuming it, and
the kill-or-validate experiment cannot run without one.

**Discipline (non-negotiable, carried from the panel):** mechanisms, never benefits. No clause asserts effectiveness;
that is the experiment's job. Every normative clause is mechanically checkable the way the 83 producer checks are.

## Source material

- RFC (working draft, all five asks + the element audit): `consumption-spec-proposal.md` (this dir).
- RFC (upstream-framed, Draft): `proposals/20260821-consumption-specification.md`.
- Grounding: the real `miri mcp` (miri-py `src/miri_py/mcp/server.py` + `provider.py`) — four tools, import-free
  discovery via `find_spec`, api-index cap 25, JSON-RPC/stdio. It is the reference binding; the spec generalizes it.

## Pillars

### Pillar 1 — Discovery Contract (RFC Ask 2) — DRAFTED

`standards/consumption/discovery-contract.md`. The transport-agnostic metadata-query contract (`list`, `lifecycle`,
`migration-guide`, `api-index`) with an MCP context server as the first binding. Specifies what exists in `miri mcp`,
then adds the wire discipline the panel demanded:

- [x] Four operations defined by input / response shape / semantics.
- [x] `api-index` cap + `truncated` flag made normative (pointers-not-dumps).
- [x] Top-level `schema_version` on every response (MIRI-CLI-010 convention).
- [x] One absence-vs-error envelope: absent (`present:false` + reason) distinguished from error (`ok:false` + code).
- [x] Surface version independent of the MCP protocol date.
- [x] Import-free discovery made a normative security property.
- [x] MCP as one binding (tool-name map + intact-response-document rule).
- [x] `[tool.miri.consume]` project declaration with the trust-boundary constraints.
- [x] §9 consumer-side security (untrusted framing, per-response provenance, no prompt-templates, SSRF guard).
- [x] Linters green (markdownlint / cspell / links) + wired into `standards/README.md`.
- [ ] Feed each new normative clause into `MIRI-CONSUMER-NNN` checks (Pillar 3).
- [ ] miri-py conforms `miri mcp` to §4 (schema_version + absence envelope + surface version) — their side.

### Pillar 2 — Consumption Map (RFC Ask 1 + 1b) — DRAFTED

`standards/consumption/consumption-map.md`. The task-to-document reading contract. Panel must-fixes applied:

- [x] Normative vs informative split made explicit (§2): read-order = SHOULD (general) / MUST (reference consumer);
  prohibitions = MUST for all conformant consumers; heuristics = informative, never verdicts.
- [x] Five tasks (§3): first-use, generative scaffold, upgrade, runtime-failure, security — each with Read-in-order +
  Must-not + heuristic. The generative task (scaffold a new integration) is included.
- [x] The two code-only rules folded in as normative interpretation rules (§4): absence is evidence-scoped not
  existential; CLI surfaces excluded from `api_index` → consult `--describe`.
- [x] Element audit (§5): all 11 elements state their consumption value; audit rule ("can't state a value → reserved /
  removal candidate") made normative. Linters green; indexed in both READMEs.
- [ ] Turn each §3 prohibition + §4 rule into a `MIRI-CONSUMER-NNN` check (Pillar 3).

### Pillar 3 — Consumer Conformance (RFC Ask 3) — TODO

`standards/consumption/checks/MIRI-CONSUMER-NNN.yaml` + a `consumer-conformance.md` + reference tool `miri brief`.
Symmetric to the CLI tool profile. Checkable consumer requirements: respects the cap; treats metadata as untrusted;
verifies claimed surfaces before relying on them; degrades honestly (absent reported absent, never synthesized);
cross-references migration data against the consumer's real call sites. Verified against the reference consumer driven
on the paired bare/miri fixture **and an adversarial-metadata twin** (a fixture whose metadata lies / injects — the
consumer must not be fooled). This is where the **circularity firewall** lives: the reference consumer and the
reference producer must not share the code that would make conformance trivially self-satisfying.

### Guardrails (fold into the pillars, not a separate doc)

- **Ask 4 (verification recipe):** land as a *pointer* — a declared smoke/test command the consumer can run, honest
  when absent — not a new mandatory producer artifact. SHOULD, producer-side, minimal.
- **Ask 5 (paired fixture + harness):** the bare/miri twin + comparison harness, gated in CI. Serves demonstration,
  the Pillar-3 fixture, and the experiment substrate. Honesty line verbatim: shows what is *available*, never what is
  *achieved*.

## Panel round (2026-08-22) — both pillars reviewed, fixes applied

Two panels ran against the drafted pillars: a **brutal substantive audit** (6 adversarial personas) and a
**naming-coherence review** (6 personas). Report: `.generated/miri-v0.3-pillar-review-2026-08-22-*.pdf`.

Substantive verdict: the pillars were "individually literate but did not compose." Four claims were independently
re-verified against the repo before acting; all four confirmed, including one error of our own (§2.6 does mandate
`ok`). Applied:

- [x] **Composition break (CRITICAL, all six)** — added a fifth `document` operation keyed on the `documents` array
  `list` already returns, with a closed servable whitelist that still excludes `prompt-templates.md`. Every Map
  read-step is now labelled with its vehicle (S)/(F)/(X), and every (S) step resolves to a real operation.
- [x] **Envelope (CRITICAL ×3 + naming panel)** — surface-owned envelope wrapping the publisher payload under a named
  key. Resolves five findings at once: versioning without reshaping, un-forgeable `ok`/`present`, genuine §2.6 reuse,
  a wrappable `list`, and a home for `purl`.
- [x] **Anti-hallucination (HIGH)** — rekeyed from `api-index` membership to installed-surface introspection;
  "confirms presence, never proves absence" is now normative in both pillars.
- [x] `ok` restored to the error envelope (our error, caught); error-code table added; `list` capped + wrapped;
  `purl` on every single-package envelope and every `list` row; api-index `signature`/`file` made optional;
  `[tool.miri.consume]` given a closed grammar; §9 split into §9.1/§9.2 so the citations resolve; SSRF scoped
  honestly to the consumer; invocation log given `outcome`/`session` + the two "licenses nothing" limits.
- [x] Naming: `miri brief` → **`miri consume`** (5 of 6; nobody defended "brief"); `distribution` →
  `distribution_name` (collided with the CLI `identity.distribution` enum). Kept `[tool.miri.consume]` and `package`
  (chair leaned keep on both). All shipped miri-py names affirmed and unchanged.
- [x] **Schema blocker** — `check-v1.json` id pattern excluded `CONSUMER`; extended to
  `(PY|CLI|PYX|CLIX|CONSUMER|CONSUMERX)` and added `consumer` to the `target` enum. Widening only: all 83 existing
  checks still validate. **Downstream-affecting** — miri-py's vendored mirror needs a re-sync before it can validate
  consumer checks.
- [ ] Deferred to Pillar 3: element-audit rows for `prompt-templates.md` are marked reserved; the numbered
  `MIRI-CONSUMER-NNN` profile itself is the next pillar, and two independent panels have now advised gating it on the
  fixture existing first.

## Sequencing

1. Pillar 1 drafted (done).
2. Pillar 2 — the teaching map (the maintainer's "teach the agent" core).
3. Pillar 3 + fixture — makes it checkable.
4. Version bump to 0.3-draft across headers / README / site once the suite is coherent.
5. Post-merge: miri-py conforms `miri mcp` to the §4 wire discipline and re-syncs the vendored checks.

## Not in scope for v0.3

- No effectiveness claims (experiment only). No new *mandatory* producer artifact beyond Ask 4 as SHOULD.
- Publishing miri-py to PyPI (deferred; internal dogfooding first).
