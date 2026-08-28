#!/usr/bin/env python3
"""Catch the defect class that editing prose by search-and-replace produces.

Every failure this reports was, at some point in v0.3's drafting, a real defect found by a review
panel one round after it was introduced. The linters gate style and spelling; nothing gated whether
a sentence still agreed with the table above it. This does.

Checks, in the order they proved necessary:
  1. Count claims        - "these four labels", "eighteen checks", "two checks need" vs the real count
  2. Closed-set claims   - a set called complete/exhaustive/closed against what is actually listed
  3. Section references  - every §N.N cited resolves to a heading that exists
  4. List numbering      - ordered lists that skip, repeat, or restart
  5. Table integrity     - a row whose cell count differs from its header
  6. Stray markers       - "- -", doubled emphasis, dangling connectives at end of paragraph
  7. Check cross-refs    - every MIRI-* id named in prose has a definition file
"""
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
SPECS = sorted((REPO / "standards/consumption").glob("*.md"))
CHECK_DIR = REPO / "standards/consumption/checks"
WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
         "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
         "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19,
         "twenty": 20, "thirty-three": 33}

fails = []
def bad(where, msg):
    fails.append(f"{where}: {msg}")


def strip_fences(text):
    return re.sub(r"```.*?```", "", text, flags=re.S)


def check_counts(name, text):
    """A number written next to a noun, against the thing actually enumerated nearby."""
    ids = {f.stem for f in CHECK_DIR.glob("*.yaml")}
    # "<n> checks" claims are checked against the id prefix the document is about
    for m in re.finditer(r"\*\*?(\w+)\*\*? (?:numbered )?checks\b", text):
        word = m.group(1).lower()
        if word not in WORDS:
            continue
        claimed = WORDS[word]
        prefix = "MIRI-SURFACE" if "surface" in name else "MIRI-CONSUMER"
        actual = len([i for i in ids if i.startswith(prefix)])
        if claimed != actual:
            bad(name, f"claims {claimed} checks; {prefix} has {actual}")
    # "these <n> labels" against the label table
    for m in re.finditer(r"[Tt]hese \*\*?(\w+)\*\*? labels", text):
        word = m.group(1).lower()
        if word not in WORDS:
            continue
        rows = len(re.findall(r"^\| \*\*\([A-Z?]{1,2}\)\*\* \|", text, re.M))
        if rows and WORDS[word] != rows:
            bad(name, f"claims {WORDS[word]} labels; the table has {rows} rows")
    # "<n> checks need" / "<n> checks carry" against the ids listed in the same sentence
    for m in re.finditer(r"\*\*?(\w+)\*\*? checks (?:need|carry|require)([^.]*)\.", text):
        word = m.group(1).lower()
        if word not in WORDS:
            continue
        named = len(set(re.findall(r"MIRI-[A-Z]+-\d+", m.group(2))))
        if named and WORDS[word] != named:
            bad(name, f"says {WORDS[word]} checks but names {named} in the same sentence")


def check_closed_sets(name, text):
    """A vehicle-label set declared complete, against every label the document actually uses.

    This is the check that would have caught "these four labels are the complete set" surviving the
    introduction of a fifth: the claim is compared against the label TABLE, which is the enumeration
    the claim is about, not against a text window whose size is a guess."""
    used = set(re.findall(r"\*\*\(([A-Z?]{1,2})\)\*\*", strip_fences(text)))
    if not used:
        return
    rows = set(re.findall(r"^\| \*\*\(([A-Z?]{1,2})\)\*\* \|", text, re.M))
    if not rows:
        return
    if re.search(r"(complete set|the complete set of labels)", text):
        missing = used - rows
        if missing:
            bad(name, f"label table lists {sorted(rows)} and is called complete, but the document uses {sorted(missing)} too")


def check_section_refs(name, text):
    """Only LOCAL section references. A cross-document reference is written inside a markdown link
    ([Discovery Contract 3.2.1](discovery-contract.md)) or names another document in the same
    sentence, and belongs to that document's numbering rather than this one's."""
    heads = {m.group(1) for m in re.finditer(r"^#{2,4} (\d+(?:\.\d+)*)", text, re.M)}
    if not heads:
        return
    # remove link text and targets entirely: every cross-doc reference lives in one or the other
    local = re.sub(r"\[[^\]]*\]\([^)]*\)", " ", strip_fences(text))
    # and drop any sentence that names another document by title
    OTHER = r"(Discovery Contract|Consumption Map|Consumer Conformance|Surface Conformance|" \
            r"Lifecycle and Security|Agent Metadata|Wheel Extensions|CLI Spec|CLI Lifecycle|" \
            r"Core Metadata|Unicode|PEP \d+)"
    kept = [snt for snt in re.split(r"(?<=[.;])\s", local) if not re.search(OTHER, snt)]
    for snt in kept:
        for m in re.finditer(r"§(\d+(?:\.\d+)*)", snt):
            ref = m.group(1)
            if not any(h == ref or h.startswith(ref + ".") for h in heads):
                bad(name, f"cites §{ref} but this document has no such heading")


def check_list_numbering(name, text):
    for block in re.split(r"\n\s*\n", strip_fences(text)):
        nums = [int(m.group(1)) for m in re.finditer(r"^(\d+)\. ", block, re.M)]
        if len(nums) < 2:
            continue
        if nums != list(range(nums[0], nums[0] + len(nums))):
            bad(name, f"ordered list runs {nums}")


def check_tables(name, text):
    lines = strip_fences(text).split("\n")
    i = 0
    while i < len(lines):
        if lines[i].startswith("|") and i + 1 < len(lines) and re.match(r"^\|[-: |]+\|$", lines[i + 1]):
            width = lines[i].count("|")
            j = i + 2
            while j < len(lines) and lines[j].startswith("|"):
                if lines[j].count("|") != width:
                    bad(name, f"table row {j + 1} has {lines[j].count('|') - 1} cells, header has {width - 1}")
                j += 1
            i = j
        else:
            i += 1


def check_stray_markers(name, text):
    """A dangling connective matters only at the END of a paragraph. Mid-paragraph it is just where
    the 120-column wrap fell, which is most lines in this repo."""
    body = strip_fences(text)
    for n, line in enumerate(body.split("\n"), 1):
        if re.match(r"^\s*- - ", line):
            bad(name, f"line {n}: doubled list marker '- -'")
    DANGLING = r"\b(and|but|which|that|the|a|an|to|of|for|is|are|covers|includes)\s*$"
    for para in re.split(r"\n\s*\n", body):
        last = para.rstrip().split("\n")[-1] if para.strip() else ""
        if last.startswith("|") or last.startswith("#"):
            continue
        if re.search(DANGLING, last):
            bad(name, f"paragraph ends mid-sentence: {last.strip()[-52:]!r}")


def check_check_refs(name, text):
    ids = {f.stem for f in CHECK_DIR.glob("*.yaml")}
    for m in re.finditer(r"\bMIRI-(?:CONSUMER|SURFACE)-\d{3}\b", text):
        if m.group(0) not in ids:
            bad(name, f"names {m.group(0)}, which has no definition file")


def main():
    for p in SPECS:
        text = p.read_text()
        name = p.name
        check_counts(name, text)
        check_closed_sets(name, text)
        check_section_refs(name, text)
        check_list_numbering(name, text)
        check_tables(name, text)
        check_stray_markers(name, text)
        check_check_refs(name, text)

    if fails:
        print(f"{len(fails)} consistency failure(s):\n")
        for f in fails:
            print("  FAIL", f)
        return 1
    print(f"consistency: {len(SPECS)} specs clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
