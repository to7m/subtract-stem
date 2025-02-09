import numpy as np

import subtract_stem_lib as ssl


def safe_divide():
    rng = np.random.default_rng(0)

    max_abs_ret = 0.0
    for _ in range(10):
        a = (
            rng.random(100, dtype=np.float32)
            + 1j * rng.random(100, dtype=np.float32)
        )
        b = rng.random(100, dtype=np.float32)

        ret = ssl.safe_divide(a, b, max_abs_result=10.0)

        max_abs_ret = max(np.abs(ret).max(), max_abs_ret)

    if max_abs_ret > 10.0:
        raise Exception("test failed")


def ataabtrnfatbaa():
    rng = np.random.default_rng(0)

    a = (
        rng.random(100, dtype=np.float32)
        + 1j * rng.random(100, dtype=np.float32)
    )
    b = (
        rng.random(100, dtype=np.float32)
        + 1j * rng.random(100, dtype=np.float32)
    )

    abs_a, rotated_b = ssl.ataabtrnfatbaa(a, b)

    if (np.abs(a) != abs_a).any():
        raise Exception("test failed")

    for a_factor, b_factor in zip(a / abs_a, b / rotated_b):
        if not 0.999_999 < abs(a_factor) < 1.000_001:
            raise Exception("test failed")

        if abs(b_factor - a_factor) > 0.000_001:
            raise Exception("test failed")


def all_divide():
    safe_divide()
    ataabtrnfatbaa()
