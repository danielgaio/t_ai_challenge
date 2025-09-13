# example usage (anywhere in your code or REPL)
from dispatcher.package_dispatcher import sort

# create a custom rule
class AlwaysRejectOddVolume:
    name = "reject_odd_volume"
    def evaluate(self, w,h,l,m):
        if int(w*h*l) % 2 == 1:
            return {"reject"}
        return set()


def test_add_rule():
    # register it on the module engine
    from dispatcher import package_dispatcher as pd
    pd._engine.register(AlwaysRejectOddVolume())

    # afterwards the decisions will include that rule's effect
    result = sort(1, 1, 3, 1)  # volume 3 is odd, should be rejected
    assert "REJECTED" in result, f"Expected 'REJECTED' in result, got {result}"

    # to remove it later
    pd._engine.unregister("reject_odd_volume")
    result_after = sort(1, 1, 3, 1)
    assert "REJECTED" not in result_after, f"Expected 'REJECTED' not in result after unregister, got {result_after}"
    print("end")