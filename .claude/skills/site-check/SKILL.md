---
name: site-check
description: "Audit the generated Miri Standard site (miri-whl.github.io) for structure, accuracy, clarity and machine-sounding prose before changing it, then fix it in the sources page by page. Use when asked to review, audit or rewrite the website or one of its pages, or to check the site before a release."
---

# Site check

The site is generated: `tools/generate_site.py` renders it from the check YAMLs, the specs `website/site.yaml`
lists, `docs/` and `CHANGELOG.md`, through the templates in `website/templates/`. So you **measure the built pages
and fix the sources**. Never edit generated HTML. The rule for site work is to audit everything first, agree the
fixes, then edit. The numbers below mean what the `prose-check` skill says they mean; load it first.

## 1. Build the site and run the free checks

```bash
make site                                   # validates the check YAMLs, then builds .generated/site
arghos check --require sentences,flow --json .generated/site/*.html > .generated/site-check.json
arghos lint --ban-em-dash --allow harness .generated/site
```

Each built page names its source, so a finding traces back to a file:

| Page | Source |
|---|---|
| `index.html`, `downloads.html`, `404.html` | `website/templates/` and `website/site.yaml` |
| `origin.html` | `docs/origin-story.md` |
| `why-consumption.html` | `docs/why-consumption.md` |
| `glossary.html` | `docs/glossary.md` (derived from the specs; load the `glossary` skill before editing) |
| `changelog.html` | `CHANGELOG.md` |
| the spec pages (`discovery-contract.html` and the rest) | the `specs:` list in `website/site.yaml` |
| `checks/<target>/*.html` | `standards/<target>/checks/*.yaml` (load the `check-authoring` skill before editing) |

Flow is meaningless under about 15 sentence pairs, which rules out the home page, the downloads page and most
check pages. Weigh it on the origin story, `why-consumption.html` and the explanatory sections of the spec pages.
Check pages share one template, so their repeated headings and labels are by design; judge the rationale and
example prose in each one.

## 2. Read the pages (no edits yet)

For a full audit, split the site into areas and read each one (parallel subagents work well):

1. **Structure and navigation:** the nav in `website/site.yaml` against the built pages; pages nothing links to;
   the path a first-time visitor takes from the home page to the Python checks and the downloads.
2. **Explanatory pages:** the home page, the origin story, why-consumption. Does each one say what the standard is
   and who it is for before it says how it works?
3. **Spec pages:** is every normative sentence testable, and do the examples match the schemas (the `docs` skill's
   review checklist)?
4. **Check pages:** does each rationale name the harm, a real incident and why no existing tool catches it?
5. **Facts across pages:** the version, check counts, weights and status labels agree with each other and with the
   YAML. `make consistency` catches the drift a machine can see; read for the rest.

Each area writes a findings table to `.generated/site-audit/<area>.md`: id, page, source file, location, what is
wrong, category (structure, accuracy, clarity, voice, mechanics), severity, and a one-line fix direction. "High"
means a reader would take away a wrong fact or a wrong rule. Merge them into `.generated/site-audit/AUDIT.md` with
a prioritized fix list, and **stop for the maintainer's approval** before editing.

## 3. Fix in the sources

Fix site-level problems first (navigation in `site.yaml`, a fact repeated wrongly across pages), because one fix
changes several pages. Then work page by page, starting with what a first-time visitor sees: the home page, the
origin story, why-consumption, then the Python check pages, then the rest.

Edit the source file the table above names, following the `docs` skill for wrap, fences and links. A change to a
check YAML or a spec is a change to the standard, so it also follows `check-authoring` or `schema-governance` and
gets a `CHANGELOG.md` entry. After each page, run `make site` again and measure the rebuilt page.

## 4. Gates for a page

| Gate | Pass |
|---|---|
| builds | `make site` succeeds and the page is reachable from the nav |
| facts | versions, counts, weights and levels match the YAML; `make consistency` passes |
| sentences | clarity fail tier 0 on the built page |
| voice | `arghos lint --ban-em-dash` reports 0 findings |
| flow | at most 25 jumps per 100 pairs, on pages with about 15 or more pairs |
| CI | `make lint`, `make spell` and `make links` pass on the changed sources |
| maintainer | read by the maintainer, or by a paid panel for a long page (`prose-check`, section 4) |

## 5. Ship

Run `make serve` and open every changed page at `http://localhost:8000`. Then give the maintainer the commit command
(the `/commit-cmd` command). Publishing the site is the maintainer's step.
