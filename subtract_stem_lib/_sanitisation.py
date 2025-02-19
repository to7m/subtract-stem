import numpy as np

from ._sanitisation_base import Sanitisers
from ._sanitisation_pre_buffer import (
    sanitise_array,
    sanitisers as prev_sanitisers
)
from .buffer import 


def sanitise_buffer_data(val, name):
    if type(val) is not list:
        raise TypeError(f"{name!r} should be a list")

    if len(val) == 0:
        raise ValueError(f"{name!r} should not be empty")

    for arr in val:
        if type(arr) is not np.ndarray:
            raise TypeError(f"{name!r} should contain only numpy.ndarrays")

    for arr in val[1:]:
        if arr.shape != val[0].shape:
            raise ValueError(
                f"shapes of arrays in {name!r} should all be the same"
            )

        if arr.dtype is not val[0].dtype:
            raise TypeError(
                f"dtypes of arrays in {name!r} should all be the same"
            )

    return val


def sanitise_real_buffer_data(val, name):
    sanitise_buffer_data(val, name)

    if len(val) == 1:
        raise ValueError(
            f"{name!r} should contain multiple arrays, thus RealBufferData() "
            "should not have been passed this object"
        )

    return val


def sanitise_quasi_buffer_data(val, name):
    if type(val) is list:
        raise TypeError(
            "unlike RealBufferData(), QuasiBufferData() should be passed a "
            "numpy.ndarray rather than a list"
        )
    elif type(val) is not np.ndarray:
        raise TypeError(
            "unlike RealBufferData(), QuasiBufferData() should be passed a "
            "numpy.ndarray"
        )

    return sanitise_array(val, name)


_sanitisers = Sanitisers.from_current_module(prev_sanitisers=prev_sanitisers)
sanitise_arg = _sanitisers.sanitise_arg
sanitise_args = _sanitisers.sanitise_args
