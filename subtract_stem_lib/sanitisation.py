from pathlib import Path
from fractions import Fraction
import numpy as np

from .to7m_exec import func_from_str


def _logger_ignore(**_):
    return _logger_ignore


def _logger_print(**kwargs):
    print(kwargs)

    return _logger_print


_sanitisers = {}


def _get_add_sanitiser_for_name(name):
    def add_sanitiser(sanitiser_function):
        _sanitisers[name] = sanitiser_function

        return sanitiser_function

    return add_sanitiser


def _make_sanitise_int(name, *, min_=None):
    if min_ is None:
        min_action = ""
    else:
        min_action = f"""
            if {name} < {min_}:
                raise ValueError("{name} should be at least {min_}")
        """

    sanitise_int_ge_1 = func_from_str(
        f"""
        def sanitise_{name}({name}):
            {name} = int({name})
            {min_action}
            return {name}
        """
    )

    decorator = _get_add_sanitiser_for_name(name)

    return decorator(sanitise_int_ge_1)


def _make_sanitise_mono_audio(audio_type):
    sanitise_mono_audio = func_from_str(
        f"""
        def sanitise_{audio_type}_audio({audio_type}_audio):
            if type({audio_type}_audio) is not np.ndarray:
                raise TypeError(
                    "{audio_type}_audio should be a numpy.ndarray"
                )

            if len({audio_type}_audio.shape) != 1:
                raise ValueError(
                    "{audio_type}_audio should be 1-D and therefore contain "
                    "1 channel"
                )

            return {audio_type}_audio
        """,
        globals_={"np": np}
    )

    decorator = _get_add_sanitiser_for_name(f"{audio_type}_audio")

    return decorator(sanitise_mono_audio)


def _make_sanitise_timestamp(name, *, allow_none=False, range_="any"):
    if allow_none:
        none_action = "return None"
    else:
        none_action = f"raise TypeError('{name} must not be None')"

    if range_ == "any":
        range_action = ""
    elif range_ == ">=0":
        range_action = (
            f"""
            if ts < 0:
                raise ValueError("{name} should not be less than 0")
            """
        )
    elif range_ == ">0":
        range_action = (
            f"""
            if ts <= 0:
                raise ValueError("{name} should be greater than 0")
            """
        )

    sanitise_timestamp = func_from_str(
        f"""
        def sanitise_{name}({name}):
            if {name} is None:
                {none_action}

            if type({name}) is str:
                ts = Fraction(0)
                for unit_str in {name}.split(':'):
                    ts *= 60
                    ts += Fraction(unit_str)
            else:
                ts = Fraction({name})
            {range_action}
            return ts
        """,
        globals_={"Fraction": Fraction}
    )

    decorator = _get_add_sanitiser_for_name(name)

    return decorator(sanitise_timestamp)


sanitise_additional_iterations_before \
    = _make_sanitise_int("additional_iterations_before", min_=0)
sanitise_additional_iterations_after \
    = _make_sanitise_int("additional_iterations_after", min_=0)

sanitise_num_of_retained = _make_sanitise_int("num_of_retained", min_=1)
sanitise_stem_num_of_retained \
    = _make_sanitise_int("stem_num_of_retained", min_=1)
sanitise_mix_num_of_retained \
    = _make_sanitise_int("mix_num_of_retained", min_=1)

sanitise_mono_audio = _make_sanitise_mono_audio("mono")
sanitise_intermediate_audio = _make_sanitise_mono_audio("intermediate")
sanitise_mix_audio = _make_sanitise_mono_audio("mix")
sanitise_stem_audio = _make_sanitise_mono_audio("stem")

sanitise_start_val = _make_sanitise_timestamp("start_val")
sanitise_start_add = _make_sanitise_timestamp("start_add")
sanitise_min_diff = _make_sanitise_timestamp("min_diff", range_=">0")
sanitise_min_diff_s = _make_sanitise_timestamp("min_diff_s", range_=">0")

sanitise_lookahead_s = _make_sanitise_timestamp("lookahead_s", range_=">=0")
sanitise_lookbehind_s = _make_sanitise_timestamp("lookbehind_s", range_=">=0")

sanitise_delay_audio_s = _make_sanitise_timestamp("delay_audio_s")
sanitise_delay_stem_s = _make_sanitise_timestamp("delay_stem_s")
sanitise_delay_intermediate_s \
    = _make_sanitise_timestamp("delay_intermediate_s")
sanitise_delay_stem_s_start_val \
    = _make_sanitise_timestamp("delay_stem_s_start_val")
sanitise_delay_stem_s_start_add \
    = _make_sanitise_timestamp("delay_stem_s_start_add")
sanitise_start_s = _make_sanitise_timestamp("start_s")
sanitise_stop_s = _make_sanitise_timestamp("stop_s", allow_none=True)


_get_add_sanitiser_for_name("aim_lowest")(bool)


@_get_add_sanitiser_for_name("logger")
def sanitise_logger(logger):
    if callable(logger):
        return logger
    elif logger:
        return _logger_print
    else:
        return _logger_ignore


@_get_add_sanitiser_for_name("max_amplification")
def sanitise_max_amplification(max_amplification):
    max_amplification = float(max_amplification)

    if max_amplification <= 0:
        raise ValueError("max_amplification should be greater than 0")

    return max_amplification


@_get_add_sanitiser_for_name("path")
def sanitise_path(path):
    return Path(path)


@_get_add_sanitiser_for_name("sample_rate")
def sanitise_sample_rate(sample_rate):
    sample_rate = Fraction(sample_rate)

    if sample_rate <= 0:
        raise ValueError("sample_rate should be greater than 0")

    return sample_rate


@_get_add_sanitiser_for_name("scoring_function")
def sanitise_scoring_function(scoring_function):
    if callable(scoring_function):
        return scoring_function
    else:
        raise TypeError("scoring_function should be a callable")


@_get_add_sanitiser_for_name("side_winner_mul")
def sanitise_side_winner_mul(side_winner_mul):
    side_winner_mul = Fraction(side_winner_mul)

    if side_winner_mul <= 1:
        raise ValueError("side_winner_mul should be greater than 1")

    return side_winner_mul


@_get_add_sanitiser_for_name("transform_len")
def sanitise_transform_len(transform_len):
    transform_len = int(transform_len)

    if transform_len < 2:
        raise ValueError("transform_len should not be less than 2")

    if transform_len % 2 != 0:
        raise ValueError("transform_len should be divisible by 2")

    return transform_len


def sanitise_args(args_dict):
    if type(args_dict) is not dict:
        raise TypeError("args_dict should be a dict")

    sanitised_args = {}
    for key, val in args_dict.items():
        if key in _sanitisers:
            sanitised_args[key] = _sanitisers[key](val)
        else:
            raise KeyError(f"could not sanitise argument ‘{key}’")

    return sanitised_args
