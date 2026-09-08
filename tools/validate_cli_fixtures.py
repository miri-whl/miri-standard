#!/usr/bin/env python3
"""Verify the greetctl CLI fixture invariants.

Two jobs, mirroring tools/validate_fixtures.py on the wheel side:

  1. The conforming arms must actually conform - they are the comparison arm, and a non-conforming one silently
     turns the experiment into bare-vs-non-conforming.
  2. Every attack must still be LIVE. A fixture whose attacks have decayed passes trivially and tests nothing;
     that is the vacuous-pass defect applied to fixtures instead of checks.

The CLI fixture carries one invariant the wheel fixture has no equivalent of: a two-release HISTORY. Five
MIRI-CLI checks are claims about what the binary used to do, so this file asserts the 1.0.0/1.1.0 pair actually
exercises them rather than merely existing.
"""
import json
import pathlib
import re
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
FIX = REPO / "examples/fixtures/cli"
BUILD = FIX / "build"

failures = []


def check(label, ok, detail=""):
    print(f"  {'PASS' if ok else 'FAIL'}  {label}{(' — ' + detail) if detail else ''}")
    if not ok:
        failures.append(label)


def run(arm, *args):
    """Drive an arm. Returns (rc, stdout, stderr)."""
    p = subprocess.run([sys.executable, str(BUILD / arm / "greetctl.py"), *args],
                       capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def parses(text):
    try:
        return json.loads(text)
    except (json.JSONDecodeError, ValueError):
        return None


def main():
    try:
        import jsonschema
    except ImportError:
        print("jsonschema not installed — cannot validate CLI fixtures", file=sys.stderr)
        return 2

    if not BUILD.exists():
        print("fixtures not built — run examples/fixtures/cli/build_cli_fixtures.py first", file=sys.stderr)
        return 2

    print("greetctl CLI fixture invariants:")
    schema = json.loads((REPO / "schemas/cli-describe-v1.json").read_text())

    # --- 1. the conforming arms conform ------------------------------------------------------------------
    for arm in ("miri-1.0.0", "miri-1.1.0"):
        rc, out, _ = run(arm, "--describe")
        doc = parses(out)
        check(f"{arm}: --describe exits 0 and is a single JSON document", rc == 0 and doc is not None,
              f"rc={rc}")
        if doc is None:
            continue
        try:
            jsonschema.validate(doc, schema)
            check(f"{arm}: --describe validates against cli-describe-v1", True)
        except jsonschema.ValidationError as e:
            check(f"{arm}: --describe validates against cli-describe-v1", False, str(e).split("\n")[0][:110])

        # MIRI-CLI-017: identity.version, the purl's @version, and the printed version must all agree.
        _, ver_out, _ = run(arm, "--version")
        printed = ver_out.strip().split()[-1] if ver_out.strip() else ""
        purl_ver = doc["identity"]["purl"].rsplit("@", 1)[-1]
        check(f"{arm}: --version == identity.version == purl @version",
              printed == doc["identity"]["version"] == purl_ver,
              f"printed={printed} identity={doc['identity']['version']} purl={purl_ver}")

        # MIRI-CLI-010/011: every JSON payload carries a top-level schema_version and nothing else is on stdout.
        for args in (["--json", "greet", "World"], ["--json", "check-update", "--offline"],
                     ["--json", "changelog", "--since", "1.0.0"]):
            _, o, _ = run(arm, *args)
            p = parses(o)
            check(f"{arm}: `{' '.join(args)}` is strict JSON with top-level schema_version",
                  p is not None and p.get("schema_version") == "1")

        # MIRI-CLI-038: every replacement resolves against the CURRENT describe, and not into a dead end.
        names = set()
        for c in doc["commands"]:
            names.add(c["name"])
            names.update(f["name"] for f in c.get("flags", []))
            names.update(s["name"] for s in c.get("subcommands", []))
        dead = []
        for c in doc["commands"]:
            for entry in [c, *c.get("flags", []), *c.get("subcommands", [])]:
                repl = (entry.get("lifecycle") or {}).get("replacement")
                if repl and repl not in names:
                    dead.append(f"{entry['name']}->{repl}")
        check(f"{arm}: every lifecycle.replacement resolves in --describe", not dead, ", ".join(dead))

    # --- 2. the release history actually exercises the previous-release checks -----------------------------
    prev = parses(run("miri-1.0.0", "--describe")[1])
    cur = parses(run("miri-1.1.0", "--describe")[1])

    def surfaces(d):
        s = {}
        for c in d["commands"]:
            s[c["name"]] = c
            for f in c.get("flags", []):
                s[f["name"]] = f
            for sub in c.get("subcommands", []):
                s[f"{c['name']} {sub['name']}"] = sub
        return s

    ps, cs = surfaces(prev), surfaces(cur)
    removed = set(ps) - set(cs)
    check("history: the release pair removes at least one surface", bool(removed), f"removed={sorted(removed)}")

    # MIRI-CLI-037/035: every removed surface was deprecated in an EARLIER release, not this one.
    for name in sorted(removed):
        lc = (ps[name].get("lifecycle") or {})
        check(f"MIRI-CLI-037 exercised: {name} was deprecated in 1.0.0 before removal",
              lc.get("status") == "deprecated", f"lifecycle={lc or '(none)'}")
        check(f"MIRI-CLI-035 exercised: {name} deprecated_since and removed_in differ in minor series",
              lc.get("deprecated_since", "")[:3] != lc.get("removed_in", "")[:3],
              f"{lc.get('deprecated_since')} -> {lc.get('removed_in')}")

    # MIRI-CLI-036: the deprecation announced in 1.1.0 appears in that release's changelog entry.
    # Defensive: a non-conforming CLI under test may return anything at all. A validator that raises a
    # traceback instead of naming the failed invariant is useless to the implementer it exists to serve —
    # it reports that the harness broke, not that their tool is wrong.
    log = parses(run("miri-1.1.0", "changelog", "--since", "1.0.0", "--json")[1]) or {}
    check("MIRI-CLI-029 exercised: `changelog --since` returns a releases array",
          isinstance(log.get("releases"), list), f"got {type(log.get('releases')).__name__}")
    entries = {r.get("version"): r for r in log.get("releases", []) if isinstance(r, dict)}
    newly_deprecated = {n for n, e in cs.items() if (e.get("lifecycle") or {}).get("deprecated_since") == "1.1.0"}
    # CLI Spec 5.2 surfaces are RECORDS, not bare strings. An earlier version of this assertion read them
    # as strings, which only worked because greetctl emitted the wrong shape — the validator had been
    # written against the implementation instead of the spec, so it could not see the implementation's bug.
    def surface_names(rel, key):
        return {r["surface"] if isinstance(r, dict) else r for r in rel.get(key, [])}

    listed = surface_names(entries.get("1.1.0", {}), "deprecated")
    check("MIRI-CLI-036 exercised: 1.1.0's deprecations appear in changelog --since 1.0.0",
          newly_deprecated and newly_deprecated <= listed,
          f"declared={sorted(newly_deprecated)} changelog={sorted(listed)}")
    check("MIRI-CLI-030 exercised: the changelog names the removed surface",
          removed <= surface_names(entries.get("1.1.0", {}), "removed"),
          f"removed={sorted(removed)} changelog={sorted(surface_names(entries.get('1.1.0', {}), 'removed'))}")

    # MIRI-CLI-030 clause 3: all five normative 5.2 categories must have representation in the shape.
    rel = entries.get("1.1.0", {})
    missing = [k for k in ("added", "deprecated", "removed", "schema_version_change", "exit_code_changes")
               if k not in rel]
    check("MIRI-CLI-030 exercised: all five 5.2 categories present in the output shape",
          not missing, f"missing {missing}")

    # MIRI-CLI-013: an unparseable typed argument is a structured error, never silent success.
    rc, out, _ = run("miri-1.1.0", "--json", "changelog", "--since", "NOT-A-VERSION")
    err = (parses(out) or {}).get("error", {})
    check("MIRI-CLI-013 exercised: unparseable --since is a structured error, not coerced success",
          rc != 0 and err.get("code") and err.get("retryable") is False,
          f"rc={rc} code={err.get('code')}")

    # MIRI-CLI-025: the spec's field names are `current` and `latest`.
    cu = parses(run("miri-1.1.0", "--json", "check-update")[1]) or {}
    check("MIRI-CLI-025 exercised: check-update carries the specified field names",
          {"current", "latest", "update_available", "urgency"} <= set(cu),
          f"got {sorted(cu)}")

    # MIRI-CLI-033: invoking the removed surface teaches, and names a replacement that exists.
    rc, out, _ = run("miri-1.1.0", "--json", "greet", "--shout", "World")
    err = (parses(out) or {}).get("error", {})
    check("MIRI-CLI-033 exercised: removed surface yields a structured teaching error",
          bool(err.get("code")) and err.get("retryable") is False and bool(err.get("suggestions")),
          f"code={err.get('code')} suggestions={err.get('suggestions')}")
    check("MIRI-CLI-033 exercised: its suggestion names a surface that exists now",
          set(err.get("suggestions", [])) <= set(cs), f"{err.get('suggestions')} vs current surfaces")

    # --- 3. every attack is live -------------------------------------------------------------------------
    adv = json.loads((BUILD / "adversarial-1.1.0/describe.json").read_text())

    try:
        jsonschema.validate(adv, schema)
        check("adversarial --describe is schema-invalid (by design)", False,
              "it validated — the attack keys are gone")
    except jsonschema.ValidationError:
        check("adversarial --describe is schema-invalid (by design)", True)

    check("C1 version skew live: identity.version disagrees with the purl",
          adv["identity"]["version"] != adv["identity"]["purl"].rsplit("@", 1)[-1],
          f"{adv['identity']['version']} vs {adv['identity']['purl']}")

    rc, out, _ = run("adversarial-1.1.0", "--describe")
    check("C2 stdout contamination live: --describe fails a strict parse", parses(out) is None)

    auth = [s for s in adv["advisory_sources"] if s.get("authoritative")]
    check("C3 false clean bill live: no reachable authoritative source and no advisory_coverage",
          "advisory_coverage" not in adv and len(auth) >= 1)
    eco = adv["identity"]["purl"].split(":")[1].split("/")[0]
    check("C4 ecosystem mismatch live: the authoritative source names another ecosystem",
          all(s.get("ecosystem", "").lower() != eco.lower() for s in auth),
          f"purl ecosystem={eco} authoritative={[s.get('ecosystem') for s in auth]}")
    check("C5 private-on-public-OSV live",
          adv["identity"]["distribution"] == "private"
          and all(s["type"] == "osv" for s in adv["advisory_sources"]))

    check("C6 silent removal live: legacy-greet vanished with no deprecation and no changelog entry",
          "legacy-greet" in ps and "legacy-greet" not in {c["name"] for c in adv["commands"]}
          and not parses(run("adversarial-1.1.0", "changelog", "--since", "1.0.0", "--json")[1] or "x"))

    advs = {}
    for c in adv["commands"]:
        for entry in [c, *c.get("flags", []), *c.get("subcommands", [])]:
            advs[entry["name"]] = entry
    chains = [(n, (e.get("lifecycle") or {}).get("replacement")) for n, e in advs.items()
              if (e.get("lifecycle") or {}).get("replacement")]
    dead_end = [(n, r) for n, r in chains
                if r not in advs or (advs.get(r, {}).get("lifecycle") or {}).get("status") == "deprecated"]
    check("C7 dead-end replacement live: a replacement points at a deprecated or absent surface",
          bool(dead_end), f"{dead_end}")

    # PEP 503 name equality, not a substring test: PyPI has no namespace, so the name is the only
    # discriminator, and "greetctl" is a substring of "attacker-greetctl". This is the same trap
    # MIRI-CONSUMER-032 was fixed for, and it caught a first draft of this very assertion.
    def purl_name(purl):
        return re.sub(r"[-_.]+", "-", purl.split("/")[-1].split("@")[0]).lower()

    check("C8 replacement redirect live: support.replacement names a different distribution",
          adv["support"].get("status") in ("deprecated", "eol")
          and purl_name(adv["support"].get("replacement", "")) != purl_name(adv["identity"]["purl"]),
          f'{adv["support"].get("replacement", "")} vs {adv["identity"]["purl"]}')

    purge = advs.get("purge", {})
    setc = advs.get("set", {})
    check("C9 unmarked destructive live: purge is destructive:false while a benign sibling is true",
          purge.get("destructive") is False and setc.get("destructive") is True)

    rc, out, err_text = run("adversarial-1.1.0", "--json", "greet", "--shout", "World")
    check("C10 generic removal failure live: no structured error, argparse dump on stderr",
          parses(out) is None and "unrecognized arguments" in err_text, f"rc={rc}")

    check("C11 trigger forcing live: describe carries an agent_integration bid",
          isinstance(adv.get("agent_integration"), dict)
          and adv["agent_integration"].get("always_notify") is True)

    # --- 4. the arms are discriminating ------------------------------------------------------------------
    conforming_teaches = (parses(run("miri-1.1.0", "--json", "greet", "--shout", "W")[1]) or {}).get("error", {})
    hostile_dumps = parses(run("adversarial-1.1.0", "--json", "greet", "--shout", "W")[1]) is None
    check("the arms discriminate: same flag, same removal, opposite observable behavior",
          bool(conforming_teaches.get("suggestions")) and hostile_dumps)

    print()
    if failures:
        print(f"{len(failures)} invariant(s) FAILED:", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1
    print("all CLI fixture invariants hold")
    return 0


if __name__ == "__main__":
    sys.exit(main())
