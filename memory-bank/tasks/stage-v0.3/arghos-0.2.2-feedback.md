# Feedback for the arghos team — 0.2.2 in production use

**From:** Miri Standard maintainers
**Context:** Five `review` runs of arghos 0.2.2 against the Miri v0.3 consumption suite (4 specification
documents, ~4,000 lines, 6 lenses) on 2026-08-24, plus three earlier runs on 0.2.0/0.2.1 for comparison.
**Summary:** The status header shipped and it changed how we work. One reproducible bug is costing you completed
runs and, more seriously, silently overstating coverage in the artifact people actually read.

## 1. The status header — this landed, and it earns its place

We asked for a quality number at the top of the report. What shipped is better than what we asked for:

```text
╭─ where this stands ──────────────────────────────────────────────────────────╮
│ VERDICT    not-complete  (was: complete-with-fixes)                          │
│ SEVERITY   must 24 ▲18   should 26 ▼11   noted 16 ▲15                        │
│ MOVEMENT   31 closed · 50 new · 13 persisting   vs 20260824-134244           │
│ CONFIDENCE 15 unlocatable quotes · 21 fact conflicts · 6 lenses              │
│ MUST-FIX   ▆▇▁█  19 22 10 24                                                 │
╰──────────────────────────────────────────────────────────────────────────────╯
```

Three specific things you got right that we would not have specified:

- **The caveat line.** *"volume tracks the panel's output rate, not the document. Read the severity split, not the
  total."* We hit exactly that trap on our first 0.2.2 run — total findings jumped and our instinct was to read it
  as regression. The line was already there telling us not to. A tool that warns you against over-reading its own
  headline number is rare.
- **The MUST-FIX sparkline.** Four runs of history in eight characters. This is what let us see that our fix passes
  were producing a *sawtooth*, not a decline — `19 22 10 31 6 24 11 16` — which turned out to be the single most
  useful fact of the whole exercise (see §3).
- **`--compare-to` / `--no-compare`.** Making the comparison explicit rather than implicit-to-last-run is right.
  We re-ran against a fixed baseline several times while iterating and the numbers stayed meaningful.

**MOVEMENT (closed / new / persisting) is the field we check first now.** It answers "did my fixes land" in a way
the severity counts cannot, because it separates the two things that move the total.

## 2. The bug: truncated model JSON, and a report that does not admit it

**Priority: highest.** This has two halves and the second is worse than the first.

### 2a. Reproducible lens failure

The `two-implementations` lens has failed **every time it has been attempted on this corpus** — three for three:

| Run | Failure | Truncation point |
|---|---|---|
| `20260824-134915` | whole run lost, `ChairDecision` | column 5751 |
| `20260824-145829` | lens dropped | column 31038 |
| `20260824-150633` | lens dropped | column 31192 |

```text
⚠ lens failed two-implementations: ValidationError: 1 validation error for LensReport
  Invalid JSON: EOF while parsing a string at line 1 column 31192
```

The two lens failures truncate at ~31k characters, which looks like a `max_tokens` ceiling rather than anything
about our content. The `ChairDecision` crash is the same class at the consolidation step: 68 findings went in, the
JSON came back cut mid-object, and a completed three-minute run was lost entirely. Re-running succeeded at 79
findings, so it is a threshold effect, not a hard limit.

Worth noting *which* lens this is. `two-implementations` carries the charter *"Be exhaustive about this and ignore
everything else"* — so the lens you have explicitly told to be exhaustive is the one whose output overflows. The
prompt and the buffer disagree.

Suggested fixes, in order of preference:

1. Raise the output ceiling for lens and chair calls, and set it from the corpus size rather than a constant.
2. Stream and repair: on a truncation, salvage the complete objects already emitted rather than discarding the
   pass. A partial lens report is worth far more than none.
3. Chunk the chair step. Consolidating 68+ findings in one call will keep hitting this as corpora grow.
4. At minimum, retry the failed pass once before giving up.

### 2b. The artifact does not record that it happened — this is the serious half

We checked `review.json` for the run where a lens failed:

```text
lenses -> ["conformance-editor", "two-implementations", "adversarial-reader",
           "journey-completeness", "internal-consistency", "scope-and-honesty"]
failure/degraded markers -> []
```

All six lenses are listed as having run. There is **no failure marker anywhere in the JSON**, the HTML report never
says "failed", and `lens-passes.jsonl` records all six lens *definitions* regardless of whether they produced
output. The status header says `6 lenses`. It was five.

The warning existed **only on stderr, in our terminal.** Anyone reading the PDF — which is the entire point of the
PDF, and how these get shared with stakeholders — would reasonably conclude the document had been reviewed from six
independent angles when one was missing. Our own round-4 and round-5 must-counts are undercounts and we had to note
that manually in our commit message.

For a review tool this is a correctness issue rather than a cosmetic one: **the artifact overstates its own
coverage.** Concretely:

- Record per-lens outcome (`ok` / `failed` / `partial`) in `review.json`, and render it in the HTML and PDF.
- Make the header's lens count read `5 of 6 lenses (1 failed)` when that is the truth.
- Consider a `degraded: true` flag at the top level so downstream tooling can refuse to compare a degraded run
  against a clean one — comparing them silently is what produced our misleading deltas.
- `arghos review` should exit non-zero, or at least warn loudly at the end rather than only mid-run, when a pass
  was lost.

## 3. What the tool taught us that we could not see ourselves

This is the part worth your attention as product signal, because it is a use case you may not have designed for.

We ran five rounds, fixing everything each round reported. The must-fix count went
**31 → 6 → 24 → 11 → 16**. It did not converge to zero and we now believe it will not.

What *did* change was the **class** of finding, and this was only visible because the header preserved history:

| Round | Dominant theme |
|---|---|
| 1 | Missing mechanisms — a transport with no discovery method, a MUST with no fixture |
| 2 | Field-level gaps in what round 1 added |
| 3 | Undefined terms, requirement-level mismatches |
| 4 | Arithmetic and cross-reference errors |
| 5 | **Clauses with no corresponding check** |

Round 5's finding was that seven of sixteen musts were "this MUST has no check" — a *coverage* gap, not a prose
gap. That reframed our remaining work from "keep editing" to a countable audit: 171 normative clauses against 33
checks.

**The insight we would not have reached alone:** each fix pass closes a ring of defects and exposes a smaller one
inside it, because every normative clause added has its own edges. A tool that reports only "N findings" hides
this completely. The sparkline plus the closed/new/persisting split is what made it legible, and it is the
strongest argument we can give you for keeping cross-run history central to the product rather than an add-on.

**Product suggestion:** you are one step from surfacing this yourself. If the chair tagged each finding with a
coarse class (`missing-mechanism`, `undefined-term`, `internal-contradiction`, `no-enforcement`, `arithmetic`), the
header could show class distribution shifting across runs — *"round 5 is 44% no-enforcement, up from 6%"*. That is
a genuine convergence signal, where a raw count is not. It would tell a user *what kind of work is left*, which is
the question they actually have.

## 4. Smaller observations

- **Fact conflicts are rising as the corpus tightens** (7 → 21 → 18 → 22). Some are our stale `corpus_facts`, but
  several were the panel miscounting sparse ID ranges as check counts — reading `MIRI-CONSUMER-001` through `-042`
  as 42 checks when there are 15. We fixed it on our side by stating the sparse-numbering rule in `corpus_facts`
  and in the documents. It may be worth prompting the chair that an ID range is an address space, not a count;
  it is a common convention in standards and it recurred across every run.
- **Recurring false positive.** "MUST flag replacement purl namespace mismatch has no corresponding consumer
  check" appeared in three separate runs. The check exists — it is the second `fires_when` clause of
  `MIRI-CONSUMER-032`. The panel reads the checklist tables but seemingly not the check definitions behind them.
  If a scenario could point at structured definitions as well as prose, this class would drop.
- **Quote verification is doing real work.** The `discarded — quote not found in corpus` mechanism caught several
  confident-sounding fabrications. Keep it, and consider showing the discarded count in the header next to
  unlocatable quotes, since it is evidence *for* the tool rather than against it.
- **`--yes` and the cost estimate up front** are well judged. `est. ~$0.70` before a three-minute run is exactly
  the right amount of friction.

## 5. What we would ask for next, in priority order

1. **Fix the truncation** (§2a) — you are losing whole runs.
2. **Record and render lens failures** (§2b) — the artifact currently misrepresents its coverage.
3. **Finding classification** (§3) — turns a noisy count into a convergence signal.
4. Let a scenario supply **structured artifacts** (YAML/JSON check definitions) alongside prose, to cut the
   "no check exists for this" false positives.
5. A `--fail-on must>N` exit code, so a panel run can gate CI rather than only inform a human.

## 6. Bottom line

We have run arghos against this specification suite eight times across three versions. It found a composition
break that three of our own hand-run review panels had missed, an arithmetic error in a worked example that would
have embarrassed us in public review (a score of 96 over a denominator of 88), and a contradiction between two
sections written a week apart. It is doing the job.

The one thing we would not ship without is §2b. Everything else on this list is improvement; that one is a
report that says something untrue about itself.
