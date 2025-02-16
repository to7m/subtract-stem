import numpy as np

from ._sanitisation import sanitise_arg as san
from .buffer import Buffer
from ._sanitise_spectra_buffer import sanitise_spectra_buffer



"""
not sure what will be relevant yet
class GrainsToSpectra:
    __slots__ = ["grain", "out"]

    def __init__(self, grain, *, out=None):
        self.grain = san("grain")
        self.out = self._sanitise_out(out)

    def __iter__(self):
        def iterator(fft=np.fft.fft, grain=self.grain, out=self.out):
            while True:
                fft(grain, out=out)

                yield

        return iterator()

    def _sanitise_out(self, out):
        if out is None:
            out = np.empty(self.grain.shape, dtype=np.complex64)
        else:
            out = san("out", "array_1d_complex")

            if len(out) != len(self.grain):
                raise ValueError("'out' should be the same size as 'grain'")

        return out


class GrainsToSpectraBuffer:
    __slots__ = ["grain", "out"]

    def __init__(self, grain, *, out):
        self.grain = san("grain")
        self.out = sanitise_spectra_buffer(out, name="out", grain=self.grain)

    def __iter__(self):
        def iterator(fft=np.fft.fft, grain=self.grain, out=self.out):
            while True:
                spectrum = out.increment_and_get_newest()
                fft(grain, out=spectrum)

                yield

        return iterator()

    @classmethod
    def from_grain_and_buffer_arg(
        cls, grain, *, num_of_items=None, lookbehind=None
    ):
        sanitise_arg("grain")

        out = Buffer.from_array_args(
            num_of_items=num_of_items, lookbehind=lookbehind,
            shape=grain.shape, dtype=np.complex64
        )

        return cls(grain, out=out)


class SpectraToGrains:
    __slots__ = ["spectrum", "out_complex", "out"]

    def __init__(self, spectrum, *, out_complex=None):
        self.spectrum = sanitise_arg("spectrum")
        self.out_complex = self._sanitise_out_complex(out_complex)
        self.out = self.out_complex.real

    def __iter__(self):
        def iterator(
            ifft=np.fft.ifft,
            spectrum=self.spectrum,
            out_complex=self.out_complex
        ):
            while True:
                ifft(spectrum, out=out_complex)

                yield

        return iterator()

    def _sanitise_out_complex(self, out_complex):
        if out_complex is None:
            out_complex = np.empty(self.spectrum.shape, dtype=np.complex64)
        else:
            out_complex = sanitise_arg(
                "out_complex", sanitiser_name="array_1d_complex"
            )

            if out_complex.shape != self.spectrum.shape:
                raise ValueError(
                    "'out_complex' should have same shape as 'spectrum'"
                )

        return out_complex


class SpectraBufferToGrains:
    __slots__ = [
        "spectra_buffer",
        "out_newest_complex", "out_newest", "out_oldest_complex", "out_oldest"
    ]

    def __init__(
        self, spectra_buffer, *,
        out_newest_complex=None, out_oldest_complex=None
    ):
        self.spectra_buffer \
            = sanitise_spectra_buffer(spectra_buffer, name="spectra_buffer")
        self.out_newest_complex = self._sanitise_out_complex(
            out_newest_complex, name="out_newest_complex"
        )
        self.out_oldest_complex = self._sanitise_out_complex(
            out_oldest_complex, name="out_oldest_complex"
        )

        self.out_newest = self.out_newest_complex.real
        self.out_oldest = self.out_oldest_complex.real

    def __iter__(self):
        def iterator(
            lookbehind_range=range(self.spectra_buffer.lookbehind),
            ifft=np.fft.ifft,
            spectra_buffer=self.spectra_buffer,
            out_newest_complex=self.out_newest_complex,
            out_oldest_complex=self.out_oldest_complex
        ):
            for _ in lookbehind_range:
                newest_spectrum = spectra_buffer.newest

                ifft(newest_spectrum, out=out_newest_complex)

                yield

            while True:
                newest_spectrum, oldest_spectrum \
                    = spectra_buffer.newest_and_oldest

                ifft(newest_spectrum, out=out_newest_complex)
                ifft(oldest_spectrum, out=out_oldest_complex)

                yield

        return iterator()

    def _sanitise_out_complex(self, out_complex, *, name):
        if out_complex is None:
            out_complex = np.empty(
                self.spectra_buffer.newest.shape, dtype=np.complex64
            )
        else:
            out_complex = sanitise_arg(
                name, val=out_complex, sanitiser_name="array_1d_complex"
            )

            if out_complex.shape != self.spectra_buffer.newest.shape:
                raise ValueError(
                    f"if provided, {name!r} should have same shape as "
                    "'spectra_buffer' arrays"
                )

        return out_complex
"""
