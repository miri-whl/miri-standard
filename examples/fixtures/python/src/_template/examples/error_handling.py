"""What greetlib raises when misused."""
import greetlib

try:
    greetlib.greet(None)
except TypeError:
    print("greet() needs a string")
