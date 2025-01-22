import numpy as np

from .sanitisation import sanitise_arg


class _SafeDivider_CC:
    def __init__(self, a, b, *, max_abs_result, out):
        self._a = a
        self._b = b
        self._max_abs_result = max_abs_result
        self._out = out

        self._intermediate_a = np.empty(a.shape, dtype=np.float32)
        self._intermediate_b = np.empty(a.shape, dtype=np.float32)
        self._intermediate_c = np.empty(a.shape, dtype=bool)
        self._intermediate_d = np.empty(a.shape, dtype=bool)

    def once(self):



class SafeDivider:
    def __init__(self, *, _once):
        self.once = _once

    @classmethod
    def from_args(cls, a, b, *, max_abs_result, out):
        for name in ["a", "b", "out"]:
            sanitise_arg(name, sanitiser_name="array_1d")

        if a.shape != b.shape or a.shape != out.shape:
            raise ValueError("a, b, and out should have the same shape")

        max_abs_result = sanitise_arg("max_abs_result")

        sanitise_arg("out", sanitiser_name="array_1d_c")

        if np.dtype(a) is np.dtype(np.complex64):
            if np.dtype(b) is np.dtype(np.complex64):
                safe_divider_for_types_cls = SafeDivider_CC
            elif np.dtype(b) is np.dtype(np.float32):
                safe_divider_for_types_cls = SafeDivider_CF
            else:
                raise TypeError(
                    "the only dtypes allowed are numpy.float32 and "
                    "numpy.complex64"
                )
        elif np.dtype(b) is np.dtype(np.complex64):
            if np.dtype(a) is np.dtype(np.float32):
                safe_divider_for_types_cls = SafeDivider_FC
            else:
                raise TypeError(
                    "the only dtypes allowed are numpy.float32 and "
                    "numpy.complex64"
                )
        else:
            raise TypeError(
                "at least one of 'a' and 'b' should have the dtype "
                "numpy.complex64"
            )

        safe_divider_for_types = safe_divider_for_types_cls(
            a, b, max_abs_result=max_abs_result, out=out
        )

        return cls(_once=safe_divider_for_types.once)


def safe_divide(a, b, *, max_abs_result, out=None):
    sanitise_arg("a", sanitiser_name="array_1d")

    if out is None:
        out = np.empty(a.shape, dtype=np.complex64)

    SafeDivider.from_args(a, b, max_abs_result=max_abs_result, out=out).once()

    return out
