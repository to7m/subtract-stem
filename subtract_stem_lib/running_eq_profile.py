from .math import ataabtrnfatbaa


class _Constants:
    ...


class _Generator:
    def __init__(self, constants):
        self.constants = constants

        self.curr_callable = self._process_before

    def __iter__(self):
        for transforms_pair_i in self.constants.transforms_before_range:
            stem_bins, mix_bins = next(self.bins_pairs_iter)

        for transforms_pair_i in self.constants.transforms_main_range:
            stem_bins, mix_bins = next(self.bins_pairs_iter)


class GenerateRunningEqProfile:
    def __init__(self):
        self.constants = _Constants()

    def __iter__(self):
        yield from _Generator(self.constants)
