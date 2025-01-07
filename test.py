from fractions import Fraction
import numpy as np

from subtract_stem_lib import *


def logger(msg, *, iteration=None, **kwargs):
    if iteration is not None and iteration % 100 != 0:
        return

    if kwargs:
        print(f"LOG  {msg}  {kwargs}")
    else:
        print(f"LOG  {msg}")

    return logger


def load_audios():
    keys_audio, _ = load_mono_audio("keys.wav")
    monitor_audio, _ = load_mono_audio("monitor.wav")
    bass_audio, _ = load_mono_audio("bass.wav")

    return keys_audio, monitor_audio, bass_audio


keys_audio, monitor_audio, bass_audio = load_audios()

x = GenerateSingleEqProfile(
    stem_audio=keys_audio, mix_audio=monitor_audio, sample_rate=48000,
    logger=logger
).run()
print(x)
print(np.abs(x))
print(np.angle(x))
raise SystemExit

for x in GenerateRunningEqProfile(logger=logger):
    print(x)

find_delay_stem_s(logger=logger)

subtract_single_stem_from_mix(logger=logger)

subtract_running_stem_from_mix(logger=logger)

subtract_single_intermediate_from_mix(logger=logger)

subtract_running_intermediate_from_mix(logger=logger)
