---
name: glossary
description: Keep docs/glossary.md in step with the standard when a term is added, renamed, or redefined. Load this before introducing a new defined term, changing a closed vocabulary (operations, error codes, trigger kinds, vehicle labels, skip reasons), or adding a check family.
---

# Keeping the glossary current

`docs/glossary.md` explains every term the standard defines. It is dangerous in a specific way: a glossary becomes
the thing people read *instead of* the spec, so a wrong entry does not merely fail to help — it gets cited. Treat it
as derived from the normative documents, never as a second place where meaning is decided.

## The rule

**A change to the vocabulary is not finished until the glossary reflects it.** That includes:

- introducing a term the specs define in bold (`**Trigger** is …`)
- adding to or removing from a closed set — operations, error codes, trigger kinds, vehicle labels, skip reasons,
  severity levels
- adding, withdrawing or renumbering a check family
- renaming anything, which is the case most often missed, because the old name keeps working everywhere else

## What is gated, and what is not

`make consistency` runs `check_glossary()` in `tools/check_consistency.py`. It **fails the build** on:

1. **A closed vocabulary that disagrees with its source.** Trigger kinds come from `agent-event-v1.json`, vehicle
   labels from the Consumption Map's own table, severity from `check-v1.json`. The glossary quotes; it does not
   decide.
2. **A defined term with no link** to where it is normatively defined. Every `**Term** —` entry must reach its
   home in one click, because a reader who needs the rule rather than the explanation should not have to search.
3. **A stale check count or ID range.** `MIRI-CONSUMER` runs 001–051 across seventeen checks; both numbers are
   asserted against the files.

It does **not** check whether an explanation subtly misstates the rule it links to. That is a reading, and it is
what review is for. Do not treat a green `make consistency` as evidence the prose is right — only that it is
consistent.

## Writing an entry

Follow the shape the existing entries use, because it is doing work:

Bold term, then a parenthesised markdown link to where it is normatively defined, then an em dash, then one
sentence of what it is — followed by the thing a reader actually needs, which is usually *why* it is that way or
what it is confused with.

Paths in `docs/glossary.md` are relative to `docs/`, so a spec is `../standards/consumption/...` and a schema is
`../schemas/...`. The example above uses a placeholder rather than a real path on purpose: CI's link checker scans
every markdown file in the repository, including this one, and a live relative link in a skill resolves against the
skill's own directory rather than the glossary's.

- **Lead with the link.** The entry is an explanation; the link is the authority.
- **Name the near neighbor.** Most of this vocabulary has a close term that means something else — absent and
  error, task and trigger, level and severity, not-applicable and forfeited. The glossary's value is largely in
  those distinctions, so state them.
- **Explain the mechanism, not the shape.** "The envelope's top level is surface-owned" is the shape; "the standard
  denies the payload the position from which it could be believed" is the mechanism, and it is what makes the rule
  memorable.
- **Include terms the standard deliberately does *not* define**, with the reasoning. `Hook` has an entry saying it
  is a host's word and why adopting it would be a mistake. An absence nobody recorded gets re-litigated.

## When a term is renamed

Rename in the specs first, then the glossary, then grep for the old name across `standards/`, `schemas/`,
`examples/` and `tools/`. `make consistency` will catch a closed-set mismatch but not a stale mention in prose.
