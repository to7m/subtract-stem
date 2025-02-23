import numpy as np

import subtract_stem_lib as ssl


def test_transforms():
    rng = np.random.default_rng(0)

    grain = rng.random(100, dtype=np.float32)
    first_grain = grain.copy()

    forward = ssl.GrainsToSpectraBuffer(grain)
    inverse = ssl.SpectraBufferOldestToComplexGrains(forward.out)
    out_grain = inverse.out.real

    next(zip(forward, inverse))

    if np.abs(out_grain - first_grain).max() > 0.000_001:
        raise Exception("test failed")
