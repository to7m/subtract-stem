import numpy as np

from .buffer import Buffer, buffer_from_array_args
from ._sanitisation import sanitise_arg as san
from ._sanitise_spectra_buffer import sanitise_spectra_buffer


class GrainsToSpectraBuffer:
    __slots__ = ["grain", "out"]

    def __init__(self, grain, *, out=None):
        self.grain = san("grain")
        self.out = sanitise_spectra_buffer(
            out, name="out",
            reference_shape=grain.shape, reference_name_quoted="'grain'"
        )

    def __iter__(self):
        if self.out.num_of_items == 1:
            def get_iterator(
                fft=np.fft.fft,
                grain=self.grain, out=self.out.newest
            ):
                while True:
                    fft(grain, out=out)

                    yield
        else:
            def get_iterator(
                fft=np.fft.fft,
                grain=self.grain, out=self.out
            ):
                while True:
                    fft(grain, out=out.increment_and_get_newest())

                    yield

        return get_iterator()


class SpectraBufferOldestToComplexGrains:
    __slots__ = ["spectra_buffer", "out"]

    def __init__(self, spectra_buffer, *, out=None):
        self.spectra_buffer \
            = sanitise_spectra_buffer(spectra_buffer, name="spectra_buffer")
        self.out = self._sanitise_out(out)

    def __iter__(self):
        if self.spectra_buffer.num_of_items == 1:
            def get_iterator(
                ifft=np.fft.ifft,
                spectrum=self.spectra_buffer.oldest, out=self.out
            ):
                while True:
                    ifft(spectrum, out=out)

                    yield
        else:
            def get_iterator(
                ifft=np.ftt.ifft,
                spectra_buffer=self.spectra_buffer, out=self.out
            ):
                while True:
                    ifft(spectra_buffer.oldest, out=out)

                    yield

        return get_iterator()

    def _sanitise_out(self, out):
        if out is None:
            out = np.empty(
                self.spectra_buffer.newest.shape, dtype=np.complex64
            )
        else:
            out = san("out", "array_1d_complex")

            if out.shape != self.spectra_buffer.newest.shape:
                raise ValueError(
                    "'out' should have same shape 'spectra_buffer' arrays"
                )

        return out
