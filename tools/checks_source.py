#!/usr/bin/env python3
"""Where the check definitions come from: this repository, or the installed definitions wheel.

The fixture pack ships fixtures and goldens, never check definitions — those are the wheel's job, and
two copies of a definition is two sources of truth. So a validator run from an unpacked fixture pack
has to resolve them from `miri-standard-checks`, which is the coupling the two artifacts are supposed
to have: rules from the wheel, material from the pack.
"""
import pathlib

REPO = pathlib.Path(__file__).resolve().parent.parent


def checks_dir(target: str) -> pathlib.Path:
    """`checks/<target>/` from the repository if present, else from the installed wheel.

    Raises with the install command rather than returning an empty directory: a missing corpus that
    reads as "no checks exist" turns every golden into an unknown-ID failure, which is what running
    the pack without the wheel did before this existed — seven broken invariants, none of them true.
    """
    local = REPO / "standards" / target / "checks"
    if local.is_dir():
        return local
    try:
        import miri_standard_checks
    except ImportError:
        raise SystemExit(
            f"No check definitions for '{target}'. Either run this inside a miri-standard checkout, "
            f"or install the definitions:\n"
            f"  pip install --index-url https://miri-whl.github.io/simple/ miri-standard-checks")
    packaged = miri_standard_checks.root() / "checks" / target
    if not packaged.is_dir():
        raise SystemExit(f"Installed miri-standard-checks carries no checks/{target}/")
    return packaged


def schema_path(name: str) -> pathlib.Path:
    """`schemas/<name>` from the repository if present, else from the installed wheel.

    The wheel carries every schema for the same reason it carries every definition: a linter that
    vendors the rules needs the documents those rules validate against.
    """
    local = REPO / "schemas" / name
    if local.is_file():
        return local
    try:
        import miri_standard_checks
    except ImportError:
        raise SystemExit(
            f"No schema '{name}'. Either run this inside a miri-standard checkout, or install the "
            f"definitions:\n"
            f"  pip install --index-url https://miri-whl.github.io/simple/ miri-standard-checks")
    packaged = miri_standard_checks.root() / "schemas" / name
    if not packaged.is_file():
        raise SystemExit(f"Installed miri-standard-checks carries no schemas/{name}")
    return packaged
