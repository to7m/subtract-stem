import sys
from pathlib import Path
from math import ceil, pi, tau
import numpy as np
from fractions import Fraction
import librosa


DEFAULT_TRANSFORM_LEN = 1350
DEFAULT_MAX_AMPLIFICATION = 10000.0
DEFAULT_WEIGHTING_EXPONENT = 0.0
DEFAULT_SMOOTHING_LEN = 0.0  # seems to only cause crackling

ONE_ROTATED = (-1) ** (1 / pi)
ONE_ROTATED_CONJUGATED = (-1) ** (-1 / pi)


def parse_timestamp(ts, *, default=0):
    if ts is None:
        return Fraction(default)
    elif type(ts) is str:
        seconds = Fraction(0)
        for unit_str in ts.split(':'):
            seconds *= 60
            seconds += Fraction(unit_str)

        return seconds
    else:
        return Fraction(ts)


def whole_and_remainder(x):
    whole = int(x)
    remainder = float(x - whole)
    return whole, remainder


class PreAudioData:
    def __init__(
        self, *,
        transform_len=DEFAULT_TRANSFORM_LEN,
        max_amplification=DEFAULT_MAX_AMPLIFICATION,
        weighting_exponent=DEFAULT_WEIGHTING_EXPONENT,
        smoothing_len=DEFAULT_SMOOTHING_LEN
    ):
        self.transform_len = self._sanitise_transform_len(transform_len)
        self.max_amplification \
            = self._sanitise_max_amplification(max_amplification)
        self.weighting_exponent \
            = self._sanitise_weighting_exponent(weighting_exponent)
        self.smoothing_len = self._sanitise_smoothing_len(smoothing_len)

        self.interval = self.transform_len // 2
        self.half_fade_len = ceil(self.smoothing_len) // 2
        self.fade_len = self.half_fade_len * 2
        self.smoothed_len = self.transform_len + self.fade_len
        self.fade_in_curve = self._get_fade_in_curve()

    def _sanitise_transform_len(self, transform_len):
        transform_len = int(transform_len)

        if transform_len % 2:
            raise ValueError("transform_len should be divisible by 2")

        return transform_len

    def _sanitise_weighting_exponent(self, weighting_exponent):
        return float(weighting_exponent)

    def _sanitise_max_amplification(self, max_amplification):
        max_amplification = float(max_amplification)

        if max_amplification <= 0:
            raise ValueError("max_amplification must be greater than 0")

        return max_amplification

    def _sanitise_smoothing_len(self, smoothing_len):
        smoothing_len = float(smoothing_len)

        if smoothing_len > self.transform_len:
            raise ValueError(
                "smoothing_len should not be greater than transform_len"
            )

        return max(smoothing_len, 1.0)

    def _get_fade_in_curve(self):
        phase = (
            (
                np.arange(self.fade_len, dtype=np.float32)
                + (self.smoothing_len / 2) - (self.fade_len - 1) / 2
            )
            * (tau / self.smoothing_len)
        )
        fade_in_curve = (1 - np.cos(phase)) / 2

        return fade_in_curve


class AudioData:
    def __init__(
        self, stem_path, mix_path, *,
        delay_stem=None,
        profile_start=None, profile_stop=None,
        out_start=None, out_stop=None
    ):
        self.mix_audio, self.sample_rate = librosa.load(mix_path, sr=None)
        self.stem_audio, _ = librosa.load(stem_path, sr=self.sample_rate)
        self.delay_stem_samples_whole, self.delay_stem_samples_remainder \
            = self._handle_delay_stem(delay_stem)
        (
            self.profile_start_sample, self.profile_stop_sample,
            self.out_start_sample, self.out_stop_sample
        ) = self._handle_timestamps(
            profile_start=profile_start, profile_stop=profile_stop,
            out_start=out_start, out_stop=out_stop
        )

    def _handle_delay_stem(self, delay_stem):
        delay_stem_samples = parse_timestamp(delay_stem) * self.sample_rate
        return whole_and_remainder(delay_stem_samples)

    def _handle_timestamps(
        self, *, profile_start, profile_stop, out_start, out_stop
    ):
        mix_audio_dur = Fraction(len(self.mix_audio), self.sample_rate)

        for timestamp in [
            parse_timestamp(profile_start),
            parse_timestamp(profile_stop, default=mix_audio_dur),
            parse_timestamp(out_start),
            parse_timestamp(out_stop, default=mix_audio_dur)
        ]:
            yield round(timestamp * self.sample_rate)


def make_hann_window(size, samples_early=0):
    phase = (np.arange(size, dtype=np.float32) + samples_early) * (tau / size)
    window = (1 - np.cos(phase)) / 2

    return window


class GenerateBins:
    def __init__(
        self, audio, *,
        start_i, num_to_generate, interval, window
    ):
        self.audio = audio
        self.start_i = start_i
        self.num_to_generate = num_to_generate
        self.interval = interval
        self.window = window

    def __iter__(self):
        # put objects directly into namespace for efficiency
        interval = self.interval
        window = self.window
        audio = self.audio
        audio_len = len(audio)

        start_i = self.start_i
        stop_i = start_i + len(window)
        windowed = np.empty(len(window), dtype=np.float32)
        bins = np.empty(len(window), dtype=np.complex64)
        for _ in range(self.num_to_generate):
            empty_full_i = max(-start_i, 0)
            full_empty_i = max(audio_len - start_i, 0)

            windowed[:empty_full_i] = 0
            np.multiply(
                audio[max(start_i, 0):max(stop_i, 0)],
                window[empty_full_i:full_empty_i],
                out=windowed[empty_full_i:full_empty_i]
            )
            windowed[full_empty_i:] = 0

            np.fft.fft(windowed, out=bins)

            start_i += interval
            stop_i += interval

            yield bins


def ataabtrnfatbaa(a, b, *, out_a=None, out_b=None):
    """Apply to 'a' and 'b' the rotation needed for 'a' to become abs(a)."""

    np.abs(a, out=out_a)

    phase = np.angle(a)
    np.power(ONE_ROTATED_CONJUGATED, phase, out=out_b)
    out_b *= b

    return out_a, out_b


class EqProfileCalculator:
    def __init__(self, *, pre_audio_data, audio_data, stem_window, mix_window):
        self.weighting_exponent = pre_audio_data.weighting_exponent
        self.max_amplification = pre_audio_data.max_amplification
        self.interval = pre_audio_data.interval
        self.mix_window = mix_window

        (
            stem_transforms_start_i, mix_transforms_start_i,
            self.num_of_iterations
        ) = self._calculate_alignments(audio_data)

        self.generate_stem_bins = GenerateBins(
            audio_data.stem_audio,
            start_i=stem_transforms_start_i,
            num_to_generate=self.num_of_iterations,
            interval=self.interval,
            window=stem_window
        )
        self.generate_mix_bins = GenerateBins(
            audio_data.mix_audio,
            start_i=mix_transforms_start_i,
            num_to_generate=self.num_of_iterations,
            interval=self.interval,
            window=mix_window
        )

        self.eq_profile = None

    def _calculate_alignments(self, audio_data):
        ideal_mix_transforms_start_i \
            = audio_data.profile_start_sample - len(self.mix_window) / 4

        profile_len \
            = audio_data.profile_stop_sample - audio_data.profile_start_sample
        len_after_first_transform = profile_len - len(self.mix_window) // 2
        ideal_num_of_subsequent_transforms \
            = len_after_first_transform / self.interval
        subsequent_num_of_transforms \
            = round(ideal_num_of_subsequent_transforms)

        profile_middle_sample = (
            (audio_data.profile_start_sample + audio_data.profile_stop_sample)
            / 2
        )
        centre_of_first_transform = (
            profile_middle_sample
            - subsequent_num_of_transforms * self.interval / 2
        )
        mix_transforms_start_i \
            = round(centre_of_first_transform - len(self.mix_window) // 2)

        stem_transforms_start_i \
            = mix_transforms_start_i - audio_data.delay_stem_samples_whole
        num_of_iterations = 1 + subsequent_num_of_transforms

        return (
            stem_transforms_start_i, mix_transforms_start_i, num_of_iterations
        )

    def run_gen(self):
        abs_stem_bins = np.empty(len(self.mix_window), dtype=np.float32)
        rotated_mix_bins = np.empty(len(self.mix_window), dtype=np.complex64)
        weights = np.empty(len(self.mix_window), dtype=np.float32)
        abs_stem_bins_sum = np.zeros(len(self.mix_window), dtype=np.float32)
        rotated_mix_bins_sum \
            = np.zeros(len(self.mix_window), dtype=np.complex64)

        # put objects directly into namespace for efficiency
        num_of_iterations = self.num_of_iterations
        weighting_exponent = self.weighting_exponent

        for i, (stem_bins, mix_bins) in enumerate(
            zip(self.generate_stem_bins, self.generate_mix_bins)
        ):
            ataabtrnfatbaa(
                stem_bins, mix_bins,
                out_a=abs_stem_bins, out_b=rotated_mix_bins
            )

            np.power(abs_stem_bins, weighting_exponent, out=weights)
            abs_stem_bins *= weights
            rotated_mix_bins *= weights

            abs_stem_bins_sum += abs_stem_bins
            rotated_mix_bins_sum += rotated_mix_bins

            yield i, num_of_iterations


class StemInMixCalculator:
    def __init__(
        self, *,
        interval, fade_in_curve, audio_data, stem_window, eq_profile
    ):
        self.interval = interval
        self.fade_in_curve = fade_in_curve
        self.stem_audio = audio_data.stem_audio
        self.stem_window = stem_window
        self.eq_profile = eq_profile

        self.fade_len = len(fade_in_curve)
        self.half_fade_len = self.fade_len // 2
        self.smoothed_len = len(stem_window) + self.fade_len

        (
            self.margin_before,
            self.result_len,
            self.margin_after,
            self.total_len,
            self.num_of_transforms,
            self.stem_transforms_start_i
        ) = self._calculate_alignments(audio_data)

        self.stem_in_mix_audio = None

    def _calculate_alignments(self, audio_data):
        result_len = audio_data.out_stop_sample - audio_data.out_start_sample
        min_margin = self.smoothed_len - self.interval
        min_total_len = result_len + 2 * min_margin
        num_of_subsequent_transforms \
            = (min_total_len - self.smoothed_len - 1) // self.interval + 1
        total_len \
            = self.smoothed_len + num_of_subsequent_transforms * self.interval

        margin_before = min_margin
        margin_after = total_len - margin_before - result_len
        num_of_transforms = num_of_subsequent_transforms + 1

        stem_transforms_start_i = (
            audio_data.out_start_sample - margin_before + self.half_fade_len
            - audio_data.delay_stem_samples_whole
        )

        return (
            margin_before, result_len, margin_after, total_len,
            num_of_transforms,
            stem_transforms_start_i
        )

    def _get_intermediate_views(self):
        smoothed_eqd_complex \
            = np.empty(self.smoothed_len, dtype=np.complex64)

        smoothed_eqd = smoothed_eqd_complex.real

        beginning_fade = smoothed_eqd[:self.fade_len]
        eqd_complex = smoothed_eqd_complex[
            self.half_fade_len:self.smoothed_len - self.half_fade_len
        ]
        end_fade_reversed = smoothed_eqd[:-self.fade_len - 1:-1]

        beginning_outer_fade = smoothed_eqd[:self.half_fade_len]
        beginning_inner_fade = smoothed_eqd[self.half_fade_len:self.fade_len]
        end_inner_fade = smoothed_eqd[
            self.smoothed_len - self.fade_len
            :self.smoothed_len - self.half_fade_len
        ]
        end_outer_fade = smoothed_eqd[self.smoothed_len - self.half_fade_len:]

        return (
            smoothed_eqd,
            beginning_fade, eqd_complex, end_fade_reversed,
            beginning_outer_fade, beginning_inner_fade,
            end_inner_fade, end_outer_fade
        )

    def run_gen(self):
        # put objects directly into namespace for efficiency
        (
            smoothed_eqd,
            beginning_fade, eqd_complex, end_fade_reversed,
            beginning_outer_fade, beginning_inner_fade,
            end_inner_fade, end_outer_fade
        ) = self._get_intermediate_views()
        num_of_transforms = self.num_of_transforms
        interval = self.interval
        eq_profile = self.eq_profile
        fade_in_curve = self.fade_in_curve
        smoothed_len = self.smoothed_len

        stem_in_mix_audio = np.zeros(self.total_len, dtype=np.float32)

        for i, stem_bins in enumerate(
            GenerateBins(
                self.stem_audio,
                start_i=self.stem_transforms_start_i,
                num_to_generate=num_of_transforms,
                interval=interval,
                window=self.stem_window
            )
        ):
            stem_bins *= eq_profile

            np.fft.ifft(stem_bins, out=eqd_complex)

            beginning_outer_fade[:] = end_inner_fade
            end_outer_fade[:] = beginning_inner_fade
            beginning_fade *= fade_in_curve
            end_fade_reversed *= fade_in_curve

            start_i = i * interval
            stop_i = start_i + smoothed_len

            stem_in_mix_audio[start_i:stop_i] += smoothed_eqd

            yield i, num_of_transforms

        self.stem_in_mix_audio = stem_in_mix_audio[
            self.margin_before:self.total_len - self.margin_after
        ]

    def run(self):
        for _ in self.run_gen():
            pass

        return self.stem_in_mix_audio


def get_mix_minus_stem(mix_audio, stem_audio, *, out_start_sample):
    mix_minus_stem_audio \
        = mix_audio[:out_start_sample + len(stem_audio)].copy()
    mix_minus_stem_audio[:out_start_sample] = 0
    mix_minus_stem_audio[out_start_sample:] -= stem_audio

    return mix_minus_stem_audio
