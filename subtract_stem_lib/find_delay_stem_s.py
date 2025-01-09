from fractions import Fraction
import numpy as np

from .defaults import (
    DELAY_STEM_S_START_ADD, MAX_AMPLIFICATION, MIN_DIFF_S, TRANSFORM_LEN
)
from .sanitisation import sanitise_args
from .hone_in_simple import hone_in
from .eq_profile import GenerateSingleEqProfile


class _DelayStemSFinder:
    def __init__(
        self, *,
        delay_stem_s_start_val, delay_stem_s_start_add,
        min_diff_s,
        logger,
        **static_args
    ):
        self._start_val = delay_stem_s_start_val
        self._start_add = delay_stem_s_start_add
        self._min_diff = min_diff_s
        self._static_args = static_args

        self._hone_in_logger = self._wrap_logger(logger)

    def _wrap_logger(self, logger):
        def hone_in_logger(msg, iteration, val, score=None):
            if score is None:
                logger(
                    msg=f"scoring delay_stem_s: {float(val)}",
                    iteration=iteration, delay_stem_s=val
                )

                outer_iteration = iteration

                def generate_single_eq_profile_logger(
                    msg, iteration, num_of_iterations
                ):
                    logger(
                        msg=(
                            f"delay_stem_s {float(val)}: pairs of spectra "
                            f"made and rotated: {iteration} of "
                            f"{num_of_iterations}"
                        ),
                        iteration=outer_iteration, delay_stem_s=val,
                        inner_iteration=iteration,
                        num_of_inner_iterations=num_of_iterations
                    )

                return generate_single_eq_profile_logger
            else:
                logger(
                    msg=f"delay_stem_s {float(val)} score: {score}",
                    iteration=iteration, delay_stem_s=val, score=score
                )

        return hone_in_logger

    def _scoring_function(self, delay_stem_s, logger):
        eq_profile = GenerateSingleEqProfile(
            **self._static_args,
            delay_stem_s=delay_stem_s,
            logger=logger
        ).run()

        return np.sum(np.abs(eq_profile))

    def run(self):
        return hone_in(
            self._scoring_function,
            aim_lowest=False,
            start_val=self._start_val, start_add=self._start_add,
            min_diff=self._min_diff,
            logger=self._hone_in_logger
        )


def find_delay_stem_s(
    *,
    stem_audio, mix_audio, sample_rate,
    start_s=Fraction(0), stop_s=None,
    delay_stem_s_start_val=Fraction(0),
    delay_stem_s_start_add=DELAY_STEM_S_START_ADD,
    min_diff_s=MIN_DIFF_S,
    transform_len=TRANSFORM_LEN,
    max_amplification=MAX_AMPLIFICATION,
    logger=None
):
    return _DelayStemSFinder(**sanitise_args({
        "stem_audio": stem_audio, "mix_audio": mix_audio,
        "sample_rate": sample_rate,
        "start_s": start_s, "stop_s": stop_s,
        "delay_stem_s_start_val": delay_stem_s_start_val,
        "delay_stem_s_start_add": delay_stem_s_start_add,
        "min_diff_s": min_diff_s,
        "transform_len": transform_len,
        "max_amplification": max_amplification,
        "logger": logger
    })).run()
