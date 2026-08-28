"""A package that records the fact of being imported, then refuses to load.

This is the canary for import-free discovery (Discovery Contract §5, MIRI-SURFACE-022).
A surface that resolves metadata through the import system rather than through path
finders will execute this module, leave a sentinel file behind, and be detected.

It lives OUTSIDE the byte-identical trio: its whole purpose is to have a side effect
on import, which the trio's shared source cannot express.

The raise is deliberate. A surface that survives importing this package has still
failed — the sentinel is what proves it, not the exception.
"""

import os
import pathlib
import tempfile

SENTINEL = pathlib.Path(os.environ.get("MIRI_IMPORT_SENTINEL", tempfile.gettempdir())) / "miri-import-canary"

# The side effect. Import-free discovery never runs this line.
SENTINEL.write_text("greet_hostile_import was imported\n")

raise ImportError(
    "greet_hostile_import must never be imported. A surface reached this line, which means "
    "it resolved metadata by importing rather than by reading — see Discovery Contract §5."
)
