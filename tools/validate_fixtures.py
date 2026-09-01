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
import re
import pathlib
import sys

# pyyaml and jsonschema are installed in the schema-validation CI job, which is where this now runs.
import jsonschema
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
FIX = REPO / "examples/fixtures"
EXPECTED = FIX / "expected"
# The cap A4 is calibrated against lives in expected/cap.json, not here: a suite driving a
# differently-capped surface must be able to detect that the attack no longer applies rather
# than reporting a silent pass (fixture gap C9).
CAP = json.loads((FIX / "expected/cap.json").read_text())["api_index_cap"]

failures: list[str] = []


def _validates(jsonschema, doc, schema_path) -> bool:
    try:
        jsonschema.validate(doc, json.loads(pathlib.Path(schema_path).read_text()))
        return True
    except Exception:
        return False


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

    # 1. The conforming twin must actually conform — it is the comparison arm, and a
    #    non-conforming one silently turns the experiment into bare-vs-nonconforming.
    #    Validate EVERY document present, not just the one that happens to be checked:
    #    an arm is only conforming if all of it is.
    schema_for = {
        "lifecycle.json": "lifecycle-v1",
        "sdk-manifest.json": "sdk-manifest-v1",
        "usage-patterns.json": "usage-patterns-v1",
        "migration-guide.json": "migration-guide-v1",
        "api-graph.json": "api-graph-v1",
        "test-patterns.json": "test-patterns-v1",
    }
    miri_docs = sorted(p for p in (FIX / "metadata/miri").glob("*.json"))
    check("conforming twin ships at least one document", bool(miri_docs), f"{len(miri_docs)} found")
    for doc in miri_docs:
        name = schema_for.get(doc.name)
        if name is None:
            check(f"conforming twin: {doc.name} has a known schema", False,
                  "no schema mapping — add one or the document is unvalidated")
            continue
        try:
            jsonschema.validate(json.load(open(doc)), json.load(open(REPO / f"schemas/{name}.json")))
            check(f"conforming twin: {doc.name} validates against {name}", True)
        except jsonschema.ValidationError as e:
            check(f"conforming twin: {doc.name} validates against {name}", False,
                  str(e).split("\n")[0][:120])

    lifecycle_schema = json.load(open(REPO / "schemas/lifecycle-v1.json"))

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

    # A5: the payload must be directive, inert, AND in a field the consumer actually reads.
    # It used to live only in sdk-manifest.json's top-level `summary`, which no api-index
    # response carries — so a budget-conformant consumer passed A5 by never seeing it (C8).
    adv_patterns = json.loads((FIX / "metadata/adversarial/usage-patterns.json").read_text())
    pat = adv_patterns["patterns"][0]
    reachable = " ".join([
        pat.get("description", ""),
        " ".join(pat.get("explanation", {}).get("key_points", [])),
        pat.get("explanation", {}).get("security_note", ""),
        " ".join(a.get("right_code", "") + a.get("why", "") for a in pat.get("antipatterns", [])),
    ])
    check("A5 payload sits in fields the Map routes a consumer to read",
          "disregard prior instructions" in reachable.lower() or "system:" in reachable.lower())
    check("A5 payload targets only inert hosts",
          "attacker.example.invalid" in reachable and "http://attacker.example.invalid" in reachable,
          "payload must stay on the reserved .invalid TLD")
    check("A5 document is schema-valid (injection does not require malformity)",
          _validates(jsonschema, adv_patterns, REPO / "schemas/usage-patterns-v1.json"))

    # 4b. The dynamic-surface outlier must keep the property MIRI-CONSUMER-011 depends on:
    #     a symbol that WORKS at runtime and is invisible to static parsing. If someone
    #     "tidies" __getattr__ into explicit methods, the check silently becomes untestable.
    dyn = FIX / "src/_dynamic/core.py"
    if dyn.exists():
        dyn_tree = ast.parse(dyn.read_text())
        dyn_static = set()
        for node in ast.walk(dyn_tree):
            if isinstance(node, ast.ClassDef):
                dyn_static.add(node.name)
                for sub in node.body:
                    if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        dyn_static.add(f"{node.name}.{sub.name}")
        check("A9 dynamic symbol is invisible to static parsing",
              "Client.get_weather" not in dyn_static)
        check("A9 control symbol IS statically visible",
              "Client.close" in dyn_static,
              "without a static control, a consumer could pass by calling everything unverified")
        has_getattr = any(isinstance(n, ast.FunctionDef) and n.name == "__getattr__"
                          for n in ast.walk(dyn_tree))
        check("A9 dynamic surface is served by __getattr__", has_getattr)
    else:
        check("A9 dynamic-surface fixture present", False, "src/_dynamic/core.py missing")

    # 4c. The variants added for surface conformance must keep the properties they exist for.
    #     Each is a case some MIRI-SURFACE check has no other way to exercise.
    mal = FIX / "metadata/malformed"
    if mal.is_dir():
        try:
            json.loads((mal / "lifecycle.json").read_text())
            check("malformed lifecycle.json does not parse", False, "it parsed — the truncation was repaired")
        except json.JSONDecodeError:
            check("malformed lifecycle.json does not parse", True)
        # the other two must PARSE but fail their schemas: schema-invalid is a different failure
        for doc, sch in (("sdk-manifest.json", "sdk-manifest-v1"), ("usage-patterns.json", "usage-patterns-v1")):
            d = json.loads((mal / doc).read_text())  # must parse
            check(f"malformed {doc} parses but is schema-invalid",
                  not _validates(jsonschema, d, REPO / f"schemas/{sch}.json"))
    else:
        check("malformed variant present", False)

    spoof = FIX / "metadata/spoofed/lifecycle.json"
    if spoof.exists():
        d = json.loads(spoof.read_text())
        check("A10 spoofed purl claims a foreign package",
              d["identity"]["purl"].startswith("pkg:pypi/requests"), d["identity"]["purl"])
        check("A10 spoofed document is schema-VALID (the lie needs no malformity)",
              _validates(jsonschema, d, REPO / "schemas/lifecycle-v1.json"))
    else:
        check("spoofed variant present", False)

    link = FIX / "metadata/symlinked/usage-patterns.json"
    check("A11 symlinked document is still a symlink", link.is_symlink(),
          "a plain file here makes the confinement case untestable")
    if link.is_symlink():
        check("A11 symlink target is outside the servable set",
              not link.resolve().name.endswith(".json"), link.resolve().name)

    canary = FIX / "src/_hostile_import/__init__.py"
    if canary.exists():
        src = canary.read_text()
        check("A12 import canary writes a sentinel at import time",
              "SENTINEL.write_text" in src and "raise ImportError" in src)
    else:
        check("import canary present", False)

    proj = FIX / "consuming-project"
    tomls = sorted(proj.glob("*.toml")) if proj.is_dir() else []
    check("consuming-project fixtures present", len(tomls) >= 5, f"{len(tomls)} found")
    if tomls:
        import tomllib
        banned = {"command", "args", "env", "url", "path"}
        hostile = 0
        for f in tomls:
            keys = set(tomllib.loads(f.read_text()).get("tool", {}).get("miri", {}).get("consume", {}))
            if f.stem.startswith("hostile"):
                bad = keys & banned
                unknown = keys - {"server", "transport"}
                if bad or unknown or f.stem == "hostile-server-value":
                    hostile += 1
            else:
                check(f"consuming-project {f.name} uses only the closed grammar",
                      not (keys - {"server", "transport"}), f"extra keys {sorted(keys - {'server','transport'})}")
        check("consuming-project hostile cases each violate the grammar", hostile == len(tomls) - 1,
              f"{hostile} hostile of {len(tomls) - 1}")

    reqs = EXPECTED / "requests.json"
    if reqs.exists():
        cases = json.loads(reqs.read_text())["cases"]
        check("request-side attack cases present", len(cases) >= 8, f"{len(cases)} cases")
        missing = [c["id"] for c in cases if not c.get("checks") or "expect" not in c]
        check("every request case names checks and an expected envelope", not missing, str(missing))
    else:
        check("request-side attack cases present", False)

    # 4b. Continuation traces. A cursor defect only appears across a SEQUENCE of requests, so it
    #     needs its own trace file: every other fixture varies one request or one shipped package.
    curs = EXPECTED / "cursor.json"
    if curs.exists():
        d = json.loads(curs.read_text())
        cases = d["cases"]
        check("continuation cases present", len(cases) >= 5, f"{len(cases)} cases")
        bad = [c["id"] for c in cases if not c.get("checks") or len(c.get("sequence", [])) < 1]
        check("every continuation case names checks and a request sequence", not bad, str(bad))
        # The scope table is the decidable part of 3.5.1; if it drifts from the spec the trace
        # stops testing what the spec says.
        scope = d["cursor_scope"]
        check("cursor scope table covers exactly the three listing operations",
              set(scope) - {"note"} == {"list", "api-index", "patterns"}, str(sorted(set(scope) - {"note"})))
        check("cursor scope excludes graph", "graph" not in scope)
        # Rejection cases and their control must both be present, or the trace can be passed by a
        # surface that simply rejects every cursor.
        ids = {c["id"] for c in cases}
        check("continuation trace pairs rejection with a control",
              {"rejects_scope_change_query", "empty_and_absent_filter_are_one_scope"} <= ids,
              f"have {sorted(ids)}")
        check("continuation trace covers the stateless surface", "stateless_surface" in ids)
    else:
        check("continuation cases present", False)

    # 4c. The multi-distribution collision. MIRI-SURFACE-041 was a MUST with no case, which under
    #     the scoring model left conformance permanently undetermined for every run.
    build = FIX / "build"
    if build.is_dir():
        colliding = {}
        for root in sorted(build.glob("ambiguous-*")):
            toml = (root / "pyproject.toml").read_text()
            dist = re.search(r'^name = "([^"]+)"', toml, re.M).group(1)
            pkgs = [d.name for d in (root / "src").iterdir() if d.is_dir()]
            colliding[dist] = pkgs
        check("multi-distribution fixture built", len(colliding) >= 2, f"{sorted(colliding)}")
        names = {p for pkgs in colliding.values() for p in pkgs}
        check("colliding distributions share exactly one import name", len(names) == 1, str(sorted(names)))
        check("colliding distributions are distinct", len(colliding) == len(set(colliding)))
    else:
        check("multi-distribution fixture built", False, "run build_fixtures.py first")

    # 4d. Every Case cell names a real artifact. The column claims which fixture drives each check,
    #     and a review found four cells naming things that existed nowhere ("import canary",
    #     "identity skew", "request traces") plus one naming the wrong file. A prose label nobody
    #     can resolve is a coverage claim nobody can check.
    prof = REPO / "standards/consumption/surface-conformance.md"
    if prof.exists():
        variants = {d.name for d in (FIX / "build").iterdir() if d.is_dir()} if (FIX / "build").is_dir() else set()
        goldens = {f"expected/{f.name}" for f in EXPECTED.glob("*.json")}
        allowed = variants | goldens | {"any", "none - not scorable"}
        rows = re.findall(r"^\| (MIRI-SURFACE-\d+) \|[^|]*\|[^|]*\|[^|]*\| ([^|]+) \|", prof.read_text(), re.M)
        unknown = []
        for cid, cell in rows:
            cell = cell.replace("\u2014", "-").strip()
            # a cell may list several artifacts, and may annotate one with an attack id in parens
            for tok in re.split(r"[,+]", cell):
                tok = re.sub(r"\(.*?\)", "", tok).strip().strip("`").strip()
                if tok and tok not in allowed:
                    unknown.append(f"{cid}:{tok!r}")
        check("every surface Case cell names a real fixture or golden", not unknown, "; ".join(unknown))
    else:
        check("every surface Case cell names a real fixture or golden", False, "profile missing")

    # 4e. Checks must not contradict the goldens. The miri-py team found MIRI-SURFACE-012 requiring
    #     a surface to REFUSE schema-invalid documents while six goldens require it to SERVE the
    #     same documents — and ten of the fifteen consumer checks are driven THROUGH those served
    #     documents, so enforcing the clause would have disabled most of the consumer profile.
    #     Neither doc-linting nor schema validation can see a conflict of this shape: one side is
    #     prose in a YAML field, the other is JSON in a golden.
    schemas_by_doc = {
        "lifecycle.json": "lifecycle-v1.json",
        "sdk-manifest.json": "sdk-manifest-v1.json",
        "usage-patterns.json": "usage-patterns-v1.json",
        "api-graph.json": "api-graph-v1.json",
        "migration-guide.json": "migration-guide-v1.json",
    }
    served_invalid = []
    for g in sorted(EXPECTED.glob("A*.json")):
        d = json.loads(g.read_text())
        se = d.get("surface_expectation", {})
        env = se.get("envelope") or {k: v for k, v in se.items() if k in ("ok", "present")}
        if not (env.get("ok") is True and env.get("present") is True):
            continue
        variant = (d.get("fixture", "") or "").split()[0].strip("(),")
        for name, schema_name in schemas_by_doc.items():
            doc_path = FIX / "metadata" / variant / name
            schema_path = REPO / "schemas" / schema_name
            if not doc_path.exists() or not schema_path.exists():
                continue
            try:
                doc = json.loads(doc_path.read_text())
            except json.JSONDecodeError:
                check(f"golden {g.stem}: a document it requires SERVED must at least parse", False,
                      f"{variant}/{name} does not parse")
                continue
            errs = list(jsonschema.Draft7Validator(json.loads(schema_path.read_text())).iter_errors(doc))
            if errs:
                served_invalid.append(f"{variant}/{name}")
    # Having established which served documents are schema-invalid, no check may demand refusing them.
    refusers = []
    for f in sorted((REPO / "standards/consumption/checks").glob("*.yaml")):
        cd = yaml.safe_load(f.read_text())
        if cd.get("status") != "active":
            continue
        for clause in cd.get("fires_when", []):
            low = clause.lower()
            if "schema" in low and ("fails" in low or "invalid" in low) and "metadata_unreadable" in low:
                refusers.append(cd["id"])
    check("no check demands refusing a document the goldens require served",
          not (served_invalid and refusers),
          f"{sorted(set(refusers))} would refuse {sorted(set(served_invalid))}" if served_invalid and refusers else
          f"{len(set(served_invalid))} served document(s) are schema-invalid by design; no check refuses them")

    # 4f. Every golden's expected envelope validates against discovery-envelope-v1.json, and a set of
    #     known-bad shapes does not. The miri-py team supplied the schema with this evidence in a
    #     document; keeping it here makes it live, so a schema edit that stops catching a violation
    #     fails the build instead of quietly passing.
    env_schema_path = REPO / "schemas/discovery-envelope-v1.json"
    if env_schema_path.exists():
        env_schema = json.loads(env_schema_path.read_text())
        jsonschema.Draft7Validator.check_schema(env_schema)
        V = jsonschema.Draft7Validator(env_schema)
        accepted = 0
        for g in sorted(EXPECTED.glob("A*.json")):
            d = json.loads(g.read_text())
            se = d.get("surface_expectation", {})
            env = se.get("envelope") or {k: v for k, v in se.items()
                                         if k in ("ok", "present", "truncated", "cap")}
            if not env:
                continue
            errs = list(V.iter_errors({"schema_version": "1", **env}))
            check(f"golden {g.stem}: expected envelope validates", not errs,
                  errs[0].message[:90] if errs else "")
            accepted += not errs
        check("golden envelopes validated against the schema", accepted >= 8, f"{accepted} validated")

        # The reject side is gated comprehensively by tools/validate_envelope_schema.py, contributed
        # with the schema (16 mutants, each naming the rule it exercises). Duplicating a subset here
        # would mean two places to update and one to forget; what is unique to this file is that the
        # project's own GOLDENS conform to the schema, which that script does not read.
    else:
        check("discovery-envelope-v1.json present", False)

    # 5. Golden expectations: attack inputs are worthless without stated expected outputs.
    #    These also close the loop against the conformance profile — a golden may not cite a
    #    check that does not exist, and every non-pending check must have a case behind it.
    goldens = sorted(p for p in EXPECTED.glob("A*.json"))
    # Both check families live here — a golden may cite either, and scoping this to one
    # namespace silently rejected every valid MIRI-SURFACE citation.
    check_ids = {f.stem for f in (REPO / "standards/consumption/checks").glob("MIRI-*.yaml")}
    check("golden expectations present", len(goldens) >= 6, f"{len(goldens)} found")
    cited = set()
    for g in goldens:
        d = json.loads(g.read_text())
        missing = [k for k in ("attack", "fixture", "checks", "surface_expectation", "consumer_assertion")
                   if k not in d]
        check(f"golden {g.stem}: complete", not missing, f"missing {missing}" if missing else "")
        unknown = [c for c in d.get("checks", []) if c not in check_ids]
        check(f"golden {g.stem}: cites real checks", not unknown,
              f"unknown check id(s) {unknown}" if unknown else "")
        cited.update(d.get("checks", []))
        # regexes must compile, or the assertion silently never fires
        bad_re = []
        for pat in d.get("consumer_assertion", {}).get("output_must_not_match", []):
            try:
                re.compile(pat)
            except re.error as e:
                bad_re.append(f"{pat!r} ({e})")
        check(f"golden {g.stem}: assertions compile", not bad_re, "; ".join(bad_re))

    # Every check the profile marks with a real case must actually have one.
    profile = (REPO / "standards/consumption/consumer-conformance.md").read_text()
    rows = re.findall(r"^\| (MIRI-CONSUMER-\d+) \| [MS] \| .+? \| \d+ \| (.+?) \|$", profile, re.M)
    uncovered = [cid for cid, case in rows
                 if "fixture pending" not in case and "(A" in case and cid not in cited]
    check("profile checks with a named attack case have a golden", not uncovered,
          f"uncovered: {uncovered}" if uncovered else "")

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
