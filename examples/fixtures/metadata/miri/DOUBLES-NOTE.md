# Why `supported_test_doubles` is populated

`supported_test_doubles` was `[]` until 0.4.1, which made **MIRI-CONSUMER-041 undrivable**. With nothing declared,
the only conforming behavior is to present no double at all — which is also exactly what an inert consumer does. The
check could not distinguish a careful consumer from one that never looked, so it passed vacuously against this
project's own reference fixture.

Declaring `FakeGreeter` gives the check an affirmative path. A consumer that presents it for `greet_miri.Greeter`
passes; one that synthesizes its own mock and calls it the package's fails; and those two are now different
observable outcomes rather than the same one.

The note lives here rather than inside the document because `test-patterns-v1.json` closes `additionalProperties` —
the same reason the `spoofed` variant carries its `ATTACK.md` alongside rather than an `_attack_note` key. A fixture
that had to be made schema-invalid to explain itself would be a poor fixture.

Reported by the miri-py team, who hit it implementing `test.author` and found no fixture that could exercise the
affirmative path of either MUST.
