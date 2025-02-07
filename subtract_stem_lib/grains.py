class AudioToGrains:
    def __init__(self):
        self.audio
        self.start_i
        self.interval_len
        self.num_of_iterations
        self.window
        self.out

        self._start_grain_stop_i = start_i + len(window)
        self._grain_ranges = dict(self._get_grain_ranges())

    def __iter__(self):
        return chain(*self._get_subiterators())

    def _get_grain_num(self, *, start_i=None, stop_i=None):
        if stop_i is None:
            return (start_i - self.start_i) // self.interval_len
        else:
            return (stop_i - self._start_grain_stop_i) // self.interval_len

    def _get_grain_start_i(self, grain_num):
        return self.start_i + grain_num * self.interval_len

    def _get_grain_stop_i(self, grain_num):
        return self._start_grain_stop_i + grain_num * self.interval_len

    def _get_start_indices_from_grain_range(self, grain_range):
        return range(
            self._get_grain_start_i(grain_range.start),
            self._get_grain_start_i(grain_range.stop),
            self.interval_len
        )

    def _get_stop_indices_from_grain_range(self, grain_range):
        return range(
            self._get_grain_stop_i(grain_range.start),
            self._get_grain_stop_i(grain_range.stop),
            self.interval_len
        )

    def _get_clamped_grain_range(self, start_grain_num, stop_grain_num):
        return range(
            min(max(start_grain_num, 0), self.num_of_iterations),
            min(max(stop_grain_num, 0), self.num_of_iterations)
        )

    def _get_draft_entering_grain_range(self):
        start_grain_stop_i \
            (self._start_grain_stop_i - 1) % self.interval_len + 1
        stop_grain_start_i = self.start_i % self.interval_len

        start_grain_num = self._get_grain_num(stop_i=start_grain_stop_i)
        stop_grain_num = self._get_grain_num(start_i=stop_grain_start_i)

        return self._get_clamped_grain_range(start_grain_num, stop_grain_num)

    def _get_draft_exiting_grain_range(self):
        start_grain_stop_i = (
            (self._start_grain_stop_i - len(self.audio) - 1)
            % self.interval_len
            + len(self.audio) + 1
        )
        stop_grain_start_i = (
            (self.start_i - len(self.audio))
            % self.interval_len
            + len(self.audio)
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
            yield "island", range(exiting.draft_start, entering_draft.stop)
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

    def _get_before_iterator(self, grain_range):
        out = self.out

        def iterator():
            out.fill(0)

            for _ in grain_range:
                yield 

        return iterator()

    def _get_entering_iterator(self, grain_range):
        stop_indices = _get_stop_indices_from_grain_range(grain_range)

        multiply = np.multiply
        audio = self.audio
        window = self.window
        out = self.out

        if grain_range.start == 0:
            view_to_zero = out[:-stop_indices.start]

            def iterator():
                view_to_zero.fill(0)

                for stop_i in stop_indices:
                    multiply(
                        audio[:stop_i],
                        window[-stop_i:],
                        out=out[-stop_i:]
                    )

                    yield
        else:
            def iterator():
                for stop_i in stop_indices:
                    multiply(
                        audio[:stop_i],
                        window[-stop_i:],
                        out=out[-stop_i:]
                    )

                    yield

        return iterator()

    def _get_full_iterator(self, grain_range):
        start_indices = self._get_start_indices_from_grain_range(grain_range)

        multiply = np.multiply
        audio = self.audio
        window = self.window
        grain_len = len(window)
        out = self.out

        def iterator():
            for start_i in start_indices:
                multiply(
                    audio[start_i:start_i + grain_len],
                    window,
                    out=out
                )

            yield

        return iterator()

    def _get_island_iterator(self, grain_range):
        # unoptimised edge case

        start_indices = _get_start_indices_from_grain_range(grain_range)

        for start_i in start_indices:
            stop_i = start_i + self.grain_len

            before_len = -start_i
            after_len = stop_i - len(self.audio)

            self.out[:before_len] = 0
            np.multiply(
                self.audio,
                self.window[before_len:-after_len],
                out=self.out
            )
            self.out[-after_len:] = 0

            yield

    def _get_exiting_iterator(self, grain_range):
        start_indices = self._get_start_indices_from_grain_range(grain_range)

        multiply = np.multiply
        audio = self.audio
        window = self.window
        out = self.out
        interval_len = self.interval_len

        prev_full_len = self.grain_len
        curr_full_len = self.audio_len - start_indices[0]

        def iterator():
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
    def __init__(
        self, audio, *,
        start_i, interval_len, num_of_iterations,
        grain_len
        self.window
        self.out)
