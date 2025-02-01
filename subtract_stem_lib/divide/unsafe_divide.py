import numpy as np

from ._sanitise_a_b_out import sanitise_a_b_out


class UnsafeDivider:
    __slots__ = ["a", "b", "out"]

    def __init__(self, a, b, *, out=None):
        self.a, self.b, self.out = sanitise_a_b_out(a, b, out)

    def __iter__(self):
        divide = np.divide
        a, b, out = self.a, self.b, self.out

        def iterator():
            while True:
                divide(a, b, out=out)
                yield

        return iterator()
