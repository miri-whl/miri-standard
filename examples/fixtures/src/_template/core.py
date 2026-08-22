"""The entire public surface of the fixture package: one class, one function."""


class Greeter:
    """Builds greetings in a configured language."""

    def __init__(self, language: str = "en") -> None:
        self.language = language

    def greet(self, name: str) -> str:
        """Return a greeting for `name` in the configured language."""
        prefix = {"en": "Hello", "es": "Hola", "fr": "Bonjour"}.get(self.language, "Hello")
        return f"{prefix}, {name}!"


def greet(name: str, language: str = "en") -> str:
    """Return a greeting for `name` without constructing a Greeter."""
    return Greeter(language).greet(name)
