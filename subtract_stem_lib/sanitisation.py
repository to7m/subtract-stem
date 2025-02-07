# Black majicks happen here.


##############################################################################


def _make_sanitise_int(allow_convert=False, limit=None):
    def sanitise_int(val, name):
        if allow_convert:
            val = int(val)
        elif type(val) is not int:
            raise TypeError(f"{name!r} should be an int")

        if limit == ">=0":
            if val < 0:
                raise ValueError(f"{name!r} should not be less than zero")

        return val

    return sanitise_int


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
            val = inspect.stack()[1 + additional_frames].f_locals[name]
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
