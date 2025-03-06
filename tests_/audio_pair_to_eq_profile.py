from math import tau
import numpy as np

import subtract_stem_lib as ssl


def _make_cos_wave(len_, *, freq, delay_samples=0.0):
    return np.cos(
        (np.arange(len_, dtype=np.float32) - delay_samples)
        * (freq * tau / len_)
    )


def test_freq_and_noise():
    rng = np.random.default_rng(0)

    stem_block = _make_cos_wave(20, freq=4)
    mix_block = _make_cos_wave(20, freq=4, delay_samples=3.0) * 700

    stem_audio = rng.random(10000, dtype=np.float32) * 0.2 - 0.1
    mix_audio = rng.random(10000, dtype=np.float32) * 0.2 - 0.1
    mix_audio[:-3] += stem_audio[3:] * 5
    for i in range(0, 10000, 20):
        stem_audio[i:i+20] += stem_block
        mix_audio[i:i+20] += mix_block

    audio_pair_to_eq_profile = ssl.AudioPairToEqProfile(
        stem_audio, mix_audio,
        start_i=100, interval_len=10, num_of_iterations=900,
        grain_len=20,
        delay_stem_samples=-3
    )

    for _ in audio_pair_to_eq_profile:
        pass

    result = audio_pair_to_eq_profile.calculate_eq_profile()

    result[3:6] *= 5 / 700
    result[-5:-2] *= 5 / 700

    if abs(abs(result) - 5).max() > 0.1:
        raise Exception("test failed")


def test_random():
    rng = np.random.default_rng(0)

    stem_block = rng.random(20, dtype=np.float32)

    mix_block = np.empty(20, dtype=np.float32)
    mix_block[:-3] = stem_block[3:]
    mix_block[-3:] = stem_block[:3]
    mix_block *= 456

    stem_audio = np.zeros(10000, dtype=np.float32)
    mix_audio = rng.random(10000, dtype=np.float32) * 200 - 100
    for i in range(0, 10000, 20):
        stem_audio[i:i+20] += stem_block
        mix_audio[i:i+20] += mix_block

    audio_pair_to_eq_profile = ssl.AudioPairToEqProfile(
        stem_audio, mix_audio,
        start_i=100, interval_len=10, num_of_iterations=900,
        grain_len=20,
        delay_stem_samples=-3
    )

    for _ in audio_pair_to_eq_profile:
        pass

    result = audio_pair_to_eq_profile.calculate_eq_profile()

    if abs(abs(result) - 456).max() > 21:
        raise Exception("test failed")


def all_audio_pair_to_eq_profile():
    test_freq_and_noise()
    test_random()
