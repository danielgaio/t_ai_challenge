"""Package dispatcher for Thoughtful's robotic automation factory.

Provides sort(width, height, length, mass) -> str which returns one of:
  - "STANDARD"
  - "SPECIAL"
  - "REJECTED"

Rules:
  - bulky: volume >= 1_000_000 cm^3 OR any dimension >= 150 cm
  - heavy: mass >= 20 kg
  - REJECTED: both heavy and bulky
  - SPECIAL: heavy or bulky (but not both)
  - STANDARD: neither heavy nor bulky
"""

from typing import Literal

Stack = Literal["STANDARD", "SPECIAL", "REJECTED"]


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

    # Determine bulky and heavy according to the rules (thresholds are inclusive)
    volume = w * h * l
    is_bulky = volume >= 1_000_000 or w >= 150 or h >= 150 or l >= 150
    is_heavy = m >= 20

    if is_bulky and is_heavy:
        return "REJECTED"
    if is_bulky or is_heavy:
        return "SPECIAL"
    return "STANDARD"


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
