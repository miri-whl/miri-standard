# Response: Substance and Freshness — both defects accepted, the version is wrong, five questions block the rest

*Proposal Version: 0.1-draft*
*Status: Draft — the standard's response to the substance-and-freshness proposal*
*Created: 2026-09-18*
*From: the miri-standard maintainers*
*To: the miri-py implementation team*
*Re: `substance-and-freshness-graduated-scoring.md`*

## Summary

Both defects are real. We verified them against our own checks rather than taking the report, and one of them is
worse than you stated. Ask 5 is adopted and has landed. Asks 1 to 4 are not declined, but they cannot be decided
until you answer five questions, one of which the proposal does not address at all and which determines whether
graduated scoring is a scoring change or a conformance change.

The whole of this is 0.6.0. None of it is 0.5.1, including ask 5 — see §2, where we also record that we first got
that wrong in our own draft.

## 1. Both defects verified

**Presence scores as substance.** Confirmed, and it is sharper than "a document earns its weight by existing".
`MIRI-PY-014` awards **4 weight at MUST** for `examples/quickstart.py` existing, importing its package, and holding
at least one executable statement. `MIRI-PY-037` awards 2 for a `docs/` directory that is not a stub. There is an
anti-emptiness floor and no coverage floor anywhere, so a one-line quickstart and a taught one price identically.
The defect is not that substance is unmeasured — it is that the checklist already draws the line at *non-empty* and
then stops, which is the shape of a rule that was going to be finished later and was not.

**Stale is invisible.** Confirmed. The wheel metadata set has seven schemas and none of them is a changelog, so
there is no artifact for "what was fixed" to live in and nothing that could detect version silence. Your
`MIRI-PY-016` / `030` / `036` citations are all accurate, including that the previous-release machinery your joins
need is already required by `030`.

## 2. The version: all of it is 0.6.0

Your document targets 0.5.1. It cannot be. Graduated scoring moves every conformance score, and a required
`changelog.json` makes every currently conforming wheel non-conforming until it ships one. This repository's policy
is that a patch carries clarifications only, and that a reader should be able to see a patch number and know it
contains no additions without checking.

**Ask 5 is 0.6.0 as well, and our first draft of this response said otherwise.** We filed the pure-function property
as a 0.5.1 clarification on the grounds that all 119 definitions already satisfy it and no score moves. Both are
true and neither is sufficient. It introduces a MUST that narrows what a check definition may be: a `fires_when`
clause resting on model judgment would have validated before and does not now. A rule forbidding something
previously permitted is new even when nobody has yet done it. The supporting argument was also circular — it leaned
on our internal check-authoring guidance as evidence the rule already existed, while citing the absence of any
normative statement as the reason to write one. Recording this because the same reasoning would have let the rest
of your proposal in through the same door.

## 3. Ask 5: adopted

The property is now stated in `fires_when` in `check-v3.json`. One location, not four: it is family-independent, and
copying a global fact into the four Scoring Model sections is how `semantics_version` failed in 0.5.0.

Your "written down nowhere" was exactly right, and more so than you could have known from outside. `fires_when` said
only "the situations in which a conforming linter raises this check". The phrase *mechanically decidable* existed
solely in our internal authoring guidance, which is tooling and not a normative source, so an implementer reading
only the published standard had no way to learn the constraint.

No schema bump. JSON Schema cannot express this, so it binds the check author and the linter and is verified by
review; a consumer holding the previous reading of `check-v2.json` computes identical verdicts and identical
numbers for every definition that declares no `tiers`. Verified before adopting: all 119 active definitions comply.

## 4. Five questions that block asks 1 to 4

These are not rhetorical. We cannot draft checklist text without the answers.

**Q1 — Under tiers, does a partially-earned MUST pass or fail?** The proposal never says, and everything else
depends on it. Today a failing MUST makes the artifact non-conforming and caps the score at 74. Under a tier
schedule a check is no longer a bit: `MIRI-PY-014` is a MUST, and a wheel earning T0+T1 of its four tiers has
neither passed nor failed it. If that is a failure, every wheel in existence becomes non-conforming on the day this
ships, including both of yours. If it is a pass, MUST stops meaning what it means and the 74 cap stops firing for
the checks most worth capping. If the answer is a threshold — MUST is satisfied at T1, tiers above it are score
only — say so explicitly, because that is a third scoring concept and it needs its own name and its own report
field.

**Q2 — What is the calibration corpus, exactly, and can we reproduce it?** You offer "our five-wheel corpus plus
both of our own wheels". If the five are the ones in `0.5.0-measured-rerun.md`, then three are Google or gRPC
packages and two are yours, and floors derived from seven artifacts by percentile are not calibration. We would
need the wheel list, the probe that produces each countable, and the raw measurements, so the floors can be
recomputed by someone who does not have your laptop.

**Q3 — Do tiers apply to all four families or only `python-wheel`?** Every tier table in §3 is a wheel document.
The CLI, surface and consumer families have substance-bearing checks too. If tiers are wheel-only, the standard
grows two scoring models and a score stops being comparable across targets.

**Q4 — Is `changelog.json` required unconditionally?** A first release has nothing to describe, and `030` and `034`
are already `conditional` for exactly that reason. State whether the document is required always, required from the
second release, or conditional on a measured delta existing.

**Q5 — Confirm the tier-forfeit consequence.** You say a missing tool forfeits the affected tier rather than
passing it, which is right and matches 0.5.0. Then note where it lands: a forfeited MUST leaves conformance
**undetermined**. A linter without Sybil forfeits T1 on the docs family, and if docs checks are MUSTs, every such
linter reports `undetermined` for that family forever. Is that the intent? We think it may be, and that it is
defensible, but it should be chosen rather than discovered.

## 5. Three objections

**The floors are the weakest part and you know it.** §4 says numbers invite gaming and taste, then sets them from a
corpus of seven. The anti-gaming argument is good — a countable must clear T1, so a call-everything script has to
actually run — but it addresses gaming, not calibration. See Q2.

**The tier shares are asserted.** 20/30/30/20 arrives with no derivation. You flag them as committee numbers, which
is honest, but it means a scoring change ships with four constants nobody can defend from evidence. We would rather
adopt tiers with shares stated as provisional and revisited against the corpus than pretend the split is measured.

**`MIRI-PY-016` cannot be "absorbed".** §3 folds it into an examples tier. Check IDs are stable forever here; a
check leaves by being marked `withdrawn` with `withdrawn_in` set and its weight redistributed in the same change,
keeping its file and its ID. Absorption would silently delete an ID that linters and reports reference. If the join
016 performs belongs in a tier, then 016 is withdrawn and the tier takes its weight, and both halves happen
together.

## 6. What we are not arguing with

The self-demotion. "Our own flagship would earn T0+T1 and fail T2, a score we consider correct and accept publicly"
is the right posture and it is the reason this proposal reads as an argument rather than a pitch. A proposal that
priced its authors' artifact higher would have earned the suspicion you named.

The forfeit-rather-than-pass treatment of missing tools, which independently reaches the rule 0.5.0 arrived at from
the capability direction. And the insistence on determinism, which is why ask 5 went first.

## 7. What we need back

1. Answers to Q1 through Q5, Q1 above all.
2. The corpus, probe and raw measurements behind the floors.
3. Your view on `MIRI-PY-016`: withdrawal with redistribution, or leave it standing outside the tier schedule.
