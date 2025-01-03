from pathlib import Path
from fractions import Fraction
import numpy as np

from .to7m_exec import func_from_str


def _logger_ignore(**_):
    return _logger_ignore


def _logger_print(**kwargs):
    print(kwargs)

    return _logger_print


def _parse_timestamp(ts):
    if ts is None:
        raise TypeError("None is not a valid timestamp")
    if type(ts) is str:
        seconds = Fraction(0)
        for unit_str in ts.split(':'):
            seconds *= 60
            seconds += Fraction(unit_str)

        return seconds
    else:
        return Fraction(ts)


sanitisers = {}


def _get_add_sanitiser_for_name(name):
    def add_sanitiser(sanitiser_function):
        sanitisers[name] = sanitiser_function

        return sanitiser_function

    return add_sanitiser


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
                    "{audio_type}_audio should contain 1 channel"
                )

            return {audio_type}_audio
        """,
        globals_={"np": np}
    )

    decorator = _get_add_sanitiser_for_name(f"{audio_type}_audio")

    return decorator(sanitise_mono_audio)


def _make_sanitise_fraction(name):
    sanitise_fraction = func_from_str(
        f"""
        def sanitise_{name}({name}):
            return Fraction({name})
        """,
        globals_={"Fraction": Fraction}
    )

    decorator = _get_add_sanitiser_for_name(name)

    return decorator(sanitise_fraction)


def _make_sanitise_lookbehindahead_s(direction):
    sanitise_lookbehindahead_s = func_from_str(
        f"""
        def sanitise_look{direction}_s(look{direction}_s):
            look{direction}_s = _parse_timestamp(look{direction}_s)

            if look{direction}_s < 0:
                raise ValueError(
                    "look{direction}_s should not be less than 0"
                )

            return look{direction}_s
        """,
        globals_={"_parse_timestamp": _parse_timestamp}
    )

    decorator = _get_add_sanitiser_for_name(f"look{direction}_s")

    return decorator(sanitise_lookbehindahead_s)


def _make_sanitise_timestamp(name):
    sanitise_timestamp = func_from_str(
        f"""
        def sanitise_{name}({name}):
            if {name} is None:
                return None
            else:
                return _parse_timestamp({name})
        """,
        globals_={"_parse_timestamp": _parse_timestamp}
    )

    decorator = _get_add_sanitiser_for_name(name)

    return decorator(sanitise_timestamp)


sanitise_mono_audio = _make_sanitise_mono_audio("mono")
sanitise_intermediate_audio = _make_sanitise_mono_audio("intermediate")
sanitise_mix_audio = _make_sanitise_mono_audio("mix")
sanitise_stem_audio = _make_sanitise_mono_audio("stem")

sanitise_start_val = _make_sanitise_fraction("start_val")
sanitise_start_add = _make_sanitise_fraction("start_add")
sanitise_min_diff = _make_sanitise_fraction("min_diff")
sanitise_side_winner_mul = _make_sanitise_fraction("side_winner_mul")

sanitise_lookahead_s = _make_sanitise_lookbehindahead_s("ahead")
sanitise_lookahead_s = _make_sanitise_lookbehindahead_s("behind")

sanitise_delay_stem_s_start_val \
    = _make_sanitise_timestamp("delay_stem_s_start_val")
sanitise_delay_stem_s_start_add \
    = _make_sanitise_timestamp("delay_stem_s_start_add")
sanitise_start_s = _make_sanitise_timestamp("start_s")
sanitise_stop_s = _make_sanitise_timestamp("stop_s")


@_get_add_sanitiser_for_name("logger")
def sanitise_logger(logger):
    if callable(logger):
        return logger
    elif logger:
        return _logger_print
    else:
        return _logger_ignore


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
        if key in sanitisers:
            sanitised_args[key] = sanitisers[key](val)
        else:
            raise KeyError(f"could not sanitise argument ‘{key}’")

    return sanitised_args
