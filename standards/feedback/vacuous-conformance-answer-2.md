# Answer: Vacuous Conformance, second round

*Answer Version: 0.1*
*Status: Draft — miri-py's reply to the second-round answer*
*Created: 2026-09-10*
*In reply to: [miri-standard-answer-vacuous-conformance.md](miri-standard-answer-vacuous-conformance.md)*

Two asks. The second is settled here; the first is committed to, with the
prediction written down first so measurement can contradict it.

## 1. The pin format after the tag — pin the sha, name the tag

Settled, and we think it is already settled by the field's own name.

**`checks_commit_sha` takes a commit sha.** A tag is a movable label; a
sha is not. The whole point of the field is that a reader can fetch the
exact definitions a score was computed against, and a tag that is moved
after the fact — even by accident, even by a re-tag during a release —
silently changes what a published report points at. Putting a tag in a
field named `commit_sha` would also be the defect class this whole
exchange is about: a name that says one thing and a value that is
another.

**The tag belongs in `checklist.standard_version`.** We added that field
this week for an adjacent reason — the report named `0.2-draft` (the
checklist stamp) and never named `0.4.0` (the release), so a reader
could not tell which MIRI version a report was scored against. It is
read from the standard's own `website/site.yaml` at the pinned commit,
so once there is a tag it will carry `0.4.1` without any change on our
side.

That gives every report both halves, each in the field that matches it:

```text
Standard   MIRI 0.4.1                      ← human-legible release
Checklist  0.2-draft, definitions at 8dc2d49   ← immutable pin
```

**What we do at sync time.** `scripts/sync_checks.py` will accept a tag
as its `--sha` argument, resolve it to the commit it points at, and
record the sha. The tag is an input; the sha is what is recorded. That
way a re-pin can be requested by release name without the recorded
provenance ever being movable.

One note on the schema, since it is an interop detail: `lint-report-v1`
constrains `checks_commit_sha` to `type: string` with no `pattern`. If
you want the sha-not-tag rule to be machine-checkable rather than
conventional, a `pattern` of `^[0-9a-f]{40}$` would do it, and we would
welcome it. We are not asking for it — a convention both sides follow is
enough — but a schema that permits a tag will eventually be given one.

## 2. The measured re-run — committed, and predicted first

Yes. We will re-run the proposal's §1 table and report measured numbers,
and we would rather do it against a merged tag than against a branch, so
it happens once.

To make it worth reporting, here is the prediction on record **before**
measuring. If the measured numbers differ, the difference is the finding
and we will say so rather than quietly reconciling.

### The redistribution balances

Gating `MIRI-PY-001`–`003` frees **6** points; the specified
redistribution places **6** (`007` +2, `008` +2, `014` +1, `015` +1).
The scored set after gating is worth exactly **100**. Confirmed against
the vendored definitions.

### Predicted, for the five wheels in §1

| Package | Today | §4 only | §3 + §4 |
|---|---:|---:|---:|
| miri-py | 79/100 | 100% | **100%** |
| patitur-sdk-api-client | 47/100 | 43% | **35%** |
| google-ai-generativelanguage | 40/100 | 30% | **20%** |
| google-api-python-client | 40/100 | 30% | **20%** |
| grpcio | 36/100 | 28% | **19%** |

### Category A's constant share — the number your ask names

| Package | Fixed 100 | §4 only | §3 + §4 |
|---|---:|---:|---:|
| the four pure-Python wheels | 8.0% | 14.3% | **3.6%** |
| grpcio (larger denominator) | 8.0% | 13.3% | **3.4%** |

**3.4–3.6%**, against your "near 4%". If measurement lands there, the
prediction survived; if it lands at 14% the gating did not take effect,
and if it lands near 8% the renormalization did not.

### Two things the prediction exposes that we had not seen

**The spread narrows at the top, not just widens at the bottom.**
Under §4 alone the range is 28–100; under §3+§4 it is 19–100. The
third-party wheels drop further because the six redistributed points
land on `007`, `008` and `014` — three checks they all fail — while
`miri-py` passes all four recipients and holds at 100%. §3 therefore
sharpens the *distinction* rather than simply widening the range, which
is a better argument for it than the one we made.

**One redistribution target is capability-gated.** `MIRI-PY-015`
requires execution, so offline its extra point leaves the denominator
with it. The redistribution is worth 6 points to a fully-capable run and
5 to a default one. Not a problem — every weight behaves this way — but
worth knowing before someone compares an offline number against a
documented total.

### An arithmetic error we caught in our own projection

Our first computation returned **112%** for `miri-py`. The gated points
move *into* other checks, so the scored set is still worth 100; we
subtracted them from the denominator *and* left the redistributed points
in, double-counting the 6. A percentage above 100 is not a subtle
failure, which is the only reason it was caught immediately.

Recording it because the pattern in your §2 note applies: we were
computing a number we expected to be lower and did not check the total
before reading the result. The corrected figures are the ones above.

## 3. On the third reachability miss

Noted without complaint. The habit that caught it is cheap — five
branches, thirty seconds — and we will keep applying it to claims from
our own side too, since the `api_index` confound and the 112% above were
both us doing the same thing to ourselves within one exchange.

## 4. What we do next, in order

1. Wait for the merge and tag. Nothing below starts before it, and we
   will not pin an unmerged branch.
2. `make sync-checks` at the tag, resolving it to a sha.
3. Add `scoring` to `CheckDefinition` and honour it in the scorer. We
   have a guard for this: a test asserts our model declares every field
   each family's check schema declares, so a re-pin carrying `scoring`
   fails loudly rather than dropping it. Without that, `scoring: gate`
   would have validated fine and vanished, and we would have scored
   three gated checks at full weight — the vacuous-pass shape, in our
   own scorer.
4. Implement the excluded/forfeited denominator, the three newly
   required `scores` fields, and the `undetermined` grade.
5. Re-run §1 and report measured numbers against the table above.
