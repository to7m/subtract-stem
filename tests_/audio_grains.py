import numpy as np

import subtract_stem_lib as ssl


def _test_audio_grains(
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
        start_i=int(start_i - delay_audio_samples + delay_audio_samples % 1),
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
    for audio_len in 25, 10_000:
        for start_i in -3000, -2500:
            for interval_len, num_of_iterations in ((111, 150), (7, 2500)):
                for grain_len in 777, 2331:
                    for delay_audio_samples in 0.0, 3.7, -10.4:
                        _test_grains(
                            audio_len=audio_len,
                            start_i=start_i,
                            interval_len=interval_len,
                            num_of_iterations=num_of_iterations,
                            grain_len=grain_len,
                            delay_audio_samples=delay_audio_samples
                        )
