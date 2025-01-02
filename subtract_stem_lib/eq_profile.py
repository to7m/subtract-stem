import numpy as np

from .defaults import TRANSFORM_LEN, LOOKBEHIND_S, LOOKAHEAD_S
from .sanitisation import sanitise_args
from .math import (
    ataabtrnfatbaa, from_abs_and_angle, safe_divide__cf, to_abs_and_angle
)


class _SingleConstants:
    def __init__(self):
        ...


class _RunningConstants:
    def __init__(
        self, *,
        sample_rate, transform_len, lookbehind_s, lookahead_s
    ):
        _transforms_interval_s = transform_len / sample_rate

        self.num_of_before_iterations \
            = round(lookbehind_s / _transforms_interval_s)
        self.num_of_after_iterations \
            = round(lookahead_s / _transforms_interval_s)
        self.num_of_initialisation_iterations \
            = self.num_of_before_iterations + self.num_of_after_iterations

    def _(self):

        subsequent_num_of_transforms \
            = round(ideal_num_of_subsequent_transforms)

        centre_of_first_transform = (
            profile_middle_sample
            - subsequent_num_of_transforms * self.interval / 2
        )
        mix_transforms_start_i \
            = round(centre_of_first_transform - len(self.mix_window) // 2)

        stem_transforms_start_i \
            = mix_transforms_start_i - audio_data.delay_stem_samples_whole
        num_of_iterations = 1 + subsequent_num_of_iterations

        return (
            stem_transforms_start_i, mix_transforms_start_i, num_of_iterations
        )


class _SingleIterator:
    def __init__(self, constants):
        self._constants = constants

        self._i = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._i == self._constants.num_of_total_iterations:
            raise StopIteration

        +...


class _RunningIterator:
    def __init__(self, constants):
        self._constants = constants

        self._stem_and_mix_spectra_iter \
            = iter(constants._stem_and_mix_spectra)

        self._i = 0

        self._eq_profile \
            = np.empty(constants.transform_len, dtype=np.complex64)

        self._handle_before_spectra()

        # cumsums have to be 1 2d array each

    def __iter__(self):
        return self

    def __next__(self):
        if self._i == self._constants.num_of_total_iterations:
            raise StopIteration

        self._common_routine()
        eq_profile = self._calculate_eq_profile()
        stem_spectrum = self._get_old_stem_spectrum()

        self._i += 1

        return eq_profile, stem_spectrum

    def _add_to_cumsum(self, spectrum, *, cumsum):
        curr_i = self._i % self._constants.cumsum_len

        if curr_i == 0:
            cumsum[0] = spectrum
        else:
            np.add(cumsum[curr_i - 1], spectrum, out=cumsum[curr_i])

    def _common_routine(self):
        stem_spectrum, mix_spectrum = next(self._stem_and_mix_spectra_iter)
        self._retained_stem_spectra[self._i % self._constants.retained_len] \
            = stem_spectrum

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

    def _handle_before_spectra(self):
        while (
            self._i
            < self._constants.num_of_initialisation_iterations
        ):
            self._common_routine()
            self._i += 1

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
            **self._intermediate_arrays,
            out=self._eq_profile
        )

    def _get_old_stem_spectrum(self):
        return self._retained_stem_spectra[
            (self._i - self._constants.num_of_lookahead_transforms)
            % self._constants.retained_len
        ]


class GenerateSingleEqProfile:
    def __init__(
        self, *,
        sample_rate,
        transform_len=TRANSFORM_LEN,
        start_s=None, stop_s=None,
        fully_cover_all=False, centre=True,
    ):
        self.constants = _SingleConstants(**sanitise_args({
            "sample_rate": sample_rate,
            "transform_len": transform_len,
            "start_s": start_s, "stop_s": stop_s,
            "fully_cover_all": fully_cover_all, "centre": centre
        }))

    def __iter__(self):
        return _SingleIterator(self.constants)

    def run(self):
        for _ in self:
            pass

        return self.eq_profile


class GenerateRunningEqProfile:
    def __init__(
        self, *,
        sample_rate,
        transform_len=TRANSFORM_LEN,
        start_s=None, stop_s=None,
        fully_cover_all=True, centre=True,
        lookbehind_s=LOOKBEHIND_S, lookahead_s=LOOKAHEAD_S,
    ):
        self.constants = _RunningConstants(**sanitise_args({
            "sample_rate": sample_rate,
            "transform_len": transform_len,
            "start_s": start_s, "stop_s": stop_s,
            "fully_cover_all": fully_cover_all, "centre": centre,
            "lookbehind_s": lookbehind_s, "lookahead_s": lookahead_s
        }))

    def __iter__(self):
        return _Iterator(self.constants)
