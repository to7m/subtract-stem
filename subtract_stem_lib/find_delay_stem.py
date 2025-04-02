from .defaults import (
    FIND_DELAY_STEM_SAMPLES_VAL_ADD, FIND_DELAY_STEM_SAMPLES_MIN_DIFF
    FIND_DELAY_STEM_SECONDS_VAL_ADD, FIND_DELAY_STEM_SECONDS_MIN_DIFF
)
from ._sanitisation import san
from ._sanitise_unique_arrays_of_shape import sanitise_unique_arrays_of_shape


class FindDelayStemSamples:
    __slots__ = [
        "stem_audio", "mix_audio",
        "start_i", "interval_len", "num_of_iterations_per_guess",
        "grain_len",
        "first_guess", "first_guess_add", "min_guess_diff",
        "max_abs_eq_profile",
        "intermediate_a", "intermediate_b", "intermediate_c",
        "intermediate_d", "intermediate_e",
        "logger",
        "results"
    ]

    def __init__(
        self,
        stem_audio, mix_audio,
        start_i, 
    ):
        self.stem_audio, self.mix_audio = san("stem_audio"), san("mix_audio")
        self.start_i = san("start_i")
        self.grain_len, self.interval_len \
            = sanitise_hann_grain_len_interval_len(grain_len, interval_len)
        self.num_of_iterations_per_guess = san("num_of_iterations_per_guess")
        self.first_guess = san("first_guess")
        self.first_guess_add = san("first_guess_add")
        self.min_guess_diff = san("min_guess_diff")
        self.max_abs_eq_profile = san("max_abs_eq_profile")
        (
            self.intermediate_a, self.intermediate_b, self.intermediate_c,
            self.intermediate_d, self.intermediate_e
        ) = self._sanitise_intermediates(
            intermediate_a, intermediate_b, intermediate_c, intermediate_d,
            intermediate_e
        )
        self.logger = san("logger")
        self.results = None

    def __iter__(self):
        for results in hone_in(
            self._get_sum_abs_eq_profile,
            first_val=self.first_guess, val_add=self.first_guess_add,
            highest_wins=True,
            min_diff=self.min_guess_diff
        ):
            self.results = results

            yield

    def _sanitise_intermediates(
        self,
        intermediate_a, intermediate_b, intermediate_c, intermediate_d,
        intermediate_e
    ):
        return sanitise_unique_arrays_of_shape(
            array_infos=[
                (intermediate_a, "intermediate_a", "float"),
                (intermediate_b, "intermediate_b", "complex"),
                (intermediate_c, "intermediate_c", "complex"),
                (intermediate_d, "intermediate_d", "bool"),
                (intermediate_e, "intermediate_e", "complex")
            ],
            reference_shape=(self.grain_len,),
            reference_name="'grain_len'"
        )

    def _get_sum_abs_eq_profile(self, delay_stem_samples):
        logger = self.logger

        audio_pair_to_eq_profile = AudioPairToEqProfile(
            self.stem_audio, self.mix_audio,
            start_i=self.start_i, interval_len=self.interval_len,
            num_of_iterations=self.num_of_iterations_per_guess,
            grain_len=self.grain_len,
            delay_stem_samples=delay_stem_samples,
            max_abs_result=self.max_abs_eq_profile,
            intermediate_a=self.intermediate_a,
            intermediate_b=self.intermediate_b,
            intermediate_c=self.intermediate_c,
            intermediate_d=self.intermediate_d,
            out=self.intermediate_e
        )

        logger(delay_stem_samples, 0)
        for i, _ in enumerate(audio_pair_to_eq_profile, 1):
            logger(delay_stem_samples, i)

        eq_profile = audio_pair_to_eq_profile.calculate_eq_profile()

        return abs(eq_profile).sum()


+...
class FindDelayStemSeconds:
    ...
