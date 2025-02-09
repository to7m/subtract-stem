import numpy as np

import subtract_stem_lib as ssl


rng = np.random.default_rng(0)


def safe_divide():
    for _ in range(10):
        a = (
            rng.random(10, dtype=np.float32)
            + 1j * rng.random(10, dtype=np.float32)
        )
        b = rng.random(10, dtype=np.float32)

        result = ssl.safe_divide(
            a, b,
            max_abs_result=3.5
        )

        print(np.abs(result).max())


def all_divide():
    safe_divide()
