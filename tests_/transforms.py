import numpy as np


from subtract_stem_lib import (
    GrainsToSpectra, GrainsToSpectraBuffer,
    SpectraToGrains, SpectraBufferToGrains
)


def test_spectra():
    rng = np.random.default_rng(0)

    grain = rng.random(100, dtype=np.float32)

    grains_to_spectra = GrainsToSpectra(grain)
    spectra_to_grains = SpectraToGrains(grains_to_spectra.out)

    next(zip(grains_to_spectra, spectra_to_grains))

    if (spectra_to_grains.out - grain).max() > 0.000_001:
        raise Exception("test failed")


def test_spectra_buffer():
    rng = np.random.default_rng(0)

    grain = rng.random(100, dtype=np.float32)
    first_grain = grain.copy()

    grains_to_spectra_buffer \
        = GrainsToSpectraBuffer.from_grain_and_buffer_arg(
              grain, lookbehind=10
          )
    spectra_buffer_to_grains \
        = SpectraBufferToGrains(grains_to_spectra_buffer.out)

    iter_ = zip(grains_to_spectra_buffer, spectra_buffer_to_grains)

    next(iter_)

    for _ in range(10):
        rng.random(dtype=np.float32, out=grain)
        next(iter_)

    if (spectra_buffer_to_grains.out_newest - grain).max() > 0.000_001:
        raise Exception("test failed")

    if (spectra_buffer_to_grains.out_oldest - first_grain).max() > 0.000_001:
        raise Exception("test failed")


def all_transforms():
    test_spectra()
    test_spectra_buffer()
