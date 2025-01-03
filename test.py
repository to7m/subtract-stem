from fractions import Fraction

from subtract_stem_lib import *


def load_audios():
    keys_audio, _ = load_mono_audio("keys.wav")
    monitor_audio, _ = load_mono_audio("monitor.wav")
    bass_audio, _ = load_mono_audio("bass.wav")

    return keys_audio, monitor_audio, bass_audio


keys_audio, monitor_audio, bass_audio = load_audios()

save_mono_audio("audio_path.wav", keys_audio, sample_rate=Fraction(48000))


safe_reciprocal__c()
safe_divide__cf()
for x in GenerateSpectra(logger=True):
    print(x)
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
