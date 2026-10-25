#!/usr/bin/env python3
"""Check that an edit pass changed wording only: compare a snapshot to the edited tree.

    cp -R site site.before          # snapshot before editing
    ... edit ...
    python3 scripts/verify-wording-only.py site.before site

For every file that changed (HTML and Markdown), it reports:
  - anchors, links, image sources and TODO notes that disappeared
  - numbers in the visible text that were added or removed (a changed figure shows up)
  - RFC 2119 keywords (MUST, SHOULD, MAY, …) whose count changed (a normative change)
  - code blocks that changed (code is never "wording")
  - HTML only: a <nav> or <footer> that changed, and files that no longer parse
Exit code 1 when any file needs a look. Every flag is a prompt to read, not proof of a
problem: a heading that reuses a number already on the page shows up too.
"""

from __future__ import annotations

import collections
import html
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

SUFFIXES = (".html", ".htm", ".md")
RFC2119 = re.compile(r"\b(MUST NOT|MUST|SHALL NOT|SHALL|SHOULD NOT|SHOULD|REQUIRED|RECOMMENDED|NOT RECOMMENDED|MAY|OPTIONAL)\b")
SPELLED = {"one": "1", "two": "2", "three": "3", "four": "4", "five": "5", "six": "6",
           "seven": "7", "eight": "8", "nine": "9", "ten": "10"}


def block(text: str, tag: str) -> str:
    match = re.search(rf"<{tag}\b.*?</{tag}>", text, re.S | re.I)
    return match.group(0) if match else ""


def code_blocks(text: str, is_html: bool) -> list[str]:
    if is_html:
        return re.findall(r"<pre\b.*?</pre>", text, re.S | re.I)
    return re.findall(r"```.*?```", text, re.S)


def visible(text: str, is_html: bool) -> str:
    if is_html:
        body = text[text.find("<body"):] if "<body" in text else text
        body = re.sub(r"<(script|style|nav|footer|pre)\b.*?</\1>", " ", body, flags=re.S | re.I)
        body = re.sub(r"<!--.*?-->", " ", body, flags=re.S)
        return html.unescape(re.sub(r"<[^>]+>", " ", body))
    return re.sub(r"```.*?```", " ", text, flags=re.S)


def numbers(text: str) -> collections.Counter:
    found = [n.rstrip(".,") for n in re.findall(r"\d[\d,.]*\d|\d", text)]
    found += [SPELLED[w.lower()] for w in re.findall(r"\b(" + "|".join(SPELLED) + r")\b", text, re.I)]
    return collections.Counter(n for n in found if len(n) > 1)


def references(text: str, is_html: bool) -> dict[str, set[str]]:
    if is_html:
        return {"id": set(re.findall(r'\bid="([^"]+)"', text)),
                "link": set(re.findall(r'\bhref="([^"]+)"', text)),
                "image": set(re.findall(r'\bsrc="([^"]+)"', text)),
                "TODO": set(re.findall(r"TODO\([^)]*\)[^>\n]{0,60}", text))}
    return {"link": set(re.findall(r"\]\(([^)\s]+)", text)),
            "TODO": set(re.findall(r"TODO\([^)]*\)[^\n]{0,60}", text))}


def compare(before: Path, after: Path) -> list[str]:
    old, new = before.read_text(errors="replace"), after.read_text(errors="replace")
    is_html = after.suffix.lower() in (".html", ".htm")
    notes = []
    if is_html:
        for tag in ("nav", "footer"):
            if block(new, tag) != block(old, tag):
                notes.append(f"<{tag}> changed")
    old_refs, new_refs = references(old, is_html), references(new, is_html)
    for kind in old_refs:
        lost = old_refs[kind] - new_refs[kind]
        if lost:
            notes.append(f"lost {kind}: {sorted(lost)[:5]}")
    if code_blocks(old, is_html) != code_blocks(new, is_html):
        notes.append("a code block changed")
    old_kw, new_kw = collections.Counter(RFC2119.findall(old)), collections.Counter(RFC2119.findall(new))
    if old_kw != new_kw:
        notes.append(f"RFC 2119 keywords changed: removed {dict(old_kw - new_kw)} added {dict(new_kw - old_kw)}")
    old_n, new_n = numbers(visible(old, is_html)), numbers(visible(new, is_html))
    if old_n != new_n:
        notes.append(f"numbers removed {dict(old_n - new_n)} added {dict(new_n - old_n)}")
    if is_html:
        try:
            HTMLParser().feed(new)
        except Exception as exc:  # noqa: BLE001
            notes.append(f"parse error: {exc}")
    return notes


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    before_root, after_root = Path(sys.argv[1]), Path(sys.argv[2])
    flagged = 0
    for after in sorted(p for p in after_root.rglob("*") if p.suffix.lower() in SUFFIXES):
        before = before_root / after.relative_to(after_root)
        if not before.exists() or before.read_bytes() == after.read_bytes():
            continue
        notes = compare(before, after)
        flagged += bool(notes)
        print(("CHECK " if notes else "OK    ") + str(after.relative_to(after_root))
              + "".join(f"\n      - {n}" for n in notes))
    print(f"\n{flagged} changed file(s) need a look")
    return 1 if flagged else 0


if __name__ == "__main__":
    sys.exit(main())
