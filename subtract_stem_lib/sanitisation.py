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


sanitise_num_of_before_iterations = _make_sanitise_int(">=0")


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


def _sanitise_arg_given_caller_locals(arg, caller_locals):
    if type(arg) is not str:
        raise TypeError("arg should be a str")

    if arg not in caller_locals:
        raise KeyError(f"variable {arg!r} not found in locals")
    else:
        val = caller_locals[arg]

    if arg in _sanitisers:
        return _sanitisers[arg](val)
    else:
        raise KeyError(f"no sanitiser found for variable {arg!r}")


def sanitise_arg(arg):
    caller_locals = inspect.currentframe().f_back.f_locals

    return _sanitise_arg_given_caller_locals(arg, caller_locals)


def sanitise_args_list(args_list):
    if type(args_list) is not list:
        raise TypeError("args_list should be a list of str instances")

    caller_locals = inspect.currentframe().f_back.f_locals

    for i, arg in enumerate(args_list):
        args_list[i] = _sanitise_arg_given_caller_locals(arg, caller_locals)

    return args_list


def sanitise_args_list_to_dict(args_list):
    if type(args_list) is not list:
        raise TypeError("args_list should be a list of str instances")

    caller_locals = inspect.currentframe().f_back.f_locals

    args_dict = {}
    for arg in args_list:
        args_dict[arg] = _sanitise_arg_given_caller_locals(arg, caller_locals)

    return args_dict
