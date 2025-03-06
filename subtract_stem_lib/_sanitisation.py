from pathlib import Path
from fractions import Fraction
import numpy as np

from ._sanitisation_base import Sanitisers


def _make_sanitise_array(*, dimensions=None, dtype=None, allow_empty=False):
    def sanitise_array(val, name):
        if type(val) is not np.ndarray:
            raise TypeError(f"{name!r} should be a numpy.ndarray")

        if dimensions is not None:
            if len(val.shape) != dimensions:
                raise ValueError(f"{name!r} should be {dimensions}-D")

        if dtype is not None:
            if val.dtype is not np.dtype(dtype):
                raise TypeError(f"{name!r} should have dtype {dtype}")

        if not allow_empty:
            if 0 in val.shape:
                raise ValueError(f"{name!r} should not be empty")

        return val

    return sanitise_array


sanitise_array = _make_sanitise_array()
sanitise_array_1d = _make_sanitise_array(dimensions=1)
sanitise_array_1d_bool = sanitise_is_safe \
    = _make_sanitise_array(dimensions=1, dtype=bool)
sanitise_array_1d_float = _make_sanitise_array(dimensions=1, dtype=np.float32)
sanitise_audio = sanitise_array_1d_float
sanitise_grain = sanitise_array_1d_float
sanitise_mix_audio = sanitise_array_1d_float
sanitise_stem_audio = sanitise_array_1d_float
sanitise_window = sanitise_array_1d_float
sanitise_array_1d_complex = sanitise_eq_profile = sanitise_spectrum \
    = _make_sanitise_array(dimensions=1, dtype=np.complex64)


def _sanitise_bool(val, name):
    if type(val) is bool:
        return val
    else:
        raise TypeError(f"{name!r} should be a bool")


sanitise_error_if_not_mono = _sanitise_bool
sanitise_highest_wins = _sanitise_bool
sanitise_subtract = _sanitise_bool
sanitise_ret_reciprocal_eq = _sanitise_bool


def _sanitise_callable(val, name):
    if callable(val):
        return val
    else:
        raise TypeError(f"{name!r} should be callable")


sanitise_constructor = sanitise_scoring_function = _sanitise_callable


def _make_sanitise_float(*, allow_convert=False, range_=None):
    def sanitise_float(val, name):
        if allow_convert:
            val = float(val)
        elif type(val) is not float:
            raise TypeError(f"{name!r} should be a float")

        if range_ == "!=0":
            if val == 0:
                raise ValueError(f"{name!r} should not be equal to 0.0")
        elif range_ == ">=0":
            if val < 0:
                raise ValueError(f"{name!r} should not be less than 0.0")
        elif range_ == ">0":
            if val <= 0:
                raise ValueError(f"{name!r} should be greater than 0.0")

        return val

    return sanitise_float


sanitise_first_val = _make_sanitise_float(allow_convert=True)
sanitise_val_add = _make_sanitise_float(allow_convert=True, range_="!=0")
sanitise_max_abs_result = sanitise_min_diff \
    = _make_sanitise_float(allow_convert=True, range_=">=0")


def _make_sanitise_fraction(*, range_=None):
    def sanitise_fraction(val, name):
        if range_ == ">0":
            if val <= 0:
                raise ValueError(f"{name!r} should be greater than 0")

        return Fraction(val)

    return sanitise_fraction


_sanitise_fraction = _make_sanitise_fraction()
sanitise_delay_audio_samples = _sanitise_fraction
sanitise_delay_stem_samples = _sanitise_fraction
sanitise_total_seconds = _sanitise_fraction
sanitise_sample_rate = _make_sanitise_fraction(range_=">0")


def _make_sanitise_int(*, allow_convert=False, range_=None):
    def sanitise_int(val, name):
        if allow_convert:
            val = int(val)
        elif type(val) is not int:
            raise TypeError(f"{name!r} should be an int")

        if range_ == ">=0":
            if val < 0:
                raise ValueError(f"{name!r} should not be less than 0")
        if range_ == ">=1":
            if val < 1:
                raise ValueError(f"{name!r} should be at least 1")
        if range_ == ">=2":
            if val < 2:
                raise ValueError(f"{name!r} should be at least 2")

        return val

    return sanitise_int


sanitise_start_i = _make_sanitise_int()
sanitise_lookbehind = _make_sanitise_int(range_=">=0")
sanitise_interval_len = sanitise_num_of_items = sanitise_num_of_iterations \
    = _make_sanitise_int(range_=">=1")
sanitise_grain_len = _make_sanitise_int(range_=">=2")


def sanitise_s(val, name):
    if type(val) is not str:
        raise TypeError(f"{name!r} should be a str")

    return val


def sanitise_path(val, name):
    if isinstance(val, Path):
        return val
    elif type(val) is str:
        return Path(val)
    else:
        raise TypeError(f"{name!r} should be a pathlib.Path or a str")


def sanitise_reference_point(val, name):
    sanitise_s(val, name)

    if val not in {
        "ZERO",
        "DELAY_STEM", "DELAY_INTERMEDIATE",
        "OLD_STEM_END", "NEW_STEM_END",
        "OLD_INTERMEDIATE_END", "NEW_INTERMEDIATE_END",
    }:
        raise ValueError(f"{name!r} should be a recognised reference point")

    return val


def sanitise_buffer_data(val, name):
    if type(val) is not list:
        raise TypeError(f"{name!r} should be a list")

    if len(val) == 0:
        raise ValueError(f"{name!r} should contain multiple arrays")

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
            f"{name!r} should contain multiple arrays, thus RealBuffer() "
            "should not have been passed this object"
        )

    return val


def sanitise_quasi_buffer_data(val, name):
    if type(val) is list:
        raise TypeError(
            "unlike RealBuffer(), QuasiBuffer() should be passed a "
            "numpy.ndarray rather than a list"
        )
    elif type(val) is not np.ndarray:
        raise TypeError(
            "QuasiBuffer() should be passed a numpy.ndarray"
        )

    return val


_sanitisers = Sanitisers.from_current_module()
sanitise_arg = _sanitisers.sanitise_arg
sanitise_args = _sanitisers.sanitise_args
