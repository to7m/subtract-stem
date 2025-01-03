from fractions import Fraction
import numpy as np

from subtract_stem_lib import *


def load_audios():
    keys_audio, _ = load_mono_audio("keys.wav")
    monitor_audio, _ = load_mono_audio("monitor.wav")
    bass_audio, _ = load_mono_audio("bass.wav")

    return keys_audio, monitor_audio, bass_audio


keys_audio, monitor_audio, bass_audio = load_audios()


for x in GenerateSpectra(
    transforms_start_i=100, num_of_transforms=100, interval_len=500,
    audio=keys_audio, window=
    logger=True
):
    print(x)


raise SystemExit


for x in GenerateStemAndMixSpectra(logger=True):
    print(x)
x = GenerateSingleEqProfile(logger=True).run()
for x in GenerateRunningEqProfile(logger=True):
    print(x)
find_delay_stem_s(logger=True)
subtract_single_stem_from_mix(logger=True)
subtract_running_stem_from_mix(logger=True)
subtract_single_intermediate_from_mix(logger=True)
subtract_running_intermediate_from_mix(logger=True)
