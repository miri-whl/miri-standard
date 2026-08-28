# Feature request: a status header on the review report

**To:** the arghos maintainers
**From:** the Miri Standard maintainer
**Evidence:** three `miri-v03` runs — `20260824-025336`, `-052817`, `-054403`

## The gap

Reading a review report, there is no way to tell **where we stand**. The verdict is there, and the findings are
there, but the question a maintainer actually opens the report with — *is this better or worse than last time, and by
how much* — takes running `review-compare` separately and reading counts out of two JSON files.

That should be at the top of the report. We agree with the need.

## What it should not be

Our three runs make a specific argument against the obvious answer, which is a single quality score.

```text
run 1 (0.2.0)  must 19 ███████████████████       should 13 █████████████
run 2 (0.2.1)  must 22 ██████████████████████    should 19 ███████████████████
run 3 (fixed)  must 10 ██████████                should 28 ████████████████████████████

must-fix    19 → 22 → 10   halved
should-fix  13 → 19 → 28   more than doubled
kept total  40 → 45 → 43   flat
```

Between runs 2 and 3 we fixed twenty real defects. Must-fix halved — and should-fix more than doubled, while the
total held flat. **The findings did not disappear; they were reclassified downward.** That is a genuinely good
outcome and it is also not the outcome "twenty defects fixed" would predict.

A single number would have moved up and hidden all of it. Worse, it would have hidden the more uncomfortable
observation:

**Total findings stayed flat across a document that measurably improved.** Three runs, 40 / 45 / 43 kept findings,
against a corpus that gained twenty fixes in between. That suggests finding *volume* is closer to a property of the
panel's output rate than of the document under review. If that holds up, **count is not a quality signal at all** —
only the severity distribution and *which specific* findings persist carry information. A score built on volume
would be measuring the tool.

## What we would put there instead

A status header, four lines, no invented arithmetic:

```text
┌ miri v0.3 consumption suite ─────────────────── arghos 0.2.1 ─┐
│ VERDICT   complete-with-fixes        (was: complete-with-fixes)│
│ SEVERITY  must 10 ▼12   should 28 ▲9   noted 6 ▬              │
│ MOVEMENT  34 closed · 32 new · 11 persisting     vs -052817    │
│ CONFIDENCE 6 unlocatable quotes · 11 fact conflicts · 6 lenses │
└────────────────────────────────────────────────────────────────┘
```

Four things, each already computed and none of them a new judgment:

1. **Verdict, with the previous verdict beside it.** The single most useful number in the report is the one you
   already produce; it just needs its predecessor next to it.
2. **Severity distribution with deltas.** This is where the real signal lives, and it is what a single score
   destroys. `must 10 ▼12` alongside `should 28 ▲9` tells the whole reclassification story in one line.
3. **Movement**, from `review-compare` when a prior run exists. Today this requires a second command; it is the
   thing a maintainer wants first.
4. **Confidence signals**, which you already compute and print at the bottom. `6 unlocatable quotes · 11 fact
   conflicts` belongs at the *top*, because it is how much of the report to trust before reading any of it.

`--json` should carry the same block as a `status` object, so this is scriptable and not only human-readable.

## On the graph

A sparkline of **must-fix across runs** is the one time series worth plotting, for the same reason: it is the number
a maintainer manages by. `must 19 ▁ 22 ▂ 10 ▁` in the header, and the full series in the HTML report, would have told
us in one glance what we only learned by writing a script.

We would **not** plot total findings. Per the flatness above, that line would look like progress or regression at
random.

## One caution, since you will be tempted

Whatever goes in the header will be read as a score, whether or not you call it one. `must 10` at the top of a page
becomes "we are at 10" in someone's status update by the end of the week. The mitigation is not to omit the number —
it is to keep the confidence line **adjacent to it**, so that "10 must-fix" is never seen without "6 unlocatable
quotes, 11 fact conflicts" in the same glance. A number with its error bars attached survives being quoted; a bare
number does not.

That is the same reason your run output already prints the unverified-quote warning rather than silently dropping
those findings, and it is the right instinct to carry upward.
