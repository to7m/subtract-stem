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

    spectra_buffers_to_eq_profile.calculate_eq_profile()
    result = spectra_buffers_to_eq_profile.out

    if np.abs(result - eq_profile).max() > 0.000_001:
        raise Exception("test failed")

    if np.abs(mix_spectra - stem_spectra * result).max() > 0.000_001:
        raise Exception("test failed")


def test_running():
    rng = np.random.default_rng(0)

    stem_spectra = np.empty(100, dtype=np.complex64)
    mix_spectra = np.empty(100, dtype=np.complex64)

    spectra_buffers_to_eq_profiles = ssl.SpectraBuffersToEqProfiles(
        stem_spectra, mix_spectra, lookbehind=10
    )

    spectra_buffers_to_eq_profiles_iter = iter(spectra_buffers_to_eq_profiles)

    eq_profile_a = (
        rng.random(100, dtype=np.float32)
        + 1j * rng.random(100, dtype=np.float32)
    )
    eq_profile_b = (
        rng.random(100, dtype=np.float32)
        + 1j * rng.random(100, dtype=np.float32)
    )

    for _ in range(11):
        rng.random(dtype=np.float32, out=stem_spectra.view(np.float32))
        np.multiply(stem_spectra, eq_profile_a, out=mix_spectra)
        next(spectra_buffers_to_eq_profiles_iter)

    print(spectra_buffers_to_eq_profiles.out - eq_profile_a)



def all_eq_profiles():
    test_single()
    test_running()
    test_apply()
