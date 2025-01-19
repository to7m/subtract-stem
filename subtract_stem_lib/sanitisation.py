# Black majicks happen here.


##############################################################################


def _make_sanitise_int(allow_convert=False, limit=None):
    def sanitise_int(x, name):
        if allow_convert:
            x = int(x)
        elif type(x) is not int:
            raise TypeError(f"{name} should be an int")

        if limit == ">=0":
            if x < 0:
                raise ValueError(f"{name} should not be less than zero")

        return x

    return sanitise_int


##############################################################################


import inspect



class _Sanitiser:
    def __init__(self, name, callable_):
        self.name = name
        self.callable_ = callable_

    def __call__(self, x):
        return self.callable_(x, self.name)


def _get_sanitisers():
    for attr_name, val in globals().items():
        if not attr_name.startswith("sanitise_"):
            continue

        name = attr_name[9:]

        if not callable(val):
            raise RuntimeError(f"sanitiser for {name} is not callable")

        sanitiser = _Sanitiser(name, val)

        globals()[attr_name] = sanitiser
        yield name, sanitiser


_sanitisers = dict(_get_sanitisers())


def _sanitise_arg_given_val(arg, val):
    if type(arg) is not str:
        raise TypeError("arg should be a str")

    if arg in _sanitisers:
        return _sanitisers[arg](val)
    else:
        raise KeyError(f"no sanitiser found for variable {arg!r}")


def _sanitise_arg_given_args_dict(arg, args_dict):
    if type(arg) is not str:
        raise TypeError("arg should be a str")

    if arg not in args_dict:
        raise KeyError(f"variable {arg!r} not found")
    else:
        val = args_dict[arg]

    if arg in _sanitisers:
        return _sanitisers[arg](val)
    else:
        raise KeyError(f"no sanitiser found for variable {arg!r}")


def sanitise_arg(arg):
    caller_locals = inspect.currentframe().f_back.f_locals

    return _sanitise_arg_given_args_dict(arg, caller_locals)


def sanitise_args(*xargs, **kwargs):
    caller_locals = inspect.currentframe().f_back.f_locals
    for arg in xargs:
        yield _sanitise_arg_given_args_dict(arg, caller_locals)

    for arg, val in kwargs.items():
        yield _sanitise_arg_given_val(arg, val)


def sanitise_args_to_dict(*xargs, **kwargs):
    args_dict = {}

    caller_locals = inspect.currentframe().f_back.f_locals
    for arg in xargs:
        args_dict[arg] = _sanitise_arg_given_args_dict(arg, caller_locals)

    for arg, val in kwargs.items():
        args_dict[arg] = _sanitise_arg_given_val(arg, val)

    return args_dict
