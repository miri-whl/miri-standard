---
name: rewrite-to-brief
description: "Write or rewrite a long piece (a blog post in docs/blog, the origin story, why-consumption, the README, the explanatory part of a spec) against a written brief, round by round, with arghos measuring each round. Use when asked to write a new post, or to restructure, tighten or rewrite a long page so it stays on its point, flows, and does not read as machine-written."
---

# Rewrite to a brief

The brief is the reference for every round. A round is judged against the brief, never against the previous draft,
and arghos does the measuring, so the writer never grades its own work. Load `prose-check` and `docs` first: the
first explains the commands and the numbers, the second the wrap, fence and link rules every round must keep.

## 1. The brief (approved before any prose)

Write `memory-bank/briefs/<piece>-brief.md`: YAML front matter that arghos reads, then the same brief in prose for
people. This is a public repo, so the brief holds no internal notes. Mark open choices `[DECIDE: …]` and leave them
for the maintainer; never settle them yourself.

```yaml
---
reader: >-
  A Python developer or security engineer who relies on a dependency scanner. Arrives from a link.
point: >-
  One or two sentences: what the reader should believe after reading.
takeaways:
  - "3 to 5 things the reader can repeat a week later"
reader_questions:
  - "What would the reader ask before they trust this?"
fixed_facts:
  - "Facts that may be reworded but never changed: versions, counts, check IDs, citations"
out_of_scope:
  - "Topics this piece must not drift into, including anything the standard does not yet say"
voice:
  byline: <author>
gates:
  flow_jumps_per_100: 25
  clarity_fail: 0
  cadence_comma_tail_rate_max: 5
  cadence_paragraph_closers_max: 1
  cadence_echo_openers_max: 0
  cadence_clause_chain_rate_max: 1
---
```

Pair the piece with its brief in `memory-bank/briefs/brief-map.yaml` (a path or glob mapped to a brief file).

## 2. Baseline

Measure the current version before you change it, so every round has something to beat:

```bash
arghos lint --clarity-only --json <file> > .generated/drafts/<piece>/baseline-clarity.json
arghos check --brief-map memory-bank/briefs/brief-map.yaml --panel --reads 3 --yes \
  --save .generated/scorecards --label baseline <file>
```

The second command costs about 11 model calls; ask before running it.

## 3. Rounds

Keep each round as `.generated/drafts/<piece>/round-N.md` (gitignored). In each round, top down:

1. **Structure.** Every section serves a takeaway. Cut or merge what serves none. Put the strongest material where
   readers are still reading; the scorecard's `skim_from` says where they stop.
2. **Paragraphs.** Each paragraph moves its section forward, and each sentence opens from something the one before
   set up.
3. **Sentences.** `arghos lint --clarity-only` until the fail tier is 0, then reread the `read` tier.
4. **Facts.** Check every new claim against its source (the YAML, the spec section, the cited paper or advisory)
   before measuring. A proposal is labelled as a proposal until the standard adopts it.

Then run the free pass and, for a public piece, the paid check with `--label round-N`, and compare with the last
round. If two rounds in a row move nothing, look at the brief before you write another round.

For a long public post, add an editorial panel run (`prose-check`, section 4) once the brief gates pass. Record each
rejected finding and its reason in the scenario's `corpus_facts`, so the next run does not raise it again.

## 4. The author's read

The author reads the last round, or listens to it: on macOS, `say -f round-N.txt -o round-N.aiff` reads a plain-text
export aloud. Structure problems are easiest to hear, such as an ending that does not end.

## 5. Publish

Stop when every gate passes and the author approves. Copy the approved round into place, reflow it to 120 columns,
run `make lint`, `make spell` and `make links`, and, for a page the site renders, `make site`. Update the index the
piece belongs to (`docs/blog/README.md` for a post), then give the maintainer the commit command.

## Rules that came from review

- End on why it matters: sum up, give the bigger reason, then a one-line close tied to the opening.
- Show, don't pitch: give the command, the code and the real output so readers can run it themselves.
- Never present a proposal as part of the standard, and never claim a tool does something it does not.
