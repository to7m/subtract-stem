import numpy as np

from .timestamp import Timestamp
from .buffer import (
    Buffer, buffer_from_constructor, buffer_from_array_args, buffer_from_array
)
from .hone_in import hone_in
from .divide import (
    UnsafeDivider, GenerateIsSafes, InterpolateMissing,
    SafeDivider, safe_divide, Ataabtrnfatbaa, ataabtrnfatbaa
)
from .io import load_audio, save_audio
from .audio_grains import AudioToGrains, AudioToHannGrains, AddGrainsToAudio
from .transforms import (
    GrainsToSpectraBuffer, SpectraBufferOldestToComplexGrains
)
from .eq_profiles import (
    SpectraBuffersToEqProfile, SpectraBuffersToEqProfiles,
    ApplyEqProfilesToSpectraBufferOldest
)
from .audio_pair_to_eq_profile import AudioPairToEqProfile
from .find_delay_stem import FindDelayStemSamples, FindDelayStemSeconds


# There's no thread-safe way of doing this so I'm just putting it here to make
# it obvious.
np.seterr(all="raise", divide="ignore", invalid="ignore")


""" old:
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
