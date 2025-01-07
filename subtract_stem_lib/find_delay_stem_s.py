from fractions import Fraction

from .defaults import DEFAULT_DELAY_STEM_S_START_ADD, DEFAULT_MIN_DIFF_S
from .sanitisation import sanitise_args
from .hone_in import hone_in_high


class _DelayStemSFinder:
    def __init__(
        self, *,
        stem_audio, mix_audio, sample_rate,
        start_s, stop_s,
        delay_stem_s_start_val, delay_stem_s_start_add,
        min_diff_s,
        logger
    ):
        ...

    def _scoring_function(self, delay_stem_s, logger):
        ...



def find_delay_stem_s(
    *,
    stem_audio, mix_audio, sample_rate,
    start_s=None, stop_s=None,
    delay_stem_s_start_val=Fraction(0),
    delay_stem_s_start_add=DEFAULT_DELAY_STEM_S_START_ADD,
    min_diff_s=DEFAULT_MIN_DIFF_S,
    logger=None
):
    return delay_stem_s_finder = _DelayStemSFinder(**sanitise_args({
        "stem_audio": stem_audio, "mix_audio": mix_audio,
        "sample_rate": sample_rate,
        "start_s": start_s, "stop_s": stop_s,
        "delay_stem_s_start_val": delay_stem_s_start_val,
        "delay_stem_s_start_add": delay_stem_s_start_add,
        "min_diff_s": min_diff_s,
        "logger": logger
    })).run()

    def scoring_function(delay_stem_s, logger):
        eq_profile = GenerateSingleEqProfile(
            stem_audio=stem_audio, mix_audio=mix_audio,
            start_s=start_s, stop_s=stop_s, delay_stem_s=delay_stem_s,
            logger=logger
        ).run()

        return np.sum(np.abs(eq_profile))

    delay_stem_s = hone_in_high(
        scoring_function,
        start_val=delay_stem_s_start_val, start_add=delay_stem_s_start_add,
        min_diff=min_diff_s,
        logger=logger
    )

    return delay_stem_s
