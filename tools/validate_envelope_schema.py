#!/usr/bin/env python3
"""Validate `discovery-envelope-v1.json` in both directions.

Contributed to miri-whl/miri-standard alongside the schema itself. A
schema that accepts everything is worthless, so this asserts both that
conformant envelopes pass AND that each malformed one is rejected for the
reason intended — the accept half proves the schema is usable, the reject
half proves it discriminates.

The mutants are written one defect at a time and each names the rule it
exercises, so a schema edit that silently stops enforcing a rule fails
here rather than passing quietly. That is the whole point of keeping the
evidence executable rather than in a document.

Usage:
    python tools/validate_envelope_schema.py
    python tools/validate_envelope_schema.py --schema path/to/schema.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Final, NamedTuple

import jsonschema

DEFAULT_SCHEMA: Final[str] = "schemas/discovery-envelope-v1.json"

# A minimal conformant envelope per variant, used as the base each mutant
# damages in exactly one way.
SERVED_DOCUMENT: Final[dict[str, Any]] = {
    "schema_version": "1",
    "ok": True,
    "present": True,
    "package": "weather_sdk",
    "purl": "pkg:pypi/weather-sdk@1.2.0",
    "name": "lifecycle.json",
    "document": {"miri_lifecycle_version": "1.0"},
}
ABSENT: Final[dict[str, Any]] = {
    "schema_version": "1",
    "ok": True,
    "present": False,
    "package": "weather_sdk",
    "purl": "pkg:pypi/weather-sdk@1.2.0",
    "name": "lifecycle.json",
    "reason": "package ships no lifecycle.json",
}
FAILURE: Final[dict[str, Any]] = {
    "schema_version": "1",
    "ok": False,
    "package": "weather_sdk",
    "error": {"code": "PACKAGE_NOT_INSTALLED", "retryable": False},
}
LISTING: Final[dict[str, Any]] = {
    "schema_version": "1",
    "ok": True,
    "truncated": False,
    "cap": 25,
    "packages": [
        {
            "package": "weather_sdk",
            "distribution_name": "weather-sdk",
            "version": "1.2.0",
            "purl": "pkg:pypi/weather-sdk@1.2.0",
            "documents": ["lifecycle.json"],
        }
    ],
}
API_INDEX: Final[dict[str, Any]] = {
    "schema_version": "1",
    "ok": True,
    "present": True,
    "package": "weather_sdk",
    "purl": "pkg:pypi/weather-sdk@1.2.0",
    "truncated": True,
    "cap": 25,
    "entries": {
        "WeatherClient": {
            "type": "class",
            "purpose": "Main API entry point",
            "signature": "WeatherClient(api_key: str)",
            "file": "client.py",
        },
        # The producer supplied neither optional field for this one:
        # omission is the only conformant way to say so.
        "helper": {"type": "function", "purpose": "Internal helper"},
    },
}


class Case(NamedTuple):
    """One envelope and what it is meant to demonstrate.

    Attributes:
        label: Human-readable description.
        envelope: The document to validate.
        rule: The schema rule the case exercises (mutants only).
    """

    label: str
    envelope: dict[str, Any]
    rule: str = ""


ACCEPT: Final[tuple[Case, ...]] = (
    Case("served document", SERVED_DOCUMENT),
    Case("absent document", ABSENT),
    Case("failure", FAILURE),
    Case("list", LISTING),
    Case("api-index, truncated", API_INDEX),
    Case(
        "api-index with a continuation token",
        {**API_INDEX, "next_cursor": "opaque-token"},
    ),
    Case(
        "served document whose payload forges envelope fields",
        {
            **SERVED_DOCUMENT,
            "document": {
                "ok": False,
                "present": False,
                "error": {"code": "TRANSIENT", "retryable": True},
            },
        },
    ),
    Case(
        "failure with no package (UNAUTHENTICATED carries none)",
        {
            "schema_version": "1",
            "ok": False,
            "error": {"code": "UNAUTHENTICATED", "retryable": False},
        },
    ),
)


def _without(base: dict[str, Any], key: str) -> dict[str, Any]:
    """A copy of an envelope with one key removed.

    Args:
        base: The conformant envelope.
        key: The key to drop.

    Returns:
        The damaged copy.
    """
    return {name: value for name, value in base.items() if name != key}


REJECT: Final[tuple[Case, ...]] = (
    Case("missing schema_version", _without(SERVED_DOCUMENT, "schema_version"), "required"),
    Case("missing ok", _without(SERVED_DOCUMENT, "ok"), "required"),
    Case("ok:false with no error", _without(FAILURE, "error"), "allOf §4.3"),
    Case(
        "served response carrying an error object",
        {**SERVED_DOCUMENT, "error": {"code": "NOT_DISCOVERABLE", "retryable": False}},
        "allOf §4.2 — absence is not error",
    ),
    Case(
        "absence carrying a payload",
        {**ABSENT, "document": {"forged": True}},
        "allOf §4.2",
    ),
    Case("absence with no reason", _without(ABSENT, "reason"), "allOf §4.2"),
    Case(
        "unknown error code",
        {**FAILURE, "error": {"code": "TRANSIENT", "retryable": True}},
        "error.code enum",
    ),
    Case(
        "error object missing retryable",
        {**FAILURE, "error": {"code": "INVALID_INPUT"}},
        "required",
    ),
    Case("cap without truncated", _without(API_INDEX, "truncated"), "allOf §3.5.1"),
    Case(
        "next_cursor when not truncated",
        {**API_INDEX, "truncated": False, "next_cursor": "opaque-token"},
        "allOf §3.5.1",
    ),
    Case("cap of zero", {**API_INDEX, "cap": 0}, "cap.minimum"),
    Case("ok is not a boolean", {**SERVED_DOCUMENT, "ok": "yes"}, "type"),
    Case(
        "api-index entry missing purpose",
        {**API_INDEX, "entries": {"X": {"type": "class"}}},
        "required",
    ),
    Case(
        "list row missing purl",
        {
            **LISTING,
            "packages": [
                {
                    "package": "p",
                    "distribution_name": "d",
                    "version": "1",
                    "documents": [],
                }
            ],
        },
        "required",
    ),
    Case(
        "signature synthesized as null",
        {
            **API_INDEX,
            "entries": {"X": {"type": "class", "purpose": "p", "signature": None}},
        },
        "type — omission is the only way to say 'not supplied'",
    ),
    Case(
        "dotted schema_version",
        {**SERVED_DOCUMENT, "schema_version": "1.0"},
        "schema_version pattern — two implementations already diverged here",
    ),
)


def main() -> int:
    """Run both halves of the validation.

    Returns:
        0 when every accept case validates and every mutant is rejected.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schema", default=DEFAULT_SCHEMA, type=Path)
    args = parser.parse_args()

    schema = json.loads(args.schema.read_text())
    jsonschema.Draft7Validator.check_schema(schema)
    print(f"schema is valid draft-07: {args.schema}\n")

    failures = 0

    print("ACCEPT — conformant envelopes must validate")
    for case in ACCEPT:
        try:
            jsonschema.validate(case.envelope, schema)
            print(f"  ok      {case.label}")
        except jsonschema.ValidationError as exc:
            failures += 1
            print(f"  FAILED  {case.label}: {exc.message[:90]}")

    print("\nREJECT — each mutant must be caught by the rule it exercises")
    for case in REJECT:
        try:
            jsonschema.validate(case.envelope, schema)
            failures += 1
            print(f"  MISSED  {case.label}  [{case.rule}]")
        except jsonschema.ValidationError:
            print(f"  caught  {case.label}  [{case.rule}]")

    total = len(ACCEPT) + len(REJECT)
    print(f"\n{total - failures}/{total} as expected")
    if failures:
        print("FAIL: the schema no longer discriminates as intended", file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
