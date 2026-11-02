# Writing rules: no machine tells

These apply to everything in this repo that a person reads: the specs, check rationales, the site, `docs/`, the blog,
proposals, README files, the changelog and PR descriptions. They apply to people and to coding agents alike.
`arghos lint` catches the mechanical part; the constructions in section 2 still need a human read. This file quotes
the banned forms as examples, so `arghos lint` flags it; that is expected and the only exception.

## 1. Banned outright

- **Em dashes**, and spaced hyphens or en dashes used as dashes (` -- `, ` – `). Use a comma, a colon, parentheses,
  a semicolon or two sentences. This covers captions, tables, alt text and code comments. Number and version ranges
  keep the en dash (`3.10–3.13`).
- **AI-tell vocabulary:** load-bearing, delve, leverage (as a verb), unlock, elevate, empower, foster, streamline,
  tapestry, landscape (figurative), realm, journey (figurative), testament, beacon, cornerstone, paradigm, robust,
  seamless, crucial, pivotal, vital, cutting-edge, game-changing, best-in-class, a myriad of, navigate
  (figurative), underscore, nuanced. "Harness" is allowed only for a test or golden harness.
- **Throat-clearing:** it's worth noting, it's important to note, let's dive in, here's the thing, that said,
  moreover, furthermore, in conclusion, in short, at the end of the day.
- **Tics:** honest, honestly, plainly, obviously, simply, just (as filler).

## 2. Banned constructions

| Construction | Example | Write instead |
|---|---|---|
| Statement plus fragment | "Four directory levels, and no supported way to reach them." | "The file sits four levels above the package, and the package has no supported way to reach it." |
| The page narrating itself | "Everything above is mechanism." "The answer is short." | Delete the sentence and start with the point. |
| Fragment as a paragraph opener | "Five keys. None of them is a path." | "None of the five keys is a path inside your package." |
| "X, not Y" antithesis | "Declare sources, not verdicts." | State the positive claim. Keep a contrast only when the reader really believes Y. |
| Drumroll line | "This matters." "That is the whole setup." | Say the consequence directly. |
| Colon reveal | "The catch: …" | Make the claim as an ordinary sentence. |
| Rule of three for rhythm | "fast, safe, and simple" | Keep a list only when there really are three things. |
| Comma tail | "…, ensuring every check runs." | Give it a subject and make it a sentence, or cut it. |
| Stacked hedges | "can potentially help" | Pick one hedge, or none. |

## 3. What good looks like

- Full sentences with a subject and a verb, one idea each. Vary the length because the content varies.
- Concrete nouns and real numbers: the version, the command, the check ID, the measured result.
- Say what is not done yet in ordinary words, once, and mark planned documents _(Planned)_ as the `docs` skill
  says. Status is a fact here, so state it precisely.
- Show the reader the command and its real output instead of describing it.
