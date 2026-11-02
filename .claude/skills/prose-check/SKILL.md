---
name: prose-check
description: "Check the English in the specs, docs/, the blog, proposals, READMEs and the generated site with arghos: AI-voice tells, clarity, flow and cadence (free, offline), plus the paid brief check and editorial panel review. Use before merging or publishing any prose change, and when asked to check, proofread, tighten or review writing, or when a page reads as machine-written. Complements the `docs` skill, which covers the house style and the CI linters."
---

# Prose check with arghos

Readers stop trusting a page the moment it reads as machine-written, however good the content is. arghos measures
the things that give that away, so the writer never has to grade their own work. The `docs` skill covers what CI
gates on (markdownlint, cspell, links); this skill covers whether the English is clear. Run both before you call a
prose change done. The rules the checks enforce are in `writing-rules.md` next to this file; read them once per
session.

## What arghos gives you

| Command | Cost | What it answers |
|---|---|---|
| `arghos lint` | free, offline | Mechanical AI-voice tells: em dashes, the banned word list, "X, not Y", self-narration |
| `arghos lint --clarity-only` | free, offline | Clarity on a dependency parse: figures of speech, clausal subjects, flow, cadence |
| `arghos check --require sentences,flow` | free, offline | The two free gates per document, worst first, with a pass or fail |
| `arghos check --brief-map … --panel` | about 11 model calls a document | Does a cold reader get the point, the takeaways and the fixed facts? |
| `arghos -C .panel/<panel> review` | about $0.60 a run | Editorial lenses report located defects; a chair sorts them into must-fix and should-fix |

Every finding is a hypothesis about where a defect is. Check each one against the text before you act on it.

## Setup

```bash
arghos --version                      # 0.7.3 or later
~/.local/pipx/venvs/arghos/bin/python -c "import spacy"   # the clarity rules need this
pipx install --force 'arghos[clarity]'                     # only if the line above fails
```

The paid commands need `ANTHROPIC_API_KEY` in the panel's `.env`. Never print, copy or commit a `.env`.

## 1. The free pass (every prose change)

Run both on each file you changed. arghos reads Markdown and HTML, and the 120-column hard wrap measures the same
as unwrapped text, so check the source as it is.

```bash
arghos lint --ban-em-dash --each --allow harness docs/blog/upgraded-but-still-vulnerable.md
arghos lint --clarity-only --json docs/blog/upgraded-but-still-vulnerable.md > .generated/clarity.json
```

`--allow harness` exists because this repo has real golden harnesses; add `--allow` for any other banned word used
as a technical term. `--ban-em-dash` makes every em dash a finding, which is the house rule (`writing-rules.md`,
section 1).

For several files at once, `arghos check` gives one pass or fail per document:

```bash
arghos check --require sentences,flow docs/*.md docs/blog/*.md README.md standards/README.md
```

Check rationales and other prose that lives in YAML reach readers through the site, so measure them on the built
pages (see the `site-check` skill).

## 2. Reading the result

`arghos lint` prints `file:line severity kind: quote`. Fix every one, or allow the word on purpose.

The clarity JSON holds the numbers. Read these keys:

| Key | Ceiling | What it means |
|---|---|---|
| findings with `"tier": "fail"` | 0 | A sentence a reader will misread: a figure of speech, a clausal subject, an intensifier |
| `clarity.jumps_per_100` | 25 | How often a sentence starts from nothing the sentence before set up |
| `clarity.cadence.comma_tail_rate` | 5 | Sentences that trail into an extra comma clause ("…, so …", "…, which …") |
| `clarity.cadence.paragraph_closers` | 1 | Paragraphs that end on a summing-up line ("So …", "That is …") |
| `clarity.cadence.echo_openers` | 0 | A sentence that opens by repeating the last one's words |
| `clarity.cadence.clause_chain_rate` | 1 | Sentences built from three or more chained clauses |

Reread the sentences in the `read` tier and fix the ones that are unclear. The `info` tier is counted and
hidden unless you pass `--verbose`. Each cadence block also lists the offending sentences (`comma_tail_sentences`
and so on), so you can go straight to them.

Flow means nothing on a short or reference page. Look at `clarity.pairs` first: under about 15 pairs, ignore
`jumps_per_100`. A check page, a schema reference or a table-heavy spec section will always score high, and that is
fine. Flow matters on the blog, the origin story, `docs/why-consumption.md` and the explanatory parts of a spec.

## 3. Fixing

Work top down, because sentence fixes made one at a time make flow worse:

1. **Structure.** Every section does one job for the reader. Cut or merge a section that does none.
2. **Paragraphs.** Each paragraph moves the section forward. Open each sentence from something the one before set
   up: a shared noun, "it" or "this", or a connecting word.
3. **Sentences.** Clear the fail tier, then reread the `read` tier.

Then run the free pass again. If the sentence checks pass and flow got worse, rewrite the paragraph as a whole
instead of patching more sentences. Reflow the paragraph to 120 columns afterwards, or markdownlint fails it.

Rules that keep the fixes honest:

- Don't game the measure. Adding "This" to the front of every sentence lowers `jumps_per_100` and makes the prose
  worse. A high number points to a paragraph that needs rewriting.
- Normative text keeps its meaning. A MUST or SHOULD clause, a check's level and a defined term keep their wording;
  rewrite the sentence around them, or leave a flagged sentence alone when the fix would change what an
  implementer must do.
- Never change a number, a version, a check ID or a citation to make a sentence read better. Check counts and
  weights come from the YAML in `standards/<target>/checks/`, and `make consistency` catches drift.
- One name per concept. Rewording must not introduce a synonym for a term `docs/glossary.md` defines.

## 4. Paid checks

Run these only when the free pass is clean and the piece is long or public (a blog post, the origin story, the
README). Ask before spending: the commands print an estimate and wait unless you pass `--yes`.

### Against a brief

A brief says who the reader is, the one point, the takeaways and the facts that must survive (see the
`rewrite-to-brief` skill). `arghos check` then measures whether a cold reader gets them:

```bash
arghos check --brief-map memory-bank/briefs/brief-map.yaml --panel --reads 3 \
  --save .generated/scorecards --label round-2 docs/blog/upgraded-but-still-vulnerable.md
```

Read the evidence in the saved scorecard (`review.reads[].one_point`, `skim_from`, `takeaways[].reason`), not just
the pass or fail.

### Editorial panel

A review panel is a directory with `.panel/lenses.yaml`, `.panel/personas.yaml` and
`.panel/scenarios/<scenario>/scenario.yaml`, reading the plain-text corpus in that scenario's `artifacts/`. This repo
keeps none yet. Add `.panel/` to `.gitignore` before you create one, since it holds an API key and run output, and
copy a working review panel rather than starting from `arghos init`, which scaffolds the buyer-panel templates.
Then put a `.txt` export of the piece in `artifacts/`, write the scenario's `corpus_facts` (what the piece argues,
what is already verified, what was rejected last round and why), and run:

```bash
arghos -C .panel/blog-review review --scenario blog --label <piece>-rev-N --max-cost 2
```

The run lands in `.panel/blog-review/runs/<timestamp>/` with `review.html` and `review.json`. Recording rejected
findings in `corpus_facts` stops the next run from raising them again.

## Before you call it done

- `arghos lint --ban-em-dash` reports 0 findings on every changed file (allowed terms aside).
- The clarity fail tier is 0, and the cadence numbers sit under the ceilings above.
- Flow is under 25 jumps per 100 on any post or explanatory page with 15 or more pairs.
- `make lint` and `make spell` pass (the `docs` skill), so the rewrite did not break the wrap or add an unknown word.
