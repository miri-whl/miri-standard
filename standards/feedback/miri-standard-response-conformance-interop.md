# Response: A Shared Conformance Kernel (0.1)

*Response Version: 0.1*
*Status: miri-standard maintainers' response*
*Created: 2026-09-17*
*In reply to: [conformance-interop-contract-proposal.md](conformance-interop-contract-proposal.md)*

Two of the four asks are accepted, one is accepted in a narrower form than requested, and one is deferred with a
reason. Before any of that, a correction to your scorecard, because it changes the numbers you published and it is
the standard's own rule doing the work.

## 0. Your three behavioural families are `undetermined`, not "N pass / 0 fail"

Your §4 is right and you implemented it: a check with no rule file forfeits its weight rather than passing. But the
scorecard in §6 then reports the outcome as `24 pass / 0 fail`, `12 pass / 0 fail`, `15 pass / 0 fail`. Under 0.5.0
those families have no grade at all.

A forfeited MUST does not cost weight — it removes the verdict. `lint-report-v1.json` is explicit: `undetermined`
is the grade "where a MUST check was FORFEITED — the obligation applied and went unassessed, so the artifact is
neither known to conform nor known to fail." A missing rule file is the definition of that case: the obligation
applies, and nothing assessed it. It is a forfeit, not an exclusion, because exclusion requires the condition
provably not applying.

You do not need to tell us which checks you skipped for this to follow. It is arithmetic:

| Family | Active checks | of which MUST | Your rules | Uncovered | Uncovered MUSTs, at minimum | Verdict |
|---|---:|---:|---:|---:|---:|---|
| `cli` | 43 | 36 | 24 | 19 | 12 | `undetermined` |
| `surface` | 18 | 18 | 12 | 6 | 6 | `undetermined` |
| `consumer` | 18 | 17 | 15 | 3 | 2 | `undetermined` |

Even if every SHOULD in a family were among the checks you did not cover, there are not enough SHOULDs to absorb the
gap. `surface` is the starkest: all 18 of its checks are MUST, so all 6 uncovered ones are MUSTs.

This is not a scolding about presentation. It is the same defect the whole exchange has been about, arriving one
level up: you built the mechanism that prevents a number from overstating what was verified, and then reported a
number that overstates what was verified. `0 fail` and `no MUST unassessed` are different claims, and only the
second one licenses a grade.

It also sharpens your ask 2, which we are accepting — see below.

## 1. Ask 2 — driver semantics, stated normatively: accepted

This is the ask closest to what the standard already owns, and 0.5.0 built most of the vocabulary for it:
`excluded` versus `forfeited`, `scores.effective_denominator`, `scores.undetermined`, and the
not-applicable-is-not-a-pass rule. Your §4 is the same principle applied to a source of ignorance we had not named.
0.5.0 scoped forfeiting to *capability* gaps — no network, no previous release, execution disabled. Yours is an
*implementation coverage* gap, and it forfeits for the same reason: the obligation applied and nothing looked.

What we will state normatively goes one clause further than you asked, per §0:

1. Every defined check in a family reports an outcome. No check is absent from the report.
2. A check the implementation does not verify is **forfeited**, never passed, and never excluded.
3. A forfeited MUST makes the family verdict `undetermined`. Forfeiting is not a discount on the score; for a MUST
   it withdraws the grade.
4. A rule that cannot execute fails loudly at load or run time.
5. Coverage is reported per family, and every uncovered check carries a named blocker.

Point 3 is the one that makes a coverage percentage comparable, which is what you said you wanted from this ask. A
standard that let an implementation forfeit MUSTs and keep a grade would be handing out exactly the incomparable
number your §7 rule was written against — a score that does not vary across artifacts that plainly differ.

## 2. Ask 1 — adopt `rule-v1` and `operators-v1` as standard-owned: not yet, and here is the test for when

Declining the artifact, not the idea. Two reasons, both from your own measurements.

**The vocabulary does not reach the founding family.** Your §3 is the most valuable paragraph in the proposal: you
tried to migrate `python-wheel` and found 36 of its 40 checks irreducibly computational. We accept that finding
without re-litigating it. But it means an adopted operator vocabulary would be normative for three families and
inert for the one carrying the most weight, while looking uniform from outside. What you actually demonstrated is
shareable there is the *obligation manifest* — the named binding per native rule — which is a different artifact
from an operator grammar and a better one to standardize first.

**A vocabulary frozen at half coverage gets worked around rather than grown.** By your own table the four operators
cover 51 of 79 behavioural checks, and the remaining 28 need three operator classes that do not exist. If the
standard blesses the grammar now, the first implementation to need key-set closure has a choice between waiting for
the committee and reaching for `native`. It will reach for `native`, and `native` will become the escape hatch your
§3 correctly insists it is not.

So: we will publish the rule corpus and both schemas as a **versioned reference artifact** alongside the check
definitions — cited, diffable, and safe for a second implementation to build against — but not as a normative
interop contract. The test for promotion is your ask 4: when the three missing operator classes exist and the
behavioural families are covered without `native` standing in for a missing operator, the grammar has been shown to
be complete enough to freeze, and we will freeze it. Our schemas would also need their `$id` rebased; see §5.

## 3. Ask 3 — fixture wheels: recipe blessed and checksummed, binaries not shipped

Blessing the recipe is correct and cheap, and you have already done the hard half by mirroring
`examples/fixtures/build_fixtures.py` exactly, byte-identity check included. We will make that recipe normative for
fixture construction and add a checksum manifest so two implementations can prove they built identical bytes.

We will not ship prebuilt wheels. The standard's own position is to declare sources rather than verdicts, and a
published binary is a verdict about bytes you did not build — it is also a distribution channel we would have to
secure, for a project whose Lifecycle and Security Metadata §9.4 argues that authoritative-looking artifacts are a
better target than plain ones. A recipe plus a checksum gives you the identical-bytes guarantee without either.

## 4. Ask 4 — the three missing operator classes: accepted as the roadmap

Accepted, and one of the three is less speculative than you present it. **Multi-invocation comparison** is already
required by our side: `tools/score_cli_linter.py` grades a linter against paired arms and rejects a submission with
no control arm, and the consumer profile drives each check against a hostile arm and a control. So the standard
already demands a comparison your grammar cannot express, which makes that operator class a defect in the
vocabulary rather than an enhancement to it. We would put it first.

Key-set closure and process observation we take as stated.

## 5. Two corrections in the delivered material

**Your §5 divergence does not hold at the commit you pinned.** You report that the goldens carry `package_kind` and
a distribution name while `agent-event-v1` "takes an import name and closes `subject`", and that your trigger rules
therefore use import names. The schema does close `subject`. It also carries `package_kind` as an
`import | distribution` enum, and the goldens exercise both arms — `greet-bare` as `distribution`,
`greet_adversarial` as `import`. That field was added in 0.5.0 and did not exist at 0.4.0, so the divergence was
fixed by `6f4493c3` itself, the commit you pinned at. Your trigger rules can carry distribution names today. This
is a loosening available to you, not a change we need to make.

**Both delivered schemas carry `$id https://miri-standard.org/schemas/...`.** That domain does not exist and is
explicitly disallowed in this repository; all fourteen schemas here use `miri-whl.github.io`. It costs nothing now
and would be a published-identity break later, so it wants fixing before anything validates against these files.

## 6. What we need from you

1. **Re-report the three behavioural families with their real verdicts.** `undetermined` with a named coverage
   figure is a more useful number than `0 fail`, and it is the one your own §4 implies.
2. **Rebase the two `$id` values** onto `miri-whl.github.io` if you want them published as reference artifacts
   under that name.
3. **Confirm the forfeit taxonomy matches your implementation** — specifically that you forfeit rather than exclude
   a check with no rule file, since the two have identical arithmetic and different meanings, and only exclusion is
   permitted to leave a MUST without a verdict.
4. **Name which of the three operator classes you would build first** if we sequence ask 4 together. We would start
   with multi-invocation comparison for the reason in §4.

One thing worth saying plainly: your rule corpus is now the largest body of executable verification that exists for
this standard. Ours is 11 CLI goldens, 14 consumer goldens and 8 event traces; 361 of 400 weight has no test
material on our side at all. The disagreement in §0 and §2 is about what may be frozen as normative, not about the
quality of the work — and on the substance, the layer separation in your §1 is the right shape.
