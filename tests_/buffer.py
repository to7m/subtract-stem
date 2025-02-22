import numpy as np

import subtract_stem_lib as ssl


def test_buffer():
    for lookbehind in range(5):
        buffer = ssl.buffer_from_array_args(
            10, dtype=np.int8, lookbehind=lookbehind
        )

        buffer.newest[:] = 13

        for iteration in range(lookbehind):
            buffer.increment_and_get_newest()[:] = 17

        if (buffer.oldest[:] != 13).any():
            raise Exception("test failed")
