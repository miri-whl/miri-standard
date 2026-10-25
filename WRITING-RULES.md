# Writing rules: no AI tells

*Applies to everything this project publishes: the site, the specifications under `standards/`, `README.md`, `docs/`,
the check definitions' prose, and feedback documents sent to implementers. It applies to people and to AI writers alike.
Check a file with `python3 tools/check_writing.py --allow harness <file>` before it ships.*

**Why.** Readers stop trusting a piece the moment they think a model wrote it, however solid the content. A reviewer of
the Patitur wheel post stopped reading at the third em dash and the second "load-bearing" (October 2026). A standard
asks implementers to take its wording literally, so prose that reads as generated costs more here than on a marketing
page: an implementer who stops trusting the text stops implementing it.

## 1. Banned outright

- **Em dashes (—, `&mdash;`), and spaced hyphens or en dashes used as dashes (` -- `, ` – `).** Use a comma, a colon,
  parentheses, a semicolon, or two sentences instead. This includes alt text, captions, tables, code comments and
  reference lists. Date and number ranges keep the en dash (`2015–2017`).
- **These words and phrases:**
  - **AI-tell vocabulary:** load-bearing, delve, leverage (as a verb), harness, unlock, elevate, empower, foster,
    streamline, tapestry, landscape (figurative), realm, journey (figurative), testament, beacon, cornerstone, paradigm,
    robust, seamless(ly), crucial, pivotal, vital, cutting-edge, game-changing, best-in-class, a myriad of, navigate
    (figurative), underscore(s), nuanced.
  - **Throat-clearing and filler:** it's worth noting, it's important to note, let's dive in, here's the thing, that
    said, moreover, furthermore, in conclusion, in short, at the end of the day.
  - **This project's house tics**, measured on the generated site in October 2026: honest (43), honestly (5), plainly
    (6), load-bearing (8). Also "say so", "and we say so", "stated rather than", "recorded rather than", "worth
    stating", "which is the point".

**Allowed, because they are technical here:** `harness` (a scoring harness is a named thing in this project; pass
`--allow harness`). Add a term to the allow list rather than deleting it from the rules, and only when it names
something the standard defines.

## 2. Banned constructions

| Construction | Example (real, from our pages) | Write instead |
|---|---|---|
| **Statement followed by a fragment** | "Four directory levels, and no supported way to traverse them." | "The file sits four directory levels above the package, and there is no supported way for the package to reach it." |
| **The piece narrating itself** | "Everything above is mechanism." "The opening promised to say…" "The answer is short." | Delete the sentence and start with the point. |
| **Fragment as a paragraph opener** | "Five keys. They are not paths…" | "None of the five keys is a path inside your package." |
| **"X, not Y" / "not X — it's Y" antithesis** | "Four lineages, not one standard." "beside the package, not in it" | State the positive claim. Keep a contrast only when the reader actually believes Y. |
| **Drumroll or filler line** | "This matters practically." "That is the whole point." "That is the list, and it takes a minute:" | Say the consequence directly: "In practice, a search for … lands on…" |
| **Colon reveal** | "The catch: …" "Here's why: …" | Make the claim as an ordinary sentence. |
| **Rule of three for rhythm** | "direct access, a real say, and pilot terms" (on every page) | Keep a list only when there really are three things, and vary it between pages. |
| **Participle tail** | "…, ensuring every alert is actionable." | Make it a sentence with a subject, or cut it. |
| **Templated sentences across pages** | the same "becomes an export" line on ten vertical pages | Write each page for its own reader. |
| **Stacked hedges** | "can potentially help" | Pick one, or none. |

## 3. Specifications are different

`standards/` holds normative documents, so a wording edit must not change what they require.

- **Every RFC 2119 keyword stays exactly as it is** (MUST, MUST NOT, SHOULD, SHOULD NOT, MAY, REQUIRED). Run
  `tools/verify_wording_only.py <before> <after>`; it fails if a count changes.
- **Never touch** code blocks, schema snippets, check IDs, `fires_when` clauses, or section numbers that other
  documents cite.
- Keep the 120-character hard wrap, and pass markdownlint, cspell and the link check that CI runs.
- Record the pass in the CHANGELOG as an editorial change, under `GOVERNANCE.md`.
- The 124 check pages share six headings by design. That is reference structure; judge the prose and leave the
  headings alone.

## 4. What good looks like

- Full sentences with a subject and a verb. Vary the length because the content varies, not to create rhythm.
- One idea per sentence; commas and parentheses for asides.
- Concrete nouns and real numbers with a source. If we don't know something, say so in ordinary words, once, without
  labelling it as honesty.
- Let the specifics carry the trust: the measurement, the command, the version number.

## 5. Checking

`python3 tools/check_writing.py --allow harness <file or folder>` checks HTML and Markdown. It reports em dashes, banned
words, and the most detectable constructions (fragment openers, self-narration, "X, not Y"), with line numbers. It skips
code blocks. The exit code is non-zero on any hit, so it can gate a publish. The script catches the mechanical tells;
the constructions in section 2 still need a human read.
