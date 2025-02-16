import numpy as np

from ._pre_buffer_sanitisers import sanitise_arg as san


class Buffer:
    __slots__ = ["_data", "num_of_items", "lookbehind", "_curr_i"]

    def __init__(self):
        raise RuntimeError(
            "Buffer should not have instances; only its subclasses should"
        )


class RealBuffer(Buffer):
    __slots__ = []

    def __init__(self, *, _data):
        self._data = san("_data", "real_buffer_data")

        self.num_of_items = len(self._data)
        self.lookbehind = self.num_of_items - 1

        self._curr_i = 0

    @property
    def newest(self):
        return self._data[self._curr_i]

    @property
    def oldest(self):
        data = self._data

        return data[(self._curr_i + 1) % len(data)]

    @property
    def newest_and_oldest(self):
        data = self._data
        curr_i = self._curr_i

        return data[curr_i], data[(curr_i + 1) % len(data)]

    def increment_and_get_newest(self):
        data = self._data
        curr_i = (self._curr_i + 1) % len(data)

        self._curr_i = curr_i

        return data[curr_i]


class QuasiBuffer:
    __slots__ = []

    def __init__(self, *, _data):
        self._data = sanitise_arg("_data", sanitiser_name="quasi_buffer_data")

        self.num_of_items = 1
        self.lookbehind = 0

        self._curr_i = 0

    @property
    def newest(self):
        return self._data

    oldest, increment_and_get_newest = newest

    @property
    def newest_and_oldest(self):
        data = self._data
        return data, data


def _buffer_from_data(*, _data):
    san("_data", "buffer_data")

    if len(_data) == 1:
        return QuasiBuffer(_data=_data[0])
    else:
        return RealBuffer(_data=_data)


def buffer_from_constructor(
    constructor, *, num_of_items=None, lookbehind=None
):
    sanitise_arg("constructor")

    if num_of_items is None:
        if lookbehind is None:
            raise TypeError(
                "one of 'num_of_items' or 'lookbehind' should be provided"
            )
        else:
            num_of_items = sanitise_arg("lookbehind") + 1
    else:
        if lookbehind is None:
            sanitise_arg("num_of_items")
        else:
            raise TypeError(
                "only one of 'num_of_items' or 'lookbehind' should be "
                "provided"
            )

    return _buffer_from_data([constructor() for _ in range(num_of_items)])


def buffer_from_array_args(
    shape, *, dtype, num_of_items=None, lookbehind=None
):
    def constructor():
        return np.empty(shape, dtype=dtype)

    return buffer_from_constructor(
        constructor, num_of_items=num_of_items, lookbehind=lookbehind
    )


def buffer_from_array(array):
    san("array")

    return QuasiBuffer(_data=array)
