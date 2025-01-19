from itertools import repeat

from .math import safe_divide__cc
from .spectra import GenerateSpectra, GenerateStemAndMixSpectra


class _Constants:
    def __init__(
        self, *,
        intermediate_spectra=None,
        stem_and_intermediate_spectra=None,
        intermediate_and_mix_spectra=None,
        intermediate_to_mix_eq_profiles=None,
        stem_to_intermediate_reciprocal_eq_profiles=None,
        stem_to_intermediate_eq_profiles=None,
        stem_to_mix_eq_profiles=None
    ):
        self._nums_of_main_iterations = set()
        self._transform_lens = set()
        self._iterables = []
        self._resources = {}
        self._yields_len = 0
        self._static_eq_profiles = {}

        self._add_intermediate_spectra_to_resources(
            intermediate_spectra
        )
        self._add_stem_and_mix_spectra_to_resources(
            stem_and_intermediate_spectra,
            arg_name="stem_and_intermediate_spectra",
            intermediate_spectra_yields_i=1
        )
        self._add_stem_and_mix_spectra_to_resources(
            intermediate_and_mix_spectra,
            arg_name="intermediate_and_mix_spectra",
            intermediate_spectra_yields_i=0
        )
        self._add_eq_profiles_to_resources(
            intermediate_to_mix_eq_profiles,
            arg_name="intermediate_to_mix_eq_profiles",
            from_="intermediate", to="mix", intermediate_spectra_yields_i=1
        )
        self._add_eq_profiles_to_resources(
            stem_to_intermediate_reciprocal_eq_profiles,
            arg_name="stem_to_intermediate_reciprocal_eq_profiles",
            from_="intermediate", to="stem", intermediate_spectra_yields_i=2

        )
        self._add_eq_profiles_to_resources(
            stem_to_intermediate_eq_profiles,
            arg_name="stem_to_intermediate_eq_profiles",
            from_="stem", to="intermediate", intermediate_spectra_yields_i=2

        )
        self._add_eq_profiles_to_resources(
            stem_to_mix_eq_profiles,
            arg_name="stem_to_mix_eq_profiles",
            from_="stem", to="mix"
        )

        self._ensure_intermediate_to_mix_eq_profiles()
        self._ensure_intermediate_spectra()

    def _add_intermediate_spectra_to_resources(self, x):
        if x is None:
            return
        elif isinstance(x, GenerateSpectra):
            self._nums_of_main_iterations.add(x.num_of_iterations)
            self._transform_lens.add(x.transform_len)
            self._iterables.append(x)
            self._resources["intermediate_spectra"] = self._yields_len
            self._yields_len += 1
        else:
            raise TypeError(
                "if provided, intermediate_spectra should be a "
                "GenerateSpectra instance"
            )

    def _add_stem_and_mix_spectra_to_resources(
        self, x, *, arg_name, intermediate_spectra_yields_i
    ):
        if x is None:
            return
        elif isinstance(x, StemAndMixSpectra):
            self._nums_of_main_iterations.add(x.num_of_iterations)
            self._transform_lens.add(x.transform_len)
            self._iterables.append(x)
            self._resources["intermediate_spectra"] \
                = self._yields + intermediate_spectra_yields_i
            self._yields_len += 2
        else:
            raise TypeError(
                f"if provided, {arg_name} should be a "
                "GenerateStemAndMixSpectra instance"
            )

    def _add_eq_profiles_to_resources(
        self, x, *, arg_name, from_, to, intermediate_spectra_yields_i=None
    ):
        if x is None:
            return
        elif isinstance(x, GenerateRunningEqProfile):
            self._nums_of_main_iterations.add(x.num_of_main_iterations)
            self._transform_lens.add(x.transform_len)
            self._iterables.append(x)
            self._resources[f"{from_}_to_{to}_eq_profiles"] = self._yields_len

            if intermediate_spectra_yields_i is not None:
                self._resources["intermediate_spectra"] \
                    = self._yields_len + intermediate_spectra_yields_i

            self._yields_len += 3
        elif isinstance(x, np.ndarray):
            if len(x.shape) != 1:
                raise ValueError(
                    f"if provided as a numpy.ndarray, {arg_name} should be "
                    "1-D"
                )

            self._transform_lens.add(len(x))
            self._iterables.append(repeat(x))
            self._resources[f"{from_}_to_{to}_eq_profiles"] = self._yields_len
            self._yields_len += 1
            self._static_eq_profiles[f"{from_}_to_{to}"] = x
        else:
            raise TypeError(
                f"if provided, {arg_name} should be a "
                "GenerateRunningEqProfile instance or a numpy.ndarray"
            )

    +...
    def _make_and_add_stem_to_mix_eq_profiles(self):
        ...

    +...
    def _make_and_add_intermediate_to_stem_eq_profiles(self):
        ...

    def _try_make_and_add_static_intermediate_to_mix_eq_profile(self):
        if "stem_to_mix" not in self._static_eq_profiles:
            return

        if "intermediate_to_stem" in self._static_eq_profiles:
            static_intermediate_to_mix_eq_profile = (
                self._static_eq_profiles["intermediate_to_stem"]
                * self._static_eq_profiles["stem_to_mix"]
            )
        elif "stem_to_intermediate" in self._static_eq_profiles:
            static_intermediate_to_mix_eq_profile = safe_divide__cc(
                self._static_eq_profiles["stem_to_mix"],
                self._static_eq_profiles["stem_to_intermediate"]
            )
        else:
            return

        self._add_eq_profiles_to_resources(
            static_intermediate_to_mix_eq_profile,
            arg_name="intermediate_to_mix_eq_profiles",
            from_="intermediate", to="mix"
        )

    def _ensure_intermediate_to_mix_eq_profiles(self):
        if "intermediate_to_mix_eq_profiles" in self._resources:
            return

        if "stem_to_mix_eq_profiles" not in self._resources:
            self._make_and_add_stem_to_mix_eq_profiles()

        if (
            "intermediate_to_stem_eq_profiles" not in self._resources
            and "stem_to_intermediate_eq_profiles" not in self._resources
        ):
            self._make_and_add_intermediate_to_stem_eq_profiles()

        self._try_make_and_add_static_intermediate_to_mix_eq_profile()

    def _ensure_intermediate_spectra(self):
        if "intermediate_spectra" in self._resources:
            return
        elif 

    def _get_resources_for_compound_eq(self):
        if "intermediate_to_stem_eq_profiles" in self._resources:
            mul_or_div = np.multiply

            yield self._resources["intermediate_to_stem_eq_profiles"]
        else:
            max_abs_val = self._max_abs_val
            intermediate_a = np.empty(self._transform_len, dtype=np.float32)
            intermediate_b = np.empty(self._transform_len, dtype=np.float32)
            intermediate_c = np.empty(self._transform_len, dtype=bool)
            intermediate_d = np.empty(self._transform_len, dtype=bool)

            def mul_or_div(a, b, *, out):
                return safe_divide_cc(
                    a, b,
                    intermediate_a=intermediate_a,
                    intermediate_b=intermediate_b,
                    intermediate_c=intermediate_c,
                    intermediate_d=intermediate_d,
                    out=out
                )

            yield self._resources["stem_to_intermediate_eq_profiles"]

        yield self._resources["stem_to_mix_eq_profiles"]

        yield mul_or_div

    def make_get_intermediate_in_mix_grain(self):
        intermediate_spectum_yields_i \
            = self._resources["intermediate_spectra"]

        if "intermediate_to_mix_eq_profiles" in self._resources:
            intermediate_to_mix_eq_profile_yields_i \
                = self._resources["intermediate_to_mix_eq_profiles"]

            def get_intermediate_in_mix_grain(*, yields, out):
                # intermediate spectrum
                a = yields[intermediate_spectrum_yields_i]

                # intermediate to mix EQ profile
                b = yields[intermediate_to_mix_eq_profile_yields_i]

                # intermediate in mix spectrum
                np.multiply(a, b, out=out)

                # intermediate in mix grain
                np.fft.ifft(out, out=a)

                return out
        else:
            (
                intermediate_to_stem_eq_profile_yields_i,
                stem_to_mix_eq_profile_yields_i,
                mul_or_div
            ) = self._get_resources_for_compound_eq()

            def get_intermediate_in_mix_grain(*, yields, out):
                # intermediate spectrum
                a = yields[intermediate_spectrum_yields_i]

                # intermediate to stem (or possibly other way) EQ profile
                b = yields[intermediate_to_stem_eq_profile_yields_i]

                # stem to mix EQ profile
                c = yields[stem_to_mix_eq_profile_yields_i]

                # intermediate to mix EQ profile
                mul_or_div(c, b, out=out)

                # intermediate in mix spectrum
                out *= a

                # intermediate in mix grain
                np.fft.ifft(out, out=out)

                return out

        return get_intermediate_in_mix_grain


class _Iterator:
    def __init__(self):
        ...

    def __iter__(self):
        return self

    def __next__(self):
        if self._i == self._constants.num_of_iterations:
            raise StopIteration

        for yields in self._consolidated_resources_iter:
            i0, i1 = self._constants.intermediate_spectrum_coords
            intermediate_spectrum = yields[i0][i1]

            intermediate_to_mix_eq \
                = self._constants.get_intermediate_to_mix_eq(
                      yields=yields,
                      intermediate_arrays=self._intermediate_arrays,
                )

        self._common_routine()

        intermediate_spectrum = next(self._intermediate_spectra_iter)
        intermediate_to_mix_eq_profile \
            = next(self._intermediate_to_mix_eq_profile_iter)
        intermediate_spectrum *= intermediate_to_mix_eq_profile
        np.fft.ifft(
            intermediate_spectrum, out=self._intermediate_in_mix_grain__c
        )

        self._i += 1
        self._log_main_progress()

        return self._intermediate_in_mix_grain__c.real


class GenerateIntermediateInMixGrains:
    def __iter__(self):
        if
        return _Iterator(self._constants)
