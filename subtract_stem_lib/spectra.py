import numpy as np

from .sanitisation import sanitise_args


class _Constants:
    def __init__(
        self, *,
        transforms_start_i, num_of_transforms, interval_len,
        audio, window,
        num_of_retained
    ):
        ...


class _Iterator:
    def __init__(self, constants):
        self._constants = constants

        self._i = 0

        self._block_start_i, self._block_stop_i = None

    def __iter__(self):
        return self

    def __next__(self):
        if self._i == self._constants.num_of_transforms:
            raise StopIteration

        self._set_block_start_stop_indices()
        self._fill_windowed()

        spectrum = self._spectra[self._i % self._constants.num_of_retained]
        np.fft.fft(self._windowed, out=spectrum)

        self._i += 1

        return spectrum

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
            = max(len(self._constants.audio) - self._block_start_i, 0)

        self._windowed[:break_empty_to_full_i] = 0
        np.multiply(
            self._constants.audio[
                max(self._block_start_i, 0):max(self._block_stop_i, 0)
            ],
            self._constants.window[
                break_empty_to_full_i:break_full_to_empty_i
            ],
            out=self._windowed[break_empty_to_full_i:break_full_to_empty_i]
        )
        self._windowed[break_full_to_empty_i:] = 0


class GenerateSpectra:
    def __init__(
        self, *,
        transforms_start_i, num_of_transforms, interval_len,
        audio, window,
        num_of_retained=1
    ):
        self.constants = _Constants(**sanitise_args({
            "transforms_start_i": transforms_start_i,
            "num_of_transforms": num_of_transforms,
            "interval_len": interval_len,
            "audio": audio,
            "window": window,
            "num_of_retained": num_of_retained
        }))

    def __iter__(self):
        return _Iterator(self.constants)


class GenerateStemAndMixSpectra:
    def __init__(
        self, *,
        stem_transforms_start_i, mix_transforms_start_i,
        num_of_iterations, interval_len,
        stem_audio, mix_audio,
        stem_window, mix_window,
        stem_num_of_retained=1, mix_num_of_retained=1
    ):
        self.stem_spectra = Spectra(
            transforms_start_i=stem_transforms_start_i,
            num_of_transforms=num_of_iterations, interval_len=interval_len,
            audio=stem_audio, window=stem_window,
            num_of_retained=stem_num_of_retained
        )
        self.mix_spectra = Spectra(
            transforms_start_i=mix_transforms_start_i,
            num_of_transforms=num_of_iterations, interval_len=interval_len,
            audio=mix_audio, window=mix_window,
            num_of_retained=mix_num_of_retained
        )

    def __iter__(self):
        return zip(self.stem_spectra, self.mix_spectra)
