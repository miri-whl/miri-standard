# arghos — false positives and duplicate findings, from 13 review runs

**From:** Miri Standard maintainers
**Basis:** 13 `arghos review` runs against the same 4-document corpus, 2026-08-24/25, versions 0.2.0–0.2.5.
**Summary:** The tool is finding real defects — we have fixed well over a hundred because of it. This report covers
the noise around them, with counts, because two of the four causes are mechanical and cheap to fix.

## 1. Duplicate findings inside a single run

**8 of 13 runs contained at least one finding duplicated verbatim within the same run.** Not "similar" — the same
title, consolidated as separate entries and counted separately in the severity totals.

| Run | Duplicated |
|---|---|
| `20260824-073631` | 3 findings |
| `20260824-135512` | 2 |
| `20260825-042620` | 3 (one appeared **three** times: "§3.4 step 4 trigger condition…") |
| `20260825-052415` | 2 |

Examples, verbatim:

```text
The connection file specifies `address` as "127.0.0.1" in the example, but §7's loopback definition says…
The connection file specifies `address` as "127.0.0.1" in the example, but §7's loopback definition says…
```

This inflates `must` directly. Our round-7 count of 24 contained at least 4 duplicate entries, so the real figure was
~20 — and because the status header's delta is computed on those totals, the movement numbers inherit the inflation.

**Fix:** deduplicate in the chair before assigning severity. Exact-title match would catch most of it; near-match on
the cited location would catch the rest.

## 2. "No check exists for X" when the check exists — and why

**4 recurrences across separate runs** of one finding: *"MIRI-CONSUMER-032 does not score the cross-namespace
flagging MUST."* It does — that is literally its second `fires_when` clause. Same shape for
*"No surface conformance check enforces the prohibition on publisher bytes in `reason`"* (it is `MIRI-SURFACE-002`).

**The cause was ours, and it is worth writing down because the fix generalizes.** Our scenario's corpus contained
only the 4 markdown specifications. The check definitions live in `standards/consumption/checks/*.yaml` and were
never in the corpus, so every "no check covers this" finding was **unverifiable by construction** — the panel was
asked whether an obligation was enforced while holding none of the enforcement.

We fixed it by projecting the 33 YAML definitions into a generated markdown artifact and adding it to the corpus.
The effect was immediate and large:

| | before | after |
|---|---|---|
| must-fix | 33 | **17** |
| discarded findings | 34 | **10** |
| unlocatable quotes | 18 | **9** |

**Suggestion:** a scenario should be able to declare non-prose artifacts (YAML/JSON) directly, rather than requiring
the author to hand-project them into markdown. More usefully — when a lens is about to claim something *does not
exist*, that is exactly the claim most sensitive to corpus completeness, and the chair could mark such findings with
a lower confidence, or require them to cite what they searched.

## 3. Findings that quote text the fix already changed

Round 7 reported *"No operation resolves a purl to an import name; §3.3 step 3 is unserviceable."* The bridge was at
line 271 of the corpus file the panel was given, added in the round-6 fix pass. Similar: a claim that two documents
used different literals for a `Case` cell when both used the identical string, which we checked byte-for-byte.

We do not think this is stale-corpus — we re-copy the artifacts before every run and verified the text was present.
It reads more like a lens asserting a general absence without searching for the specific mechanism. Rarer than the
other classes (2 clear instances in 13 runs), but the most expensive to triage, because disproving it means reading
the whole document.

## 4. Cross-document section references read as local

Several findings flagged a `§N.N` reference as dangling when it pointed at another document in the suite. Our specs
cite each other constantly — written as a markdown link whose text carries the section and whose target is the sibling
file —, and a lens reading one document
in isolation cannot resolve them.

**This one was half ours and it taught us something.** We built a consistency checker on our side and hit the same
problem: our first version reported **40** such failures, of which **34 were false**. Stripping markdown links and
any sentence naming another document before looking for `§` references cut it to 6 — and all 6 were **real defects**:
unqualified cross-document references that a reader would resolve against the wrong document.

So the signal was there; it needed the same filter. If a lens is given sibling documents in one corpus, resolving a
`§` against all of them before reporting it as dangling would turn this class from noise into one of the more
valuable checks available — it is exactly the error a human reviewer never catches.

## 5. What we are NOT claiming

The tool's hit rate on real defects is high and we want to be precise about that, because a false-positive report
read alone would misrepresent it. From these same runs, arghos found — cold, with no prior knowledge:

- A **DNS-rebinding bypass** in our SSRF guard: we re-validated after redirects but resolved the hostname twice.
- A **TOCTOU race** on a bearer-credential file we had specified without an atomicity rule.
- A rule permitting a consumer to **execute publisher-authored `code` fields**, which nothing forbade.
- A **scoping bug in our own fix** where `list` — which enumerates only metadata-shipping packages — was being read
  as an installed-package inventory.
- A worked example scoring **96 over a denominator of 88**.

None of those were reachable by reading our own text again, which we had done repeatedly.

## 6. Priority

1. **Deduplicate findings within a run** (§1) — mechanical, inflates every severity count you report.
2. **Resolve `§` references across the whole corpus** before calling one dangling (§4) — turns noise into signal.
3. **Support non-prose artifacts in a scenario** (§2) — or at minimum, flag existence-claims as corpus-sensitive.
4. Consider a confidence signal on findings of the form "no X exists anywhere", which are the ones a partial corpus
   most reliably fabricates.
