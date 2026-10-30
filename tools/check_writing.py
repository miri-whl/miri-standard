#!/usr/bin/env python3
"""Flag AI-writing tells in HTML and Markdown copy (see WRITING-RULES.md).

    python3 scripts/check-writing.py website-0.11.5/blogs/what-actually-goes-into-a-wheel.html
    python3 scripts/check-writing.py website-0.11.5            # a whole folder
    python3 scripts/check-writing.py --include-head index.html   # also <title>/<meta>
    python3 scripts/check-writing.py --allow harness docs/       # a project's technical terms
    python3 scripts/check-writing.py --dupes website-0.11.5      # sentences/headings repeated across pages

Exit code 1 when anything is found, so it can gate a publish. Code blocks
(<pre>, <code>, fenced Markdown) are skipped. This catches the mechanical tells;
the constructions table in WRITING-RULES.md still needs a human read.
"""

from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path
from typing import Iterator, List, NamedTuple

SUFFIXES = (".html", ".htm", ".md")

# A spaced hyphen (" - ") used as a dash counts too; the check YAMLs carried 28 of them unflagged.
DASH = re.compile(r"—|&mdash;|&#8212;|\s--\s|\s–\s|\s&ndash;\s|(?<=\w)\s-\s(?=\w)")

BANNED_WORDS = [
    "load-bearing", "load bearing", "delve", "delves", "delving", "leverage", "leverages",
    "leveraging", "harness", "harnessing", "unlock", "unlocks", "unlocking", "elevate",
    "empower", "empowers", "empowering", "foster", "fostering", "streamline", "streamlines",
    "tapestry", "realm", "testament", "beacon", "cornerstone", "paradigm", "robust",
    "seamless", "seamlessly", "crucial", "pivotal", "cutting-edge", "game-changing",
    "best-in-class", "a myriad of", "underscore", "underscores", "nuanced",
    "it's worth noting", "it is worth noting", "it's important to note", "let's dive in",
    "here's the thing", "that said", "moreover", "furthermore", "in conclusion", "in short",
    "at the end of the day", "honest", "honestly", "plainly", "is a permission",
]
WORD_RE = re.compile(r"\b(?:" + "|".join(re.escape(w) for w in BANNED_WORDS) + r")\b", re.IGNORECASE)
# Terms the standard defines that contain a banned word. "Honest degradation" names a consumer check category
# (MIRI-CONSUMER-001 to 003) and a spec term, so it stays; every other "honest" is still flagged.
DEFINED_TERMS = re.compile(r"\bhonest[- ]degradation\b", re.IGNORECASE)

# Sentence-level heuristics: each is (label, pattern) applied to one sentence.
CONSTRUCTIONS = [
    ("self-narration", re.compile(
        r"^(?:Everything (?:above|below)|The opening (?:promised|said)|The answer is (?:short|simple)|"
        r"Here(?:'s| is) (?:why|how|what|the)|This is a tour|That is the (?:whole|list|point)|"
        r"Hold on to that|As we(?:'ll| will) see)\b", re.IGNORECASE)),
    ("statement + fragment", re.compile(
        r"^[A-Z][\w'’ -]{2,40}, and no [\w'’ -]{3,60}\.$")),
    ("fragment opener", re.compile(r"^(?:[A-Z][a-z]+ ){0,2}[A-Za-z]+s?\.$")),
    ("X, not Y", re.compile(r"\b\w+, not (?:a |an |the |one |in |on )?\w+[.;,]|\bnot (?:just|only|merely) [^.]{3,60}\bbut\b|"
                            r"\bisn'?t\b[^.]{2,40}[;:,] it'?s\b", re.IGNORECASE)),
    ("drumroll", re.compile(r"^(?:This matters(?: practically)?|That is the whole point|"
                            r"That'?s it|The catch|Here'?s the catch)\b[.:]?", re.IGNORECASE)),
]
SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z“\"(])")


class Hit(NamedTuple):
    path: Path
    line: int
    kind: str
    text: str


def _blank(match: re.Match[str]) -> str:
    """Replace a skipped region with the same number of newlines, keeping line numbers."""
    return "\n" * match.group(0).count("\n")


def prose(text: str, is_html: bool, include_head: bool) -> str:
    """Return the text with code, markup and (by default) the HTML head blanked out."""
    if is_html:
        if not include_head:
            text = re.sub(r"<head\b.*?</head>", _blank, text, flags=re.S | re.I)
        text = re.sub(r"<(pre|code|script|style)\b.*?</\1>", _blank, text, flags=re.S | re.I)
        text = re.sub(r"<!--.*?-->", _blank, text, flags=re.S)
        # A bold label opening a list item ("<li><strong>Analytics.</strong> We use…")
        # is a format, not a fragment; turn its full stop into a colon.
        text = re.sub(r"(<li>\s*<strong>[^<]{1,40})\.(</strong>)", r"\1:\2", text)
        # Alt text, titles and aria labels are read by people (and screen readers) too.
        text = re.sub(r'<[^>]*?\b(?:alt|title|aria-label)="([^"]*)"[^>]*>', lambda m: " " + m.group(1) + " ", text)
        # Inline tags join the text around them ("miri<span>-</span>standard" is one word); block tags separate.
        text = re.sub(r"</?(?:span|a|em|strong|b|i|sup|sub)\b[^>]*>", "", text, flags=re.I)
        text = re.sub(r"<[^>]+>", " ", text)
        return text
    text = re.sub(r"```.*?```", _blank, text, flags=re.S)
    return re.sub(r"`[^`\n]*`", " ", text)


def check_file(path: Path, include_head: bool, allow: frozenset = frozenset()) -> Iterator[Hit]:
    raw = path.read_text(encoding="utf-8", errors="replace")
    is_html = path.suffix.lower() in (".html", ".htm")
    for lineno, line in enumerate(prose(raw, is_html, include_head).splitlines(), 1):
        if is_html:
            if DASH.search(line):
                yield Hit(path, lineno, "em dash", html.unescape(line).strip())
            line = html.unescape(line)
        elif DASH.search(line):
            yield Hit(path, lineno, "em dash", line.strip())
        defined = [m.span() for m in DEFINED_TERMS.finditer(line)]
        for match in WORD_RE.finditer(line):
            if match.group(0).lower() in allow:
                continue
            if any(a <= match.start() < b for a, b in defined):
                continue
            yield Hit(path, lineno, f"banned word '{match.group(0).lower()}'", line.strip())
        for sentence in SENTENCE_SPLIT.split(re.sub(r"\s+", " ", line).strip()):
            for label, pattern in CONSTRUCTIONS:
                if pattern.search(sentence):
                    yield Hit(path, lineno, label, sentence)


def duplicates(paths: List[Path], min_files: int = 3) -> List[str]:
    """Sentences (6+ words) and headings that appear in min_files or more files: a template showing."""
    sentences: dict[str, set] = {}
    headings: dict[str, set] = {}
    for path in paths:
        raw = path.read_text(encoding="utf-8", errors="replace")
        is_html = path.suffix.lower() in (".html", ".htm")
        if is_html:
            for h in re.findall(r"<h[23][^>]*>(.*?)</h[23]>", raw, re.S | re.I):
                text = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", h))).strip()
                if text:
                    headings.setdefault(text, set()).add(path)
            raw = re.sub(r"<(nav|footer)\b.*?</\1>", " ", raw, flags=re.S | re.I)
        else:
            for h in re.findall(r"^#{2,3}\s+(.+)$", raw, re.M):
                headings.setdefault(h.strip(), set()).add(path)
        text = re.sub(r"\s+", " ", html.unescape(prose(raw, is_html, False)))
        for sentence in SENTENCE_SPLIT.split(text):
            sentence = sentence.strip()
            if len(sentence.split()) >= 6:
                sentences.setdefault(sentence, set()).add(path)
    out = []
    for label, table in (("heading", headings), ("sentence", sentences)):
        for text, files in sorted(table.items(), key=lambda kv: -len(kv[1])):
            if len(files) >= min_files:
                out.append(f"{len(files):3d} files  {label}: {text[:140]}")
    return out


def targets(paths: List[str]) -> Iterator[Path]:
    for name in paths:
        root = Path(name)
        if root.is_dir():
            yield from sorted(p for p in root.rglob("*") if p.suffix.lower() in SUFFIXES)
        else:
            yield root


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("paths", nargs="+", help="files or folders to check")
    parser.add_argument("--include-head", action="store_true", help="also check <title> and <meta> text")
    parser.add_argument("--summary", action="store_true", help="print counts per file only")
    parser.add_argument("--dupes", action="store_true", help="report sentences and headings repeated across 3+ files")
    parser.add_argument("--allow", default="", help="comma-separated banned words this project uses technically")
    args = parser.parse_args()
    allow = frozenset(w.strip().lower() for w in args.allow.split(",") if w.strip())
    if args.dupes:
        found = duplicates(list(targets(args.paths)))
        print("\n".join(found) if found else "no sentence or heading repeats across 3+ files")
        return 1 if found else 0

    hits = [hit for path in targets(args.paths) for hit in check_file(path, args.include_head, allow)]
    if args.summary:
        per: dict[Path, int] = {}
        for hit in hits:
            per[hit.path] = per.get(hit.path, 0) + 1
        for path, count in sorted(per.items(), key=lambda item: -item[1]):
            print(f"{count:4d}  {path}")
    else:
        for hit in hits:
            print(f"{hit.path}:{hit.line}: {hit.kind}: {hit.text[:160]}")
    print(f"{len(hits)} finding(s)", file=sys.stderr)
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
