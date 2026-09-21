# Response: the `compare` operator — shape accepted, and one rule in it is vacuous

*Response Version: 0.1*
*Status: miri-standard maintainers' response*
*Created: 2026-09-20*
*In reply to: `multi-invocation-comparison-operator-draft.md`*
*Pinned at: `a769e50` (0.6.0 on `main`)*

The shape is right and we would adopt it close to as drafted. Your five questions are answered in §6, all five
favourably. Before them, three findings from drafting your rules against our definitions — one of which says a rule
in §4 passes on a subject that does nothing, and one of which is a defect in *our* check rather than your rule.

## 1. The `CONSUMER-051` rule is satisfied by a consumer that never fires

Your rule captures `ok` from both arms and asserts `equal`. Look at what the correct behavior actually is, from the
`E3` golden that mandates it:

```text
adversarial arm:  ok: true, present: true,  findings: [ exactly one, level must ]
miri arm:         ok: true, present: false, reason: "...task 3.5 found nothing to report"
```

`ok` is **true on both arms**. So `equal: [conforming.responded, adversarial.responded]` holds for the correct
behavior — and it also holds for a consumer that emits nothing at all, because both captures bind the absent
sentinel and absent equals absent. A dead subject passes. So does one that answers both arms with an error envelope,
since `ok: false` on both is equal too.

This is the vacuous pass, arriving in a rule file. It is the same shape our own `A13` had and the reason `E3` exists:
a negative assertion is not a discriminating test. `E3` fixes it by pairing a *required positive* envelope on the arm
carrying the bid with a *required absent* shape on the control, and it carries `assertions` and
`what_this_pair_discriminates` for exactly that purpose — neither arm decides it alone.

The fix is inside your grammar, which is why we think the grammar is right: arms already carry their transport's
`expect`, judged per arm. The rule needs both halves — per-arm anchors *and* the cross-arm comparison:

```yaml
  arms:
    - name: adversarial
      argv: [trigger]
      stdin: '{"schema_version":"1","kind":"dependency.add","phase":"after",
               "subject":{"package":"greet-adversarial","package_kind":"distribution"}}'
      expect:
        stdout_json:
          ok:               { eq: true }
          present:          { eq: true }
          findings[0].level: { eq: "must" }
      capture:
        responded: { stdout_json: "ok" }
    - name: conforming
      argv: [trigger]
      stdin: '{"schema_version":"1","kind":"dependency.add","phase":"after",
               "subject":{"package":"greet-miri","package_kind":"distribution"}}'
      expect:
        stdout_json:
          ok:      { eq: true }
          present: { eq: false }
          reason:  { exists: true }
      capture:
        responded: { stdout_json: "ok" }
  compare:
    - equal: [adversarial.responded, conforming.responded]
```

Generalized, and we would want this normative in §3 rather than left to rule authors:

> **A `compare` rule MUST anchor at least one arm with `expect`.** Comparison alone relates two subjects to each
> other and neither to the standard, so a rule made only of `compare` assertions is satisfiable by a subject that
> produces nothing. This is the rule-file form of the vacuous pass.

It is the same discipline our CLI harness enforces from the other side: `tools/score_cli_linter.py` rejects a
submission with no control arm *and* rejects an inert one that reports nothing. Your operator supplies the control
arm the grammar was missing; the anchor is what keeps the pair from being inert.

Your `package` values, incidentally, validate as written — we ran both events against `agent-event-v1`. Note that
the goldens send `greet-adversarial` with `package_kind: distribution`, while your draft sends the import name
`greet_adversarial` and relies on the schema default. Both are legal; the distribution form is what `E3` uses, and
it is the harder path for a consumer, since the name must be joined through the installed distribution's metadata.

## 2. Two of the four checks need an `env` the grammar does not have

`compare` as drafted closes the *first* `fires_when` clause of each of your four. It cannot close these:

| Check | Clause it cannot reach | Why |
|---|---|---|
| `MIRI-CLI-012` | *"Output ordering changes with the locale environment"* (`LC_ALL`, `LC_COLLATE`) | needs two arms differing **only** in environment |
| `MIRI-SURFACE-031` | *"Entries are ordered by locale collation rather than Unicode code point"* | same |

Your §3 says arms run "in the same environment", deliberately, and `operators-v1.json` has no `env` anywhere — we
checked. That is the right default and the wrong absolute: these two clauses are *about* environment sensitivity, and
they are the clauses that catch the real defect, since a tool that sorts by locale collation orders identically on
two runs in one environment and wrongly the moment the reader's locale differs.

We would add a per-arm `env` mapping, string to string, applied over the inherited environment, with no
interpolation and no removal. That stays declarative — it is data, not control flow — and it is the smallest addition
that makes the two clauses expressible. If you would rather it wait for a separate class, say so; but then neither
check is closed, and the ledger should say that rather than counting them.

## 3. Clause-level coverage, and what your driver semantics say about it

This follows from §2 and is the more structural point. Two more clauses are not comparison problems even with `env`:

- `MIRI-SURFACE-031`: *"A listing operation orders by a key other than the one §3.5.1 assigns it"* — one request,
  judged against a key the specification assigns. Single-invocation; it needs no second arm.
- `MIRI-CLI-012`: *"Array order tracks map/hash iteration or directory-read order rather than a documented sort key"*
  — two runs in one process can be stably wrong, so comparison cannot see it.

So a rule that closes clause 1 leaves the check partly verified. Your driver semantics, which we adopted verbatim
into `scoring-v1.json` `conformance.coverage`, say a check the implementation does not verify is forfeited and never
passed. They say nothing about a check the implementation *partly* verifies — and a rule file existing is what makes
the difference between `not_implemented` and a pass. A rule covering one of three clauses currently reports pass.

That is the vacuous pass one level up again, and we would rather name it now than after the grammar is normative. Two
options, and we prefer the first: a rule declares which `fires_when` clauses it covers, and a check with uncovered
clauses reports `not_implemented` with the clause numbers as its `blocker`; or clause coverage stays editorial and
the ledger counts clauses rather than checks. Either way the honest count for `compare` is **four checks' first
clauses**, not four checks.

## 4. A defect in our check, not your rule

Your rule faithfully implements `MIRI-CONSUMER-051`'s `fires_when` clause 1, which reads *"emits a response for one
arm and NO RESPONSE AT ALL for the other"*. That clause is weaker than the `E3` golden it points at: `E3` requires a
specific positive envelope and a specific absent one, and the clause requires only that the two arms agree on
whether anything came back. The rule is vacuous because **the clause is**, and drafting the rule is what exposed it.

We will strengthen clause 1 to name the two envelope shapes `E3` already mandates, so that a rule implementing the
clause literally is a discriminating rule. That is our fix, in a later release; we record it here because you would
otherwise have implemented ours and inherited the hole.

## 5. The re-clustering: agreed, both of them

`MIRI-CLI-007` — its `fires_when` is *"`<cli> list | head -1` leaves a traceback"* and *"the tool's exit after a
closed pipe reflects an internal crash rather than clean termination (a plain SIGPIPE death is acceptable)"*. That is
a downstream reader closing the pipe and an assertion about signal disposition. Process observation, as you say.

`MIRI-CLI-024` — artifact inspection (`go version -m`, a `.dep-v0` section) plus a resolvable `identity.sbom`, and
its first clause is a scope test that makes it conditional before it is anything else. Not comparison.

Correcting a ledger downward before a grammar freezes on it is worth more than the operator.

## 6. Your five questions

1. **`via` reusing the transport's grammar — yes.** The alternative duplicates the arm grammar per transport and
   duplicates it again for the third. `MIRI-SURFACE-031` being the same obligation shape as `MIRI-CLI-012` over a
   different transport is the argument, and it is a good one.
2. **Four assertions is the right closure — yes.** Keep predicates out; each one is a step toward a rule that
   computes, and a rule that computes is a second implementation nobody reviews. What is missing is not a fifth
   relation but the per-arm anchor of §1, which is not a comparison at all.
3. **`[*]` is acceptable — yes**, as projection, not iteration, and not nestable. It is not key-set closure: that
   class is about the *set of keys* a document carries, this is one field across an array. Your reason is the right
   one — a rule that compares raw stdout reports "these two strings differ", which tells a publisher nothing.
4. **The re-clustering — agreed**, see §5.
5. **Two-stage arm validation — yes, and make the second stage fail-closed.** One operator per transport-shape is
   worth the cost. But `additionalProperties: false` cannot close an arm in pass one, so pass two must reject an
   unknown key rather than ignore it; otherwise a typo in `argv` validates and the arm runs with a default. Our own
   rule applies: where a schema cannot express a guarantee, say so and enforce it elsewhere, rather than implying
   the schema covers it.

## 7. What we ask back

1. The `CONSUMER-051` rule re-drafted with per-arm `expect`, and your view on making the anchor rule normative.
2. A decision on per-arm `env`: add it now, or drop the two locale clauses from what `compare` claims to close.
3. Your preference between the two clause-coverage options in §3. You are the implementation this lands on.
