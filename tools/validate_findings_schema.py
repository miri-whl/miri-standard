#!/usr/bin/env python3
"""Round-trip agent-findings-v1.json in both directions.

A schema that accepts everything is worthless. The accept half proves it does not reject what the
specification permits; the REJECT half proves it discriminates. Without the reject half, a schema edit that
silently stops enforcing a rule passes quietly.

This file exists because an adversarial panel pointed the ENVELOPE's validator at agent-findings-v1 and got
15/24 — of which only 4 were genuine catches, the other 11 being 5 outright misses plus 6 masked by the
`findings`-required rule firing first. The schema claimed in prose to BE the envelope and inherited one of
its nine rules. Every mutant below is one of the documents that divergence let through.
"""
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
FIND = {"task": "3.5", "level": "must", "summary": "s", "source": "lifecycle.json"}

ACCEPT = [
    ("silence", {"schema_version": "1", "ok": True, "present": False, "reason": "nothing to report"}),
    ("one finding", {"schema_version": "1", "ok": True, "present": True, "findings": [FIND]}),
    ("error", {"schema_version": "1", "ok": False,
               "error": {"code": "PACKAGE_NOT_INSTALLED", "retryable": False}}),
    ("finding without optional purl/quote", {"schema_version": "1", "ok": True, "present": True,
        "findings": [{"task": "3.3", "level": "should", "summary": "x", "source": "migration-guide.json"}]}),
]

REJECT = [
    ("dotted schema_version", {"schema_version": "1.0", "ok": True, "present": False, "reason": "r"},
     "schema_version pattern — two implementations already diverged on this"),
    ("v-prefixed schema_version", {"schema_version": "v1", "ok": True, "present": False, "reason": "r"},
     "schema_version pattern"),
    ("ok:false with no error", {"schema_version": "1", "ok": False}, "envelope §4.3"),
    ("error as a bare string", {"schema_version": "1", "ok": False, "error": "kaboom"}, "error definition"),
    ("invented error code", {"schema_version": "1", "ok": False,
        "error": {"code": "TRANSIENT", "retryable": True}}, "error.code enum"),
    ("error missing retryable", {"schema_version": "1", "ok": False,
        "error": {"code": "PACKAGE_NOT_INSTALLED"}}, "error required"),
    ("served answer carrying an error", {"schema_version": "1", "ok": True, "present": True,
        "findings": [FIND], "error": {"code": "PACKAGE_NOT_INSTALLED", "retryable": False}},
     "envelope §4.2 — absence is not error"),
    ("findings with no present key", {"schema_version": "1", "ok": True, "findings": [FIND]},
     "3.3 converse — a response carrying findings must assert presence"),
    ("present:true with no findings", {"schema_version": "1", "ok": True, "present": True}, "3.3"),
    ("findings alongside present:false", {"schema_version": "1", "ok": True, "present": False,
        "reason": "r", "findings": [FIND]}, "3.3"),
    ("absence with no reason", {"schema_version": "1", "ok": True, "present": False}, "4.1"),
    ("the empty answer", {"schema_version": "1", "ok": True},
     "a non-answer more complete than the empty array 3.3 forbids"),
    ("empty findings array", {"schema_version": "1", "ok": True, "present": True, "findings": []},
     "4.1 — silence is the absent shape, not an empty payload"),
    ("findings: [null]", {"schema_version": "1", "ok": True, "present": True, "findings": [None]}, "item type"),
    ("finding with no source", {"schema_version": "1", "ok": True, "present": True,
        "findings": [{"task": "3.5", "level": "must", "summary": "x"}]}, "attribution is required"),
    ("check-severity vocabulary as level", {"schema_version": "1", "ok": True, "present": True,
        "findings": [dict(FIND, level="CRITICAL")]}, "level enum — conformance vocabulary only"),
    ("upper-case MUST as level", {"schema_version": "1", "ok": True, "present": True,
        "findings": [dict(FIND, level="MUST")]}, "level enum is lower-case"),
    ("task outside the six", {"schema_version": "1", "ok": True, "present": True,
        "findings": [dict(FIND, task="3.7")]}, "task enum"),
    ("publisher-invented finding key", {"schema_version": "1", "ok": True, "present": True,
        "findings": [dict(FIND, priority="critical")]}, "finding object is closed"),
    ("hook deny control block", {"schema_version": "1", "ok": True, "present": False, "reason": "r",
        "hookSpecificOutput": {"permissionDecision": "deny"}}, "4.4 — output must not carry a control shape"),
    ("legacy decision:block", {"schema_version": "1", "ok": True, "present": False, "reason": "r",
        "decision": "block"}, "4.4"),
    ("continue:false", {"schema_version": "1", "ok": True, "present": False, "reason": "r",
        "continue": False}, "4.4"),
    ("suppressOutput", {"schema_version": "1", "ok": True, "present": False, "reason": "r",
        "suppressOutput": True}, "4.4"),
]


def main():
    try:
        import jsonschema
    except ImportError:
        print("jsonschema not installed", file=sys.stderr)
        return 2
    schema = json.loads((REPO / "schemas/agent-findings-v1.json").read_text())
    jsonschema.Draft7Validator.check_schema(schema)
    V = jsonschema.Draft7Validator(schema)

    bad = 0
    for label, doc in ACCEPT:
        ok = V.is_valid(doc)
        print(f"  {'accepted' if ok else 'REJECTED':9s} {label}")
        bad += not ok
    for label, doc, why in REJECT:
        ok = not V.is_valid(doc)
        print(f"  {'caught  ' if ok else 'MISSED  '} {label}  [{why}]")
        bad += not ok

    total = len(ACCEPT) + len(REJECT)
    print(f"\n{total - bad}/{total} as expected")
    if bad:
        print("FAIL: the schema does not discriminate as intended", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
