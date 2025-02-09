# Black majicks happen here.


##############################################################################


import numpy as np


def _make_sanitise_array(dimensions=None, dtype=None, allow_empty=False):
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


sanitise_array_1d = _make_sanitise_array(dimensions=1)
sanitise_array_1d_bool = sanitise_is_safe \
    = _make_sanitise_array(dimensions=1, dtype=bool)
sanitise_array_1d_float = sanitise_audio = sanitise_grain = sanitise_window \
    = _make_sanitise_array(dimensions=1, dtype=np.float32)
sanitise_array_1d_complex \
    = _make_sanitise_array(dimensions=1, dtype=np.complex64)


def _sanitise_bool(val, name):
    if type(val) is bool:
        return val
    else:
        raise TypeError(f"{name!r} should be a bool")


sanitise_subtract = _sanitise_bool


def _make_sanitise_float(allow_convert=False, range_=None):
    def sanitise_float(val, name):
        if allow_convert:
            val = float(val)
        elif type(val) is not float:
            raise TypeError(f"{name!r} should be a float")

        if range_ == ">0":
            if val <= 0:
                raise ValueError(f"{name!r} should be greater than 0.0")

        return val

    return sanitise_float


sanitise_delay_audio_samples = _make_sanitise_float(allow_convert=True)
sanitise_max_abs_result \
    = _make_sanitise_float(allow_convert=True, range_=">0")


def _make_sanitise_int(allow_convert=False, range_=None):
    def sanitise_int(val, name):
        if allow_convert:
            val = int(val)
        elif type(val) is not int:
            raise TypeError(f"{name!r} should be an int")

        if range_ == ">=1":
            if val < 1:
                raise ValueError(f"{name!r} should be at least 1")
        if range_ == ">=2":
            if val < 2:
                raise ValueError(f"{name!r} should be at least 2")

        return val

    return sanitise_int


sanitise_start_i = _make_sanitise_int()
sanitise_interval_len = sanitise_num_of_iterations \
    = _make_sanitise_int(range_=">=1")
sanitise_grain_len = _make_sanitise_int(range_=">=2")


##############################################################################


import inspect


_UNIQUE_NONE = object()


class _Sanitiser:
    def __init__(self, callable_, name):
        self.callable_ = callable_
        self.name = name

    def __call__(self, val, name=None):
        if name is None:
            return self.callable_(val, self.name)
        elif type(name) is str:
            return self.callable_(val, name)
        else:
            raise TypeError("if provided, name should be a str")


def _get_sanitisers():
    for attr_name, val in globals().items():
        if not attr_name.startswith("sanitise_"):
            continue

        name = attr_name[9:]

        if not callable(val):
            raise RuntimeError(f"sanitiser for {name} is not callable")

        sanitiser = _Sanitiser(val, name)

        globals()[attr_name] = sanitiser
        yield name, sanitiser


_sanitisers = dict(_get_sanitisers())


def sanitise_arg(
    name, val=_UNIQUE_NONE, *,
    args_dict=None, sanitiser_name=None,
    additional_frames=0
):
    if type(name) is not str:
        raise TypeError("name should be a str")

    if args_dict is not None and type(args_dict) is not dict:
            raise TypeError("if provided, args_dict should be a dict")

    if sanitiser_name is None:
        sanitiser_name = name
    elif type(sanitiser_name) is not str:
        raise TypeError("if provided, sanitiser_name should be a str")

    if type(additional_frames) is not int:
        raise TypeError("if provided, additional_frames should be an int")

    if val is _UNIQUE_NONE:
        if args_dict is None:
            val = inspect.stack()[1 + additional_frames].frame.f_locals[name]
        else:
            val = args_dict[name]

    return _sanitisers[sanitiser_name](val, name)


def sanitise_args(*xargs, **kwargs):
    vals = []

    for name in xargs:
        vals.append(sanitise_arg(name, additional_frames=1))

    for name, val in kwargs.items():
        vals.append(sanitise_arg(name, val))

    return vals


def sanitise_args_to_dict(*xargs, **kwargs):
    args_dict = {}

    for name in xargs:
        args_dict[name] = sanitise_arg(name, additional_frames=1)

    for name, val in kwargs.items():
        args_dict[name] = sanitise_arg(name, val)

    return args_dict
