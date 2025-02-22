import numpy as np

from ..defaults import MAX_ABS_RESULT
from .._sanitisation import sanitise_arg as san


class GenerateIsSafes:
    __slots__ = ["a", "max_abs_result", "intermediate", "out"]

    def __init__(
        self, a, *,
        max_abs_result=MAX_ABS_RESULT,
        intermediate=None,  # numpy.float32
        out=None
    ):
        self.a = san("a", "array_1d_complex")
        self.max_abs_result = san("max_abs_result")
        self.intermediate, self.out \
            = self._sanitise_intermediate_and_out(intermediate, out)

    def __iter__(self):
        abs_, less_equal = np.abs, np.less_equal
        a, max_abs_result, intermediate, out \
            = self.a, self.max_abs_result, self.intermediate, self.out

        def get_iterator(
            abs_=np.abs, less_equal=np.less_equal,
            a=self.a,
            max_abs_result=self.max_abs_result,
            intermediate=self.intermediate,
            out=self.out
        ):
            while True:
                abs_(a, out=intermediate)
                less_equal(intermediate, max_abs_result, out=out)
                yield

        return get_iterator()

    def _sanitise_intermediate_and_out(self, intermediate, out):
        for arr, dtype, name, sanitiser_name in (
            (intermediate, np.float32, "intermediate", "array_1d_float"),
            (out, bool, "out", "array_1d_bool")
        ):
            if arr is None:
                arr = np.empty(self.a.shape, dtype=dtype)
            else:
                san(name, sanitiser_name)

                if arr.shape != self.a.shape:
                    raise ValueError(
                        f"if provided, {name!r} should have same shape as 'a'"
                    )

            yield arr
