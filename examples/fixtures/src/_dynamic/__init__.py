"""A package whose public surface is partly constructed at runtime.

This fixture lives OUTSIDE the byte-identical trio on purpose: it must differ in
source, so it cannot be one of the three variants the build script byte-compares.

Its reason for existing is `MIRI-CONSUMER-011`. `resolve` determines existence by
parsing source (Discovery Contract §3.6.1), which cannot see an attribute built by
`__getattr__` — so `resolve` reports `not-in-source` for a symbol that nonetheless
works. A consumer that reads that as proof of non-existence is wrong about every
dynamically-generated API, which is exactly the failure the check forbids.
"""

from .core import Client

__all__ = ["Client"]
__version__ = "1.0.0"
