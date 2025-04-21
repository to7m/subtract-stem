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

    def _parse_names(self, name_or_names, *, var_name):
        names = [name.strip() for name in name_or_names.split(',')]

        if not names[0]:
            raise ValueError(f"{var_name!r} starts with invalid name")

        if not names[-1]:
            del names[-1]

        for name in names:
            if not name:
                raise ValueError(f"name missing in {var_name!r}")

        return names

    def _sanitise_arg(self, name, sanitiser_name, *, val, f_locals):
        if val is _UNIQUE_NONE:
            if name in f_locals:
                val = f_locals[name]
            else:
                raise KeyError(
                    f"{name!r} not found in locals of calling frame"
                )

        if sanitiser_name in self._data:
            sanitiser = self._data[sanitiser_name]
        else:
            raise KeyError(f"no sanitiser for {sanitiser_name!r} found")

        return sanitiser(val, name)

    def _handle_multiple(self, names, sanitiser_names, *, vals):
        names = self._parse_names(names, var_name="name_or_names")

        if ',' in sanitiser_names:
            sanitiser_names = self._parse_names(
                sanitiser_names, var_name="sanitiser_name_or_names"
            )

            if len(names) != len(sanitiser_names):
                raise ValueError(
                    "'name_or_names' contains a different number of names to "
                    "'sanitiser_name_or_names'"
                )
        else:
            sanitiser_name = sanitiser_names.strip()

            if not sanitiser_name:
                raise ValueError(
                    "if provided, 'sanitiser_name_or_names' should start with "
                    "a valid name"
                )

            sanitiser_names = [sanitiser_name for _ in range(len(names))]

        if vals is _UNIQUE_NONE:
            vals = [_UNIQUE_NONE for _ in range(len(names))]
        elif type(vals) in [tuple, list]:
            if len(names) != len(vals):
                raise ValueError(
                    "'name_or_names' contains a different number of names to "
                    "'vals'"
                )
        else:
            raise TypeError("if provided, 'vals' should be a tuple or list")

        f_locals = inspect.stack()[1].frame.f_locals

        return tuple(
            self._sanitise_arg(
                name, sanitiser_name, val=val, f_locals=f_locals
            )
            for name, sanitiser_name, val
            in zip(names, sanitiser_names, vals)
        )

    def _handle_single(self, name, sanitiser_name, *, val):
        name = name.strip()

        if not name:
            raise ValueError("'name_or_names' should start with a valid name")

        sanitiser_name = sanitiser_name.strip()

        if not sanitiser_name:
            raise ValueError(
                "if provided, 'sanitiser_name_or_names' should start with a "
                "valid name"
            )

        f_locals = inspect.stack()[1].frame.f_locals

        return self._sanitise_arg(
            name, sanitiser_name, val=val, f_locals=f_locals
        ) 

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

    def sanitise(
        self,
        name_or_names, sanitiser_name_or_names=None, *,
        val=_UNIQUE_NONE, vals=_UNIQUE_NONE
    ):
        if type(name_or_names) is not str:
            raise TypeError("'name_or_names' should be a str")

        if sanitiser_name_or_names is None:
            sanitiser_name_or_names = name_or_names
        elif type(sanitiser_name_or_names) is not str:
            raise TypeError(
                "if provided, 'sanitiser_name_or_names' should be a str"
            )

        if ',' in name_or_names:
            if val is _UNIQUE_NONE:
                return self._handle_multiple(
                    name_or_names, sanitiser_name_or_names, vals=vals
                )
            else:
                raise TypeError(
                    "if multiple names are provided, 'vals' may be provided, "
                    "but 'val' should not"
                )
        else:
            if vals is _UNIQUE_NONE:
                return self._handle_single(
                    name_or_names, sanitiser_name_or_names, val=val
                )
            else:
                raise TypeError(
                    "if only one name is provided, 'val' may be provided, "
                    "but 'vals' should not"
                )
