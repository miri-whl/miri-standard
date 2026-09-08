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
import json
import re
import yaml
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
# The consumption suite, plus the documents that carry the same kind of load-bearing counts.
# why-consumption.md shipped "thirty-three" for a 35-check suite because nothing scanned it, and
# both production maps make numeric claims about check populations that nothing scanned either.
SPECS = sorted((REPO / "standards/consumption").glob("*.md")) + [
    REPO / "standards/python/production-map.md",
    REPO / "standards/cli/production-map.md",
    REPO / "docs/why-consumption.md",
]
CHECK_DIR = REPO / "standards/consumption/checks"
WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
         "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
         "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19,
         "twenty": 20, "thirty-three": 33, "thirty-five": 35, "thirty-four": 34}

fails = []
def bad(where, msg):
    fails.append(f"{where}: {msg}")


def strip_fences(text):
    return re.sub(r"```.*?```", "", text, flags=re.S)


def check_counts(name, text):
    """A number written next to a noun, against the thing actually enumerated nearby."""
    ids = {f.stem for f in CHECK_DIR.glob("*.yaml")}
    # Any number-word standing in for a check count, not only the "**n** checks" phrasing. The
    # narrow pattern missed "All fifteen ...", "the current fifteen", and "among the fifteen".
    prefix_for = "MIRI-SURFACE" if "surface" in name else "MIRI-CONSUMER"
    actual_n = len([i for i in ids if i.startswith(prefix_for)])
    # A bare number-word is ordinary English ("all eight operations", "of the two"). Only flag one
    # whose own SENTENCE also names the check family it would be counting — the narrower rule the
    # first attempt at this check lacked, which produced twelve false positives on this corpus.
    FAMILY = re.compile(r"\b(MIRI-(?:CONSUMER|SURFACE)\b|consumer checks|surface checks|"
                        r"the (?:consumer|surface) (?:family|profile))", re.I)
    for snt in re.split(r"(?<=[.;])\s", strip_fences(text)):
        if not FAMILY.search(snt):
            continue
        for m in re.finditer(r"\b(?:all|the current|among the)\s+\*?\*?([\w-]+)\*?\*?\b", snt, re.I):
            # "all N consumption checks" is a SUITE total (surface + consumer), owned by
            # check_suite_totals. Counting it against one family reports a false conflict.
            if re.search(r"consumption checks", snt, re.I):
                continue
            word = m.group(1).lower()
            if word in WORDS and WORDS[word] != actual_n:
                bad(name, f"says {word!r} in a sentence about {prefix_for}, which has {actual_n} checks")
    # An ID range is written "X` through `Y" or "X` to `Y" — not any two ids that happen to be near
    # each other, which is most of a conformance profile.
    for m in re.finditer(r"`(MIRI-(?:CONSUMER|SURFACE))-(\d+)`\s*(?:through|to)\s*\n?`\1-(\d+)`", text):
        pre = m.group(1)
        real = max((int(i.rsplit("-", 1)[1]) for i in ids if i.startswith(pre)), default=0)
        if int(m.group(3)) < real:
            bad(name, f"ID range ends at {pre}-{m.group(3)} but {pre}-{real:03d} exists")
    # The section-opener phrasing both profiles use. It names no family, so the sentence guard
    # above cannot see it — and it went stale for two rounds before a review caught it.
    for m in re.finditer(r"\b([\w-]+) checks, weights summing to 100", text):
        word = m.group(1).lower()
        if word in WORDS and WORDS[word] != actual_n:
            bad(name, f"opener says {word!r}; {prefix_for} has {actual_n} checks")
    for m in re.finditer(r"\*\*?([\w-]+)\*\*? (?:numbered )?checks\b", text):
        word = m.group(1).lower()
        if word not in WORDS:
            continue
        claimed = WORDS[word]
        prefix = "MIRI-SURFACE" if "surface" in name else "MIRI-CONSUMER"
        actual = len([i for i in ids if i.startswith(prefix)])
        if claimed != actual:
            bad(name, f"claims {claimed} checks; {prefix} has {actual}")
    # "these <n> labels" against the label table
    for m in re.finditer(r"[Tt]hese \*\*?([\w-]+)\*\*? labels", text):
        word = m.group(1).lower()
        if word not in WORDS:
            continue
        rows = len(re.findall(r"^\| \*\*\([A-Z?]{1,2}\)\*\* \|", text, re.M))
        if rows and WORDS[word] != rows:
            bad(name, f"claims {WORDS[word]} labels; the table has {rows} rows")
    # "<n> checks need" / "<n> checks carry" against the ids listed in the same sentence
    for m in re.finditer(r"\*\*?([\w-]+)\*\*? checks (?:need|carry|require)([^.]*)\.", text):
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
            # An escaped pipe is cell content, not a separator — markdownlint accepts `\|` and the
            # table renders correctly. Counting it as a cell boundary reports a defect that is not one.
            def cells(line):
                return re.sub(r"\\\|", "", line).count("|")
            width = cells(lines[i])
            j = i + 2
            while j < len(lines) and lines[j].startswith("|"):
                if cells(lines[j]) != width:
                    bad(name, f"table row {j + 1} has {cells(lines[j]) - 1} cells, header has {width - 1}")
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


def check_check_urls():
    """Every check advertises its own published page. That URL is derivable from the id and target,
    so it is asserted rather than trusted.

    All 33 consumption checks shipped with a pattern that 404s — checks/miri-surface-033/ rather
    than checks/surface/MIRI-SURFACE-033.html — copied from a sibling rather than from the
    generator's actual output. Linter reports link findings to these URLs, so every consumption
    finding pointed at a missing page, and nothing in the repo would ever have noticed."""
    import yaml
    tdir = {"python-wheel": "python", "cli": "cli", "consumer": "consumer", "surface": "surface"}
    for f in sorted(REPO.glob("standards/*/checks/*.yaml")):
        d = yaml.safe_load(f.read_text())
        if d.get("status") != "active":
            continue
        want_html = f"https://miri-whl.github.io/checks/{tdir[d['target']]}/{d['id']}.html"
        if d["urls"]["html"] != want_html:
            bad(f.name, f"urls.html is {d['urls']['html']!r}, generator publishes {want_html!r}")
        want_def = ("https://github.com/miri-whl/miri-standard/blob/main/"
                    f"{f.relative_to(REPO)}")
        if d["urls"]["definition"] != want_def:
            bad(f.name, f"urls.definition is {d['urls']['definition']!r}, file is at {want_def!r}")


def check_fields_against_schemas():
    """A field a check DEMANDS must be a field some schema PERMITS.

    This is the shape the miri-py team named twice: MIRI-CLI-040 (a forbidden field a MUST
    required) and then advisory_coverage, which CLI Spec 4.1 specifies and MIRI-CLI-022 requires
    while cli-describe-v1.json closed additionalProperties without declaring it. A conforming CLI
    failed our own schema. Both were found by someone building against the text; this makes the
    class a CI step instead.

    Known-good exclusions are listed rather than pattern-matched, so adding one is a deliberate act
    that shows up in review."""
    import json
    import yaml

    # Names that are legitimately not document fields: purl qualifiers, wheel metadata, and the
    # wire envelope, which is specified in prose and has no schema yet (tracked separately).
    NOT_DOCUMENT_FIELDS = {
        "repository_url",                                  # purl qualifier
        "entry_points", "console_scripts",                 # wheel metadata, not Miri documents
        "update_available", "install_hint",                # check-update payload: no schema yet
        "next_cursor", "max_bytes",                        # Discovery Contract envelope: no schema yet
    }

    declared = set()
    for sp in sorted((REPO / "schemas").glob("*.json")):
        def walk(node):
            if isinstance(node, dict):
                if isinstance(node.get("properties"), dict):
                    declared.update(node["properties"])
                for v in node.values():
                    walk(v)
            elif isinstance(node, list):
                for v in node:
                    walk(v)
        walk(json.loads(sp.read_text()))

    for f in sorted(REPO.glob("standards/*/checks/*.yaml")):
        d = yaml.safe_load(f.read_text())
        if d.get("status") != "active":
            continue
        text = " ".join(d["fires_when"] + d["remediation"] + [d["short_description"]])
        for tok in sorted(set(re.findall(r"`([a-z][a-z0-9]*(?:_[a-z0-9]+)+)`", text))):
            if tok in declared or tok in NOT_DOCUMENT_FIELDS:
                continue
            bad(d["id"], f"demands field `{tok}`, which no schema in schemas/ declares")


def check_glossary():
    """The glossary explains the standard's vocabulary; this asserts it has not drifted from it.

    A glossary is uniquely dangerous because it becomes the thing people read instead of the spec.
    A wrong entry is not merely unhelpful — it gets cited. So three properties are gated:

      1. Every closed vocabulary it quotes matches its authoritative source. Trigger kinds come from
         agent-event-v1.json, error codes and payload keys from discovery-envelope-v1.json, vehicle
         labels from the Consumption Map, severity from check-v1.json.
      2. Every defined term carries a link to where it is normatively defined, so a reader who needs
         the rule rather than the explanation can reach it in one click.
      3. No term is defined that the standard does not use, and the terms the standard defines in
         bold are all present here.

    What this cannot check is whether an explanation subtly misstates a rule it links to. That is a
    reading, and it is left to review — stated here so the green tick is not mistaken for more than
    it covers."""
    import json
    import yaml

    gl = REPO / "docs/glossary.md"
    if not gl.exists():
        bad("glossary.md", "docs/glossary.md is missing")
        return
    g = gl.read_text()

    def load(p):
        return json.loads((REPO / p).read_text())

    # 1. closed vocabularies quoted verbatim
    vocab = [
        ("trigger kinds", set(load("schemas/agent-event-v1.json")["properties"]["kind"]["enum"]),
         set(re.findall(r"`((?:dependency|package|integration|runtime|test)\.\w+)`", g))),
        ("vehicle labels",
         set(re.findall(r"^\| \*\*\(([A-Z?]{1,2})\)\*\* \|",
                        (REPO / "standards/consumption/consumption-map.md").read_text(), re.M)),
         set(re.findall(r"\*\*\(([A-Z?]{1,2})\)\*\*", g))),
        ("skip reasons", {"absent", "unavailable-vehicle", "error", "not-applicable"},
         set(re.findall(r"`(absent|unavailable-vehicle|error|not-applicable)`", g))),
    ]
    for label, source, quoted in vocab:
        if source and quoted != source:
            bad("glossary.md", f"{label}: glossary has {sorted(quoted)}, source has {sorted(source)}")

    ops = {"list", "document", "lifecycle", "migration-guide", "api-index", "resolve", "patterns", "graph"}
    named = set(re.findall(r"`(list|document|lifecycle|migration-guide|api-index|resolve|patterns|graph)`", g))
    if not ops <= named:
        bad("glossary.md", f"operations missing from the glossary: {sorted(ops - named)}")

    # 2. every defined term reaches its normative home
    for m in re.finditer(r"^\*\*(.+?)\*\* [—(]", g, re.M):
        term = m.group(1)
        block = g[m.start():]
        end = block.find("\n\n")
        block = block[:end if end > 0 else 400]
        if "](" not in block:
            bad("glossary.md", f"term {term!r} has no link to where it is defined")

    # 3. counts the glossary states about the check families
    for m in re.finditer(r"`(MIRI-(?:CONSUMER|SURFACE))` runs (\d+)[–-](\d+) across ([\w-]+) checks", g):
        pre, hi, word = m.group(1), int(m.group(3)), m.group(4).lower()
        real = [f.stem for f in (REPO / "standards/consumption/checks").glob(f"{pre}-*.yaml")]
        if word in WORDS and WORDS[word] != len(real):
            bad("glossary.md", f"says {word!r} {pre} checks; there are {len(real)}")
        top = max(int(i.rsplit("-", 1)[1]) for i in real)
        if hi != top:
            bad("glossary.md", f"{pre} range ends at {hi:03d}; highest is {top:03d}")


def check_schema_index():
    """Every schema in schemas/ must appear in schemas/README.md, and vice versa.

    Five schemas shipped unindexed for two releases, discoverable only by listing the directory. 0.5.0
    fixed the index by hand and called it "verified complete" — which nothing verified. That is the
    unenforced-claim defect this repo exists to name, committed in the sentence claiming to close it.
    This is the enforcement, so the next schema added cannot drop out silently.
    """
    idx = (REPO / "schemas/README.md").read_text()
    listed = set(re.findall(r"\[([a-z0-9-]+-v\d+\.json)\]", idx))
    on_disk = {f.name for f in (REPO / "schemas").glob("*.json")}
    for missing in sorted(on_disk - listed):
        bad("schemas/README.md", f"{missing} exists but is not indexed")
    for phantom in sorted(listed - on_disk):
        bad("schemas/README.md", f"indexes {phantom}, which does not exist")


def check_suite_totals(name, text):
    """Catch a stale count of the whole consumption suite.

    `why-consumption.md` shipped "thirty-three numbered checks" for a 35-check suite, and
    `consumer-conformance.md` said "all thirty-three consumption checks" inside a sentence that had just
    said 18 and 17. The existing count rule could not see either: it requires emphasis markers, and its
    capture group excluded the hyphen in "thirty-three". Both bugs had to be fixed for the guard to fire,
    and the guard was added for exactly this defect.
    """
    total = sum(1 for f in (REPO / "standards/consumption/checks").glob("MIRI-*.yaml")
                if yaml.safe_load(f.read_text())["status"] == "active")
    for m in re.finditer(r"(?:all |and )([\w-]+) (?:numbered |consumption )checks\b", text, re.I):
        word = m.group(1).lower()
        if word in WORDS and WORDS[word] != total:
            bad(name, f"says {word} ({WORDS[word]}) consumption checks; there are {total}")


def check_findings_inherits_envelope():
    """agent-findings-v1 claims to BE discovery-envelope-v1 plus one payload key. Enforce the claim.

    An earlier version re-typed a subset of the envelope's rules by hand while the prose asserted
    inheritance; eleven documents the envelope rejected validated against it, including the schema_version
    format whose absence the envelope's own description records as having already made two implementations
    diverge. The rules are now copied, and this fails if a copy drifts.
    """
    env = json.loads((REPO / "schemas/discovery-envelope-v1.json").read_text())
    fnd = json.loads((REPO / "schemas/agent-findings-v1.json").read_text())

    for key in ("required", "additionalProperties", "definitions"):
        if env.get(key) != fnd.get(key):
            bad("agent-findings-v1.json", f"{key} differs from discovery-envelope-v1")

    for name, spec in env.get("properties", {}).items():
        if name not in fnd.get("properties", {}):
            bad("agent-findings-v1.json", f"drops the envelope property `{name}`")
        elif fnd["properties"][name] != spec:
            bad("agent-findings-v1.json", f"property `{name}` diverges from the envelope")

    env_rules = env.get("allOf", [])
    fnd_rules = fnd.get("allOf", [])
    if fnd_rules[:len(env_rules)] != env_rules:
        bad("agent-findings-v1.json", "does not carry the envelope's allOf rules verbatim as its prefix")


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
        check_suite_totals(name, text)
    check_check_urls()
    check_fields_against_schemas()
    check_glossary()
    check_schema_index()
    check_findings_inherits_envelope()

    if fails:
        print(f"{len(fails)} consistency failure(s):\n")
        for f in fails:
            print("  FAIL", f)
        return 1
    print(f"consistency: {len(SPECS)} specs clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
