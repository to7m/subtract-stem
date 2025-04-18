from itertools import chain
from math import tau
from fractions import Fraction
import numpy as np

from .defaults import INNER_GRAIN_LEN
from ._sanitisation import sanitise_arg as san, sanitise_args


def sanitise_pad_lens(self, pad_len, left_pad_len, right_pad_len):
    if pad_len is None:
        yield 0 if left_pad_len is None else san("left_pad_len")
        yield 0 if right_pad_len is None else san("right_pad_len")
    else:
        if left_pad_len is not None or right_pad_len is not None:
            raise TypeError(
                "if 'pad_len' is provided, neither 'left_pad_len' nor "
                "'right_pad_len' should be provided"
            )

        yield san("pad_len")
        yield pad_len


class InnerGrainInfo:
    __slots__ = ["inner_grain_len", "interval_len", "overlap"]

    def __init__(
        self, *, inner_grain_len=None, interval_len=None, overlap=None
    ):
        self.inner_grain_len, self.interval_len, self.overlap \
            = self._sanitise_args(inner_grain_len, interval_len, overlap)

    def _strip_none(inner_grain_len, interval_len, overlap):
        if inner_grain_len is None:
            if None in (interval_len, overlap):
                inner_grain_len = INNER_GRAIN_LEN
            else:
                inner_grain_len = interval_len * overlap
        elif interval_len is None and overlap is None:
            interval_len = INTERVAL_LEN
        elif interval_len is None:
            if inner_grain_len % overlap == 0:
                interval_len = inner_grain_len // overlap
            else:
                raise ValueError(
                    f"'inner_grain_len' ({inner_grain_len}) is not divisible "
                    f"by 'overlap' ({overlap})"
                )
        else:
            if inner_grain_len % interval_len == 0:
                overlap = inner_grain_len // interval_len
            else:
                raise ValueError(
                    f"'inner_grain_len' ({inner_grain_len}) is not divisible "
                    f"by 'interval_len' ({interval_len})"
                )

        return inner_grain_len, interval_len, overlap

    def _sanitise_args(self, inner_grain_len, interval_len, overlap):
        if inner_grain_len is not None:
            inner_grain_len = san("inner_grain_len")

        if interval_len is not None:
            interval_len = san("interval_len")

        if overlap is not None:
            overlap = san("overlap")

        while None in (inner_grain_len, interval_len, overlap):
            inner_grain_len, interval_len, overlap \
                = self._strip_none(inner_grain_len, interval_len, overlap)

        if inner_grain_len != interval_len * overlap:
            raise ValueError(
                f"'inner_grain_len' ({inner_grain_len}) is not "
                f"'interval_len' ({interval_len}) * 'overlap' ({overlap})"
            )

        return inner_grain_len, interval_len, overlap

    def _get_hann_window_arrays(self):
        window_len = left_pad_len + self.inner_grain_len + right_pad_len
        window = np.empty(window_len, dtype=np.float32)

        window[:left_pad_len] = 0
        inner_window = window[left_pad_len:len(window) - right_pad_len]
        window[len(window) - right_pad_len:] = 0

        return window, inner_window

    def _set_unscaled_inner_window(self, arr):
        # arr = phase
        np.arange(self.inner_grain_len, out=arr)
        arr += float(delay_audio_samples)
        arr *= tau / self.inner_grain_len

        # arr = unscaled inner window
        np.cos(arr, out=arr)
        np.subtract(1, arr, out=arr)

    def _get_scale(self, inner_window):
        scale = inner_window[:self.interval_len].copy()

        for i in range(1, self.overlap):
            start_i = i * self.interval_len
            stop_i = start_i + self.interval_len
            scale += inner_window[start_i:stop_i]

        np.divide(1, scale, out=scale)

        return scale

    def _apply_scale(self, inner_window, scale):
        for i in range(self.overlap):
            start_i = i * self.interval_len
            stop_i = start_i + self.interval_len
            inner_window[start_i:stop_i] *= scale

    def get_hann_window(
        self, *,
        pad_len=None, left_pad_len=None, right_pad_len=None,
        delay_audio_samples=Fraction(0)
    ):
        left_pad_len, right_pad_len \
            = sanitise_pad_lens(pad_len, left_pad_len, right_pad_len)
        delay_audio_samples = san("delay_audio_samples")

        window, inner_window = self._get_hann_window_arrays()

        self._set_unscaled_inner_window(inner_window)
        scale = self._get_scale(inner_window)
        self._apply_scale(inner_window, scale)

        return window


class _GrainRanges:
    __slots__ = [
        "_start_grain_stop_i", "_data",
        "start_i", "interval_len", "num_of_iterations",
        "audio_len", "grain_len"
    ]

    def __init__(
        self, *,
        start_i, interval_len, num_of_iterations,
        audio_len, grain_len
    ):
        self.start_i = start_i
        self.interval_len = interval_len
        self.num_of_iterations = num_of_iterations
        self.audio_len, self.grain_len = audio_len, grain_len

        self._start_grain_stop_i = self.start_i + self.grain_len

        self._data = list(self._get_grain_ranges())

    def __iter__(self):
        return iter(self._data)

    def _get_grain_num(self, *, start_i=None, stop_i=None):
        if stop_i is None:
            return (start_i - self.start_i) // self.interval_len
        else:
            return (stop_i - self._start_grain_stop_i) // self.interval_len

    def _get_clamped_grain_range(self, start_grain_num, stop_grain_num):
        return range(
            min(max(start_grain_num, 0), self.num_of_iterations),
            min(max(stop_grain_num, 0), self.num_of_iterations)
        )

    def _get_draft_entering_grain_range(self):
        start_grain_stop_i \
            = (self._start_grain_stop_i - 1) % self.interval_len + 1
        stop_grain_start_i = self.start_i % self.interval_len

        start_grain_num = self._get_grain_num(stop_i=start_grain_stop_i)
        stop_grain_num = self._get_grain_num(start_i=stop_grain_start_i)

        return self._get_clamped_grain_range(start_grain_num, stop_grain_num)

    def _get_draft_exiting_grain_range(self):
        start_grain_stop_i = (
            (self._start_grain_stop_i - self.audio_len - 1)
            % self.interval_len
            + self.audio_len + 1
        )
        stop_grain_start_i = (
            (self.start_i - self.audio_len)
            % self.interval_len
            + self.audio_len
        )

        start_grain_num = self._get_grain_num(stop_i=start_grain_stop_i)
        stop_grain_num = self._get_grain_num(start_i=stop_grain_start_i)

        return self._get_clamped_grain_range(start_grain_num, stop_grain_num)

    def _get_unpruned_grain_ranges(self):
        entering_draft = self._get_draft_entering_grain_range()
        exiting_draft = self._get_draft_exiting_grain_range()

        yield "before", range(entering_draft.start)

        if exiting_draft.start < entering_draft.stop:
            yield "entering", range(entering_draft.start, exiting_draft.start)
            yield "island", range(exiting_draft.start, entering_draft.stop)
            yield "exiting", range(entering_draft.stop, exiting_draft.stop)
        else:
            yield "entering", range(entering_draft.start, entering_draft.stop)
            yield "full", range(entering_draft.stop, exiting_draft.start)
            yield "exiting", range(exiting_draft.start, exiting_draft.stop)

        yield "after", range(exiting_draft.stop, self.num_of_iterations)

    def _get_grain_ranges(self):
        for name, grain_range in self._get_unpruned_grain_ranges():
            if grain_range.start != grain_range.stop:
                yield name, grain_range

    def get_grain_start_i(self, grain_num):
        return self.start_i + grain_num * self.interval_len

    def get_grain_stop_i(self, grain_num):
        return self._start_grain_stop_i + grain_num * self.interval_len

    def get_start_indices_from_grain_range(self, grain_range):
        return range(
            self.get_grain_start_i(grain_range.start),
            self.get_grain_start_i(grain_range.stop),
            self.interval_len
        )

    def get_stop_indices_from_grain_range(self, grain_range):
        return range(
            self.get_grain_stop_i(grain_range.start),
            self.get_grain_stop_i(grain_range.stop),
            self.interval_len
        )


class AudioToGrains:
    __slots__ = [
        "_grain_ranges",
        "audio",
        "start_i", "interval_len", "num_of_iterations",
        "window", "out"
    ]

    def __init__(
        self, audio, *,
        start_i, interval_len, num_of_iterations,
        window,
        out=None
    ):
        (
            self.audio,
            self.start_i, self.interval_len, self.num_of_iterations,
            self.window
        ) = sanitise_args(
            "audio",
            "start_i", "interval_len", "num_of_iterations",
            "window"
        )
        self.out = self._sanitise_out(out)

        self._grain_ranges = _GrainRanges(
            start_i=start_i,
            interval_len=interval_len,
            num_of_iterations=num_of_iterations,
            audio_len=len(audio),
            grain_len=len(window)
        )

    def __iter__(self):
        subiterators = list(self._get_subiterators())

        if len(subiterators) == 1:
            return subiterators[0]
        else:
            return chain(*subiterators)

    def _sanitise_out(self, out):
        if out is None:
            out = np.empty(self.window.shape, dtype=np.float32)
        else:
            out = san("out", "array_1d_float")

            if out.shape != self.window.shape:
                raise ValueError("'out' should have same shape as 'window'")

        return out

    def _get_before_iterator(self, grain_range):
        def get_iterator(fill_out=self.out.fill, grain_range=grain_range):
            fill_out(0)

            for i in grain_range:
                yield

        return get_iterator()

    def _get_entering_iterator(self, grain_range):
        stop_indices = self._grain_ranges.get_stop_indices_from_grain_range(
            grain_range
        )

        if grain_range.start == 0:
            view_to_zero = self.out[:-stop_indices.start]

            def get_iterator(
                fill_view_to_zero=view_to_zero.fill,
                stop_indices=stop_indices,
                multiply=np.multiply,
                audio=self.audio, window=self.window, out=self.out
            ):
                fill_view_to_zero(0)

                for stop_i in stop_indices:
                    multiply(
                        audio[:stop_i],
                        window[-stop_i:],
                        out=out[-stop_i:]
                    )

                    yield
        else:
            def get_iterator(
                stop_indices=stop_indices,
                multiply=np.multiply,
                audio=self.audio, window=self.window, out=self.out
            ):
                for stop_i in stop_indices:
                    multiply(
                        audio[:stop_i],
                        window[-stop_i:],
                        out=out[-stop_i:]
                    )

                    yield

        return get_iterator()

    def _get_full_iterator(self, grain_range):
        start_indices = self._grain_ranges.get_start_indices_from_grain_range(
            grain_range
        )

        def get_iterator(
            start_indices=start_indices,
            multiply=np.multiply,
            audio=self.audio,
            window=self.window,
            grain_len=len(self.window),
            out=self.out
        ):
            for start_i in start_indices:
                multiply(
                    audio[start_i:start_i + grain_len],
                    window,
                    out=out
                )

                yield

        return get_iterator()

    # unoptimised edge case
    def _get_island_iterator(self, grain_range):
        for start_i in self._grain_ranges.get_start_indices_from_grain_range(
            grain_range
        ):
            stop_i = start_i + len(self.window)

            before_len = -start_i
            after_len = stop_i - len(self.audio)

            self.out[:before_len] = 0
            np.multiply(
                self.audio,
                self.window[before_len:-after_len],
                out=self.out[before_len:-after_len]
            )
            self.out[-after_len:] = 0

            yield

    def _get_exiting_iterator(self, grain_range):
        start_indices = self._grain_ranges.get_start_indices_from_grain_range(
            grain_range
        )

        def get_iterator(
            start_indices=start_indices,
            multiply=np.multiply,
            audio=self.audio,
            window=self.window,
            out=self.out,
            interval_len=self.interval_len,
            prev_full_len=len(self.window),
            curr_full_len=len(self.audio) - start_indices[0]
        ):
            for start_i in start_indices:
                multiply(
                    audio[start_i:],
                    window[:curr_full_len],
                    out=out[:curr_full_len]
                )
                out[curr_full_len:prev_full_len] = 0

                yield

                prev_full_len = curr_full_len
                curr_full_len -= interval_len

        return get_iterator()

    # the out.fill(0) could be a tiny bit more optimised
    _get_after_iterator = _get_before_iterator

    def _get_subiterators(self):
        for name, grain_range in self._grain_ranges:
            bound_method = getattr(self, f"_get_{name}_iterator")

            yield bound_method(grain_range)


class AudioToHannGrains:
    __slots__ = [
        "_inner_grain_info",
        "_audio_to_grains",
        "_delay_audio_samples_remainder",
        "audio",
        "start_i", "num_of_iterations",
        "inner_grain_len", "interval_len", "overlap",
        "left_pad_len", "right_pad_len", "grain_len",
        "delay_audio_samples",
        "out"
    ]

    def __init__(
        self, audio, *,
        start_i, num_of_iterations,
        inner_grain_len=None, interval_len=None, overlap=None,
        pad_len=None, left_pad_len=None, right_pad_len=None,
        delay_audio_samples=Fraction(0),
        out=None
    ):
        self.start_i = san("start_i")

        self._inner_grain_info = InnerGrainInfo(
            inner_grain_len=inner_grain_len,
            interval_len=interval_len, overlap=overlap
        )
        self.inner_grain_len = self._inner_grain_info.inner_grain_len
        self.interval_len = self._inner_grain_info.interval_len
        self.overlap = self._inner_grain_info.overlap

        self.left_pad_len, self.right_pad_len \
            = sanitise_pad_lens(pad_len, left_pad_len, right_pad_len)
        self.grain_len \
            = self.left_pad_len + self.inner_grain_len + self.right_pad_len

        self.delay_audio_samples = san("delay_audio_samples")
        self._delay_audio_samples_remainder = self.delay_audio_samples % 1
        delay_audio_samples_whole = int(
            self.delay_audio_samples - self._delay_audio_samples_remainder
        )

        self.out = self._sanitise_out(out)

        self._audio_to_grains = AudioToGrains(
            audio,
            start_i=start_i - delay_audio_samples_whole,
            interval_len=self.interval_len,
            num_of_iterations=num_of_iterations,
            window=self._get_window(),
            out=self.out[self.left_pad_len:len(self.out) - self.right_pad_len]
        )
        self.audio = audio
        self.num_of_iterations = num_of_iterations

    def __iter__(self):
        return iter(self._audio_to_grains)

    def _sanitise_out(self, out):
        if out is None:
            out = np.empty(self.grain_len, dtype=np.float32)
        else:
            out = san("out", "array_1d_float")

            if len(out) != self.grain_len:
                raise ValueError(
                    "if provided, 'out' should be of size (inner_grain_len + "
                    "pad_len * 2) or (left_pad_len + padded_grain_len + "
                    "right_pad_len)"
                )

        out[:self.left_pad_len] = 0
        out[self.grain_len - self.right_pad_len:] = 0

        return out

    def _get_window(self):
        return self._inner_grain_info.get_hann_window(
            left_pad_len=self.left_pad_len, right_pad_len=self.right_pad_len,
            delay_audio_samples=self._delay_audio_samples_remainder
        )


class AddGrainsToAudio:
    __slots__ = [
        "_grain_ranges",
        "grain",
        "start_i", "interval_len", "num_of_iterations",
        "subtract",
        "audio"
    ]

    def __init__(
        self, grain, *,
        start_i, interval_len, num_of_iterations,
        subtract=False,
        audio
    ):
        (
            self.grain,
            self.start_i, self.interval_len, self.num_of_iterations,
            self.subtract,
            self.audio
        ) = sanitise_args(
            "grain",
            "start_i", "interval_len", "num_of_iterations",
            "subtract",
            "audio"
        )

        self._grain_ranges = _GrainRanges(
            start_i=start_i,
            interval_len=interval_len,
            num_of_iterations=num_of_iterations,
            audio_len=len(audio),
            grain_len=len(grain)
        )

    def __iter__(self):
        subiterators = list(self._get_subiterators())

        if len(subiterators) == 1:
            return subiterators[0]
        else:
            return chain(*subiterators)

    def _get_before_iterator(self, grain_range):
        def get_iterator(grain_range=grain_range):
            for _ in grain_range:
                yield

        return get_iterator()

    def _get_entering_iterator(self, grain_range):
        stop_indices = self._grain_ranges.get_stop_indices_from_grain_range(
            grain_range
        )

        if self.subtract:
            def get_iterator(
                stop_indices=stop_indices,
                grain=self.grain, audio=self.audio
            ):
                for stop_i in stop_indices:
                    audio[:stop_i] -= grain[-stop_i:]

                    yield
        else:
            def get_iterator(
                stop_indices=stop_indices,
                grain=self.grain, audio=self.audio
            ):
                for stop_i in stop_indices:
                    audio[:stop_i] += grain[-stop_i:]

                    yield

        return get_iterator()

    def _get_full_iterator(self, grain_range):
        start_indices = self._grain_ranges.get_start_indices_from_grain_range(
            grain_range
        )

        if self.subtract:
            def get_iterator(
                start_indices=start_indices,
                grain=self.grain, audio=self.audio, grain_len=len(self.grain)
            ):
                for start_i in start_indices:
                    audio[start_i:start_i + grain_len] -= grain

                    yield
        else:
            def get_iterator(
                start_indices=start_indices,
                grain=self.grain, audio=self.audio, grain_len=len(self.grain)
            ):
                for start_i in start_indices:
                    audio[start_i:start_i + grain_len] += grain

                    yield

        return get_iterator()

    # unoptimised edge case
    def _get_island_iterator(self, grain_range):
        for start_i in self._grain_ranges.get_start_indices_from_grain_range(
            grain_range
        ):
            grain_start_i = -start_i
            grain_stop_i = grain_start_i + len(self.audio)

            grain_island = self.grain[grain_start_i:grain_stop_i]

            if self.subtract:
                self.audio -= grain_island
            else:
                self.audio += grain_island

            yield

    def _get_exiting_iterator(self, grain_range):
        start_indices = self._grain_ranges.get_start_indices_from_grain_range(
            grain_range
        )

        if self.subtract:
            def get_iterator(
                start_indices=start_indices,
                grain=self.grain, audio=self.audio, audio_len=len(self.audio)
            ):
                for start_i in start_indices:
                    audio[start_i:] -= grain[:audio_len - start_i]

                    yield
        else:
            def get_iterator(
                start_indices=start_indices,
                grain=self.grain, audio=self.audio, audio_len=len(self.audio)
            ):
                for start_i in start_indices:
                    audio[start_i:] += grain[:audio_len - start_i]

                    yield

        return get_iterator()

    _get_after_iterator = _get_before_iterator

    def _get_subiterators(self):
        for name, grain_range in self._grain_ranges:
            bound_method = getattr(self, f"_get_{name}_iterator")

            yield bound_method(grain_range)
