import numpy as np

from ._pre_buffer_sanitisers import sanitisers


sanitise_arg = sanitisers.sanitise_arg


class Buffer:
    __slots__ = ["_data", "_curr_i", "num_of_items", "lookbehind"]

    def __init__(self, _data):
        self._data = sanitise_arg("_data", sanitiser_name="buffer_data")

        self.num_of_items = len(self._data)
        self.lookbehind = self.num_of_items - 1

        self._curr_i = 0

    @classmethod
    def from_constructor(
        cls, constructor, *, num_of_items=None, lookbehind=None
    ):
        sanitise_arg("constructor")

        if num_of_items is None:
            if lookbehind is None:
                raise TypeError(
                    "one of 'num_of_items' or 'lookbehind' should be provided"
                )
            else:
                sanitise_arg("lookbehind")
                num_of_items = lookbehind + 1
        else:
            if lookbehind is None:
                sanitise_arg("num_of_items")
            else:
                raise TypeError(
                    "only one of 'num_of_items' or 'lookbehind' should be "
                    "provided"
                )

        return cls([constructor() for _ in range(num_of_items)])

    @classmethod
    def from_array_args(
        cls, *, num_of_items=None, lookbehind=None, shape, dtype
    ):
        def constructor():
            return np.empty(shape, dtype=dtype)

        return cls.from_constructor(
            constructor, num_of_items=num_of_items, lookbehind=lookbehind
        )

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
