import numpy as np

from ..defaults import MAX_ABS_RESULT
from .._sanitisation import sanitise_arg as san
from .._sanitise_unique_arrays_of_shape import sanitise_unique_arrays_of_shape
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
            iter_=zip(
                self._unsafe_divider,
                self._generate_is_safes,
                self._interpolate_missing
            )
        ):
            while True:
                next(iter_)

                yield

        return get_iterator()

    def _sanitise_intermediates(self, intermediate_a, intermediate_b):
        return sanitise_unique_arrays_of_shape(
            array_infos=[
                (intermediate_a, "intermediate_a", "float"),
                (intermediate_b, "intermediate_b", "bool")
            ],
            reference_shape=self.a.shape,
            reference_name="'a' and 'b'"
        )


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
