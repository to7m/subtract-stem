from itertools import count
import numpy as np

from .buffer import Buffer
from .divide import Ataabtrnfatbaa


class _AddToCumsumsForCumsumI:
    __slots__ = [
        "rotator",
        "prev_abs_stem_spectra_sum", "curr_abs_stem_spectrum_sum",
        "prev_rotated_mix_spectra_sum", "curr_rotated_mix_spectra_sum"
    ]

    def __init__(
        self, *,
        rotator,
        prev_abs_stem_spectra_sum=None, curr_abs_stem_spectra_sum=None,
        prev_rotated_mix_spectra_sum=None, curr_rotated_mix_spectra_sum=None
    ):
        self.rotator = rotator
        self.prev_abs_stem_spectra_sum = prev_abs_stem_spectra_sum
        self.curr_abs_stem_spectra_sum = curr_abs_stem_spectra_sum
        self.prev_rotated_mix_spectra_sum = prev_rotated_mix_spectra_sum
        self.curr_rotated_mix_spectra_sum = curr_rotated_mix_spectra_sum

    def __iter__(self):
        if self.prev_abs_stem_spectra_sum is None:
            iterator = iter(self.rotator)
        else:
            def iterator(
                rotator_iter=iter(self.rotator),
                prev_abs_stem_spectra_sum=self.prev_abs_stem_spectra_sum,
                curr_abs_stem_spectra_sum=self.curr_abs_stem_spectra_sum,
                prev_rotated_mix_spectra_sum
                    =self.prev_rotated_mix_spectra_sum,
                curr_rotated_mix_spectra_sum
                    =self.curr_rotated_mix_spectra_sum
            ):
                next(rotator_iter)

                curr_abs_stem_spectra_sum += prev_abs_stem_spectra_sum
                curr_rotated_mix_spectra_sum += prev_rotated_mix_spectra_sum

                yield

        return iterator()

    @classmethod
    def from_args(
        cls, *,
        stem_spectra_buffer, mix_spectra_buffer,
        abs_stem_cumsum, rotated_mix_cumsum,
        cumsum_i
    ):
        rotator = Ataabtrnfatbaa(
            stem_spectra_buffer, mix_spectra_buffer,
            out_a=abs_stem_cumsum[cumsum_i],
            out_b=rotated_mix_cumsum[cumsum_i]
        )

        if cumsum_i == 0:
            return cls(rotator=rotator)
        else:
            return cls(
                rotator=rotator,
                prev_abs_stem_spectra_sum=abs_stem_cumsum[cumsum_i - 1],
                prev_rotated_mix_spectra_sum=rotated_mix_cumsum[cumsum_i - 1],
                curr_abs_stem_spectra_sum=abs_stem_cumsum[cumsum_i],
                curr_rotated_mix_spectra_sum=rotated_mix_cumsum[cumsum_i]
            )


class SpectraBufferPairsToEqProfiles:
    __slots__ = [,
        "_add_to_cumsums_for_cumsum_indices",
        "_main_routine_for_cumsum_indices",
        "stem_spectra_buffer", "mix_spectra_buffer",
        "num_of_items", "lookbehind",
        "abs_stem_cumsum", "rotated_mix_cumsum",
        "out"
    ]

    def __init__(self):
        self._add_to_cumsums_for_cumsum_indices \
            = list(self._get_add_to_cumsums_for_cumsum_indices())
        self._main_routine_for_cumsum_indices \
            = list(self._get_main_routine_for_cumsum_indices())

    def __iter__(self):
        def iterator(
            lookbehind=self.lookbehind,
            lookbehind_range=range(self.lookbehind),
            cumsum_len=self.num_of_items,
            add_to_cumsums_for_cumsum_i_iters
                =[iter(x) for x in self._add_to_cumsums_for_cumsum_indices],
            main_routine_for_cumsum_i_iters
                =[iter(x) for x in self._main_routine_for_cumsum_indices]
        ):
            for i in lookbehind_range:
                next(add_to_cumsums_for_cumsum_i_iters[i])

                yield

            while True:
                i = (i+1) % cumsum_len

                next(main_routine_for_cumsum_i_iters[i])

                yield

        return iterator()

    def _get_add_to_cumsums_for_cumsum_indices(self):
        for cumsum_i in range(self.num_of_items):
            yield _AddToCumsumsForCumsumI.from_args(
                stem_spectra_buffer=self.stem_spectra_buffer,
                mix_spectra_buffer=self.mix_spectra_buffer,
                abs_stem_cumsum=self.abs_stem_cumsum,
                rotated_mix_cumsum=self.rotated_mix_cumsum,
                cumsum_i=cumsum_i
            )

    def _get_main_routine_for_cumsum_indices(self):
        for cumsum_i in range(self.num_of_items):
            ...
