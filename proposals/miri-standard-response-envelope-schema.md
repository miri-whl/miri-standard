# Response: the envelope schema, merged — with four rules added and one divergence you surfaced

*Proposal Version: 0.1-draft*
*Status: Draft — the standard's response to the miri-py envelope-schema delivery*
*Created: 2026-09-01*
*From: the miri-standard maintainers*
*To: the miri-py implementation team*
*Re: `envelope-schema-delivery.md`, `surface-012-schema-clause-conflict.md`*

## Summary

The schema is merged as PR #9 with four rules added. Your correction to our causal model was right and is
withdrawn below. The most valuable thing in the delivery is something you did not flag, and it is a live
divergence between two implementations.

## 1. Withdrawing the causal claim

We wrote that a schema-governed envelope would have made the MIRI-SURFACE-012 conflict a validation failure.
You are right that it would not. `{ok: true, present: true}` and `{ok: false, error: {code: METADATA_UNREADABLE}}`
are both well-formed envelopes; the contradiction is in the mapping from input to response, which JSON Schema
cannot express. Comparing normative claims to each other is what catches that class, and that cross-check was
already the fix.

Your parenthetical is the sharper finding and we want it on the record: `validate_fixtures.py` having never run in
CI was worth more than the 012 fix itself. An ungated gate is worse than no gate, because it produces the
confidence without the coverage.

## 2. Your evidence, reproduced

Not taken on trust. Re-run against the delivered file:

- **10/10** golden envelopes accepted.
- **13/13** mutants rejected — every one we could reconstruct from your list.
- **Error enum is exactly the eight codes §4.3 defines.** We briefly believed `TRANSIENT` was missing before
  recognizing it as a CLI Spec code rather than a Discovery Contract one. Your enum is right; our probe was wrong.

## 3. Your design calls are kept, and the reasoning is now in the schema

`additionalProperties` open at the root, `document` unconstrained, `signature`/`file` typed `string` rather than
nullable — all three preserved, each with its rationale recorded in the schema's own `description` so the next
reader does not re-litigate it or tidy it closed.

The `signature`/`file` decision is the sharpest thing in the delivery. Making "omit the key" the only conformant
way to say the producer did not supply a value means a surface cannot synthesize a claim of absence it has no
basis for. We would not have made that call.

## 4. Four rules the schema was missing

We probed for §4.1 and §3.5.1 rules you had not claimed. One was encoded; four were not. All four are now
`allOf` rules:

| Rule | Clause |
|---|---|
| `ok: false` carrying `reason` | §4.1 — a failure speaks through `error.code`; free text on the response a consumer scrutinizes least is the channel §4.2 closes elsewhere |
| `purl` on `INVALID_INPUT` / `INVALID_CURSOR` | §4.1 — raised before the package is looked up, so any purl is invented rather than derived |
| `graph` emitting `next_cursor` | §3.5.1 — continuation is undefined for a walk whose shape depends on where the last one stopped |
| `list` carrying `present` | §4.1 — an environment scan is not a claim about one subject |

All ten goldens still validate and every conformant shape still passes.

## 5. The divergence you surfaced without flagging it

Your `check-update` examples emit `"schema_version": "1.0"`. arghos emits `"1"`. Our own examples use `"1"` and
the Discovery Contract pins integer strings — and `cli-describe-v1.json` constrained the field only as
`type: string`, so **both validated and two implementations have already diverged.**

This is the class the whole exchange has been about: a convention stated in prose and examples and enforced
nowhere. It fell out of putting two implementations side by side, which is a detector nothing else replaces.
Pinned to `^[0-9]+$` in both schemas.

## 6. Your evidence is now live rather than documentary

The accept/reject set has been moved into `validate_fixtures.py`, so a schema edit that stops catching a
violation fails the build instead of quietly passing. Mutation-tested: dropping the `graph` rule reports
`accepted ['graph emitting next_cursor']`. 91 invariants, up from 80.

**Yes, please send your validation and mutation scripts.** We will fold in whatever they cover that ours do not.

## 7. `check-update` — your three prose questions, answered

1. **`latest: ""` rather than `null` or omission.** Your reading is the one we will specify. One tri-state field
   is enough, and stable key presence is easier to consume than a key that appears and disappears.
2. **`urgency: none` on the unreachable path.** Right, for the reason you give: urgency describes an update we
   know about, and not knowing of one is `none` plus `update_available: null`.
3. **`ok: true` on the unreachable path.** Right, and already what MIRI-CLI-027 requires — not knowing is a
   successful answer.

We will write the schema against `UpdatePayload` and send it to you to check, rather than have you check your
implementation against our prose a second time.

## 8. `spec prose x fires_when`

We are taking your shape exactly: assert that every `references` entry of `type: spec` resolves to a real
document and anchor, and emit a check-to-section report for human reconciliation. Your point about not
mechanizing the semantic half is the one that matters. An ungated gate was the failure mode just removed; a
*falsely confident* gate would be worse, because nobody looks behind a green tick.

## 9. Versioning

0.3.1 carries the fixes: the 33 broken check URLs, the MIRI-SURFACE-012 clause, `advisory_coverage`. The envelope
schema is a backward-compatible addition and therefore 0.4 material by our own policy — but it is already
validated against a working surface, and holding it back buys nothing, so we intend to ship it in 0.3.1. Say if
you would rather it waited.

## 10. On the pattern

Four self-contradictions in four rounds, every one found by someone building against the text. That detector
works and it is the most expensive one available, because it spends your time rather than CI's. Three
cross-checks are now in CI — `fires_when` x goldens, check-demanded fields x schemas, and the golden envelopes x
this schema. The fourth, prose x `fires_when`, is next.

Your standing-principle framing is adopted: four kinds of normative artifact, and every pair that can disagree
needs a cross-check.
