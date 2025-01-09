from fractions import Fraction
import numpy as np

from subtract_stem_lib import *


np.set_printoptions(suppress=True)


def logger(msg=None, **kwargs):
    key = "inner_iteration" if "delay_stem_s" in kwargs else "iteration"
    if key in kwargs and kwargs[key] % 1000 != 0:
        return

    print(f"LOG  {msg}")

    return logger


def load_audios():
    keys_audio, _ = load_mono_audio("keys.wav")
    monitor_audio, _ = load_mono_audio("monitor.wav")
    bass_audio, _ = load_mono_audio("bass.wav")

    return keys_audio, monitor_audio, bass_audio


keys_audio, monitor_audio, bass_audio = load_audios()

stem_in_mix, delay_samples = GenerateSingleStemInMix(
    stem_audio=keys_audio, sample_rate=48000,
    logger=logger
).run()
print(stem_in_mix,delay_samples)

raise SystemExit

GenerateRunningStemInMix(
    logger=logger
)

GenerateSingleIntermediateInMix(
    logger=logger
)

GenerateRunningIntermediateInMix(
    logger=logger
)

subtract_single_stem_from_mix(logger=logger)

subtract_running_stem_from_mix(logger=logger)

subtract_single_intermediate_from_mix(logger=logger)

subtract_running_intermediate_from_mix(logger=logger)
