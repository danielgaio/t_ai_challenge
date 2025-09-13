Short plan

- Add a small RulesEngine that collects rule results (labels like "bulky", "heavy", "reject") and makes the final decision.
- Provide default rules as pluggable classes.
- Keep the public sort(...) API unchanged but delegate decision to the engine.
- Runtime: register/unregister rule objects to change behavior.

``` python
# Documentation:
# - Protocol: Imported from typing, Protocol is used to define structural subtyping (static duck typing) for classes. It allows you to specify methods and properties that a class must implement, without requiring explicit inheritance.
# - Set: Imported from typing, Set is a generic type representing a collection of unique, unordered elements. It is commonly used to specify that a variable or parameter should be a set of items of a particular type.
from typing import Protocol, Set, List, Literal

Stack = Literal["STANDARD", "SPECIAL", "REJECTED"]


class Rule(Protocol):
    name: str

    def evaluate(self, width: float, height: float, length: float, mass: float) -> Set[str]:
        """Return a set of flags such as {"bulky"}, {"heavy"}, {"reject"} or empty set."""


class RulesEngine:
    def __init__(self) -> None:
        self._rules: List[Rule] = []

    def register(self, rule: Rule) -> None:
        """Register a rule instance (order is preserved)."""
        self._rules.append(rule)

    def unregister(self, name: str) -> None:
        """Remove rules matching the given name."""
        self._rules = [r for r in self._rules if getattr(r, "name", None) != name]

    def decide(self, width: float, height: float, length: float, mass: float) -> Stack:
        # A set named 'flags' is initialized to store unique string values representing various flags.
        # Using a set ensures that each flag is stored only once and allows for efficient membership checks.
        # flags: Set[str]
        # The set() function is a built-in Python constructor that creates an empty set object. Sets are unordered collections of unique elements, and set() initializes an empty set ready to store flag strings.
        flags: Set[str] = set()
        for r in self._rules:
            try:
                flags |= r.evaluate(width, height, length, mass)
            except Exception:
                # ignore faulty rule; engine stays resilient
                continue

        # explicit override
        if "reject" in flags:
            return "REJECTED"

        is_bulky = "bulky" in flags
        is_heavy = "heavy" in flags

        if is_bulky and is_heavy:
            return "REJECTED"
        if is_bulky or is_heavy:
            return "SPECIAL"
        return "STANDARD"
```

Default rules (register these by default)

```python
from typing import Set


class BulkyByVolumeRule:
    name = "bulky_by_volume"

    def evaluate(self, width: float, height: float, length: float, mass: float) -> Set[str]:
        volume = width * height * length
        if volume >= 1_000_000 or width >= 150 or height >= 150 or length >= 150:
            <!--
            Returns a set containing the string "bulky".
            This structure is likely used to indicate or categorize an item or entity as "bulky".
            -->
            return {"bulky"}
        return set()


class HeavyRule:
    name = "heavy"

    def evaluate(self, width: float, height: float, length: float, mass: float) -> Set[str]:
        if mass >= 20:
            return {"heavy"}
        return set()
```

Modify package_dispatcher to use the engine (keeps existing public API)

```python
"""Package dispatcher for Thoughtful's robotic automation factory.

Provides sort(width, height, length, mass) -> str which returns one of:
  - "STANDARD"
  - "SPECIAL"
  - "REJECTED"
...
"""
from typing import Literal

# ...existing code...
from .rules_engine import RulesEngine
from .default_rules import BulkyByVolumeRule, HeavyRule

Stack = Literal["STANDARD", "SPECIAL", "REJECTED"]

# ...existing code...
"""
This module contains a module-level object, which is a variable, function, or class defined directly within the module's global scope (outside of any function or class). 
Module-level objects are accessible throughout the module and can be imported from other modules.

Please refer to the object's specific documentation below for details on its purpose and usage.
"""
# create a module-level engine and register default rules
_engine = RulesEngine()
_engine.register(BulkyByVolumeRule())
_engine.register(HeavyRule())


def sort(width: float, height: float, length: float, mass: float) -> Stack:
    """Decide which stack a package should go to.

    Args:
        width: width in centimeters
        height: height in centimeters
        length: length in centimeters
        mass: mass in kilograms

    Returns:
        One of the strings: "STANDARD", "SPECIAL", or "REJECTED".
    """

    # Defensive: coerce to floats
    try:
        w = float(width)
        h = float(height)
        l = float(length)
        m = float(mass)
    except Exception:
        # If inputs are not numbers, consider it rejected as a safe default
        return "REJECTED"

    # Delegate decision to the pluggable rules engine
    return _engine.decide(w, h, l, m)

# ...existing code...
if __name__ == "__main__":
    # Quick manual smoke examples
    examples = [
        (10, 10, 10, 1),      # STANDARD
        (100, 100, 100, 1),   # SPECIAL (volume == 1_000_000)
        (150, 10, 10, 1),     # SPECIAL (dimension >= 150)
        (10, 10, 10, 20),     # SPECIAL (mass == 20)
        (100, 100, 100, 20),  # REJECTED (both)
    ]
    for args in examples:
        print(args, "->", sort(*args))
```

Example: add/remove a plugin at runtime

```python
# example usage (anywhere in your code or REPL)
from dispatcher.package_dispatcher import sort
from dispatcher.rules_engine import RulesEngine  # or access module-level _engine if exported
from dispatcher.default_rules import BulkyByVolumeRule

# create a custom rule
class AlwaysRejectOddVolume:
    name = "reject_odd_volume"
    def evaluate(self, w,h,l,m):
        if int(w*h*l) % 2 == 1:
            return {"reject"}
        return set()

# register it on the module engine
from dispatcher import package_dispatcher as pd
pd._engine.register(AlwaysRejectOddVolume())

# afterwards the decisions will include that rule's effect
print(sort(1, 1, 3, 1))  # maybe REJECTED if volume 3 is odd

# to remove it later
pd._engine.unregister("reject_odd_volume")
```