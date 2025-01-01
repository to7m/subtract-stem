from .defaults import TRANSFORM_LEN, LOOKBEHIND_S, LOOKAHEAD_S
from .sanitisation import sanitise_args
from .math import ataabtrnfatbaa, from_abs_and_angle, to_abs_and_angle


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

        self._i = 0

        self._handle_before_spectra()

    def __iter__(self):
        return self

    def __next__(self):
        if self._i == self._constants.num_of_total_iterations:
            raise StopIteration

        self._common_routine()
        eq_profile = self._safe_divide()
        stem_spectrum = self._get_old_stem_spectrum()

        self._i += 1

        return eq_profile, stem_spectrum

    def _common_routine(self):
        ...

    def _handle_before_spectra(self):
        while (
            self._i
            < self._constants.num_of_initialisation_iterations
        ):
            self._common_routine()
            self._i += 1

    def _get_is_safe(self):
        np.multiply(
            self._abs_stem_spectra_sum,
            self._constants.max_amplification,
            out=self._max_abs_mix_spectra_sum
        )
        np.abs(self._mix_spectra_sum, out=self._abs_mix_spectra_sum)
        np.less_equal(
            self._max_abs_mix_spectra_sum,
            self._abs_mix_spectra_sum,
            out=self._is_within_amplification_limit
        )

        np.not_equal(
            self._abs_stem_spectra_sum, 0,
            out=self._is_safe_from_zero_division
        )

        return np.logical_and(
            self._is_within_amplification_limit,
            self._is_safe_from_zero_division,
            out=self._is_safe
        )

    def _interpolate_missing_segment(
        self, last_present_before_i, first_present_after_i
    ):
        divisions = first_present_after_i - last_present_before_i

        abs_before, angle_before \
             = to_abs_and_angle(self._eq_profile[last_present_before_i])
        abs_after, angle_after \
            = to_abs_and_angle(self._eq_profile(first_present_after_i))
        abs_diff = abs_after - abs_before
        angle_diff = (angle_after - angle_before + pi) % tau - pi

        for i in range(1, divisions):
            abs_val = abs_before + i * abs_diff
            angle_val = angle_before + i * angle_diff
            val = from_abs_and_angle(abs_val, angle_val)

            self._eq_profile[last_present_before_i + i] = val


    def _interpolate_missing(self, is_present_arr):
        is_present_iter = enumerate(is_present_arr)

        if not next(is_present_iter)[1]:
            for i, is_present in is_present_iter:
                if is_present:
                    self._eq_profile[:i] = self._eq_profile[i]

        last_present_before_i = None
        for i, is_present in is_present_iter:
            if not is_present:
                last_present_before_i = i-1

                for i, is_present in is_present_iter:
                    if is_present:
                        self._interpolate_missing_segment(
                            last_present_before_i, i
                        )

                        last_present_before_i = None

                        break

        if last_present_before_i is not None:
            self._eq_profile[last_present_before_i + 1:] \
                = self._eq_profile[last_present_before_i]

    def _safe_divide(self):
        is_safe = self._get_is_safe()
        if np.any(is_safe):
            np.divide(
                self._rotated_mix_bins_sum,
                self._abs_stem_bins_sum,
                out=self._eq_profile
            )

            if not np.all(is_safe):
                self._interpolate_missing(is_safe)
        else:
            self._eq_profile.fill(0)

        return self._eq_profile

    def _get_old_stem_spectrum(self):
        return self._retained_stem_spectra[
            (
                self._transforms_pair_i
                - self._constants.num_of_lookahead_transforms
            )
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
