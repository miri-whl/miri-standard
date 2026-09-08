#!/usr/bin/env python3
"""greetctl - the CLI conformance fixture for the Miri Standard.

One implementation, four arms. Everything this program knows about its own surface it reads from a sibling
`describe.json`; `--help`, `--describe`, `changelog` and the removal errors are all derived from that one document.
That is the CLI Lifecycle Specification 9.6 property ("all of the above derive from the same schema-as-data source
as --help") which no check can verify from outside - here it is true by construction, so the fixture is a positive
example of a requirement the checklist cannot grade.

The arms differ ONLY in the two JSON files beside this script. This file is byte-identical across all of them, which
is what makes any observed difference metadata-attributable rather than code-attributable.
"""
import json
import os
import pathlib
import signal
import sys

HERE = pathlib.Path(__file__).resolve().parent
SCHEMA_VERSION = "1"


def _load(name):
    p = HERE / name
    return json.loads(p.read_text()) if p.exists() else {}


DESCRIBE = _load("describe.json")
FIXTURE = _load("fixture.json")
BARE = bool(FIXTURE.get("bare"))
VERSION = FIXTURE.get("version", "0.0.0")


def out_json(payload, code=0):
    """Every JSON payload carries a top-level schema_version (MIRI-CLI-010) and nothing else touches stdout
    (MIRI-CLI-011). Keys are sorted so identical inputs give identically ordered output (MIRI-CLI-012)."""
    body = {"schema_version": SCHEMA_VERSION}
    body.update(payload)
    sys.stdout.write(json.dumps(body, indent=2, sort_keys=True) + "\n")
    return code


def fail(code_str, message, retryable=False, suggestions=None, as_json=True):
    """Structured error envelope (MIRI-CLI-013/014): a stable machine code, a retryable flag, and suggestions."""
    if as_json:
        out_json({"ok": False, "error": {
            "code": code_str, "message": message,
            "retryable": retryable, "suggestions": sorted(suggestions or []),
        }})
    else:
        sys.stderr.write(f"greetctl: {message}\n")
    return 1


def banner():
    """The C2 attack: prose on stdout ahead of the JSON document, on every invocation."""
    if FIXTURE.get("banner"):
        sys.stdout.write("greetctl: a new version is available! run `greetctl check-update` for details.\n")


def commands():
    return DESCRIBE.get("commands", [])


def walk_surfaces():
    """Yield (path, entry) for every command, subcommand and flag in the describe document."""
    for c in commands():
        yield c["name"], c
        for s in c.get("subcommands", []):
            yield f"{c['name']} {s['name']}", s
        for f in c.get("flags", []):
            yield f["name"], f


def find_surface(name):
    for path, entry in walk_surfaces():
        if path == name or entry.get("name") == name:
            return entry
    return None


def deprecation_warning(entry):
    """MIRI-CLI-034: grace-period warnings go to stderr, never stdout."""
    lc = entry.get("lifecycle") or {}
    if lc.get("status") == "deprecated":
        repl = lc.get("replacement")
        tail = f"; use {repl} instead" if repl else ""
        sys.stderr.write(f"greetctl: warning: {entry['name']} is deprecated since "
                         f"{lc.get('deprecated_since', '?')}{tail}\n")


def render_help(sub=None):
    """MIRI-CLI-002/004: help on stdout, exit 0, derived from the same document --describe serves."""
    if BARE:
        lines = ["usage: greetctl [--json] <command> [args]", "", "commands:",
                 "  greet NAME", "  legacy-greet NAME", "  config set KEY VALUE", "  cache purge", ""]
        sys.stdout.write("\n".join(lines))
        return 0
    if sub:
        entry = find_surface(sub)
        if entry is None:
            return fail("UNKNOWN_COMMAND", f"unknown command: {sub}", suggestions=[c["name"] for c in commands()])
        lines = [f"usage: greetctl {sub} [options]", "", entry.get("description", "")]
        for f in entry.get("flags", []):
            mark = " (deprecated)" if (f.get("lifecycle") or {}).get("status") == "deprecated" else ""
            lines += [f"  {f['name']:<12} {f.get('description', '')}{mark}"]
        for s in entry.get("subcommands", []):
            lines += [f"  {s['name']:<12} {s.get('description', '')}"]
        sys.stdout.write("\n".join(lines) + "\n")
        return 0
    lines = ["usage: greetctl [--json] [--dry-run] <command> [args]", "", "commands:"]
    for c in commands():
        mark = " (deprecated)" if (c.get("lifecycle") or {}).get("status") == "deprecated" else ""
        lines += [f"  {c['name']:<14} {c.get('description', '')}{mark}"]
    lines += ["", "  check-update   Report whether a newer release exists",
              "  changelog      Machine-readable change history", "",
              "global options:", "  --json         Machine-readable output on stdout",
              "  --describe     Print the introspection document", "  --version      Print the version",
              "  --dry-run      Simulate a mutating command without performing it", ""]
    sys.stdout.write("\n".join(lines))
    return 0


def cmd_describe():
    if BARE:
        return fail("UNKNOWN_FLAG", "unrecognized option: --describe", as_json=False)
    banner()
    sys.stdout.write(json.dumps(DESCRIBE, indent=2, sort_keys=True) + "\n")
    return 0


def cmd_check_update(offline):
    """MIRI-CLI-025/027: the specified shape; offline is update_available: null and exit 0, not an error."""
    if BARE:
        return fail("UNKNOWN_COMMAND", "unrecognized command: check-update", as_json=False)
    banner()
    if offline:
        return out_json({"ok": True, "update_available": None, "urgency": "none",
                         "current_version": VERSION, "advisories": []})
    return out_json({"ok": True, "update_available": False, "urgency": "none",
                     "current_version": VERSION, "latest_version": VERSION, "advisories": []})


def cmd_changelog(since):
    """MIRI-CLI-029/030: added / removed / deprecated surfaces per release, since a given version."""
    if BARE:
        return fail("UNKNOWN_COMMAND", "unrecognized command: changelog", as_json=False)
    banner()
    if not since:
        return fail("MISSING_ARGUMENT", "changelog requires --since <version>",
                    suggestions=["greetctl changelog --since 1.0.0 --json"])
    log = FIXTURE.get("changelog", {})
    releases = [{"version": v, "added": sorted(e.get("added", [])),
                 "deprecated": sorted(e.get("deprecated", [])), "removed": sorted(e.get("removed", []))}
                for v, e in sorted(log.items()) if v > since]
    return out_json({"ok": True, "since": since, "releases": releases})


def removed_surface_error(name):
    """MIRI-CLI-033: a removed surface teaches; it does not emit a generic parse failure."""
    rec = (FIXTURE.get("removed") or {}).get(name)
    if rec is None:
        return None
    if FIXTURE.get("generic_removal_error"):
        sys.stderr.write(f"usage: greetctl greet [-h] NAME\ngreetctl: error: unrecognized arguments: {name}\n")
        return 2
    return fail(rec.get("code", "SURFACE_REMOVED"),
                f"{name} was removed in {rec.get('removed_in', '?')}",
                retryable=False, suggestions=rec.get("suggestions", []))


def cmd_greet(name, opts, as_json, dry_run):
    for opt in opts:
        removed = removed_surface_error(opt)
        if removed is not None:
            return removed
        entry = find_surface(opt)
        if entry is None:
            return fail("UNKNOWN_FLAG", f"unrecognized option: {opt}",
                        suggestions=[f["name"] for c in commands() for f in c.get("flags", [])])
        deprecation_warning(entry)
    text = f"Good day, {name}." if "--formal" in opts else f"Hello, {name}!"
    if "--loud" in opts or "--shout" in opts:
        text = text.upper()
    if as_json:
        return out_json({"ok": True, "greeting": text})
    sys.stdout.write(text + "\n")
    return 0


def cmd_mutate(path, args, as_json, dry_run):
    """MIRI-CLI-039: every mutating command supports --dry-run and simulates faithfully."""
    entry = find_surface(path) if not BARE else {"name": path}
    if entry is None:
        return fail("UNKNOWN_COMMAND", f"unknown command: {path}",
                    suggestions=[c["name"] for c in commands()])
    deprecation_warning(entry)
    action = {"config set": f"would set {args[0] if args else '?'}={args[1] if len(args) > 1 else '?'}",
              "cache purge": "would delete all cached data"}.get(path, f"would run {path}")
    performed = not dry_run
    if as_json:
        return out_json({"ok": True, "command": path, "dry_run": dry_run,
                         "performed": performed, "effect": action})
    sys.stdout.write((action if dry_run else action.replace("would ", "")) + "\n")
    return 0


def main(argv):
    # MIRI-CLI-007: a closed pipe is not an error condition for a filter.
    if hasattr(signal, "SIGPIPE"):
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    # MIRI-CLI-043: leave no partial state behind on interrupt.
    signal.signal(signal.SIGINT, lambda *_: sys.exit(130))
    # MIRI-CLI-005: NO_COLOR and a non-TTY stdout both drop decoration. This fixture emits none either way,
    # which satisfies the check trivially and honestly - there is nothing to suppress.
    _ = os.environ.get("NO_COLOR") is not None or not sys.stdout.isatty()

    args, opts, terminator = [], [], False
    for a in argv:
        if terminator:
            args.append(a)
        elif a == "--":
            terminator = True                      # MIRI-CLI-001: `--` ends option parsing
        elif a.startswith("-") and a != "-":
            opts.append(a)
        else:
            args.append(a)

    as_json = "--json" in opts                     # MIRI-CLI-009: one flag, every command
    dry_run = "--dry-run" in opts
    offline = "--offline" in opts                  # fixture-only: forces the no-network path of MIRI-CLI-027
    for consumed in ("--json", "--dry-run", "--offline", "--no-color"):
        while consumed in opts:
            opts.remove(consumed)

    if "--version" in opts:                        # MIRI-CLI-003
        sys.stdout.write(f"greetctl {VERSION}\n")
        return 0
    if "--describe" in opts:                       # MIRI-CLI-015
        return cmd_describe()
    if "--help" in opts or "-h" in opts:           # MIRI-CLI-002/004
        return render_help(args[0] if args else None)
    if not args:
        return render_help()

    cmd, rest = args[0], args[1:]
    if cmd == "check-update":
        return cmd_check_update(offline)
    if cmd == "changelog":
        since = None
        if "--since" in argv:
            i = argv.index("--since")
            since = argv[i + 1] if i + 1 < len(argv) else None
            if since in rest:
                rest.remove(since)
        return cmd_changelog(since)
    if cmd in ("greet", "legacy-greet"):
        entry = find_surface(cmd)
        if entry is None and not BARE:
            gone = removed_surface_error(cmd)
            if gone is not None:
                return gone
            return fail("UNKNOWN_COMMAND", f"unknown command: {cmd}",
                        suggestions=[c["name"] for c in commands()])
        if entry is not None:
            deprecation_warning(entry)
        if not rest:
            # MIRI-CLI-006: never block on a prompt; a missing operand is a structured error, not a question.
            return fail("MISSING_ARGUMENT", f"{cmd} requires a NAME operand",
                        suggestions=[f"greetctl {cmd} World"], as_json=as_json)
        return cmd_greet(rest[0], opts, as_json, dry_run)
    if cmd in ("config", "cache") and rest:
        return cmd_mutate(f"{cmd} {rest[0]}", rest[1:], as_json, dry_run)
    gone = removed_surface_error(cmd)
    if gone is not None:
        return gone
    return fail("UNKNOWN_COMMAND", f"unknown command: {cmd}",
                suggestions=[c["name"] for c in commands()] if not BARE else ["greet"])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
