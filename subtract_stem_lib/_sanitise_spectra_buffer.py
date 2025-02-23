import numpy as np

from .buffer import Buffer, buffer_from_array_args, buffer_from_array


def sanitise_spectra_buffer(
    spectra_buffer, *, name,
    reference_shape=None, reference_name_quoted=None
):
    if spectra_buffer is None:
        if reference_shape is None:
            raise TypeError(f"{name!r} not provided")
        else:
            spectra_buffer = buffer_from_array_args(
                reference_shape, dtype=np.complex64, num_of_items=1
            )
    elif type(spectra_buffer) is np.ndarray:
        spectra_buffer = buffer_from_array(spectra_buffer)
    elif not isinstance(spectra_buffer, Buffer):
        raise TypeError(
            f"{name!r} should be a subtract_stem_lib.Buffer subclass "
            "instance or a numpy.ndarray"
        )

    if spectra_buffer.newest.dtype is not np.dtype(np.complex64):
        raise TypeError(f"{name!r} arrays should have dtype numpy.complex64")

    if reference_shape is None:
        if len(spectra_buffer.newest.shape) != 1:
            raise ValueError(f"{name!r} arrays should be 1-D")

        if len(spectra_buffer.newest) == 0:
            raise ValueError(f"{name!r} should not be empty")
    else:
        if spectra_buffer.newest.shape != reference_shape:
            raise ValueError(
                f"{name!r} arrays should have same shape as "
                f"{reference_name_quoted}"
            )

    return spectra_buffer


def sanitise_stem_mix_spectra_buffers(
    stem_spectra_buffer, mix_spectra_buffer
):
    stem_spectra_buffer = sanitise_spectra_buffer(
        stem_spectra_buffer, name="stem_spectra_buffer"
    )
    mix_spectra_buffer = sanitise_spectra_buffer(
        mix_spectra_buffer, name="mix_spectra_buffer"
    )

    if len(stem_spectra_buffer.newest) != len(mix_spectra_buffer.newest):
        raise ValueError(
            "'stem_spectra_buffer' arrays and 'mix_spectra_buffer' arrays "
            "should have the same shape"
        )

    return stem_spectra_buffer, mix_spectra_buffer