import numpy as np
from fractions import Fraction

from .defaults import (
    LOOKBEHIND_S, LOOKAHEAD_S, MAX_AMPLIFICATION, TRANSFORM_LEN
)
from .sanitisation import sanitise_args, sanitise_logger
from .math import (
    ataabtrnfatbaa, from_abs_and_angle, safe_divide__cf, to_abs_and_angle
)
from .spectra import GenerateStemAndMixSpectra


class _SingleConstants:
    def __init__(
        self, *,
        stem_audio, mix_audio, sample_rate,
        start_s, stop_s,
        delay_stem_s,
        transform_len,
        max_amplification,
        logger
    ):
        self.stem_and_mix_spectra = GenerateStemAndMixSpectra(
            stem_audio=stem_audio, mix_audio=mix_audio,
            sample_rate=sample_rate,
            start_s=start_s, stop_s=stop_s,
            delay_stem_s=delay_stem_s,
            transform_len=transform_len,
        )

        self.transform_len = transform_len
        self.max_amplification = max_amplification
        self.logger = logger

        self.num_of_iterations = self.stem_and_mix_spectra.num_of_iterations
        self.last_iteration_i = self.num_of_iterations - 1


class _RunningConstants:
    def __init__(
        self, *,
        stem_audio, mix_audio, sample_rate,
        start_s, stop_s,
        delay_stem_s,
        transform_len,
        lookbehind_s, lookahead_s,
        max_amplification,
        logger
    ):
        self.retained_len = lookahead_iterations + 1
        self.stem_and_mix_spectra = GenerateStemAndMixSpectra(
            stem_audio=stem_audio, mix_audio=mix_audio,
            sample_rate=sample_rate,
            start_s=start_s, stop_s=stop_s,
            delay_stem_s=delay_stem_s,
            transform_len=transform_len,
            additional_iterations_before=lookbehind_iterations,
            additional_iterations_after=lookahead_iterations,
            stem_num_of_retained=self.retained_len
        )

        self._sample_rate = sample_rate
        self.transform_len = transform_len
        self._lookbehind_s, self._lookahead_s = lookbehind_s, lookahead_s
        self.max_amplification = max_amplification
        self.logger = logger

        (
            self.num_of_initialisation_iterations,
            self.num_of_main_iterations,
            self.num_of_total_iterations
        ) = self._get_nums_of_iterations_for_stages()

        self.cumsum_len = self.num_of_initialisation_iterations + 2
        self.cumsum_shape = self.cumsum_len, transform_len

    def _get_nums_of_iterations_for_stages(self):
        interval_s = (self.transform_len // 2) / self._sample_rate
        num_of_lookbehind_iterations = round(self._lookbehind_s / interval_s)
        num_of_lookahead_iterations = round(self._lookahead_s / interval_s)

        num_of_total_iterations = self.stem_and_mix_spectra.num_of_iterations
        num_of_initialisation_iterations \
            = num_of_lookbehind_iterations + num_of_lookahead_iterations
        num_of_main_iterations \
            = num_of_total_iterations - num_of_initialisation_iterations

        return (
            num_of_initialisation_iterations, num_of_main_iterations,
            num_of_total_iterations
        )


class _SingleIterator:
    def __init__(self, constants):
        self._constants = constants

        self._stem_and_mix_spectra_iter \
            = iter(constants.stem_and_mix_spectra)

        self._i = 0
        self._abs_stem_spectrum \
            = np.empty(constants.transform_len, dtype=np.float32)
        self._rotated_mix_spectrum \
            = np.empty(constants.transform_len, dtype=np.complex64)
        self._abs_stem_spectra_sum \
            = np.zeros(constants.transform_len, dtype=np.float32)
        self._rotated_mix_spectra_sum \
            = np.zeros(constants.transform_len, dtype=np.complex64)

        self._log_progress()

    def __iter__(self):
        return self

    def __next__(self):
        if self._i >= self._constants.last_iteration_i:
            if self._i == self._constants.last_iteration_i:
                self._routine()

                return self._calculate_eq_profile()
            else:
                raise StopIteration
        else:
            self._routine()

            return None

    def _log_progress(self):
        num_of_iterations = self._constants.num_of_iterations

        self._constants.logger(
            msg=(
                f"pairs of spectra made and rotated: {self._i} of "
                f"{num_of_iterations}"
            ),
            iteration=self._i, num_of_iterations=num_of_iterations
        )

    def _routine(self):
        stem_spectrum, mix_spectrum = next(self._stem_and_mix_spectra_iter)

        abs_stem_spectrum, rotated_mix_spectrum = ataabtrnfatbaa(
            stem_spectrum, mix_spectrum,
            out_a=self._abs_stem_spectrum, out_b=self._rotated_mix_spectrum
        )

        self._abs_stem_spectra_sum += abs_stem_spectrum
        self._rotated_mix_spectra_sum += rotated_mix_spectrum

        self._i += 1
        self._log_progress()

    def _calculate_eq_profile(self):
        return safe_divide__cf(
            self._rotated_mix_spectra_sum, self._abs_stem_spectra_sum,
            max_abs_val=self._constants.max_amplification
        )


class _RunningIterator:
    def __init__(self, constants):
        self._constants = constants

        self._stem_and_mix_spectra_iter \
            = iter(constants.stem_and_mix_spectra)

        self._i = 0
        self._abs_stem_spectrum \
            = np.empty(constants.transform_len, dtype=np.float32)
        self._rotated_mix_spectrum \
            = np.empty(constants.transform_len, dtype=np.complex64)
        self._retained_stem_spectra \
            = [None for _ in range(constants.retained_len)]
        self._abs_stem_spectra_cumsum \
            = np.empty(constants.cumsum_shape, dtype=np.float32)
        self._rotated_mix_spectra_cumsum \
            = np.empty(constants.cumsum_shape, dtype=np.complex64)
        self._abs_stem_spectra_sum \
            = np.empty(constants.transform_len, dtype=np.float32)
        self._rotated_mix_spectra_sum \
            = np.empty(constants.transform_len, dtype=np.complex64)
        self._safe_divide_intermediate_arrays \
            = self._get_safe_divide_intermediate_arrays()
        self._eq_profile \
            = np.empty(constants.transform_len, dtype=np.complex64)

        self._log_initialisation_progress()
        self._initialisation_iterations()

        self._log_main_progress()

    def __iter__(self):
        return self

    def __next__(self):
        if self._i == self._constants.num_of_total_iterations:
            raise StopIteration

        self._common_routine()
        eq_profile = self._calculate_eq_profile()
        stem_spectrum = self._get_old_stem_spectrum()

        self._i += 1
        self._log_main_progress()

        return eq_profile, stem_spectrum

    def _get_safe_divide_intermediate_arrays(self):
        return {
            f"intermediate_{chr(ord('a') + i)}":
                np.empty(self._constants.transform_len, dtype=dtype)
            for i, dtype in enumerate([np.float32, np.float32, bool, bool])
        }

    def _log_initialisation_progress(self):
        num_of_iterations = self._constants.num_of_initialisation_iterations

        self._constants.logger(
            msg=(
                f"pairs of initialisation spectra made and rotated: "
                f"{self._i} of {num_of_iterations}"
            ),
            iteration=self._i,
            num_of_initialisation_iterations=num_of_iterations
        )

    def _add_to_cumsum(self, spectrum, *, cumsum):
        curr_i = self._i % self._constants.cumsum_len

        if curr_i == 0:
            cumsum[0] = spectrum
        else:
            np.add(cumsum[curr_i - 1], spectrum, out=cumsum[curr_i])

    def _common_routine(self):
        stem_spectrum, mix_spectrum = next(self._stem_and_mix_spectra_iter)

        retained_i = self._i % self._constants.retained_len
        self._retained_stem_spectra[retained_i] = stem_spectrum

        abs_stem_spectrum, rotated_mix_spectrum = ataabtrnfatbaa(
            stem_spectrum, mix_spectrum,
            out_a=self._abs_stem_spectrum, out_b=self._rotated_mix_spectrum
        )

        self._add_to_cumsum(
            abs_stem_spectrum, cumsum=self._abs_stem_spectra_cumsum
        )
        self._add_to_cumsum(
            rotated_mix_spectrum, cumsum=self._rotated_mix_spectra_cumsum
        )

    def _initialisation_iterations(self):
        while self._i < self._constants.num_of_initialisation_iterations:
            self._common_routine()

            self._i += 1
            self._log_initialisation_progress()

    def _log_main_progress(self):
        main_i = self._i - self._constants.num_of_initialisation_iterations
        num_of_iterations = self._constants.num_of_main_iterations

        self._constants.logger(
            msg=(
                f"number of EQ profiles made: {main_i} of {num_of_iterations}"
            ),
            iteration=main_i, num_of_main_iterations=num_of_iterations
        )

    def _get_sum(self, *, cumsum, out):
        curr_i = self._i % self._constants.cumsum_len
        take_i = (curr_i + 1) % self._constants.cumsum_len

        np.subtract(cumsum[curr_i], cumsum[take_i], out=out)

        if take_i != 0:
            out += cumsum[-1]

        return out

    def _calculate_eq_profile(self):
        abs_stem_spectra_sum = self._get_sum(
            cumsum=self._abs_stem_spectra_cumsum,
            out=self._abs_stem_spectra_sum
        )
        rotated_mix_spectra_sum = self._get_sum(
            cumsum=self._rotated_mix_spectra_cumsum,
            out=self._rotated_mix_spectra_sum
        )

        return safe_divide__cf(
            rotated_mix_spectra_sum, abs_stem_spectra_sum,
            max_abs_val=self._constants.max_amplification,
            **self._safe_divide_intermediate_arrays,
            out=self._eq_profile
        )

    def _get_old_stem_spectrum(self):
        return self._retained_stem_spectra[
            (self._i + 1) % self._constants.retained_len
        ]


class GenerateSingleEqProfile:
    def __init__(
        self, *,
        stem_audio, mix_audio, sample_rate,
        start_s=Fraction(0), stop_s=None,
        delay_stem_s=Fraction(0),
        transform_len=TRANSFORM_LEN,
        max_amplification=MAX_AMPLIFICATION,
        logger=None
    ):
        self._constants = _SingleConstants(
            stem_audio=stem_audio, mix_audio=mix_audio,
            sample_rate=sample_rate,
            start_s=start_s, stop_s=stop_s,
            delay_stem_s=delay_stem_s,
            transform_len=transform_len,
            **sanitise_args({
                "max_amplification": max_amplification,
                "logger": logger
            })
        )

        self.num_of_iterations = self._constants.num_of_iterations

    def __iter__(self):
        return _SingleIterator(self._constants)

    def run(self):
        for eq_profile in self:
            pass

        return eq_profile


class GenerateRunningEqProfile:
    def __init__(
        self, *,
        stem_audio, mix_audio, sample_rate,
        start_s=Fraction(0), stop_s=None,
        delay_stem_s=Fraction(0),
        transform_len=TRANSFORM_LEN,
        lookbehind_s=LOOKBEHIND_S, lookahead_s=LOOKAHEAD_S,
        max_amplification=MAX_AMPLIFICATION,
        logger=None
    ):
        self._constants = _RunningConstants(
            stem_audio=stem_audio, mix_audio=mix_audio,
            sample_rate=sample_rate,
            start_s=start_s, stop_s=stop_s,
            delay_stem_s=delay_stem_s,
            transform_len=transform_len,
            **sanitise_args({
                "lookbehind_s": lookbehind_s, "lookahead_s": lookahead_s,
                "max_amplification": max_amplification,
                "logger": logger
            })
        )

        self.num_of_initialisation_iterations \
            = self._constants.num_of_initialisation_iterations
        self.num_of_main_iterations = self._constants.num_of_main_iterations

    def __iter__(self):
        return _RunningIterator(self._constants)
