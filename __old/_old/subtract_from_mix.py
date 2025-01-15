from fractions import Fraction

from .defaults import LOOKBEHIND_S, LOOKAHEAD_S
from .stem_in_mix import (
    GenerateSingleStemInMix, GenerateRunningStemInMix
)
from .intermediate_in_mix import (
    GenerateSingleIntermediateInMix, GenerateRunningIntermediateInMix
)


def subtract_single_stem_from_mix():
    Generate


def subtract_running_stem_from_mix(
    *,
    stem_audio, mix_audio,
    start_s=None, stop_s=None,
    centre=True,
    lookbehind_s=LOOKBEHIND_S, lookahead_s=LOOKAHEAD_S,
    delay_stem_s=Fraction(0)
):
    stem_in_mix, start_sample = GenerateRunningStemInMix(
        stem_audio=stem_audio, mix_audio=mix_audio,
        start_s=start_s, stop_s=stop_s,
        centre=centre,
        lookbehind_s=lookbehind_s, lookahead_s=lookahead_s,
        delay_stem_s=delay_stem_s,
    ).run()

    stop_sample = start_sample + len(stem_in_mix)

    out_audio = mix_audio[:stop_sample].copy()
    out_audio[:start_sample] = 0
    out_audio[start_sample:] -= stem_in_mix

    return out_audio


def subtract_single_intermediate_from_mix():
    ...


def subtract_running_intermediate_from_mix(
    *,
    stem_audio, intermediate_audio, mix_audio,
    intermediate_to_stem_eq_profile,
    start_s=None, stop_s=None,
    centre=True,
    lookbehind_s=LOOKBEHIND_S, lookahead_s=LOOKAHEAD_S,
    delay_stem_s=Fraction(0), delay_intermediate_s=Fraction(0),
):
    (
        intermediate_in_mix, start_sample
    ) = GenerateRunningIntermediateInMix(
        stem_audio=stem_audio,
        intermediate_audio=intermediate_audio,
        mix_audio=mix_audio,
        intermediate_to_stem_eq_profile=intermediate_to_stem_eq_profile,
        start_s=start_s, stop_s=stop_s,
        centre=centre,
        lookbehind_s=lookbehind_s, lookahead_s=lookahead_s,
        delay_stem_s=delay_stem_s,
        delay_intermediate_s=delay_intermediate_s
    ).run()

    stop_sample = start_sample + len(intermediate_in_mix)

    out_audio = mix_audio[:stop_sample].copy()
    out_audio[:start_sample] = 0
    out_audio[start_sample:] -= intermediate_in_mix

    return out_audio
