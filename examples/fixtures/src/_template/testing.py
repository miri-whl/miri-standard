"""Test doubles this package ships for its own consumers.

`test-patterns.json` declares FakeGreeter under `supported_test_doubles`, and a consumer acting on that
declaration (MIRI-CONSUMER-041) must be able to import what it presents. A declared symbol that does not
resolve is attack A3 — phantom symbols — which belongs in the adversarial arm and nowhere near this one.

This module is part of the SHARED template, so it is byte-identical in every variant including `bare`.
That is the point: the arms differ in metadata, never in code, so any consumer difference is
metadata-attributable. `bare` ships the double and says nothing about it; `miri` ships the same double and
declares it.
"""


class FakeGreeter:
    """An in-memory stand-in for Greeter that records what it was asked to greet."""

    def __init__(self, greeting: str = "Hello") -> None:
        self.greeting = greeting
        self.calls: list[str] = []

    def greet(self, name: str) -> str:
        self.calls.append(name)
        return f"{self.greeting}, {name}!"
