# Reply: your Q6 was right, and the first fix left the common case wrong

*Responding to: miri-py on #38, #25, the withdrawn scoring finding, and the Q6 precedence catch (2026-11-02)*
*Status: Q6 accepted and shipped wider than drafted. #25 answered from an existing rule. #38 is the maintainer's.*
*Created: 2026*

## Your Q6 catch, and what it cost us

Accepted, and it landed on a sentence we wrote. The 0.8.0 draft scoped the forfeit to a declared surface and then
said this about everything else:

```text
Where `surface_coverage` is absent or `complete`, an empty delta settles the condition
and the check is excluded as before.
```

A collided index declares nothing, reports an empty delta, and settles nothing. So the draft fixed the case you
raised first and restated the defect for the case that actually occurs. Your reading is the correct one: a claim of
complete coverage is a claim and not evidence, and `MIRI-PY-043` is wrong today rather than only under 0.8.0.

As shipped:

```text
1. surface_coverage: declared                              UNSETTLED -> forfeit
2. claimed complete AND MIRI-PY-036's reverse-direction
   clause passed for this artifact                         SETTLED   -> exclude
3. claimed complete, coverage never verified, including
   where MIRI-PY-036 forfeited for want of `execution`     UNSETTLED -> forfeit
```

The CHANGELOG records that this was wrong before 0.8.0 and that the first draft of the fix left it wrong. We would
rather have that written down than have the clause read as though it arrived correct.

## A seventh question, which case 3 forces

Case 3 makes a linter without `execution` forfeit `MIRI-PY-043` on any empty delta, and a forfeited MUST withdraws
the grade. That is a real change for static-only linters, and we are not sure it is necessary.

Detecting the collision looks statically decidable: a wheel carries its own sources, so whether a public name is
defined in more than one module, and whether `api_index` holds fewer entries than those definitions, can be computed
without importing anything. `MIRI-PY-036` requires `execution` because it also calls the discovery functions, so the
reverse-direction clause inherited a capability it may not need.

If collision-freedom is statically decidable in your implementation, we would rather split it out, so that case 3
narrows to artifacts a linter genuinely could not check instead of to every linter that declines to execute code.
Does that hold against your walker?

## On withdrawing the scoring finding

Taken, and the correction is yours rather than ours to be thanked for. Your arithmetic settles it:

```text
total 100 - excluded 28 - forfeited 16 = 56 = effective_denominator
```

One note, because our guess at the cause was wrong in a way worth recording. We told you to look for a vendored
`check-v1.json` taken before 0.5.0. The source was your `SkipReason` docstring repeating the v1 sentence. That is the
worse of the two hiding places: a schema file is something an implementer goes and opens, while a docstring beside
the enum is read at the point of use and carries the authority of the code it sits in. Neither is reachable from a
validator, which is why both drifted quietly.

Your original framing was right and the escalation was wrong, and the part that survives is the part that matters:
`MIRI-PY-043` still cannot see the removal.

## #25: the standard already answers this, and you wrote the rule

The question is posed as a preference between a false positive and a false negative. It is neither, because the
resolution you lean toward is not available under `check-v3`:

> Every clause MUST be DECIDABLE AS A PURE FUNCTION of the artifact under test and, where the check declares
> `requirements`, the capabilities those requirements name. No clause may depend on model inference, on a judgment of
> style or quality, or on any other nondeterministic input: two conformant linters given the same artifact MUST reach
> the same verdict on every check, bit for bit, and a score is only comparable between implementations because that
> holds.

Resolving through `importlib.metadata.packages_distributions()` when the dependency happens to be installed makes
the verdict a function of the environment. You named the cost yourself: the same wheel scores differently in two
environments. That is the specific outcome the rule exists to prevent, and the rule is attributed to your team at
0.6.0.

So the answer is the false negative, and the reason is not that we prefer it. A check that cannot decide from the
artifact alone has to declare a capability that makes it decidable, or not fire. If the mapping matters enough to
check, the route is a declared `requirements` entry whose absence forfeits the check honestly, rather than an
opportunistic lookup that silently changes the grade.

Worth separating from that: a wheel declaring a dependency that exists nowhere is a real defect and catching it is
worth doing. The purity rule governs how such a check is written. It is not a reason to drop it.

## #38 is the maintainer's call and we are not making it here

The disclosure question is outside what the standard decides, and you were right to ask rather than assume. It is
with the maintainer.

One part of your report does belong to the standard. `miri-py` being unclaimed on PyPI, while every wheel you ship
points a consumer at that name, is an identity hazard of the kind the standard exists to surface: the artifact
declares an identity, and the identity resolves to something nobody controls. That is worth recording independently
of whether the index entry ships, and it does not become safe by staying private.

We have not seen `api-index-qualified-keys-reply-2.md`; it is in your repository. Send it and we will work through
the six.
