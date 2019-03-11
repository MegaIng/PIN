from __future__ import annotations

from pin_client import PIN

pin = PIN('pin')

pin.int = 5
pin.double = 5.4
pin.inf = float("inf")
pin.neg_inf = float("-inf")
pin.nan = float("nan")
pin.neg_nan = float("-nan")
pin.string = "Test"
pin.bytes = b"Test"

pin.child.int = 5
pin.child.double = 5.4
pin.child.inf = float("inf")
pin.child.neg_inf = float("-inf")
pin.child.nan = float("nan")
pin.child.neg_nan = float("-nan")
pin.child.string = "Test"
pin.child.bytes = b"Test"

print(pin.int)
print(pin.double)
print(pin.inf)
print(pin.neg_inf)
print(pin.nan)
print(pin.neg_nan)
print(pin.string)
print(pin.bytes)

print(pin.child)
print(pin.child.int)
print(pin.child.double)
print(pin.child.inf)
print(pin.child.neg_inf)
print(pin.child.nan)
print(pin.child.neg_nan)
print(pin.child.string)
print(pin.child.bytes)
print(pin.child.child)
