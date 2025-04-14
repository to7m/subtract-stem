from fractions import Fraction

from .defaults import INNER_GRAIN_LEN, MAX_ABS_RESULT
from ._sanitisation import sanitise_arg as san, sanitise_args
from ._sanitise_unique_arrays_of_shape import sanitise_unique_arrays_of_shape
from ._sanitise_hann_inner_grain_len_interval_len import (
    sanitise_hann_inner_grain_len_interval_len
)
from .audio_grains import AudioToHannGrains
from .transforms import GrainsToSpectraBuffer
from .eq_profiles import SpectraBuffersToEqProfile


class AudioPairToEqProfile:
    __slots__ = [
        "_stem_audio_to_grains", "_stem_grains_to_spectra_buffer",
        "_mix_audio_to_grains", "_mix_grains_to_spectra_buffer",
        "_spectra_buffers_to_eq_profile",
        "stem_audio", "mix_audio",
        "start_i", "interval_len", "num_of_iterations",
        "inner_grain_len",
        "delay_stem_samples", "max_abs_result", "ret_reciprocal_eq",
        "intermediate_a", "intermediate_b", "intermediate_c",
        "intermediate_d",
        "out",
        "calculate_eq_profile"
    ]

    def __init__(
        self, stem_audio, mix_audio, *,
        start_i, interval_len, num_of_iterations,
        inner_grain_len=INNER_GRAIN_LEN,
        delay_stem_samples=Fraction(0),
        max_abs_result=MAX_ABS_RESULT,
        ret_reciprocal_eq=False,
        intermediate_a=None,  # numpy.float32 of size grain_len???NEED TO UPDATE THIS BIT
        intermediate_b=None,  # numpy.complex64 Buffer of size grain_len
        intermediate_c=None,  # numpy.complex64 Buffer of size grain_len
        intermediate_d=None,  # bool of size grain_len
        out=None
    ):
        self.stem_audio, self.mix_audio, self.delay_stem_samples \
            = sanitise_args("stem_audio", "mix_audio", "delay_stem_samples")
        self.inner_grain_len, self.interval_len \
            = sanitise_hann_inner_grain_len_interval_len(
                  inner_grain_len, interval_len
              )

        (
            self.intermediate_a, self.intermediate_b, self.intermediate_c,
            self.intermediate_d,
            self.out
        ) = self._sanitise_intermediates_and_out(
            intermediate_a, intermediate_b, intermediate_c, intermediate_d,
            out
        )

        self._stem_audio_to_grains = AudioToHannGrains(
            stem_audio,
            start_i=start_i, interval_len=interval_len,
            num_of_iterations=num_of_iterations,
            grain_len=grain_len,
            delay_audio_samples=delay_stem_samples,
            out=self.intermediate_a
        )

        self.start_i, self.num_of_iterations = (
            self._stem_audio_to_grains.start_i,
            self._stem_audio_to_grains.num_of_iterations
        )

        self._stem_grains_to_spectra_buffer = GrainsToSpectraBuffer(
            self.intermediate_a, out=self.intermediate_b
        )
        self._mix_audio_to_grains = AudioToHannGrains(
            mix_audio,
            start_i=start_i, interval_len=interval_len,
            num_of_iterations=num_of_iterations,
            grain_len=grain_len,
            out=self.intermediate_a
        )
        self._mix_grains_to_spectra_buffer = GrainsToSpectraBuffer(
            self.intermediate_a, out=self.intermediate_c
        )

        self._spectra_buffers_to_eq_profile = SpectraBuffersToEqProfile(
            self.intermediate_b, self.intermediate_c,
            max_abs_result=max_abs_result,
            ret_reciprocal_eq=ret_reciprocal_eq,
            intermediate_a=self.intermediate_a,
            intermediate_b=self.intermediate_d,
            out=self.out
        )

        (
            self.max_abs_result, self.ret_reciprocal_eq,
            self.calculate_eq_profile
        ) = (
            self._spectra_buffers_to_eq_profile.max_abs_result,
            self._spectra_buffers_to_eq_profile.ret_reciprocal_eq,
            self._spectra_buffers_to_eq_profile.calculate_eq_profile
        )


    def __iter__(self):
        def get_iterator(
            num_of_iterations_range=range(self.num_of_iterations),
            iter_=zip(
                self._stem_audio_to_grains,
                self._stem_grains_to_spectra_buffer,
                self._mix_audio_to_grains,
                self._mix_grains_to_spectra_buffer,
                self._spectra_buffers_to_eq_profile
            )
        ):
            for _ in num_of_iterations_range:
                next(iter_)

                yield

        return get_iterator()

    def _sanitise_intermediates_and_out(
        self,
        intermediate_a, intermediate_b, intermediate_c, intermediate_d, out
    ):
        return sanitise_unique_arrays_of_shape(
            array_infos=[
                (intermediate_a, "intermediate_a", "float"),
                (intermediate_b, "intermediate_b", "complex"),
                (intermediate_c, "intermediate_c", "complex"),
                (intermediate_d, "intermediate_d", "bool"),
                (out, "out", "complex")
            ],
            reference_shape=(self.grain_len,),
            reference_name="'grain_len'"
        )
