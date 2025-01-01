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

    return out


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
    is_safe = _get_is_safe(
        a, b,
        max_amplification=max_amplification,
        intermediate_a=intermediate_a,
        intermediate_b=intermediate_b,
        intermediate_c=intermediate_c
        out=intermediate_d
    )

    if np.any(is_safe):

    ...
        if np.any(is_safe):
            np.divide(
                self._rotated_mix_bins_sum,
                self._abs_stem_bins_sum,
                out=self._eq_profile
            )

            if not np.all(is_safe):
                self._interpolate_missing(is_safe)
        else:
            self._eq_profile.fill(0)

        return self._eq_profile