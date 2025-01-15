import numpy as np


def _get_is_safe_to_divide__cf(
    a,  # complex64
    b,  # float32
    *,
    max_abs_val,
    intermediate_a,  # float32
    intermediate_b,  # float32
    intermediate_c,  # bool
    out  # bool
):
    # abs(a) vals
    intermediate_a = np.abs(a, out=intermediate_a)

    # maximum allowable abs(a) vals
    intermediate_b = np.multiply(b, max_abs_val, out=intermediate_b)

    # is low enough
    intermediate_c \
        = np.less_equal(intermediate_a, intermediate_b, out=intermediate_c)

    # denominator is non-zero
    out = np.not_equal(b, 0, out=out)

    # is safe
    out &= intermediate_c

    return out


def _get_is_safe_to_divide__fc(
    a,  # float32
    b,  # complex64,
    *,
    max_abs_val,
    intermediate_a,  # float32
    intermediate_b,  # bool
    out  # bool
):
    # abs(b) vals
    intermediate_a = np.abs(b, out=intermediate_a)

    # maximum allowable ‘a’ vals
    intermediate_a *= max_abs_val

    # is low enough
    intermediate_b = np.less_equal(a, intermediate_a, out=intermediate_b)

    # denominator is non-zero
    out = np.not_equal(intermediate_a, 0, out=out)

    # is safe
    out &= intermediate_b

    return out


def _get_is_safe_to_divide__cc(
    a,  # complex64
    b,  # complex64
    *,
    max_abs_val,
    intermediate_a,  # float32
    intermediate_b,  # float32
    intermediate_c,  # bool
    out  # bool
):
    # abs(a) vals
    intermediate_a = np.abs(a, out=intermediate_a)

    # abs(b) vals
    intermediate_b = np.abs(b, out=intermediate_b)

    # maximum allowable abs(a) vals
    intermediate_b *= max_abs_val

    # is low enough
    intermediate_c = np.less_equal(
        intermediate_a, intermediate_b, out=intermediate_c
    )

    # denominator is non-zero
    out = np.not_equal(intermediate_b, 0, out=out)

    out &= intermediate_c

    return out


def _get_is_safe_to_reciprocal__c(
    x,  # complex64
    *,
    max_abs_val,
    out  # bool
):
    min_abs_val = 1 / max_abs_val

    return np.less_equal(min_abs_val, x, out=out)


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


def safe_divide__cf(
    a,  # complex64
    b,  # float32
    *,
    max_abs_val,
    intermediate_a=None,  # float32
    intermediate_b=None,  # float32
    intermediate_c=None,  # bool
    intermediate_d=None,  # bool
    out=None  # complex64
):
    intermediate_d = _get_is_safe_to_divide__cf(
        a, b,
        max_abs_val=max_abs_val,
        intermediate_a=intermediate_a,
        intermediate_b=intermediate_b,
        intermediate_c=intermediate_c,
        out=intermediate_d
    )

    if np.any(intermediate_d):
        out = np.divide(a, b, out=out)

        if not np.all(intermediate_d):
            _interpolate_missing(out, is_present=intermediate_d)
    elif out is None:
        out = np.zeros(a.shape, dtype=np.complex64)
    else:
        out.fill(0)

    return out


def safe_divide__fc(
    a,  # float32
    b,  # complex64
    *,
    max_abs_val,
    intermediate_a=None,  # float32
    intermediate_b=None,  # bool
    intermediate_c=None,  # bool
    out=None  # complex64
):
    intermediate_c = _get_is_safe_to_divide__fc(
        a, b,
        max_abs_val=max_abs_val,
        intermediate_a=intermediate_a,
        intermediate_b=intermediate_b,
        out=intermediate_c
    )

    if np.any(intermediate_c):
        out = np.divide(a, b, out=out)

        if not np.all(intermediate_c):
            _interpolate_missing(out, is_present=intermediate_c)
    elif out is None:
        out = np.zeros(a.shape, dtype=np.complex64)
    else:
        out.fill(0)

    return out


def safe_divide__cc(
    a,  # complex64
    b,  # complex64
    *,
    max_abs_val,
    intermediate_a,  # float32
    intermediate_b,  # float32
    intermediate_c,  # bool
    intermediate_d,  # bool
    out=None  # complex64
):
    out = _get_is_safe_to_divide__cc(
        a, b,
        max_abs_val=max_abs_val,
        intermediate_a=intermediate_a,
        intermediate_b=intermediate_b,
        intermediate_c=intermediate_c,
        out=intermediate_d
    )

    if np.any(intermediate_d):
        out = np.divide(a, b, out=out)

        if not np.all(intermediate_d):
            _interpolate_missing(out, is_present=intermediate_d)
    elif out is None:
        out = np.zeros(a.shape, dtype=np.complex64)
    else:
        out.fill(0)

    return out


def safe_reciprocal__c(x, *, max_abs_val, intermediate=None, out=None):
    intermediate = _get_is_safe_to_reciprocal__c(
        x, max_abs_val=max_abs_val, out=intermediate
    )

    if np.any(intermediate):
        out = np.divide(1, x, out=out)

        if not np.all(intermediate):
            _interpolate_missing(out, is_present=intermediate)
    elif out is None:
        out = np.zeros(x.shape, dtype=np.complex64)
    else:
        out.fill(0)

    return out
