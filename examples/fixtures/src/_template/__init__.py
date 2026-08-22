"""A deliberately tiny package used as a conformance fixture.

The same source is built three ways — bare, Miri-conforming, and adversarial —
so that a consumer can be driven against all three and its behavior compared.
Only the shipped metadata differs; this source is byte-identical across variants.
"""

from .core import Greeter, greet

__all__ = ["Greeter", "greet"]
__version__ = "1.0.0"
