import numpy as np

from ..defaults import MAX_ABS_RESULT
from .._sanitisation import sanitise_arg as san
from .unsafe_divide import UnsafeDivider
from .is_safe import GenerateIsSafes
from .interpolate_missing import InterpolateMissing


class SafeDivider:
    __slots__ = [
        "_unsafe_divider", "_generate_is_safes", "_interpolate_missing",
        "a", "b", "max_abs_result", "intermediate_a", "intermediate_b", "out"
    ]

    def __init__(
        self, a, b, *,
        max_abs_result=MAX_ABS_RESULT,
        intermediate_a=None,  # numpy.float32
        intermediate_b=None,  # bool
        out=None
    ):
        self._unsafe_divider = UnsafeDivider(a, b, out=out)

        self.a, self.b = a, b
        self.out = self._unsafe_divider.out

        self.intermediate_a, self.intermediate_b \
            = self._sanitise_intermediates(intermediate_a, intermediate_b)

        self._generate_is_safes = GenerateIsSafes(
            self.out,
            max_abs_result=max_abs_result,
            intermediate=self.intermediate_a,
            out=self.intermediate_b
        )

        self.max_abs_result = self._generate_is_safes.max_abs_result

        self._interpolate_missing = InterpolateMissing(
            self.out, is_safe=self.intermediate_b, out=self.out
        )

    def __iter__(self):
        def get_iterator(
            iter=zip(
                self._unsafe_divider,
                self._generate_is_safes,
                self._interpolate_missing
            )
        ):
            while True:
                next(iter)

                yield

        return get_iterator()

    def _sanitise_intermediates(self, intermediate_a, intermediate_b):
        for arr, dtype, name, sanitiser_name in (
            (intermediate_a, np.float32, "intermediate_a", "array_1d_float"),
            (intermediate_b, bool, "intermediate_b", "array_1d_bool"),
        ):
            if arr is None:
                arr = np.empty(self.a.shape, dtype=dtype)
            else:
                san(name, sanitiser_name)

                if arr.shape != self.a.shape:
                    raise ValueError(
                        f"{name!r} should have same shape as 'a' and 'b'"
                    )

            yield arr


def safe_divide(
    a, b, *,
    max_abs_result=MAX_ABS_RESULT,
    intermediate_a=None, intermediate_b=None,
    out=None
):
    safe_divider = SafeDivider(
        a, b,
        max_abs_result=max_abs_result,
        intermediate_a=intermediate_a,
        intermediate_b=intermediate_b,
        out=out
    )

    next(iter(safe_divider))

    return safe_divider.out
