from typing import Set


class BulkyByVolumeRule:
    name = "bulky_by_volume"

    def evaluate(self, width: float, height: float, length: float, mass: float) -> Set[str]:
        volume = width * height * length
        if volume >= 1_000_000 or width >= 150 or height >= 150 or length >= 150:
            # Returns a set containing the string "bulky".
            # This structure is likely used to indicate or categorize an item or entity as "bulky".
            return {"bulky"}
        return set()


class HeavyRule:
    name = "heavy"

    def evaluate(self, width: float, height: float, length: float, mass: float) -> Set[str]:
        if mass >= 20:
            return {"heavy"}
        return set()