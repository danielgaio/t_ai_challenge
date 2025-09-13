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