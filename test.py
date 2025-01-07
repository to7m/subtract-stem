from fractions import Fraction
import numpy as np

from subtract_stem_lib import *


np.set_printoptions(suppress=True)


def logger(msg, *, iteration=None, **kwargs):
    if iteration is not None and iteration % 100 != 0:
        return

    if msg is not None:
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


#keys_audio, monitor_audio, bass_audio = load_audios()

for val, score in hone_in(lambda x: (x-4.1)**2, logger=logger):
    print(val, score)


raise SystemExit

find_delay_stem_s(logger=logger)

raise SystemExit

subtract_single_stem_from_mix(logger=logger)

subtract_running_stem_from_mix(logger=logger)

subtract_single_intermediate_from_mix(logger=logger)

subtract_running_intermediate_from_mix(logger=logger)
