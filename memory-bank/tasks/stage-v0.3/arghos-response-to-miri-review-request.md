# Response: a `review/` scenario family for arghos

**To:** the Miri Standard maintainer
**From:** the arghos maintainers
**In reply to:** "Feature request: expand arghos to review specifications and RFCs" (2026-08-23)

## Short answer

Yes. We want to build this, and we would rather you stopped rebuilding it too.

Your read of the architecture is accurate: `kind: critique` is the right shape, the run/compare hygiene is the
part worth reusing, and the machinery genuinely is the general half of the tool. We are proposing
`kind: review` as a third scenario kind, in three phases. **Six of your seven asks land in the first two
phases**, and two of them are largely built already.

Below: one correction that makes this cheaper than you costed it, what you already have, what we are pushing
back on, one thing we are adding that you did not ask for, and what we need from you to start.

## One correction, and it changes the cost

The core ask (#1) opens with: *"arghos maps free-text responses onto numeric ratings via SSR anchor ladders."*

That is true of the **wedge** scenario. It is not true of the **critique** scenario — the one you correctly
identify as the right shape. `kind: critique` does not touch SSR. It runs each panelist's free text through a
judge model with a Pydantic schema via structured outputs (`provider.parse(schema=CritiqueJudgment)`), and the
schema is enforced server-side. The judgment happens to be rating-shaped because buyers were the first
customer; the *mechanism* is schema-shaped and has been hardened in production (we fixed a judge-truncation bug
in 0.1.5 that was silently discarding whole panelists).

So ask #1 is not "add a second instrument beside SSR." It is "declare a second judgment schema on machinery
that already exists." Same call, same retry-on-truncation path, same drop accounting, same coverage
reconciliation. That is the difference between a quarter of the work and most of it.

## Two asks are mostly already built

**#6 — multi-document shared corpus.** Artifacts keyed `_shared` are already read by *every* panelist, and the
target loaders already fold any document that does not match a vertical into `_shared`. Point a panel at a
directory of your four specification documents today and all six lenses see all four as one corpus. What is
actually missing is narrower than you think: the loader concatenates documents with `---` separators and
flattens each `Document.key` / `title` into a heading, so a finding cannot cite a stable document name. That is
a labelling fix, not new plumbing.

**#7 — finding-level comparison.** This is the ask you most want, and the machinery exists. `critique-trends`
already matches items across N runs, keyed on a stable content hash first and a **pluggable equivalence
predicate** second, and annotates each item with first-seen, run count, and active / "gone since run X". That
is closed / new / persisting under a different name. `review-compare` is mostly: define finding identity, pass
a matcher, render. It is the cheapest thing on your list.

That is why we want to build **#7 first** — see phasing.

## What we are pushing back on

**1. No configurable `finding_schema`. A fixed `Finding` model instead.**

You asked for a declared, configurable field set. We want to ship a fixed Pydantic model:

```
Finding:
  severity: Severity        # closed enum
  document: str             # required — stable document id
  quote: str                # required — verbatim
  defect: str               # required
  title: str = ""
  fix: str = ""
```

Three reasons. Configurable field sets mean dynamically-constructed schemas, which fights a convention that
holds everywhere else in the codebase (structured data is a model in `models.py`, axes are `StrEnum`). It
weakens ask #7, because cross-run *identity* depends on `document` and `quote` always being present — an
optional identity field is not an identity field. And you lose nothing real: the variation you care about
lives in the lenses, not the schema. If a field set turns out to be too rigid we would rather add a field for
everyone than support N shapes.

**2. The `quote` requirement has to bind your lenses, not just our schema.**

We agree with your finding that *"a finding with no quote is noise — omit it"* materially raised quality, and
we want to enforce it mechanically (below). That only works if lenses quote **verbatim** rather than
paraphrasing or normalising whitespace-and-ellipsis. That is a constraint on the prompts you contribute, and we
would rather agree it now than discover it in the first run.

**3. Discarded out-of-scope findings get reported with their text, not just counted.**

Your ask #5 says "with the count of discarded findings reported." We want the text too. A finding discarded as
out-of-scope is sometimes a real defect aimed at the wrong target, and a bare count hides that. Cheap to do,
and it keeps the scope guard auditable rather than a silent filter — the same reason our judge never drops a
panelist quietly.

## One thing we are adding that you did not ask for

You report that **roughly one in six findings did not survive checking against the files**, and ask for a tool
affordance (#4) to fix it. There is a much cheaper partial answer, and we want to ship it in phase 1:

**Mechanically verify that every `quote` actually appears in the corpus.** Normalised substring match, no model
call, run at analysis time — the same class of check as the jargon scan we ship today. Findings whose quote
cannot be located get flagged (and optionally dropped) before they reach the report.

That will not catch a finding that quotes correctly and reasons wrongly. It kills the hallucinated-citation
class outright, at zero marginal cost, and it turns your "omit it" instruction from an aspiration into an
invariant. We would expect it to take a visible bite out of your 1-in-6 before any tool-use work happens.

## The expensive ask, and a tension inside it

Ask #4 (read-only file and search tools for panelists) is the one real architectural change. Our provider
abstraction has exactly two call shapes — a multi-turn text turn and a one-shot structured extraction. There is
no tool loop anywhere in the pipeline. Adding one means extending the provider protocol, writing the execution
loop, and building a sandboxed read-only toolset with canonical-path confinement (a panelist-supplied path is
untrusted model output, and the failure mode is reading outside the declared root).

We think you are right that it changes the class of finding available, and right that it would improve the
buyer scenarios too. But there is a tension you did not raise, and it points straight at the feature you most
want:

**arghos guarantees seeded determinism so that runs are comparable.** A panelist who can grep sees a different
slice of the repository on every run. Run-over-run comparison (#7) assumes the two runs differ only in the
document — if they also differ in what each panelist happened to look at, a "closed" finding might just be a
finding nobody looked for this time.

Not a blocker. It does mean tool-enabled runs need to record that they were tool-enabled, and `review-compare`
needs to say so loudly when comparing across that boundary — the same treatment we already give a protocol or
scope mismatch. Worth deciding deliberately rather than discovering.

## What we need from you

**A. The six lenses, the chair charter, and the scope-guard framing.** You offered these; we accept, and we
want them as the shipped worked example (the way `buyers/` grounds the sample panel). Send them as prose or
YAML — we will shape them into whatever `lenses.yaml` ends up being.

**B. A regression corpus. This is the highest-value thing you can give us.** Specifically: the findings from
rounds 5 and 6 as structured data, plus both revisions of the four specification documents. That is the only
way to validate the two riskiest pieces before shipping them:

- does the quote-grounding check actually catch the findings that did not survive your manual verification?
- does our finding-identity matcher reproduce the closed / new / persisting split you derived by hand?

Without it we are designing the matcher blind and tuning it on synthetic data.

**C. Your 36-row hand-tracked backlog.** That is the ground truth for what `review-compare` has to produce. If
our output disagrees with it, our output is wrong.

**D. Six decisions.**

1. **Severity** — is `critical / high / medium / low` closed and final? We want it as a fixed enum so it is
   comparable across runs and sortable in the report.
2. **Document identity** — what should `document` hold: file stem, document title, or an id you declare? It has
   to be stable across revisions, because cross-run matching keys on it. A retitled document should not read as
   36 closed findings.
3. **Cross-document findings** — your best findings were *between* documents (a claim in one contradicted by
   another; a cross-reference to a section that does not exist). A single `document` + `quote` cannot express
   that. Do you want an optional second location, or a list? This affects identity matching, so we would rather
   decide it before phase 2 than bolt it on after.
4. **The chair's verdict schema** — your rounds produced "verdict + 16 must-fix, 13 should-fix." What is the
   verdict, exactly: a closed enum, a sentence, both? What else does the chair return besides the consolidated
   findings and the discarded list?
5. **Your actual `out_of_scope` list**, verbatim. We want the shipped example to carry a real one, not an
   invented one.
6. **Runs per lens.** Your model is exactly one conformance editor — no sampling, and we agree. But note that
   findings and ratings fail differently: ratings need N for stability, findings need N for *recall*, because a
   lens that misses a defect on one pass has no second opinion. Since sampling is bypassed anyway, an
   `n` per lens (run each lens k times, union, dedupe) is nearly free for us to support. Do you want it?

**E. One confirmation on scope for #4.** Is read-only file read + search, confined to a single declared root,
sufficient? Or do your lenses need to *execute* something (a checker, a linter, the fixture suite)? Those are
very different security and determinism stories, and the answer changes the design.

## Phasing, and what you get when

**Phase 1 — the spine.** `kind: review`; lenses as a flat unsampled family; the `Finding` model; the review
run; chair synthesis; `out_of_scope` injected into every lens prompt and enforced at synthesis with the
discarded set reported; corpus artifacts with stable document labels; mechanical quote verification; report and
terminal rollup. **Delivers asks 1, 2, 3, 5, 6.**

**Phase 2 — `review-compare`.** Closed / new / persisting on finding identity, reusing the cross-run tracker.
**Delivers ask 7.**

**Phase 3 — verification affordance.** Ask 4, as its own decision, gated on your answer to (E) and on how you
want to handle the determinism tension.

We would start with **phase 2** even though it is second in the list — it is small, it is the thing you most
want, and it forces the finding-identity design that phase 1 has to agree with anyway. If you would rather have
the spine landed in one pass, say so and we will invert it.

## What we are keeping shared

To be explicit about the thing that would make this a bad idea: we are not forking arghos into two tools. A
review scenario reuses the target loaders, the provider registry, the run directory and `meta.json`
provenance, cost estimation and caps, the seeding, the truncation and coverage accounting, and the report
chrome. What is genuinely new is one judgment schema, one synthesis pass, one analysis module, and one compare
command. If we find ourselves duplicating the spine, that is the signal we got the design wrong.

## The guardrail carries

You pre-empted this and you are right to. arghos's standing caveat — *a hypothesis-generation engine, not a
validated predictor* — applies to specification review at least as sharply as to buyer panels, and your 1-in-6
figure is the best evidence anyone has handed us for it. The review report will carry the same warning the
critique report does: **every finding is a place to look, not a defect that exists.** The quote check narrows
that gap; it does not close it.

---

*Noted on the CLI conformance report: send it whenever. `arghos config` (added in 0.1.4) enumerates every knob
with its resolved value, which may be relevant to whatever the standard says about discoverability.*
