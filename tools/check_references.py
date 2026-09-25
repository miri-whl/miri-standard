#!/usr/bin/env python3
"""Reconcile every check's spec citations against the specifications themselves.

The fourth normative-artifact pair. The standard has four kinds of normative artifact — check
`fires_when`, spec prose, schemas, and goldens — and each pair that can disagree needs a
cross-check. Three are already gated:

  fires_when x goldens          validate_fixtures.py  (a check demanding what a golden forbids)
  check fields x schemas        check_consistency.py  (a MUST requiring a field a schema rejects)
  golden envelopes x schema     validate_fixtures.py  (the delivered envelope schema, kept live)

This is the fourth: spec prose x fires_when. It gates the half that is mechanically decidable —
does the cited document exist, and does the cited section exist within it — and REPORTS the half
that is not, as a check-to-section list for human reconciliation.

The split is deliberate and was the miri-py team's recommendation. Asserting that a citation
resolves is sound. Asserting that a `fires_when` clause faithfully enforces the prose it cites is
a judgment, and a gate that claimed to make it would be worse than no gate: an ungated gate
produces confidence without coverage, and nobody looks behind a green tick.

Usage:
    python3 tools/check_references.py            # gate: fail on unresolvable citations
    python3 tools/check_references.py --report   # emit the check-to-section reconciliation list
"""
import argparse
import pathlib
import re
import sys

import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
SECTION = re.compile(r"§\s*(\d+(?:\.\d+)*)")


def headings(path):
    """Every numbered section in a specification, as strings: {'2', '2.5', '3.1.1', ...}."""
    found = set()
    for m in re.finditer(r"^#{2,6}\s+(\d+(?:\.\d+)*)[.\s]", path.read_text(), re.M):
        found.add(m.group(1))
    return found


def collect():
    rows, failures = [], []
    cache = {}
    for f in sorted(REPO.glob("standards/*/checks/*.yaml")):
        d = yaml.safe_load(f.read_text())
        if d.get("status") != "active":
            continue
        # a reference is relative to the suite directory, not the checks/ directory inside it
        suite = f.parent.parent
        for ref in d.get("references", []):
            if ref.get("type") != "spec":
                continue
            target = (suite / ref["url"]).resolve()
            if not target.exists():
                failures.append(f"{d['id']}: cites {ref['url']!r}, which does not exist "
                                f"(resolved against {suite.relative_to(REPO)}/)")
                continue
            if target not in cache:
                cache[target] = headings(target)
            for sec in SECTION.findall(ref.get("title", "")):
                if sec not in cache[target]:
                    failures.append(f"{d['id']}: cites §{sec} of {target.name}, which has no such section")
                rows.append((d["id"], target.relative_to(REPO).as_posix(), sec,
                             sec in cache[target]))
            if not SECTION.findall(ref.get("title", "")):
                rows.append((d["id"], target.relative_to(REPO).as_posix(), "—", True))
    return rows, failures


# Fields whose prose a producer reads. A PEP named in any of them is a citation the reader can see
# and cannot follow unless it is also in `references`.
PROSE_FIELDS = ("short_description", "long_description", "rationale", "fires_when",
                "remediation", "examples", "suggested_fix")
PEP_IN_PROSE = re.compile(r"PEP[\s\u00a0-]?(\d{3,4})")
PEP_IN_URL = re.compile(r"peps\.python\.org/pep-0*(\d{3,4})")
RFC_IN_PROSE = re.compile(r"RFC[\s\u00a0-]?(\d{3,4})")
# Every spelling the IETF serves, because this repository has used two of them. Matching only
# /rfc/rfcNNNN once made an audit report two RFCs as unlinked that were linked all along as
# /info/rfcNNNN/ — a gate that cannot read its own repository's convention manufactures work rather
# than finding it. The canonical form suggested below is datatracker: www.rfc-editor.org stalls
# under bursts, and CI requests the same RFC from several documents in quick succession, so its
# links failed the link check as a group while resolving fine one at a time.
RFC_IN_URL = re.compile(r"rfc-?editor\.org/(?:rfc|info)/rfc0*(\d{3,4})"
                        r"|datatracker\.ietf\.org/doc/html/rfc0*(\d{3,4})")

# Numbered documents only. "PEP 702" and "RFC 9745" name one document and can be turned into a URL
# with arithmetic; a check naming them is always citing them. Named bodies are NOT gateable the same
# way: 23 checks mention `purl` and 11 mention OSV, but most of those are our own field names
# (`identity.purl`) or an ecosystem aside, not a citation of the specification. Gating those would
# add 34 references nobody asked for and dilute the trail this rule exists to keep honest. They stay
# editorial, and the audit for them is a person reading the prose.


def unlinked_peps():
    """Every (check, PEP) pair where the check's own prose names a PEP its references omit.

    Proposed by the miri-py team, who render `type: external` references as the authority line on a
    failed check's fix card and found 21 such pairs across 18 checks in 0.7.1 — including PEP 702,
    the document behind the entire deprecation-coherence group, cited by nine checks and linked from
    one. Their report embedded 46 links and none reached a PEP it cited by number.

    Mechanical on purpose. The alternative is editorial judgment about which documents are important
    enough to link, which nothing can gate and everyone answers differently. This rule has one
    answer: if the text names it, the reader can reach it.
    """
    pairs = []
    for f in sorted(REPO.glob("standards/*/checks/*.yaml")):
        d = yaml.safe_load(f.read_text())
        if d.get("status") != "active":
            continue
        prose = " ".join(str(d.get(field, "")) for field in PROSE_FIELDS)
        urls = [str(ref.get("url", "")) for ref in (d.get("references") or [])]
        for kind, in_prose, in_url, canonical in (
                ("PEP", PEP_IN_PROSE, PEP_IN_URL, "https://peps.python.org/pep-{:04d}/"),
                ("RFC", RFC_IN_PROSE, RFC_IN_URL, "https://datatracker.ietf.org/doc/html/rfc{:d}")):
            cited = {int(n) for n in in_prose.findall(prose)}
            linked = {int(g) for u in urls for m in in_url.findall(u) for g in (m if isinstance(m, tuple) else (m,)) if g}
            for number in sorted(cited - linked):
                pairs.append((d["id"], kind, number, canonical.format(number)))
    return pairs


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--report", action="store_true",
                    help="print the check-to-section list for human reconciliation")
    args = ap.parse_args()
    rows, failures = collect()
    unlinked = unlinked_peps()

    if args.report:
        print(f"{'check':22s} {'cites':58s} {'section':>8s}")
        for cid, doc, sec, ok in rows:
            print(f"{cid:22s} {doc:58s} {('§' + sec) if sec != '—' else '—':>8s}"
                  f"{'' if ok else '   <- UNRESOLVED'}")
        print(f"\n{len(rows)} citation(s) across {len({r[0] for r in rows})} checks, "
              f"{len({r[1] for r in rows})} document(s).")
        print("The semantic half — whether each clause enforces what its section says — is not "
              "asserted here.\nIt is listed so a person can reconcile it, which is the only honest "
              "way to check a judgment.")
        return 0

    if failures:
        print(f"{len(failures)} unresolvable citation(s):\n")
        for f in failures:
            print("  FAIL", f)
        return 1
    if unlinked:
        print(f"{len(unlinked)} numbered document(s) named in prose but absent from `references`:\n")
        for cid, kind, number, url in unlinked:
            print(f"  FAIL  {cid} cites {kind} {number} — add "
                  f"{{title: {kind} {number}, url: {url}, type: external}}")
        return 1
    print(f"references: {len(rows)} spec citation(s) resolve, "
          f"across {len({r[0] for r in rows})} checks; "
          f"every PEP and RFC named in prose is reachable from `references`")
    return 0


if __name__ == "__main__":
    sys.exit(main())
