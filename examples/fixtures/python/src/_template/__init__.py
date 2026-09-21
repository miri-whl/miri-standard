"""greetlib — a trivial library, identical in every fixture arm.

The source is byte-compared across arms by build_python_fixtures.py. Only the shipped metadata
differs, so any finding a linter reports is attributable to metadata rather than to code. Two public
symbols exist in 1.0.0 and one of them is removed in the silent-removal arm, which is the only way to
give a previous-release check something real to compare against.
"""

__all__ = ["greet", "farewell"]


def greet(name: str) -> str:
    """Return a greeting for `name`."""
    return f"hello, {name}"


def farewell(name: str) -> str:
    """Return a parting line for `name`.

    Removed in the silent-removal arm without a deprecation trail, which is what MIRI-PY-030 exists
    to catch: the first signal a dependent gets is AttributeError in production.
    """
    return f"goodbye, {name}"
