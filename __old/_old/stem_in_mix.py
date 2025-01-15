from fractions import Fraction

from .defaults import TRANSFORM_LEN
from .sanitisation import sanitise_args, sanitise_logger
from .spectra import GenerateSpectra


class _SingleConstants:
    def __init__(
        self,
        stem_audio, sample_rate,
        start_s, stop_s,
        delay_stem_s,
        eq_profile,
        logger
    ):
        self.transform_len = len(eq_profile)
        self.stem_spectra = GenerateSpectra(
            mono_audio=stem_audio, sample_rate=sample_rate,
            start_s=start_s, stop_s=stop_s,
            delay_audio_s=delay_stem_s,
            transform_len=self.transform_len,
        )

        self.eq_profile = eq_profile
        self.logger = logger

        self.num_of_iterations = self.stem_spectra.num_of_iterations
        self.last_iteration_i = self.num_of_iterations - 1
        self.interval_len = self.stem_spectra.interval_len


class _SingleIterator:
    def __init__(self, constants):
        self._constants = constants

        self._stem_spectra_iter = iter(self._constants.stem_spectra)

        self._i = 0

        self._log_progress()

    def __iter__(self):
        return self

    def __next__(self):
        if self._i >= self._constants.last_iteration_i:
            if self._i == self._constants.last_iteration_i:
                self._routine()

                return self._calculate_result()
            else:
                raise StopIteration
        else:
            self._routine()

            return None

    def _log_progress(self):
        num_of_iterations = self._constants.num_of_iterations

        self._constants.logger(
            msg=(
                f"processed stem grains added: {self._i} of "
                f"{num_of_iterations}"
            ),
            iteration=self._i, num_of_iterations=num_of_iterations
        )

    def _get_block_start_stop_indices(self):
        start_i = self._i * self._constants.interval_len
        stop_i = start_i + self._constants.transform_len

        return start_i, stop_i

    def _get_stem_windowed_eqd(self):
        stem_spectrum = next(self._stem_spectra_iter)
        stem_spectrum *= self._constants.eq_profile
        return np.fft.ifft(stem_spectrum, out=self._stem_windowed_eqd)

    def _routine(self):
        block_start_i, block_stop_i = self._get_block_start_stop_indices()
        stem_windowed_eqd = self._get_stem_windowed_eqd()

        self._stem_in_mix[block_start_i:block_stop_i] \
            += stem_windowed_eqd.real

        self._i += 1
        self._log_progress()

    def _calculate_result(self):
        stem_in_mix = self._stem_in_mix[
            self._constants.margin_before:self._constants.margin_after
        ]

        return stem_in_mix, self._constants.delay_samples


class GenerateSingleStemInMix:
    def __init__(
        self, *,
        stem_audio, sample_rate,
        start_s=Fraction(0), stop_s=None,
        delay_stem_s=Fraction(0),
        transform_len=TRANSFORM_LEN,
        logger=None
    ):
        self._constants = _SingleConstants(
            stem_audio=stem_audio, sample_rate=sample_rate,
            start_s=start_s, stop_s=stop_s,
            delay_stem_s=delay_stem_s,
            transform_len=transform_len,
            logger=sanitise_logger(logger)
        )

    def __iter__(self):
        return _SingleIterator(self._constants)

    def run(self):
        for stem_in_mix_and_delay_samples in self:
            pass

        return stem_in_mix_and_delay_samples


class GenerateRunningStemInMix:
    def __init__(self):
        ...
