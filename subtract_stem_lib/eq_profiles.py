import numpy as np

from .defaults import MAX_ABS_RESULT
from .buffer import Buffer
from ._sanitisation import sanitise_arg as san
from ._sanitise_spectra_buffer import (
    sanitise_spectra_buffer, sanitise_stem_mix_spectra_buffers
)
from ._sanitise_unique_arrays_of_shape import sanitise_unique_arrays_of_shape
from .divide import SafeDivider, Ataabtrnfatbaa


def _rotator_for_cumsum_slot_from_args(
    *,
    stem_spectra_buffer, mix_spectra_buffer,
    abs_stem_spectra_cumsum, rotated_mix_spectra_cumsum, cumsum_i
):
    return Ataabtrnfatbaa(
        stem_spectra_buffer, mix_spectra_buffer,
        out_a=abs_stem_spectra_cumsum[cumsum_i],
        out_b=rotated_mix_spectra_cumsum[cumsum_i]
    )


class _CompleteCumsumEntryForCumsumSlot:
    __slots__ = ["prev_cumsum_entry", "curr_cumsum_entry", "is_dummy"]

    def __init__(self, *, prev_cumsum_entry, curr_cumsum_entry):
        self.prev_cumsum_entry = prev_cumsum_entry
        self.curr_cumsum_entry = curr_cumsum_entry

        self.is_dummy = prev_cumsum_entry is None

    def __iter__(self):
        if self.is_dummy:
            raise RuntimeError("this part should never be reached")

        def iterator(
            prev_cumsum_entry=self.prev_cumsum_entry,
            curr_cumsum_entry=self.curr_cumsum_entry
        ):
            while True:
                curr_cumsum_entry += prev_cumsum_entry

                yield

        return iterator()

    @classmethod
    def from_args(cls, *, cumsum, cumsum_i):
        if cumsum_i == 0:
            prev_cumsum_entry = None
        else:
            prev_cumsum_entry = cumsum[cumsum_i - 1]

        return cls(
            prev_cumsum_entry=prev_cumsum_entry,
            curr_cumsum_entry=cumsum[cumsum_i]
        )


class _GetMovingSumForCumsumSlot:
    __slots__ = [
        "curr_cumsum_entry",
        "entry_before_moving_sum_start", "last_in_prev_cumsum",
        "out",
        "is_dummy"
    ]

    def __init__(
        self, *,
        curr_cumsum_entry, entry_before_moving_sum_start, last_in_prev_cumsum,
        out
    ):
        self.curr_cumsum_entry = curr_cumsum_entry
        self.entry_before_moving_sum_start = entry_before_moving_sum_start
        self.last_in_prev_cumsum = last_in_prev_sumsum
        self.out = out

        self.is_dummy = entry_before_moving_sum_start is None

    def __iter__(self):
        if self.is_dummy:
            raise RuntimeError("this part should never be reached")

        if self.last_in_prev_cumsum is None:
            def get_iterator(
                subtract=np.subtract,
                curr_cumsum_entry=self.curr_cumsum_entry,
                entry_before_moving_sum_start
                    =self.entry_before_moving_sum_start,
                out=self.out
            ):
                subtract(
                    curr_cumsum_entry, entry_before_moving_sum_start,
                    out=out
                )
        else:
            def get_iterator(
                subtract=np.subtract,
                curr_cumsum_entry=self.curr_cumsum_entry,
                entry_before_moving_sum_start
                    =self.entry_before_moving_sum_start,
                last_in_prev_cumsum=self.last_in_prev_cumsum,
                out=self.out
            ):
                subtract(
                    curr_cumsum_entry, entry_before_moving_sum_start,
                    out=out
                )
                out += last_in_prev_cumsum

        return iterator()

    @classmethod
    def from_args(cls, *, cumsum, cumsum_i, probable_out):
        if cumsum_i == len(cumsum) - 2:
            entry_before_moving_sum_start = last_in_prev_cumsum = None
            out = cumsum[-2]
        else:
            if cumsum_i == len(cumsum) - 1:
                entry_before_moving_sum_start = cumsum[0]
                last_in_prev_cumsum = None
            else:
                entry_before_moving_sum_start = cumsum[cumsum_i + 1]
                last_in_prev_cumsum = cumsum[-1]

            out = probable_out

        return cls(
            curr_cumsum_entry=cumsum[cumsum_i],
            entry_before_moving_sum_start=entry_before_moving_sum_start,
            last_in_prev_cumsum=last_in_prev_cumsum,
            out=out
        )


def _divider_for_cumsum_slot_from_args(
    *,
    abs_stem_spectra_cumsum, rotated_mix_spectra_cumsum, cumsum_i,
    probable_abs_stem_spectra_sum, probable_rotated_mix_spectra_sum,
    max_abs_result, ret_reciprocal_eq,
    bool_arr
):
    if cumsum_i == len(abs_stem_spectra_cumsum) - 2:
        a, b = rotated_mix_spectra_cumsum[-2], abs_stem_spectra_cumsum[-2]
    else:
        a, b = probable_rotated_mix_spectra_sum, probable_abs_stem_spectra_sum

    if ret_reciprocal_eq:
        a, b = b, a

    return SafeDivider(
        a, b,
        max_abs_result=max_abs_result,
        intermediate_a=probable_abs_stem_spectra_sum, intermediate_b=bool_arr,
        out=probable_rotated_mix_spectra_sum
    )


class _IterableForCumsumSlot:
    __slots__ = [
        "_sub_iterables",
        "rotator",
        "complete_abs_stem_spectra_cumsum_entry",
        "complete_rotated_mix_spectra_cumsum_entry",
        "get_abs_stem_spectra_moving_sum",
        "get_rotated_mix_spectra_moving_sum",
        "divider",
        "is_initialisation"
    ]

    def __init__(
        self, *,
        rotator,
        complete_abs_stem_spectra_cumsum_entry,
        complex_rotated_mix_spectra_cumsum_entry,
        get_abs_stem_spectra_moving_sum,
        get_rotated_mix_spectra_moving_sum,
        divider,
        is_initialisation
    ):
        self.rotator = rotator
        self.complete_abs_stem_spectra_cumsum_entry \
            = complete_abs_stem_spectra_cumsum_entry
        self.complex_rotated_mix_spectra_cumsum_entry \
            = complex_rotated_mix_spectra_cumsum_entry
        self.get_abs_stem_spectra_moving_sum = get_abs_stem_spectra_moving_sum
        self.get_rotated_mix_spectra_moving_sum \
            = get_rotated_mix_spectra_moving_sum
        self.divider = divider
        self.is_initialisation = is_initialisation

        self._sub_iterables = list(self._get_subiterables())

    def __iter__(self):
        if len(self._sub_iterables) == 1:
            return iter(self.rotator)
        else:
            def get_iterator(iter=zip(*self._sub_iterables)):
                next(iter)

                yield

        return get_iterator()

    def _get_subiterables(self):
        yield self.rotator

        if not self.complete_abs_stem_spectra_cumsum_entry.is_dummy:
            yield self.complete_abs_stem_spectra_cumsum_entry
            yield self.complete_rotated_mix_spectra_cumsum_entry

        if self.is_initialisation:
            return

        if not self.get_abs_stem_spectra_moving_sum.is_dummy:
            yield self.get_abs_stem_spectra_moving_sum
            yield self.get_rotated_mix_spectra_moving_sum

        yield self.divider


def _sanitise_intermediates_and_out(
    intermediate_a, intermediate_b, out, *, shape
):
    yield from sanitise_unique_arrays_of_shape(
        array_infos=[
            (intermediate_a, "intermediate_a", "float"),
            (intermediate_b, "intermediate_b", "bool"),
            (out, "out", "complex")
        ],
        reference_shape=shape,
        reference_name
            ="'stem_spectra_buffer' arrays and 'mix_spectra_buffer' arrays"
    )


class SpectraBuffersToEqProfile:
    __slots__ = [
        "_abs_stem_spectra_sum", "_rotated_mix_spectra_sum",
        "_initial_rotator", "_main_rotator", "_divider",
        "stem_spectra_buffer", "mix_spectra_buffer",
        "max_abs_result", "ret_reciprocal_eq",
        "intermediate_a", "intermediate_b",
        "out"
    ]

    def __init__(
        self, stem_spectra_buffer, mix_spectra_buffer, *,
        max_abs_result=MAX_ABS_RESULT, ret_reciprocal_eq=False,
        intermediate_a=None,  # numpy.float32
        intermediate_b=None,  # bool
        out=None
    ):
        self.stem_spectra_buffer, self.mix_spectra_buffer \
            = sanitise_stem_mix_spectra_buffers(
                  stem_spectra_buffer, mix_spectra_buffer
              )
        self.max_abs_result = san("max_abs_result")
        self.ret_reciprocal_eq = san("ret_reciprocal_eq")
        self.intermediate_a, self.intermediate_b, self.out \
            = _sanitise_intermediates_and_out(
                  intermediate_a, intermediate_b, out,
                  shape=self.stem_spectra_buffer.newest.shape
              )

        self._abs_stem_spectra_sum, self._rotated_mix_spectra_sum \
            = self._get_sums()
        self._initial_rotator, self._main_rotator = self._get_rotators()
        self._divider = self._get_divider()

    def __iter__(self):
        def get_iterator(
            initial_rotator=self._initial_rotator,
            main_rotator=self._main_rotator,
            abs_stem_spectrum=self.intermediate_a,
            rotated_mix_spectrum=self.out,
            abs_stem_spectra_sum=self._abs_stem_spectra_sum,
            rotated_mix_spectra_sum=self._rotated_mix_spectra_sum,
        ):
            next(initial_rotator)

            yield

            while True:
                next(main_rotator)

                abs_stem_spectra_sum += abs_stem_spectrum
                rotated_mix_spectra_sum += rotated_mix_spectrum

                yield

        return get_iterator()

    def _get_sums(self):
        for dtype in np.float32, np.complex64:
            yield np.empty(self.out.shape, dtype=dtype)

    def _get_rotators(self):
        yield Ataabtrnfatbaa(
            self.stem_spectra_buffer, self.mix_spectra_buffer,
            out_a=self._abs_stem_spectra_sum,
            out_b=self._rotated_mix_spectra_sum
        )

        yield Ataabtrnfatbaa(
            self.stem_spectra_buffer, self.mix_spectra_buffer,
            out_a=self.intermediate_a, out_b=self.out
        )

    def _get_divider(self):
        a, b = self._rotated_mix_spectra_sum, self._abs_stem_spectra_sum

        if self.ret_reciprocal_eq:
            a, b = b, a

        return SafeDivider(
            a, b,
            max_abs_result=self.max_abs_result,
            intermediate_a=self.intermediate_a,
            intermediate_b=self.intermediate_b,
            out=self.out
        )

    def get_eq_profile(self):
        next(iter(self._divider))

        return self.out


class SpectraBuffersToEqProfiles:
    __slots__ = [
        "_abs_stem_spectra_cumsum", "_rotated_mix_spectra_cumsum",
        "_kwargs_for_cumsum_slots",
        "_initialisation_iterables", "_main_iterables",
        "stem_spectra_buffer", "mix_spectra_buffer",
        "lookbehind", "max_abs_result", "ret_reciprocal_eq",
        "intermediate_a", "intermediate_b",
        "out",
        "cumsum_len"
    ]

    def __init__(
        self, stem_spectra_buffer, mix_spectra_buffer, *,
        lookbehind, max_abs_result=MAX_ABS_RESULT, ret_reciprocal_eq=False,
        intermediate_a=None,  # numpy.float32
        intermediate_b=None,  # bool
        out=None
    ):
        self.stem_spectra_buffer, self.mix_spectra_buffer \
            = sanitise_stem_mix_spectra_buffers(
                  stem_spectra_buffer, mix_spectra_buffer
              )
        self.lookbehind = san("lookbehind")
        self.max_abs_result = san("max_abs_result")
        self.ret_reciprocal_eq = san("ret_reciprocal_eq")
        self.intermediate_a, self.intermediate_b, self.out \
            = _sanitise_intermediates_and_out(
                  intermediate_a, intermediate_b, out,
                  shape=self.stem_spectra_buffer.newest.shape
              )

        self.cumsum_len = lookbehind + 2

        self._abs_stem_spectra_cumsum, self._rotated_mix_spectra_cumsum \
            = self._get_cumsums()

        self._kwargs_for_cumsum_slots \
            = list(self._get_kwargs_for_cumsum_slots)

        self._initialisation_iterables \
            = list(self._get_initialisation_iterables())
        self._main_iterables = list(self._get_main_iterables())

    def __iter__(self):
        def get_iterator(
            initialisation_iterators
                =[iter(x) for x in self._initialisation_iterables],
            main_iterators=[iter(x) for x in self._main_iterables]
        ):
            for iterator in initialisation_iterators:
                next(iterator)

                yield

            while True:
                for iterator in main_iterators:
                    next(iterator)

                    yield

        return get_iterator()

    def _get_cumsums(self):
        cumsum_shape = self.cumsum_len, *self.out.shape

        for dtype in np.float32, np.complex64:
            yield np.empty(cumsum_shape, dtype=dtype)

    def _get_kwargs_for_cumsum_slots(self):
        for cumsum_i in range(self.cumsum_len):
            yield {
                "rotator": _rotator_for_cumsum_slot_from_args(
                    stem_spectra_buffer=self.stem_spectra_buffer,
                    mix_spectra_buffer=self.mix_spectra_buffer,
                    abs_stem_spectra_cumsum=self._abs_stem_spectra_cumsum,
                    rotated_mix_spectra_cumsum
                        =self._rotated_mix_spectra_cumsum,
                    cumsum_i=cumsum_i
                ),
                "complete_abs_stem_spectra_cumsum_entry":
                    _CompleteCumsumEntryForCumsumSlot.from_args(
                        cumsum=self._abs_stem_spectra_cumsum,
                        cumsum_i=cumsum_i
                    ),
                "complete_rotated_mix_spectra_cumsum_entry":
                    _CompleteCumsumEntryForCumsumSlot.from_args(
                        cumsum=self._rotated_mix_spectra_cumsum,
                        cumsum_i=cumsum_i
                    ),
                "get_abs_stem_spectra_moving_sum":
                    _GetMovingSumForCumsumSlot.from_args(
                        cumsum=self._abs_stem_spectra_cumsum,
                        cumsum_i=cumsum_i,
                        probable_out=self._intermediate_a
                    ),
                "get_rotated_mix_spectra_moving_sum":
                    _GetMovingSumForCumsumSlot.from_args(
                        cumsum=self._rotated_mix_spectra_cumsum,
                        cumsum_i=cumsum_i,
                        probable_out=self.out
                    ),
                "divider": _divider_for_cumsum_slot_from_args(
                    abs_stem_spectra_cumsum=self._abs_stem_spectra_cumsum,
                    rotated_mix_spectra_cumsum
                        =self._rotated_mix_spectra_cumsum,
                    cumsum_i=cumsum_i,
                    probable_abs_stem_spectra_sum=self.intermediate_a,
                    probable_rotated_mix_spectra_sum=self.out,
                    max_abs_result=self.max_abs_result,
                    ret_reciprocal_eq=self.ret_reciprocal_eq,
                    bool_arr=self.intermediate_b
                )
            }

    def _get_initialisation_iterables(self):
        for cumsum_i in range(self.lookbehind):
            yield _IterableForCumsumSlot(
                **self._kwargs_for_cumsum_slots[cumsum_i],
                is_initialisation=True
            )

    def _get_main_iterables(self):
        for subsequent_cumsum_i in range(self.cumsum_len):
            cumsum_i \
                = (subsequent_cumsum_i + self.lookbehind) % self.cumsum_len

            yield _IterableForCumsumSlot(
                **self._kwargs_for_cumsum_slots[cumsum_i],
                is_initialisation=False
            )


class ApplyEqProfilesToSpectraBufferOldest:
    __slots__ = ["eq_profile", "spectra_buffer", "out"]

    def __init__(self, eq_profile, spectra_buffer, *, out=None):
        self.eq_profile = san("eq_profile")
        self.spectra_buffer = sanitise_spectra_buffer(
            spectra_buffer, name="spectra_buffer",
            reference_shape=eq_profile.shape,
            reference_name_quoted="'eq_profile'"
        )
        self.out = sanitise_spectra_buffer(
            out, name="out",
            reference_shape=eq_profile.shape,
            reference_name_quoted="'eq_profile' and 'spectra_buffer' arrays"
        )

    def __iter__(self):
        def get_iterator(
            multiply=np.multiply,
            spectra_buffer=self.spectra_buffer,
            eq_profile=self.eq_profile,
            out=self.out
        ):
            while True:
                multiply(spectra_buffer.oldest, eq_profile, out=out.oldest)

                yield

        return get_iterator()
