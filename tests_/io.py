import numpy as np

import subtract_stem_lib as ssl


def test_io(self):
    rng = np.random.default_rng(0)

    tmp_test_path = "_tmp_test_path.wav"

    a = rng.random(10_000, dtype=np.float32)

    try:
        ssl.save_audio(a, tmp_test_path, sample_rate=123_456)
        b, sample_rate = ssl.read_audio(tmp_test_path)

        if sample_rate != 123_456:
            raise Exception("test failed")

        if (a != b).any():
            raise Exception("test failed")
    finally:
        tmp_test_path.unlink()

    print("moo")
