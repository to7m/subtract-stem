from math import atan2, pi

from ._safe_divide import safe_divide__cf, safe_reciprocal__c


ONE_ROTATED = (-1) ** (1 / pi)
ONE_ROTATED_CONJUGATED = (-1) ** (-1 / pi)


def ataabtrnfatbaa(
    a,  # complex64
    b,  # complex64
    *,
    out_a=None,  # float32
    out_b=None  # complex64
):
    """Apply to 'a' and 'b' the rotation needed for 'a' to become abs(a)."""

    np.abs(a, out=out_a)

    phase = np.angle(a)
    np.power(ONE_ROTATED_CONJUGATED, phase, out=out_b)
    out_b *= b

    return out_a, out_b


def from_abs_and_angle(a, b):
    return a * ONE_ROTATED ** b


def to_abs_and_angle(x):
    return abs(x), atan2(x.imag, x.real)
