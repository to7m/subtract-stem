import numpy as np

from .._sanitisation import sanitise as san


def sanitise_a_b_out(a, b, out):
    for name in "a", "b":
        san(name, "array_1d")

    valid_dtypes = {np.dtype(np.float32), np.dtype(np.complex64)}
    if {np.dtype(np.float32), a.dtype, b.dtype} != valid_dtypes:
        raise TypeError(
            "at least one of 'a' and 'b' should have dtype np.complex64, and "
            "the other may have dtype np.float32"
        )

    if a.shape != b.shape:
        raise ValueError("'a' and 'b' should have same shape")

    if out is None:
        out = np.empty(a.shape, dtype=np.complex64)
    else:
        san("out", "array_1d_complex")

        if out.shape != a.shape:
            raise ValueError(
                "'out' should have same shape as 'a' and 'b'"
            )

    return a, b, out
