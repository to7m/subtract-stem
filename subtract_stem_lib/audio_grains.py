from itertools import chain
from math import tau
import numpy as np

from .defaults import GRAIN_LEN
from ._sanitisation import sanitise_arg as san, sanitise_args
from ._sanitise_hann_grain_len_interval_len import (
    sanitise_hann_grain_len_interval_len
)


def get_hann_window(
    grain_len=GRAIN_LEN, *,
    interval_len=None, delay_audio_samples=0.0
):
    _, interval_len \
        = sanitise_hann_grain_len_interval_len(grain_len, interval_len)
    delay_audio_samples = san("delay_audio_samples")

    overlap = grain_len // interval_len

    # arr = phase
    arr = np.arange(grain_len, dtype=np.float32)
    arr += delay_audio_samples
    arr *= tau / grain_len

    # arr = window
    np.cos(arr, out=arr)
    np.subtract(1, arr, out=arr)
    arr *= (1 / overlap)

    return arr


class _GrainRanges:
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
        def iterator(fill_out=self.out.fill, grain_range=grain_range):
            fill_out(0)

            for i in grain_range:
                yield

        return iterator()

    def _get_entering_iterator(self, grain_range):
        stop_indices = self._grain_ranges.get_stop_indices_from_grain_range(
            grain_range
        )

        if grain_range.start == 0:
            view_to_zero = self.out[:-stop_indices.start]

            def iterator(
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
            def iterator(
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

        return iterator()

    def _get_full_iterator(self, grain_range):
        start_indices = self._grain_ranges.get_start_indices_from_grain_range(
            grain_range
        )

        def iterator(
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

        return iterator()

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

        def iterator(
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

        return iterator()

    # the out.fill(0) could be a tiny bit more optimised
    _get_after_iterator = _get_before_iterator

    def _get_subiterators(self):
        for name, grain_range in self._grain_ranges:
            bound_method = getattr(self, f"_get_{name}_iterator")

            yield bound_method(grain_range)


class AudioToHannGrains:
    __slots__ = [
        "_audio_to_grains", "_delay_audio_samples_remainder",
        "audio",
        "start_i", "interval_len", "num_of_iterations",
        "grain_len",
        "delay_audio_samples",
        "out"
    ]

    def __init__(
        self, audio, *,
        start_i, interval_len, num_of_iterations,
        grain_len=GRAIN_LEN,
        delay_audio_samples=0.0,
        out=None
    ):
        self.start_i = san("start_i")
        self.grain_len, self.interval_len \
            = sanitise_hann_grain_len_interval_len(grain_len, interval_len)
        self.delay_audio_samples = san("delay_audio_samples")
        self.out = self._sanitise_out(out)

        self._delay_audio_samples_remainder = self.delay_audio_samples % 1
        delay_audio_samples_whole = int(
            self.delay_audio_samples - self._delay_audio_samples_remainder)
        

        self._audio_to_grains = AudioToGrains(
            audio,
            start_i=start_i - delay_audio_samples_whole,
            interval_len=interval_len,
            num_of_iterations=num_of_iterations,
            window=self._get_window(),
            out=self.out
        )

        self.audio = audio
        self.interval_len = interval_len
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
                    "'out' should be the same size as 'grain_len'"
                )

        return out

    def _get_window(self):
        return get_hann_window(
            self.grain_len,
            interval_len=self.interval_len,
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
        def iterator(grain_range=grain_range):
            for _ in grain_range:
                yield

        return iterator()

    def _get_entering_iterator(self, grain_range):
        stop_indices = self._grain_ranges.get_stop_indices_from_grain_range(
            grain_range
        )

        if self.subtract:
            def iterator(
                stop_indices=stop_indices,
                grain=self.grain, audio=self.audio
            ):
                for stop_i in stop_indices:
                    audio[:stop_i] -= grain[-stop_i:]

                    yield
        else:
            def iterator(
                stop_indices=stop_indices,
                grain=self.grain, audio=self.audio
            ):
                for stop_i in stop_indices:
                    audio[:stop_i] += grain[-stop_i:]

                    yield

        return iterator()

    def _get_full_iterator(self, grain_range):
        start_indices = self._grain_ranges.get_start_indices_from_grain_range(
            grain_range
        )

        if self.subtract:
            def iterator(
                start_indices=start_indices,
                grain=self.grain, audio=self.audio, grain_len=len(self.grain)
            ):
                for start_i in start_indices:
                    audio[start_i:start_i + grain_len] -= grain

                    yield
        else:
            def iterator(
                start_indices=start_indices,
                grain=self.grain, audio=self.audio, grain_len=len(self.grain)
            ):
                for start_i in start_indices:
                    audio[start_i:start_i + grain_len] += grain

                    yield

        return iterator()

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
            def iterator(
                start_indices=start_indices,
                grain=self.grain, audio=self.audio, audio_len=len(self.audio)
            ):
                for start_i in start_indices:
                    audio[start_i:] -= grain[:audio_len - start_i]

                    yield
        else:
            def iterator(
                start_indices=start_indices,
                grain=self.grain, audio=self.audio, audio_len=len(self.audio)
            ):
                for start_i in start_indices:
                    audio[start_i:] += grain[:audio_len - start_i]

                    yield

        return iterator()

    _get_after_iterator = _get_before_iterator

    def _get_subiterators(self):
        for name, grain_range in self._grain_ranges:
            bound_method = getattr(self, f"_get_{name}_iterator")

            yield bound_method(grain_range)
