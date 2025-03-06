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
            raise TypeError("if provided, 'name' should be a str")


class Sanitisers:
    def __init__(self):
        self._data = {}

    @classmethod
    def from_current_module(cls, *, prev_sanitisers=None):
        inst = cls()

        if prev_sanitisers is not None:
            if type(prev_sanitisers) is not cls:
                raise TypeError(
                    "'prev_sanitisers' should be a Sanitisers instance"
                )

            inst._data.update(prev_sanitisers._data)

        for key, val in inspect.stack()[1].frame.f_globals.items():
            if not key.startswith("sanitise_"):
                continue

            name = key[9:]

            if not name:
                raise ValueError("invalid globals name: 'sanitise_'")

            if not callable(val):
                raise TypeError(f"sanitiser for {name!r} is not callable")

            sanitiser = _Sanitiser(val, name)

            inst._data[name] = sanitiser

        return inst

    def sanitise_arg(self, name, sanitiser_name=None, *, val=_UNIQUE_NONE):
        if type(name) is not str:
            raise TypeError("'name' should be a str")

        if val is _UNIQUE_NONE:
            f_locals = inspect.stack()[1].frame.f_locals

            if name in f_locals:
                val = f_locals[name]
            else:
                raise KeyError(
                    f"{name!r} not found in locals of calling frame"
                )

        if sanitiser_name is None:
            sanitiser_name = name
        else:
            if type(sanitiser_name) is not str:
                raise TypeError("if provided, sanitiser_name should be a str")

            if sanitiser_name not in self._data:
                raise KeyError(f"no sanitiser for {sanitiser_name!r} found")

        return self._data[sanitiser_name](val, name)

    def sanitise_args(self, *names):
        f_locals = inspect.stack()[1].frame.f_locals

        for name in names:
            if type(name) is not str:
                raise TypeError("args should be strs")

            if name in f_locals:
                val = f_locals[name]
            else:
                raise KeyError(
                    f"{name!r} not found in locals of calling frame"
                )

            if name not in self._data:
                raise KeyError(f"no sanitiser for {name!r} found")

            yield self._data[name](val)
