from .._sanitisation import sanitise as san


class InterpolateMissing:
    __slots__ = ["a", "is_safe", "out"]

    def __init__(self, a, *, is_safe, out=None):
        self.a = san("a", "array_1d_complex")
        self.is_safe = self._sanitise_is_safe(is_safe)
        self.out = self._sanitise_out(out)

    def __iter__(self):
        if self.out is self.a:
            def get_iterator(
                get_all_is_safe=self.is_safe.all,
                routine=self._routine
            ):
                while True:
                    if not get_all_is_safe():
                        routine()

                    yield
        else:
            def get_iterator(
                a=self.a, out=self.out,
                get_all_is_safe=self.is_safe.all,
                routine=self._routine
            ):
                while True:
                    out[:] = a

                    if not get_all_is_safe():
                        routine()

                    yield

        return get_iterator()

    def _sanitise_is_safe(self, is_safe):
        san("is_safe")

        if is_safe.shape != self.a.shape:
            raise ValueError("'a' and 'is_safe' should have the same shape")

        return is_safe

    def _sanitise_out(self, out):
        if out is None:
            out = np.empty(self.a.shape, dtype=np.complex64)
        else:
            out = san("out", "array_1d_complex")

            if out.shape != self.a.shape:
                raise ValueError(
                    "'out' should have the same shape as 'a' and 'is_safe'"
                )

        return out

    def _interpolate_segment(
        self, *, last_present_before, first_present_after
    ):
        out = self.out

        start_val = out[last_present_before]
        stop_val = out[first_present_after]

        divisions = first_present_after - last_present_before
        gradient = (stop_val - start_val) / divisions

        for i in range(1, divisions):
            out[last_present_before + i] = start_val + i * gradient

    def _routine(self):
        out = self.out

        if not self.is_safe.any():
            out.fill(0)

            return

        is_present_iter = enumerate(self.is_safe)

        if not next(is_present_iter)[1]:
            for i, pres in is_present_iter:
                if pres:
                    out[:i] = out[i]

                    break

        first_missing = None
        for i, pres in is_present_iter:
            if not pres:
                first_missing = i

                for i, pres in is_present_iter:
                    if pres:
                        self._interpolate_segment(
                            last_present_before=first_missing - 1,
                            first_present_after=i
                        )

                        first_missing = None

                        break

        if first_missing is not None:
            out[first_missing:] = out[first_missing - 1]
