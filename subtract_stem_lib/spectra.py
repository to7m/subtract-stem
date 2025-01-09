from math import ceil, floor, tau
from fractions import Fraction
import numpy as np

from .defaults import TRANSFORM_LEN
from .sanitisation import sanitise_args, sanitise_logger


class _Constants:
    def __init__(
        self, *,
        mono_audio, sample_rate,
        start_s, stop_s,
        delay_audio_s,
        transform_len,
        additional_iterations_before, additional_iterations_after,
        num_of_retained,
        logger
    ):
        self.mono_audio = mono_audio
        self._sample_rate = sample_rate
        self._start_s, self._stop_s = start_s, stop_s
        self._delay_audio_s = delay_audio_s
        self.transform_len = transform_len
        self._additional_iterations_before = additional_iterations_before
        self._additional_iterations_after = additional_iterations_after
        self.num_of_retained = num_of_retained
        self.logger = logger

        self.audio_len = len(mono_audio)
        self._audio_s = Fraction(self.audio_len, sample_rate)
        self.pre_delay_start_sample, self.pre_delay_stop_sample \
            = self._get_pre_delay_samples()
        self.interval_len = transform_len // 2
        self.delay_result_samples \
            = self.pre_delay_start_sample - self.interval_len
        self.num_of_iterations = self._get_num_of_iterations()
        self._delay_whole, self._delay_remainder = self._get_delay_samples()
        self.transforms_start_i = self._get_transforms_start_i()
        self.window = self._get_window()

    def _time_to_sample_i(self, t):
        if t is None:
            return self.audio_len

        if t < 0:
            t += self._audio_s

        return t * self._sample_rate

    def _get_pre_delay_samples(self):
        yield floor(
            self._time_to_sample_i(self._start_s)
        )
        yield ceil(
            self._time_to_sample_i(self._stop_s)
        )

    def _get_num_of_iterations(self):
        num_of_samples \
            = self.pre_delay_stop_sample - self.pre_delay_start_sample
        num_of_subsequent_main_iterations \
            = ceil(Fraction(num_of_samples, self.transform_len))
        num_of_main_iterations = 1 + num_of_subsequent_main_iterations
        num_of_iterations = (
            self._additional_iterations_before
            + num_of_main_iterations
            + self._additional_iterations_after
        )

        return num_of_iterations

    def _get_delay_samples(self):
        delay_samples = self._delay_audio_s * self._sample_rate
        delay_whole = floor(delay_samples)
        delay_remainder = float(delay_samples - delay_whole)

        return delay_whole, delay_remainder

    def _get_transforms_start_i(self):
        transforms_main_start_i \
            = self.delay_result_samples - self._delay_whole
        samples_before \
            = self._additional_iterations_before * self.interval_len
        transforms_start_i = transforms_main_start_i - samples_before

        return transforms_start_i

    def _get_window(self):
        phase = (
            (
                np.arange(self.transform_len, dtype=np.float32)
                + self._delay_remainder
            )
            * (tau / self.transform_len)
        )

        return (1 - np.cos(phase)) / 2


class _Iterator:
    def __init__(self, constants):
        self._constants = constants

        self._i = 0
        self._block_start_i = self._block_stop_i = None
        self._grain = np.empty(constants.transform_len, dtype=np.float32)
        self._spectra = [
            np.empty(constants.transform_len, dtype=np.complex64)
            for _ in range(constants.num_of_retained)
        ]

        self._log_progress()

    def __iter__(self):
        return self

    def __next__(self):
        if self._i == self._constants.num_of_iterations:
            raise StopIteration

        self._set_block_start_stop_indices()
        self._fill_grain()

        spectrum = self._spectra[self._i % self._constants.num_of_retained]
        np.fft.fft(self._windowed, out=spectrum)

        self._i += 1
        self._log_progress()

        return spectrum

    def _log_progress(self):
        num_of_iterations = self._constants.num_of_iterations

        self._constants.logger(
            msg=f"spectra made: {self._i} of {num_of_iterations}",
            iteration=self._i, num_of_iterations=num_of_iterations
        )

    def _set_block_start_stop_indices(self):
        self._block_start_i = (
            self._constants.transforms_start_i
            + self._i * self._constants.interval_len
        )
        self._block_stop_i \
            = self._block_start_i + self._constants.transform_len

    def _fill_windowed(self):
        break_empty_to_full_i = max(-self._block_start_i, 0)
        break_full_to_empty_i \
            = max(self._constants.audio_len - self._block_start_i, 0)

        self._grain[:break_empty_to_full_i] = 0
        np.multiply(
            self._constants.mono_audio[
                max(self._block_start_i, 0):max(self._block_stop_i, 0)
            ],
            self._constants.window[
                break_empty_to_full_i:break_full_to_empty_i
            ],
            out=self._grain[break_empty_to_full_i:break_full_to_empty_i]
        )
        self._grain[break_full_to_empty_i:] = 0


class GenerateSpectra:
    def __init__(
        self, *,
        mono_audio, sample_rate,
        start_s=Fraction(0), stop_s=None,
        delay_audio_s=Fraction(0),
        transform_len=TRANSFORM_LEN,
        additional_iterations_before=0, additional_iterations_after=0,
        num_of_retained=1,
        logger=None
    ):
        self._constants = _Constants(**sanitise_args({
            "mono_audio": mono_audio, "sample_rate": sample_rate,
            "start_s": start_s, "stop_s": stop_s,
            "delay_audio_s": delay_audio_s,
            "transform_len": transform_len,
            "additional_iterations_before": additional_iterations_before,
            "additional_iterations_after": additional_iterations_after,
            "num_of_retained": num_of_retained,
            "logger": logger
        }))

        self.num_of_iterations = self._constants.num_of_iterations
        self.interval_len = self._constants.interval_len
        self.pre_delay_start_sample = self._constants.pre_delay_start_sample
        self.pre_delay_stop_sample = self._constants.pre_delay_stop_sample
        self.delay_result_samples = self._constants.delay_result_samples

    def __iter__(self):
        return _Iterator(self._constants)


class GenerateStemAndMixSpectra:
    def __init__(
        self, *,
        stem_audio, mix_audio, sample_rate,
        start_s=Fraction(0), stop_s=None,
        delay_stem_s=Fraction(0),
        transform_len=TRANSFORM_LEN,
        additional_iterations_before=0, additional_iterations_after=0,
        stem_num_of_retained=1, mix_num_of_retained=1,
        logger=None
    ):
        sanitise_args({
            "delay_stem_s": delay_stem_s,
            "stem_num_of_retained": stem_num_of_retained,
            "mix_num_of_retained": mix_num_of_retained
        })

        wrapped_logger = self._wrap_logger(sanitise_logger(logger))

        self._stem_spectra = GenerateSpectra(
            mono_audio=stem_audio, sample_rate=sample_rate,
            start_s=start_s, stop_s=stop_s,
            delay_audio_s=delay_stem_s,
            transform_len=transform_len,
            additional_iterations_before=additional_iterations_before,
            additional_iterations_after=additional_iterations_after,
            num_of_retained=stem_num_of_retained
        )
        self._mix_spectra = GenerateSpectra(
            mono_audio=mix_audio, sample_rate=sample_rate,
            start_s=start_s, stop_s=stop_s,
            transform_len=transform_len,
            additional_iterations_before=additional_iterations_before,
            additional_iterations_after=additional_iterations_after,
            num_of_retained=mix_num_of_retained,
            logger=wrapped_logger
        )

        self.num_of_iterations = self._mix_spectra.num_of_iterations
        self.interval_len = self._mix_spectra.interval_len
        self.pre_delay_start_sample = self._mix_spectra.pre_delay_start_sample
        self.pre_delay_stop_sample = self._mix_spectra.pre_delay_stop_sample
        self.delay_result_samples = self._mix_spectra.delay_result_samples

    def __iter__(self):
        return zip(self._stem_spectra, self._mix_spectra)

    def _wrap_logger(self, logger):
        def wrapped_logger(msg, iteration, num_of_iterations):
            logger(
                msg=(
                    f"pairs of spectra made: {iteration} of "
                    f"{num_of_iterations}"
                ),
                iteration=iteration, num_of_iterations=num_of_iterations
            )

        return wrapped_logger
