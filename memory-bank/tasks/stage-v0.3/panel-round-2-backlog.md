# v0.3 Panel Round 2 — complete backlog

**Source:** the journey panel, 2026-08-22 (6 reviewers + chair). Report:
`.generated/miri-v0.3-journey-review-2026-08-22-*.pdf`. Verdict: the end-to-end journey does not work; it breaks on
turn one. Of the maintainer's 8 wants: 2 delivered, 4 partial, 2 not delivered.

**This file captures every ask.** Nothing is dropped silently — items we decline get an explicit _Declined:_ note with
a reason, so the decision is recorded rather than lost.

Legend: `[ ]` open · `[x]` done · `[~]` partially done · `[-]` declined/deferred with reason.

---

## A. Blocks Pillar 3 (must fix before any check is numbered)

- [x] **A1. Both opening steps of the flagship first-use read-order are unservable.** _(CRITICAL, 5 of 6 reviewers)_
  **FIXED 2026-08-22** together with A4 and A10 — they were one knot. `README.md` dropped from the servable set;
  step 1 is now `list`, whose inventory is surface-composed from the directory listing. `AGENT_EXAMPLES.json`
  relabelled **(F)** with its `.dist-info/` location stated; `usage-patterns.json` is the served path to working
  code. Verified mechanically: **0 unresolvable (S) steps** across the whole Map.
  _Original finding:_
  `agent-metadata/README.md` is defined by no producer spec (verified: hits only in the two consumption docs), has no
  schema, no check, and appears in no sample or fixture. `AGENT_EXAMPLES.json` is a `.dist-info/` file, so the §3.2
  whitelist row's own right-hand cell ("any path outside `agent-metadata/`") bans it, and `list.documents` can never
  advertise it — while §3.2 makes membership in `list.documents` a MUST for `name`. `miri-implementation-guide.md:750`
  writes it to a _third_ path. **Pick one resolution and apply it everywhere.**
- [x] **A2. The "conforming twin" fixture does not conform.** _(CRITICAL, 4 of 6 — our own bug, verified)_
  **FIXED 2026-08-22.** Root cause was the validator, not just the data: it had exactly two `jsonschema.validate`
  calls, both on `lifecycle.json`. Now loop-validates every document in `metadata/miri/` against its mapped schema,
  and fails loudly on a document with no schema mapping (so a new document cannot be added unvalidated). Fixing the
  data surfaced four further real errors that had all been passing silently — `api_component.key_methods` must be
  objects not strings, `version` must match `^\d+\.\d+$`, `categories` is an object not an array, and pattern IDs
  must be snake_case. All 3 documents now validate; 12/12 invariants hold. The false claim in
  `stage-v0.3/README.md` has been corrected in place rather than deleted.
- [ ] **A3. The anti-hallucination MUST cannot be discharged by any operation.** _(CRITICAL)_ The operation set is
  explicitly closed ("and no others"), every existence path ends in `(F/X)` introspection, and **`(F/X)` is not one of
  the three labels §1.1 defines** — so "a consumer MUST skip a step whose vehicle is unavailable" is unresolvable for
  exactly the steps that settle existence. Add `resolve` (see B2) or state plainly that (S)-only consumers cannot
  complete §3.2/§3.3. Add the confinement obligation: a consumer without a confined execution environment reports the
  symbol unverified rather than importing an unvetted package.
- [x] **A4. `agent-metadata/README.md` reopens the injection channel that refusing `prompt-templates.md` closed.**
  **FIXED 2026-08-22.** Dropped from the servable set, and the general criterion the panel asked for is now normative:
  **only schema-governed documents are servable; no free-form natural-language document ever is.** So future document
  types are adjudicated by principle. The element audit row is marked **reserved** rather than deleted.
  _Original finding:_
  _(CRITICAL)_ The refused file has a specified structure and a linter check (MIRI-PY-039); the newly-servable one is
  unconstrained author-authored Markdown with no schema, no check, no producer clause — and it is Map §3.1 **step 1**.
  A hostile publisher moves its payload there verbatim. Drop it from the whitelist, or require the surface to
  **compose** the inventory itself from the directory listing so the bytes are surface-owned. Add the general
  criterion the whitelist lacks: **no free-form natural-language document is servable**, so future document types are
  adjudicated by principle rather than by whether someone remembered to list them.
- [ ] **A5. Map §3.3 (upgrading) has zero fixture coverage.** _(CRITICAL)_ No `migration-guide.json` in any variant, so
  an entire normative task, its two MUST-NOTs, the `migration-guide` operation, and the producer standard's
  highest-severity attack (§9.3 replacement redirect) are unexercisable. **A reference consumer that silently
  auto-migrates onto an attacker-declared `replacement` purl passes the current fixture set clean.**
- [ ] **A6. `[tool.miri.consume]` has no fixture at all.** _(CRITICAL)_ The only arbitrary-execution trust boundary in
  the contract. `build_fixtures.py`'s pyproject template emits no `[tool.miri]` table, so the closed grammar, the
  MUST-reject-unknown-key rule, no-auto-launch, and dependency-cannot-influence-harness are all untested.
- [ ] **A7. `document` is uncapped and unfilterable** inside a contract whose stated principle is "pointers, not
  dumps". _(HIGH, 4 of 6)_ §4.1 scopes `truncated`/`cap` to `list` and `api-index` only; the only counterweight is a
  Map SHOULD-not graded "wasteful, not wrong". One `document("sdk-manifest.json")` on a pandas-scale library returns
  hundreds of KB in a single conformant result — a larger dump than selectively reading the wheel.
- [ ] **A8. The producer chain never defines `signature` and does not emit `file`.** _(HIGH)_ `api_component`
  properties are `[common_errors, complexity, example, file, init_params, key_methods, purpose, related_classes,
  type, usage_patterns]` — **`signature` is absent from the schema entirely** — and the sample SDK's entries carry
  neither. Every entry degrades to `{type, purpose}` on the flagship artifact, so the routing view's reason for
  existing over `document` evaporates. Generation Invariant §5.4 already calls `api_index` "a name→file→signature
  map", so the invariant and the schema disagree.
- [ ] **A9. `api-graph.json` cannot express a method as a node.** _(HIGH)_ Node keys are
  `^[A-Za-z_][A-Za-z0-9_]*$` + `additionalProperties: false`, so `Greeter.greet` is structurally rejected — while
  `api_index` keys on exactly that (permitted because `api_index` constrains nothing). **The two key spaces cannot be
  joined.** `graph_node` is `required: ["type"]` with no `file`/`module`, so the graph cannot say which files a change
  spans — the exact "blast radius / multi-file" role §5's audit row assigns it. Either align the key spaces and add
  source-evidenced `file`/`module`, or cut the audit row back to "type and exception hierarchy" and delete the
  blast-radius claim.
- [x] **A10. The whitelist guards name strings, not resolved paths.** _(HIGH)_
  **FIXED 2026-08-22.** New §3.2.2 makes `name` a single path segment (`^[A-Za-z0-9_.-]+$`, no `/`, `\`, or `..`,
  never normalized) and requires confinement on the **resolved** path: resolve, `realpath`, require a regular file
  physically inside `agent-metadata/`, reject symlinks outright. States explicitly that name-string filtering alone
  MUST NOT be relied on, and why editable installs make the symlink shape live. _(B8 is the same item.)_
  _Original finding:_ Only containment is a blacklist of
  string shapes. A whitelisted `agent-metadata/usage-patterns.json` shipped as a **symlink to `~/.ssh/id_rsa`**
  contains no `..`, has no absolute prefix, is advertised by `list`, and is served verbatim. Editable/source-tree
  installs preserve symlinks — the exact shape the fixtures use.
- [ ] **A11. The fixture trio varies metadata content but never well-formedness.** _(HIGH)_ Every document parses, so
  of the three-way served/absent/failed discrimination, only two thirds are testable. §4.2 calls the absent-vs-failed
  split "the single most consequential clause" and notes the reference implementation currently gets it wrong — so the
  fixture set **cannot detect the very regression the spec names as the first implementation task**.
- [ ] **A12. Import-free discovery is declared load-bearing and is structurally untestable.** _(HIGH)_ The
  byte-comparison that makes the trio honest also prevents the adversarial variant carrying an import side effect, so
  a surface regressed to `importlib.import_module` passes every current fixture. Needs a canary package _outside_ the
  trio.
- [ ] **A13. The envelope's reserved-field table is not exhaustive, and one field in it is publisher-forgeable.**
  _(HIGH)_ (a) §4.1 omits `name` and `reason`, both of which appear in normative examples and carry normative force
  ("MUST branch on `ok` and `present`, never on `reason`") — an anti-forgery argument resting on the surface owning a
  known key set needs that set stated exhaustively. (b) `purl` is the residual publisher path into that namespace
  (see B7). Also: `api-index` has **no defined absent case**, and signalling absence with an empty `entries` object
  would be read as "no symbols exist" — the inference §3.5 forbids.
- [ ] **A14. `api-index`'s cap is unspecified in value, ordering and pagination.** _(HIGH)_ §3.1's example shows 100,
  §3.5's shows 25 — both conformant. `query`'s matched fields are never stated; ordering and truncation determinism
  are unspecified; "SHOULD narrow rather than paginate" leaves no cursor. **A conformant surface at cap 50 makes the
  A4 padding attack vacuous and its future check permanently green while testing nothing.**

## B. Missing capabilities (the standard lacks these entirely)

- [ ] **B1. A testing element.** _(HEADLINE — 4 of 6 reviewers independently)_ Maintainer want #5 is served by zero
  documents, operations, read-steps and schemas. Proposal: `test-patterns.json` with per-surface
  `{surface, kind: unit|integration, setup, fake_or_mock, assertion, teardown, requires_network}`, generated from the
  package's own test suite the way `usage-patterns` is generated from examples; add to the §3.2 whitelist; add Map
  §3.6 "Writing tests against a dependency" with read-order and prohibitions (MUST NOT present a synthesized mock as
  the package's supported test double; MUST report absence rather than inventing a fixture).
  **Also: make the §5 audit rule bidirectional** — it currently checks elements→tasks only, so a capability that was
  never defined passes silently. That rule flaw is why this went unnoticed.
- [ ] **B2. A symbol-existence operation** — `resolve {package, symbol}`. The ground truth only the surface can
  provide, and the discharge path for A3.
- [ ] **B3. A pre-install / target-version scope.** Wants #1 and #4. Either a `describe {purl}` variant that reads
  from the declared registry without installing (with its own SSRF and no-execution rules), **or** an explicit
  out-of-scope statement in §1/§6.2 plus a fix to Map §3.3 step 3 so no read-step depends on an unanswerable
  operation.
- [ ] **B4. Filtered access to the big documents.** A `usage-patterns` operation (filter by `query`/`category`/
  `complexity`, capped) and a symbol-scoped `api-graph {package, symbol, depth, direction}` returning a neighbourhood
  rather than the whole graph. Both carrying `truncated`/`cap`.
- [ ] **B5. An anti-patterns field.** The guidance an author most wants to convey — "never construct this
  per-request", "not thread-safe", "do not retry this error class" — has **no field anywhere**. Proposal:
  `antipatterns: [{name, wrong_code, right_code, why}]` in `usage-patterns-v1.json`.
- [ ] **B6. Routed, gated best-practice fields.** `explanation.key_points`/`security_note`/`performance_note` exist but
  no read-step names them, no audit row mentions them, no check gates them — a fully conforming package can ship zero
  best-practice content.
- [ ] **B7. A surface-derived `purl`.** §4 argues the envelope is unforgeable because "a publisher cannot write to the
  top level", yet §4.1 puts `purl` there, §9.1 makes it the input to a per-namespace trust policy, and "resolved" is
  nowhere defined — the only purl the standard specifies is publisher-authored. **A package declaring
  `pkg:pypi/requests@2.31.0` inherits requests' trust tier.** Fix: MUST be derived by the surface from the installed
  distribution's own name+version, never read from a publisher document; where `identity.purl` disagrees, serve the
  derived value and optionally flag the mismatch. Split the §4.1 row so `purl` is REQUIRED where identity resolved and
  MUST be omitted where it did not.
- [ ] **B8. Path confinement** (same as A10; recorded here as the capability: exact-name allowlist + realpath check +
  symlink rejection + a normative single-segment name grammar, which also dissolves the `agent-metadata/README.md`
  spelling inconsistency).

## C. Fixture gaps

- [ ] C1. No `migration-guide.json` in any variant (see A5). Add **A8-attack**: adversarial `lifecycle.json` with
  `status: deprecated` + foreign-namespace `replacement` purl; adversarial `migration-guide.json` renaming
  `Greeter.greet` into that successor plus one record for a surface the consumer never calls; a same-publisher
  conforming twin so the arms differ only in the redirect. Assert the namespace divergence in the validator.
- [ ] C2. No `[tool.miri.consume]` fixture (see A6). Add `examples/fixtures/consuming-project/` with paired files:
  conforming, hostile-command, hostile-unknown-key, hostile-server-value. Pass condition: the generator refuses and
  emits no harness config. Add a dependency-side probe for the no-influence rule.
- [ ] C3. No malformed variant (see A11): `lifecycle.json` truncated mid-object, `sdk-manifest.json` with a type-wrong
  `api_index`, `usage-patterns.json` with a future `schema_version`. Assert `json.JSONDecodeError` in the validator so
  a well-meaning reformat cannot silently repair it.
- [ ] C4. No import canary (see A12): a package _outside_ the byte-identical trio whose `__init__.py` writes a
  sentinel and raises. Pass condition: a full `list` plus queries leave no sentinel.
- [ ] C5. No multi-distribution cases: `AMBIGUOUS_PACKAGE` and the one-row-per-import-package rule are inexpressible
  in a single-package trio.
- [ ] C6. **No request-side attacks at all.** No hostile `name` argument is ever exercised, so
  `DOCUMENT_NOT_SERVABLE` is never produced and the §3.2 whitelist — the newest and most security-sensitive surface —
  has zero coverage. Needs a request-trace fixture (`prompt-templates.md`, `../../../../etc/passwd`, `/etc/passwd`,
  `agent-metadata/../../core.py`, a name absent from `list.documents`) each paired with its expected envelope.
- [ ] C7. No symlinked-document fixture, so the missing realpath confinement is invisible to the validator.
- [ ] C8. **A5 can be passed by accident.** Its primary injection payload sits in `sdk-manifest.json`'s top-level
  `summary`, which no `api-index` response carries and a budget-conformant consumer never sees — so a consumer passes
  by being _efficient_, not by resisting injection. The residual reachable payload rides on a phantom symbol already
  caught by A3. The two files the producer specs name as the real injection surfaces (`prompt-templates.md`,
  `usage-patterns.json`) are absent from the adversarial variant entirely.
- [ ] C9. **A4 is calibrated against a cap no spec fixes** (see A14). Make the fixture self-calibrating
  (`build_fixtures.py --api-index-cap N`, N+5 pads) and write the assumed cap into a machine-readable
  `expected/api-index.json` the validator reads instead of a module constant.
- [ ] C10. **A7's traversal half tests a rule that exists in neither consumption spec** — no clause forbids
  dereferencing an `api_index` `file` pointer that escapes the package root, so no check can be written against it
  without inventing normative text. The validator asserts only the SSRF half.
- [ ] C11. No identity-skew case: the adversarial `lifecycle.json` declares a truthful purl, so surface-resolved vs
  publisher-claimed purl (B7) is never forced. Version skew between metadata and installed code likewise uncovered.
- [ ] C12. **The fixture set ships attack inputs with no expected outputs** — every pass condition is prose in a README
  column. Add `examples/fixtures/expected/` golden envelopes; this is what turns A1/A2 from surface-behavior
  assertions filed under consumer pass conditions into checkable properties.
- [ ] C13. The miri arm is unvalidated against its own schemas (see A2).

## D. Regression status from round 1 (10 prior findings)

| # | Finding | Status |
|---|---|---|
| 1 | Pillars do not compose | **PARTIAL** — `document` added, but two (S) steps still unservable and the whitelist self-contradicts (A1) |
| 2 | `schema_version` unsatisfiable vs carry-intact | CLOSED |
| 3 | Envelope forgeable | CLOSED (except `purl` — B7) |
| 4 | Anti-hallucination on a capped index | **NOT ADJUDICATED** by the regression pass — re-verify independently |
| 5 | CLI §2.6 reuse dropped `ok` | CLOSED |
| 6 | `list` a bare array | CLOSED |
| 7 | per-response `purl` provenance | **PARTIAL** — §4.3's error example omits `purl` (A13) |
| 8 | api-index entry shape vs producer | **PARTIAL** — over-requiring fixed, but producer still defines no `signature` (A8) |
| 9 | Identity axes conflated | CLOSED |
| 10 | SSRF guarded wrong actor / dangling cites | CLOSED |

## E. Do not churn (affirmed by every reviewer)

The surface-owned envelope (wrapping not merging); the orthogonal `ok`/`present` split with `reason` explicitly not a
machine field; the spec's candour about its own reference implementation (**keep that clause until `miri mcp`
conforms**); the fixtures' anti-rot design (byte-comparison, liveness assertions, the inverse assertion that the
adversarial document must _fail_ validation, the AST walk); the identity-axis separation and `AMBIGUOUS_PACKAGE`; the
SSRF ownership split; `usage-patterns.json` as an element.

**Strategic note:** lead the value case with `lifecycle.json` — 873 bytes replacing an unbounded search, facts an
agent cannot derive from source — _not_ with the context-budget argument, which the measurements (~8.7% on the
sample SDK) do not yet support.
