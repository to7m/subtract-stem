import numpy as np

import subtract_stem_lib as ssl


def test_grains():
    rng = np.random.default_rng(0)

    audio = rng.random(10_000, dtype=np.float32)

    for overlap in range(2, 5):
        audio_to_hann_grains = ssl.AudioToHannGrains(
            audio,
            start_i=-307, interval_len=30, num_of_iterations=400,
            grain_len=30 * overlap
        )

        grain = audio_to_hann_grains.out

        result_audio = np.zeros(10_000, dtype=np.float32)

        add_grains_to_audio = ssl.AddGrainsToAudio(
            grain,
            start_i=-307, interval_len=30, num_of_iterations=400,
            subtract=True,
            audio=result_audio
        )

        for _ in zip(audio_to_hann_grains, add_grains_to_audio):
            pass

        print(np.abs(result_audio - audio).max())
