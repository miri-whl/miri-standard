# miri-py work order — v0.3 (Consumption)

**From:** the standard, `phase-0.3` branch
**Status of the standard side:** Discovery Contract and Consumption Map drafted, panel-reviewed, and revised. Both
specs are green on all three doc linters; all 83 checks still validate.

**Read first:** `standards/consumption/discovery-contract.md` (the wire contract) and
`standards/consumption/consumption-map.md` (the reading contract). The §-numbers below refer to the Discovery Contract.

**Explicitly NOT in this work order:** publishing to PyPI. That has moved to **0.4**. Nothing here requires a public
package — a git tag is enough (item 2).

---

## 1. Re-sync the vendored checks (~10 min, unblocks CI hygiene)

The vendored mirror is stale, and it is now also missing a schema change it needs.

- Current: `src/miri_py/linter/checks/data/PROVENANCE.json` pins `commit_sha: 58b44cd…`, `checklist_version: 0.1-draft`.
- Upstream is at `607f339` with `checklist_version: 0.2-draft`.
- The sync ran today but against the old constant, so the pin never moved.

**Do:**

1. `scripts/sync_checks.py:53` — bump `PINNED_SHA` from `58b44cd56870304f9ea3f2a68f70dacfa488abb5` to the current
   `main` (`607f339`, or a later `main` if it has moved).
2. Re-run the sync. Verify `PROVENANCE.json` shows `checklist_version: 0.2-draft` and a new `content_sha256`.
3. Confirm the 100-point-sum invariant and schema validation still pass on the refreshed copy.

**Note a schema widening you will pick up in this sync.** `schemas/check-v1.json` changed on the standard side:

- the check-id pattern is now `^MIRI-(PY|CLI|PYX|CLIX|CONSUMER|CONSUMERX)-\d{3}$`
- the `target` enum now includes `consumer`

Both are **widenings** — every existing check still validates, so nothing breaks. But an un-synced mirror will reject
the `MIRI-CONSUMER-NNN` checks when they land, so this sync is a prerequisite for consuming v0.3's conformance work.

## 2. Tag a release (unblocks the standard's CI pin)

The standard's `sample-conformance` job installs miri-py from an **unpinned** git URL, so it scores against your moving
HEAD — a regression on your side turns the standard red for unrelated reasons, and a loosening passes silently.

**Do:** cut a git tag (e.g. `v0.2.0`) once item 1 lands. That is all we need; we will pin
`git+https://github.com/miri-whl/miri-py.git@<tag>`. No PyPI publish required.

## 3. Conform `miri mcp` to the Discovery Contract (the main work)

v0.3 specifies the metadata-query contract your MCP server is the first binding of. The contract was written from your
implementation, so most of it already matches — the gaps are the wire discipline. Current state referenced against
`src/miri_py/mcp/server.py` and `provider.py`.

### 3a. Adopt the surface-owned response envelope (§4)

**This is the load-bearing change.** Today a `tools/call` result's `text` is the raw producer document (or an ad-hoc
`{"error": …}`). The contract requires a surface-owned envelope with the publisher's bytes **nested** under a payload
key, so publisher content can never collide with — or forge — the surface's own signals.

```json
{ "schema_version": "1", "ok": true, "present": true,
  "package": "weather_sdk", "purl": "pkg:pypi/weather-sdk@1.2.0",
  "name": "lifecycle.json",
  "document": { "…the package's lifecycle.json, byte-for-byte…": "…" } }
```

Rules: the surface stamps `schema_version`; it MUST NOT inject envelope fields into the payload, and MUST NOT hoist
payload fields into the envelope. Wrapping matters because the producer schemas set `additionalProperties: false` —
injecting a field would make a conforming document invalid.

Payload keys by operation: `packages` (list), `document` (document / lifecycle / migration-guide), `entries`
(api-index).

### 3b. Split absence from error (§4.2, §4.3)

Today an absent document returns a **success** whose text is `{"error": "no MIRI metadata for …"}` — indistinguishable
from a real failure, with no machine code. Two independent booleans now carry the two axes:

- **Absent** (package ships no such document): `ok: true`, `present: false`, no payload key, plus a free-text `reason`
  for humans. Consumers MUST NOT branch on `reason`.
- **Error** (request could not be served): `ok: false` plus a top-level `error` object, per
  [CLI §2.6](../../../standards/cli/cli-lifecycle-specification.md) — which does include `ok`.

Contract error codes to implement:

| `code` | `retryable` | When |
|---|---|---|
| `PACKAGE_NOT_INSTALLED` | `false` | No installed package provides that import name |
| `AMBIGUOUS_PACKAGE` | `false` | Several installed distributions provide that import name |
| `DOCUMENT_NOT_SERVABLE` | `false` | Requested name outside the §3.2 whitelist |
| `NOT_DISCOVERABLE` | `false` | Could not resolve without importing the package |
| `METADATA_UNREADABLE` | `false` | Document exists but could not be read/parsed |

`METADATA_UNREADABLE` matters: never repair, re-serialize, partially serve, or report-as-absent a document that failed
to parse.

Also: a §4.3 error and a §4.2 absence are both **served answers** — they travel as ordinary tool results carrying the
envelope, never as JSON-RPC protocol errors. Reserve protocol errors for malformed requests (unknown tool,
schema-invalid input), which is what you already do for unknown tools.

### 3c. Add a fifth tool: `miri_document` (§3.2)

This is what makes the Consumption Map executable over a context server. Today four tools serve three documents; the
Map routes agents to `usage-patterns.json`, `api-graph.json`, `AGENT_EXAMPLES.json`, and `agent-metadata/README.md`
too, and none were reachable.

- **Input:** `{ package, name }`. `name` must be one the package advertised in `list.documents`.
- **Servable whitelist:** `lifecycle.json`, `migration-guide.json`, `sdk-manifest.json`, `usage-patterns.json`,
  `api-graph.json`, `agent-metadata/README.md`, `AGENT_EXAMPLES.json`.
- **Never servable:** `prompt-templates.md` (highest-risk injection surface), anything outside `agent-metadata/`,
  anything containing `..` or an absolute prefix. Return `DOCUMENT_NOT_SERVABLE` — never a filesystem error, never the
  file.
- `miri_lifecycle` and `miri_migration_guide` stay as **named shorthands** and MUST return exactly what
  `miri_document` returns for the same package and name.

### 3d. `list` — wrap, cap, identify (§3.1)

- Wrap it: a bare array cannot carry `schema_version`/`ok`, so `list` is currently exempt from the discipline that
  governs everything else.
- Cap it (declare `cap`, set `truncated`), and accept an optional `query` substring — a large environment can hold
  hundreds of metadata-shipping packages.
- Rename the row field `distribution` → **`distribution_name`**. It collided with the CLI `--describe`
  `identity.distribution`, which is an open-source/private *enum* — same name, two meanings, sibling surfaces.
- Add `purl` per row.
- One distribution providing several import packages ⇒ one row each. An import name provided by several distributions
  ⇒ `AMBIGUOUS_PACKAGE`, never a silent pick.

### 3e. `api-index` — presence only (§3.5)

- Put the cap on the wire (`cap`, alongside the existing `truncated`). `MAX_INDEX_ENTRIES = 25` is right; it just needs
  to be visible to the consumer.
- `signature` and `file` are **optional** per entry — the producer's canonical `api_index` does not guarantee either,
  so do not synthesize them.
- Normative framing to carry into any docstring/description: **api-index confirms presence, it can never prove
  absence.** A symbol may be missing because it was capped or query-filtered. Existence is settled by introspecting the
  installed package, never by index membership.

### 3f. Advertise the surface version (§4.4, §6.3)

`initialize` currently advertises only `protocolVersion` (the MCP date) and `serverInfo.version` (the implementation).
Neither names the *contract* version. Add it at the normative path **`capabilities.miri.surface_version`** as a string,
so a client negotiates the metadata contract independently of MCP's protocol date.

### 3g. Invocation log fields (§8)

The log is the H5 instrument, so its fields need to be analysis-ready:

- `operation` MUST be the **contract** operation name (`list`, `document`, `lifecycle`, `migration-guide`,
  `api-index`) — never the MCP tool name, so logs stay comparable across bindings.
- Add `outcome`: `served` | `absent` | `error` (the §4 result class, so reach and success are distinguishable).
- Add `session`: an opaque correlation id, so entries group into runs and treatment arms.
- Unchanged: logging MUST NOT influence any response, and a logging failure MUST NOT break a query.

## 4. Fix the `generate` bugs (blocks the standard's sample gate)

Still open from step-3, and it blocks the standard's CI from moving to the honest
generate → `git diff --exit-code` → build → score loop. Today the gate re-stamps `generated_at` in a temp copy to stay
MIRI-PY-011-fresh, which is a workaround, not the loop §5.4 describes.

- `miri build --generate-metadata` is a no-op.
- `miri generate --output-dir` crashes (`str`/`str`).
- `generate` writes to `src/agent-metadata/` instead of `src/<pkg>/agent-metadata/` for a src-layout package.
- `generate` omits `migration-guide.json`.

## 5. Naming: the reference consumer is `miri consume`

When the reference consumer is built (Pillar 3, not yet started), the subcommand is **`miri consume`**, not
`miri brief`. The naming panel was 5-of-6 against "brief" — it connotes a synthesized digest, which cuts against
declare-sources-not-verdicts, and it shared no stem with its own family (`consumption/`, `[tool.miri.consume]`,
`MIRI-CONSUMER`). Nothing to do yet; just do not build it under the old name.

---

## Suggested order

1. **Item 1** (sync) — 10 minutes, unblocks everything downstream.
2. **Item 2** (tag) — minutes, unblocks the standard's CI pin.
3. **Item 3a + 3b** (envelope + absence/error) — the load-bearing pair; 3b's honest-degradation signal is what all
   consumer conformance will rest on, and 3a is what makes it un-forgeable.
4. **Item 3c** (`miri_document`) — what makes the Map real.
5. **Items 3d–3g**, then **item 4**.

## Open on the standard side (context, no action)

Pillar 3 — the numbered `MIRI-CONSUMER-NNN` checks, the reference consumer, and the paired bare/miri + adversarial
fixtures — is not written yet. Two independent panels have advised building the **fixture before the numbered checks**,
so expect the fixture pair to land first.
