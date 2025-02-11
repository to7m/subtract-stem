import numpy as np

from .buffer import Buffer


def sanitise_spectra_buffer(spectra_buffer, *, name, grain=None):
    if type(spectra_buffer) is not Buffer:
        raise TypeError(f"{name!r} should be a subtract_stem_lib.Buffer")

    if grain is not None and spectra_buffer.newest.shape != grain.shape:
        raise ValueError(f"{name!r} arrays should have same shape as 'grain'")

    if spectra_buffer.newest.dtype is not np.dtype(np.complex64):
        raise TypeError(f"{name!r} arrays should have dtype numpy.complex64")

    return spectra_buffer
