"""One statically-defined class that serves part of its surface dynamically."""

_SUPPORTED = ("weather", "forecast", "alerts")


class Client:
    """A client whose `get_*` accessors are constructed on attribute access.

    `Client` and `Client.close` are statically visible and `resolve` finds them.
    `Client.get_weather` and its siblings are real, working, documented surfaces
    that no static parse can see.
    """

    def __init__(self, region: str = "eu") -> None:
        self.region = region

    def close(self) -> None:
        """Release the client. Statically defined, so `resolve` finds it."""
        return None

    def __getattr__(self, name: str):
        # Real behavior, invisible to ast.parse — the point of the fixture.
        if name.startswith("get_") and name[4:] in _SUPPORTED:
            def _accessor():
                return f"{name[4:]} for {self.region}"
            _accessor.__name__ = name
            return _accessor
        raise AttributeError(f"{type(self).__name__!r} has no attribute {name!r}")
