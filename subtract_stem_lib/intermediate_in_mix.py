from fractions import Fraction

from .defaults import LOOKBEHIND_S, LOOKAHEAD_S


class _RunningConstants:
    def __init__(
        self, *,
        stem_audio, intermediate_audio, mix_audio,
        intermediate_to_stem_eq_profile,
        start_s, stop_s,
        fully_cover_all, centre,
        lookbehind_s, lookahead_s,
        delay_stem_s, delay_intermediate_s
    ):
        ...


class _RunningIterator:
    def __init__(self, constants):
        self._constants = constants

        self._stem_to_mix_eq_profiles = iter(GenerateRunningEqProfile(
            ...
        ))
        self._intermediate_spectra = iter(GenerateSpectra(
            audio=constants.stem_audio
        ))

        self._i = 0
        self._out_block = np.empty(constants.transform_len, dtype=np.float32)
        self._untrimmed = np.zeros(constants.untrimmed_len, dtype=np.float32)
        self._trimmed \
            = self._untrimmed[constants.margin_before:constants.margin_after]

    def __iter__(self):
        return self

    def __next__(self):
        if self._i == self._constants.num_of_total_iterations:
            raise StopIteration

        stem_to_mix_eq_profile = next(self._stem_to_mix_eq_profiles)
        intermediate_spectrum = next(self._intermediate_spectra)

        intermediate_spectrum \
            *= self._constants.intermediate_to_stem_eq_profile
        intermediate_spectrum *= stem_to_mix_eq_profile
        np.fft.ifft(intermediate_spectrum, out=self._out_block)

        copy_to_start_i = self._i * self._constants.interval_len
        copy_to_stop_i = copy_to_start_i + self._constants.transform_len
        self._untrimmed[copy_to_start_i:copy_to_stop_i] += self._out_block

        self._i += 1

        return self.trimmed


class GenerateSingleIntermediateInMix:
    ...


class GenerateRunningIntermediateInMix:
    def __init__(
        self, *,
        stem_audio, intermediate_audio, mix_audio,
        intermediate_to_stem_eq_profile,
        start_s=None, stop_s=None,
        centre=True,
        lookbehind_s=LOOKBEHIND_S, lookahead_s=LOOKAHEAD_S,
        delay_stem_s=Fraction(0), delay_intermediate_s=Fraction(0)
    ):
        self.constants = _RunningConstants(**sanitise_args({
            "stem_audio": stem_audio,
            "intermediate_audio": intermediate_audio,
            "mix_audio": mix_audio,
            "intermediate_to_stem_eq_profile": intermediate_to_stem_eq_profile,
            "start_s": start_s, "stop_s": stop_s,
            "centre": centre,
            "lookbehind_s": lookbehind_s, "lookahead_s": lookahead_s,
            "delay_stem_s": delay_stem_s,
            "delay_intermediate_s": delay_intermediate_s
        }))

    def __iter__(self):
        return _Iterator(self.constants)

    def run(self):
        for intermediate_in_mix in self:
            pass

        return intermediate_in_mix, start_sample
