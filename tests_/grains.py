import numpy as np

import subtract_stem_lib as ssl


def _test_grains(
    *,
    audio_len=10_000,
    start_i=-3000, interval_len=111, num_of_iterations=150,
    grain_len=999,
    delay_audio_samples=0.0
):
    rng = np.random.default_rng(0)

    audio = np.ones(audio_len, dtype=np.float32)

    audio_to_hann_grains = ssl.AudioToHannGrains(
        audio,
        start_i=start_i,
        interval_len=interval_len,
        num_of_iterations=num_of_iterations,
        grain_len=grain_len,
        delay_audio_samples=delay_audio_samples
    )

    result_audio = audio.copy()

    add_grains_to_audio = ssl.AddGrainsToAudio(
        grain=audio_to_hann_grains.out,
        start_i=audio_to_hann_grains.start_i,
        interval_len=interval_len,
        num_of_iterations=num_of_iterations,
        subtract=True,
        audio=result_audio
    )

    for i, _ in enumerate(zip(audio_to_hann_grains, add_grains_to_audio)):
        pass

    if i != num_of_iterations - 1:
        raise Exception("test failed")

    if np.abs(result_audio).max() > 0.000_001:
        raise Exception("test failed")


def test_grains():

    _test_grains()
