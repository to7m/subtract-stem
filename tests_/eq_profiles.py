import numpy as np

import subtract_stem_lib as ssl


def test_single():
    rng = np.random.default_rng(0)

    eq_profile = (
        rng.random(100, dtype=np.float32)
        + 1j * rng.random(100, dtype=np.float32)
    )

    stem_spectra = np.empty(100, np.complex64)
    mix_spectra = np.empty(100, np.complex64)

    spectra_buffers_to_eq_profile \
        = ssl.SpectraBuffersToEqProfile(stem_spectra, mix_spectra)
    spectra_buffers_to_eq_profile_iter = iter(spectra_buffers_to_eq_profile)

    for _ in range(10):
        rng.random(dtype=np.float32, out=stem_spectra.view(np.float32))
        np.multiply(stem_spectra, eq_profile, out=mix_spectra)

        next(spectra_buffers_to_eq_profile_iter)

    result = spectra_buffers_to_eq_profile.get_eq_profile()

    if np.abs(result - eq_profile).max() > 0.000_001:
        raise Exception("test failed")

    if np.abs(mix_spectra - stem_spectra * result).max() > 0.000_001:
        raise Exception("test failed")


def all_eq_profiles():
    test_single()
    test_running()
    test_apply()
