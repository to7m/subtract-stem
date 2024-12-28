from fractions import Fraction

from subtract_stem_lib import *


start_sample, stop_sample = get_samples_for_start_stop(
    start_s, stop_s, sample_rate=sample_rate
)


generate_running_eq_profile = GenerateRunningEqProfile(
    sample_rate=48000,
    transform_len=1350,
    start_sample=start_sample, stop_sample=stop_sample,
    lookbehind_s=20, lookahead_s=20
)

for eq_profile, stem_spectrum in generate_running_eq_profile:
    pass
