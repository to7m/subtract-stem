import numpy as np

from .buffer import Buffer


class SpectrumPairsToEqProfiles:
    __slots__ = ["stem_spectrum", "mix_spectrum", "out"]

    def __iter__(self):
        match self.stem_spectrum, self.mix_spectrum:
            case np.ndarray(), np.ndarray():
                def iterator():
                    for i in lookbehind_range:
                        next(ataabtrnfatbaa_iter)

                        if (cumsum_i := i % cumsum_len):
                            abs_stem_cumsum[cumsum_i] = 



                    for i in main_count:
                        ...
            case np.ndarray(), Buffer():
                ...
            case Buffer(), np.ndarray():
                ...
            case Buffer(), Buffer():
                ...
            case _:
                raise RuntimeError("this should never be reached")


        return iterator()
