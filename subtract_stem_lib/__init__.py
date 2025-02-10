import numpy as np


from .divide import (
    UnsafeDivider, GenerateIsSafes, InterpolateMissing,
    SafeDivider, safe_divide, Ataabtrnfatbaa, ataabtrnfatbaa
)
from .audio_grains import AudioToGrains, AudioToHannGrains, AddGrainsToAudio


# There's no thread-safe way of doing this so I'm just putting it here to make
# it obvious.
np.seterr(divide="ignore", invalid="ignore")


""" old:
from .math import (
    safe_divide__cf, safe_divide__fc, safe_divide_cc, safe_reciprocal__c
)
from .hone_in_simple import hone_in
from .io import load_mono_audio, save_mono_audio
from .spectra import GenerateSpectra, GenerateStemAndMixSpectra
from .eq_profile import GenerateSingleEqProfile, GenerateRunningEqProfile
from .find_delay_stem_s import find_delay_stem_s
from .stem_in_mix import (
    GenerateSingleStemInMix, GenerateRunningStemInMix
)
from .intermediate_in_mix import (
    GenerateSingleIntermediateInMix, GenerateRunningIntermediateInMix
)
from .subtract_from_mix import (
    subtract_single_stem_from_mix,
    subtract_running_stem_from_mix,
    subtract_single_intermediate_from_mix,
    subtract_running_intermediate_from_mix
)
"""