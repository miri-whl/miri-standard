# Feedback from the first real `kind: review` run

**To:** the arghos maintainers
**From:** the Miri Standard maintainer
**Run:** `runs/20260824-025336` — 6 lenses, 1 chair, ~$0.55, 4 documents (102,437 chars), 7 `corpus_facts`
**Corpus:** the v0.3 consumption suite, immediately after a hand-run panel closed 16 must-fix defects

## Headline

It works, and the parts you built beyond the ask are the parts that earned their keep. Quote verification caught
**8 findings citing text not in the corpus**, mechanically, before the chair saw them — and the run said so loudly
rather than quietly dropping them.

Then it returned 40 findings and a `not-complete` verdict. **We verified the top five must-fix items by hand: two
were real, two were false positives, one was a real defect the wrong way round.** This is feedback about that
remainder, and about one specific, implementable thing that would have caught both false positives.

## The two false positives, and why they happened

Both are the same error, and neither is the class quote verification catches.

### FP1 — "Abstract states 042 as upper bound implying 42 checks; actual count is 15"

The sentence it quoted reads: *"fifteen numbered checks, `MIRI-CONSUMER-001` through `MIRI-CONSUMER-042`"*. The
lens read `042` as a **cardinal** when it is an **identifier in a sparse space** (001, 002, 003, 010, 011, 012,
020 … 042). The word "fifteen" is in the same sentence, four words earlier.

### FP2 — "Actor table has 12 Surface rows but 16 surface checks are claimed"

The table has 12 rows total: 6 Consumer, 6 Surface. Those 6 Surface rows reference all 16 surface check IDs, because
a row groups checks by obligation. The lens counted **rows as checks**.

The shared root cause: **a structural artifact was read as a count.** An ID is not a cardinal; a table row is not a
check.

## Why `corpus_facts` did not prevent it — the useful part

We supplied `check_counts: "… consumer: 15 checks, weights 100; …"`. The lens **had the correct count injected as
ground truth**, and its own finding text even says *"actual count is 15"* — and it filed the defect anyway.

So this is not ignorance of the corpus. The lens was not wrong about our repository; it was wrong about **what the
document said**. `corpus_facts` cannot catch that, because facts describe the corpus, not the claim. And quote
verification cannot catch it either, because **the quote was real and correctly transcribed** — it simply does not
support the assertion built on it.

That is the gap: you verify that a quote *exists*. Nothing verifies that the quote *supports the finding*.

## The proposal: fact-consistency checking, as a sibling to quote checking

A cheap mechanical version would have caught both, at zero model cost:

> When a finding asserts a numeric claim about a quantity that appears in `corpus_facts` with a different value,
> flag it the way an unlocatable quote is flagged.

FP1 asserts "42 checks"; `corpus_facts` says "consumer: 15 checks" — inconsistent, flag. FP2 asserts "16 surface
checks" against "12 rows" while `corpus_facts` says "surface: 16 checks" — the count it disputes is the count it was
given.

Implementation sketch, in the same spirit as the quote scan:

- Extract `(number, unit)` pairs from each finding's `title`/`defect` — `42 checks`, `12 rows`, `20 points`.
- Extract the same shape from every `corpus_facts` value at run start.
- Where units match and numbers differ, attach `fact_conflict: {claimed, known, fact_key}` to the finding.
- Do not drop it — **surface it**, the way you surface unverified quotes. Sometimes the finding is that the corpus
  fact is stale, which is worth knowing.

We would take this over Phase 3 tool use, for the same reason we preferred `corpus_facts`: it is deterministic,
costs nothing per run, and strengthens run-over-run comparability rather than weakening it.

## A second, smaller observation

Twelve of the forty findings (**30%**) make a countable claim of some kind. That is a large enough share that a
systematic error in counting is a systematic error in the panel — which is what we saw. It also means the check
above would touch nearly a third of output, not an edge case.

## What worked, specifically

- **Quote verification.** 8 of 48 raised findings (17%) were hallucinated citations, killed before synthesis. Our
  hand-run panels had no equivalent and we caught those by hand, one at a time, after the fact.
- **Reporting discards with their text.** Reading them was worth it: one discarded item was a real concern aimed at
  a clause that does not exist, which is a different problem from noise.
- **`strengths` / "holds up".** Six entries. A report that only accuses reads as uniformly negative and gets
  discounted; this is what makes the rest credible.
- **The `--dry-run` cost line.** `6 lens passes + 1 chair call, est. $0.55` before spending anything. We ran six
  hand-rolled panels with no idea what any of them cost.
- **Verdict vocabulary as scenario config.** `not-complete` is the right word for a specification and would be
  meaningless for a buyer panel.

## One bug, and you will want it before anyone else hits it

**`.env` in the panel directory is never read.** `settings.py` uses `env_file=".env"`, which pydantic-settings
resolves against the **working directory** — but the error message says *"copy .env.example to .env in this panel
directory"*, and the comment above `model_config` says `.env` "is read from the panel directory arghos runs in".

With `PANEL_DIR=.panel`, a user who follows the error message exactly puts the key in `.panel/.env` and it silently
never loads. `arghos config` then reports `ANTHROPIC_API_KEY — not set` while the file sits there populated. We hit
this and diagnosed it by reading your source.

Either resolve `env_file` against `PANEL_DIR`, or change the message and the comment to say the working directory.
The message is the one users obey.

## Calibration, honestly

Our hand-run panels ran at roughly **one in six** findings not surviving verification. This run, on the top five
must-fix items, ran at **two in five**. The sample is small and it is the top of one list, so do not read it as a
regression — but do read it as confirming your own caveat. *A hypothesis about where the defects are, not proof that
they exist* is exactly right, and the quote check narrows the gap without closing it.

The two findings that were real are worth naming, because they are the kind a human reviewer would not have caught:

- *"A forfeited check leaves both the numerator and the denominator"* — **"leaves" is ambiguous**: it reads as
  either "remains in" or "departs from". We meant departs. In a normative scoring clause that is a defect, and we
  wrote it twice in two documents.
- Five checks use terms the profile never defines — *"clean security verdict"*, *"attributed"*, *"matching code"*.
  The operational criteria exist, but only in the fixture goldens as regexes; **zero** appear in the profile prose.
  A reader of the profile genuinely cannot tell what fails. That is a real gap between where a rule is stated and
  where it is made decidable, and no lens of ours had found it in six rounds.

## Delivered with this

- **`lenses.yaml`** — our six lenses, in `.panel/`, as the worked example you asked for. The seed's four were close;
  the two missing were `adversarial-reader` and `scope-and-honesty`. Each carries the verbatim-quoting instruction,
  and a note that specification prose is hard-wrapped so a quoted sentence usually spans a newline.
- **The scenario** — `.panel/scenarios/miri-v03/`, with `facts.yaml` generated from the live repository rather than
  written by hand, so a stale fact cannot outlive the corpus.

Still owed: the regression corpus (rounds 5/6 findings, both document revisions) and the 36-row backlog. Both exist;
the honest caveat is that rounds 5 and 6 asked *different questions* rather than the same question over two
revisions, so they will exercise your matcher on similar-but-not-identical corpora. The clean A/B is this run
against the next one, which is now a real pair rather than a promised one.
