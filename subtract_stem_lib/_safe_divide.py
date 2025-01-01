import numpy as np


def _get_is_safe__cff(
    a,  # complex64
    b,  # float32
    *,
    max_amplification,
    intermediate_a,  # float32
    intermediate_b,  # float32
    intermediate_c,  # bool
    out  # bool
):
    # abs(a) vals
    np.abs(a, out=intermediate_a)

    # maximum allowable abs(a) vals
    np.multiply(b, max_amplification, out=intermediate_b)

    # is low enough
    np.less_equal(intermediate_a, intermediate_b, out=intermediate_c)

    # denominator is non-zero
    np.not_equal(indermediate_b, 0, out=out)

    # is safe
    out &= intermediate_c


def _interpolate_missing_segment(
    x, *, last_present_before, first_present_after
):
    start_val = x[last_present_before]
    stop_val = x[first_present_after]

    divisions = first_present_after - last_present_before
    gradient = (stop_val - start_val) / divisions

    for i in range(1, divisions):
        x[last_present_before + i] = start_val + i * gradient


def _interpolate_missing(x, *, is_present):
    is_present_iter = enumerate(is_present)

    if not next(is_present_iter)[1]:
        for i, pres in is_present_iter:
            if pres:
                x[:i] = x[i]

                break

    first_missing = None
    for i, pres in is_present_iter:
        if not pres:
            first_missing = i

            for i, pres in is_present_iter:
                if pres:
                    _interpolate_missing_segment(
                        x,
                        last_present_before=first_missing - 1,
                        first_present_after=i
                    )

                    first_missing = None

                    break

    if first_missing is not None:
        x[first_missing:] = x[first_missing - 1]


def safe_divide__cff(
    a, # float32
    b, # float32
    *,
    max_amplification,
    intermediate_a=None, # float32
    intermediate_b=None, # float32
    intermediate_c=None, # bool
    intermediate_d=None, # bool
    out=None # complex64
):
    _get_is_safe(
        a, b,
        max_amplification=max_amplification,
        intermediate_a=intermediate_a,
        intermediate_b=intermediate_b,
        intermediate_c=intermediate_c,
        out=intermediate_d
    )

    if np.any(intermediate_d):
        np.divide(a, b, out=out)

        if not np.all(intermediate_d):
            _interpolate_missing(out, is_present=intermediate_d)
    elif out is None:
        out = np.zeros(a.shape, dtype=np.complex64)
    else:
        out.fill(0)

    return out
