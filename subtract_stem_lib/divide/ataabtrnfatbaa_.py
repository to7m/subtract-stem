"""Apply to 'a' and 'b' the rotation needed for 'a' to become abs(a)."""


import numpy as np


ONE_ROTATED_CONJUGATED = (-1) ** (-1 / pi)


class Ataabtrnfatbaa:
    __slots__ = [
        "a", "b",
        "intermediate",
        "out_a", "out_b"
    ]

    def __init__(
        self, a, b, *,
        intermediate=None,  # numpy.complex64
        out_a=None, out_b=None
    ):
        self.a = sanitise_arg("a", sanitiser_name="array_1d_complex")
        self.b = sanitise_arg("b", sanitiser_name="array_1d_complex")

        if a.shape != b.shape:
            raise ValueError("'a' and 'b' should have the same shape")

        self.out_a, self.out_b = self._sanitise_outs(out_a, out_b)

        if intermediate is None:
            if out_b is b:
                self.intermediate = np.empty(a.shape, dtype=np.complex64)
            else:
                self.intermediate = out_b
        else:
            self.intermediate = sanitise_arg(
                "intermediate", sanitiser_name="array_1d_complex"
            )

            if intermediate.shape != a.shape:
                raise ValueError(
                    "if provided, 'intermediate' should have the same shape "
                    "as 'a' and 'b'"
                )

    def _sanitise_outs(self, out_a, out_b):
        for arr, dtype, name, sanitiser_name in (
            (out_a, np.float32, "out_a", "array_1d_float"),
            (out_b, np.complex64, "out_b", "array_1d_complex")
        ):
            if arr is None:
                arr = np.empty(self.a.shape, dtype=dtype)
            else:
                sanitise_arg(name, sanitiser_name=sanitiser_name)

                if arr.shape != self.a.shape:
                    raise ValueError(
                        f"if provided, {name!r} should have the same shape as "
                        "'a' and 'b'"
                    )

            yield arr

    def __iter__(self):
        angle, power, multiply = np.angle, np.power, np.multiply
        abs_ = np.abs

        a, b = self.a, self.b
        intermediate = self.intermediate
        out_a, out_b = self.out_a, self.out_b

        def iterator():
            while True:
                angle(a, out=out_a)
                power(ONE_ROTATED_CONJUGATED, out_a, out=intermediate)
                multiply(b, intermediate, out=out_b)

                abs_(a, out=out_a)

                yield

        return iterator()


def ataabtrnfatbaa(a, b, *, intermediate=None, out_a=None, out_b=None):
    ataabtrnfatbaa_ = Ataabtrnfatbaa(
        a, b, intermediate=intermediate, out_a=out_a, out_b=out_b
    )

    next(iter(ataabtrnfatbaa_))

    return ataabtrnfatbaa_.out_a, ataabtrnfatbaa_.out_b
