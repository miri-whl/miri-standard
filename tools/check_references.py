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


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--report", action="store_true",
                    help="print the check-to-section list for human reconciliation")
    args = ap.parse_args()
    rows, failures = collect()

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
    print(f"references: {len(rows)} spec citation(s) resolve, "
          f"across {len({r[0] for r in rows})} checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
