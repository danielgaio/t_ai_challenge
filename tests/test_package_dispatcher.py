from dispatcher.package_dispatcher import sort


def test_standard():
    assert sort(10, 10, 10, 1) == "STANDARD"


def test_special_by_volume():
    # volume == 1_000_000 should be considered bulky -> SPECIAL unless heavy
    assert sort(100, 100, 100, 1) == "SPECIAL"


def test_special_by_dimension():
    assert sort(150, 10, 10, 1) == "SPECIAL"
    assert sort(10, 150, 10, 1) == "SPECIAL"
    assert sort(10, 10, 150, 1) == "SPECIAL"


def test_special_by_mass():
    # mass == 20 is heavy -> SPECIAL unless bulky
    assert sort(10, 10, 10, 20) == "SPECIAL"


def test_rejected_when_bulky_and_heavy():
    assert sort(100, 100, 100, 20) == "REJECTED"
    assert sort(150, 10, 10, 20) == "REJECTED"


def test_invalid_inputs():
    # non-numeric input returns REJECTED as safe default
    assert sort("a", 10, 10, 1) == "REJECTED"
