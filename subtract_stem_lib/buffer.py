import numpy as np

from ._sanitisation import sanitise_arg as san


class Buffer:
    def __init__(self):
        raise RuntimeError(
            "Buffer should not have instances; only its subclasses should"
        )


class RealBuffer(Buffer):
    __slots__ = ["_data", "_curr_i", "num_of_items", "lookbehind"]

    def __init__(self, *, _data):
        self._data = san("_data", "real_buffer_data")

        self.num_of_items = len(self._data)
        self.lookbehind = self.num_of_items - 1

        self._curr_i = 0

    @property
    def oldest(self):
        data = self._data

        return data[(self._curr_i + 1) % len(data)]

    @property
    def newest(self):
        return self._data[self._curr_i]

    @property
    def oldest_and_newest(self):
        data = self._data
        curr_i = self._curr_i

        return data[(curr_i + 1) % len(data)], data[curr_i]

    def increment_and_get_newest(self):
        data = self._data
        curr_i = (self._curr_i + 1) % len(data)

        self._curr_i = curr_i

        return data[curr_i]


class QuasiBuffer:
    __slots__ = [
        "num_of_items", "lookbehind", "oldest", "newest", "oldest_and_newest"
    ]

    def __init__(self, *, _data):
        self.oldest = self.newest = san("_data", "quasi_buffer_data")
        self.oldest_and_newest = self.oldest, self.newest

        self.num_of_items = 1
        self.lookbehind = 0

    def increment_and_get_newest(self):
        return self.newest


def _buffer_from_data(data):
    san("data", "buffer_data")

    if len(data) == 1:
        return QuasiBuffer(_data=data[0])
    else:
        return RealBuffer(_data=data)


def buffer_from_constructor(
    constructor, *, num_of_items=None, lookbehind=None
):
    san("constructor")

    if num_of_items is None:
        if lookbehind is None:
            raise TypeError(
                "one of 'num_of_items' or 'lookbehind' should be provided"
            )
        else:
            num_of_items = san("lookbehind") + 1
    else:
        if lookbehind is None:
            san("num_of_items")
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
