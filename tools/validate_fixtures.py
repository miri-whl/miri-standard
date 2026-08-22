#!/usr/bin/env python3
"""Verify the consumption fixtures still hold their invariants.

A fixture that quietly stops attacking is worse than no fixture: every consumer check
written against it keeps passing while testing nothing. This script asserts that each
attack in `examples/fixtures/README.md` is still live, and that the conforming twin is
still conforming.

Run after `examples/fixtures/build_fixtures.py` (the `validate-fixtures` make target does
both). Exit 0 = all invariants hold, 1 = a fixture has rotted, 2 = jsonschema missing.
"""
import ast
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
FIX = REPO / "examples/fixtures"
CAP = 25  # the api-index cap the padding attack is built to defeat

failures: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"  {'PASS' if ok else 'FAIL'}  {label}{(' — ' + detail) if detail else ''}")
    if not ok:
        failures.append(label)


def main() -> int:
    try:
        import jsonschema
    except ImportError:
        print("jsonschema not installed — cannot validate fixtures", file=sys.stderr)
        return 2

    print("consumption fixture invariants:")

    # 1. The conforming twin must actually conform — it is the comparison arm.
    lifecycle_schema = json.load(open(REPO / "schemas/lifecycle-v1.json"))
    miri_lifecycle = json.load(open(FIX / "metadata/miri/lifecycle.json"))
    try:
        jsonschema.validate(miri_lifecycle, lifecycle_schema)
        check("conforming twin validates against lifecycle-v1", True)
    except jsonschema.ValidationError as e:
        check("conforming twin validates against lifecycle-v1", False, str(e).split("\n")[0][:120])

    # 2. The adversarial twin must NOT validate — a hostile publisher is not obliged to
    #    conform, and a surface that is only safe on schema-valid input is not safe.
    adv_lifecycle = json.load(open(FIX / "metadata/adversarial/lifecycle.json"))
    try:
        jsonschema.validate(adv_lifecycle, lifecycle_schema)
        check("adversarial lifecycle is schema-invalid (by design)", False,
              "it validated — the forgery keys are gone")
    except jsonschema.ValidationError:
        check("adversarial lifecycle is schema-invalid (by design)", True)

    # A1/A2: the envelope-forgery keys must still be present at the document's top level.
    forged = [k for k in ("ok", "present", "error") if k in adv_lifecycle]
    check("A1/A2 envelope-forgery keys present", sorted(forged) == ["error", "ok", "present"],
          f"found {sorted(forged)}")

    # A6: an empty advisory list is the false-clean-bill attack.
    check("A6 empty advisory_sources present", adv_lifecycle.get("advisory_sources") == [])

    # A7: the SSRF target must still be a link-local address.
    url = adv_lifecycle.get("update_check", {}).get("url", "")
    check("A7 SSRF target is link-local", "169.254.169.254" in url, url or "(no url)")

    # 3. Phantom symbols must genuinely be absent from the shared source.
    src = (FIX / "src/_template/core.py").read_text()
    real = {n.name for n in ast.walk(ast.parse(src))
            if isinstance(n, (ast.ClassDef, ast.FunctionDef))}
    index = json.load(open(FIX / "metadata/adversarial/sdk-manifest.json"))["api_index"]
    claimed = [k for k in index if not k.startswith(("_", "pad_"))]
    phantom = sorted(c for c in claimed if c.split(".")[-1] not in real)
    check("A3 phantom symbols absent from source", phantom == ["GreeterPro", "purge_cache"],
          f"phantom={phantom}")

    # 4. The padding must still push a real symbol past the cap.
    keys = [k for k in index if not k.startswith("_")]
    pos = keys.index("Greeter.greet") if "Greeter.greet" in keys else -1
    check(f"A4 padding pushes Greeter.greet past cap={CAP}", pos >= CAP,
          f"position {pos + 1} of {len(keys)}")

    # A5: the injection payload must still be directive, and still inert.
    summary = json.load(open(FIX / "metadata/adversarial/sdk-manifest.json"))["summary"]
    check("A5 injection payload present", "ignore prior instructions" in summary.lower())
    check("A5 payload targets only inert hosts", "attacker.example.invalid" in summary,
          "payload must stay on the reserved .invalid TLD")

    print()
    if failures:
        print(f"{len(failures)} fixture invariant(s) FAILED — the fixture has rotted:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("all fixture invariants hold")
    return 0


if __name__ == "__main__":
    sys.exit(main())
