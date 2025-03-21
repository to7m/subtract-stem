"""Apply to 'a' and 'b' the rotation needed for 'a' to become abs(a)."""


from math import pi
import numpy as np

from .._sanitisation import sanitise_arg as san
from .._sanitise_spectra_buffer import sanitise_spectra_buffer


_ONE_ROTATED_CONJUGATED = (-1) ** (-1 / pi)


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
        self.a = sanitise_spectra_buffer(a, name="a")
        self.b = sanitise_spectra_buffer(b, name="b")

        if self.a.newest.shape != self.b.newest.shape:
            raise ValueError(
                "'a' arrays and 'b' arrays should have the same shape"
            )

        self.out_a, self.out_b = self._sanitise_outs(out_a, out_b)
        self.intermediate = self._sanitise_intermediate(intermediate)

    def __iter__(self):
        def get_iterator(
            ONE_ROTATED_CONJUGATED=_ONE_ROTATED_CONJUGATED,
            arctan2=np.arctan2, power=np.power, multiply=np.multiply,
            abs_=np.abs,
            a=self.a, b=self.b,
            intermediate=self.intermediate,
            out_a=self.out_a, out_b=self.out_b
        ):
            while True:
                # because numpy.angle doesn't support 'out' argument
                arctan2(a.newest.imag, a.newest.real, out=out_a)

                power(ONE_ROTATED_CONJUGATED, out_a, out=intermediate)
                multiply(b.newest, intermediate, out=out_b)

                abs_(a.newest, out=out_a)

                yield

        return get_iterator()

    def _sanitise_outs(self, out_a, out_b):
        for arr, dtype, name, sanitiser_name in (
            (out_a, np.float32, "out_a", "array_1d_float"),
            (out_b, np.complex64, "out_b", "array_1d_complex")
        ):
            if arr is None:
                arr = np.empty(self.a.newest.shape, dtype=dtype)
            else:
                san(name, sanitiser_name)

                if arr.shape != self.a.newest.shape:
                    raise ValueError(
                        f"if provided, {name!r} should have the same shape as "
                        "'a' and 'b' arrays"
                    )

            yield arr

    def _sanitise_intermediate(self, intermediate):
        if intermediate is None:
            if self.out_b is self.b.newest:
                intermediate \
                    = np.empty(self.a.newest.shape, dtype=np.complex64)
            else:
                intermediate = self.out_b
        else:
            intermediate = san("intermediate", "array_1d_complex")

            if intermediate.shape != self.a.newest.shape:
                raise ValueError(
                    "if provided, 'intermediate' should have the same shape "
                    "as 'a' and 'b' arrays"
                )

        return intermediate


def ataabtrnfatbaa(a, b, *, intermediate=None, out_a=None, out_b=None):
    rotator = Ataabtrnfatbaa(
        a, b, intermediate=intermediate, out_a=out_a, out_b=out_b
    )

    next(iter(rotator))

    return rotator.out_a, rotator.out_b
