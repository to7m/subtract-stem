from fractions import Fraction


sanitisers = {}


def _get_add_sanitiser_for_name(name):
    def add_sanitiser(sanitiser_function):
        sanitisers[name] = sanitiser_function

        return sanitiser_function

    return add_sanitiser


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


@_get_add_sanitiser_for_name("lookbehind_s")
def sanitise_lookbehind_s(lookbehind_s):
    lookbehind_s = _parse_timestamp(lookbehind_s)

    if lookbehind_s < 0:
        raise ValueError("lookbehind_s should not be less than 0")

    return lookbehind_s


@_get_add_sanitiser_for_name("lookahead_s")
def sanitise_lookahead_s(lookahead_s):
    lookahead_s = _parse_timestamp(lookahead_s)

    if lookahead_s < 0:
        raise ValueError("lookahead_s should not be less than 0")

    return lookahead_s


@_get_add_sanitiser_for_name("sample_rate")
def sanitise_sample_rate(sample_rate):
    sample_rate = Fraction(sample_rate)

    if sample_rate <= 0:
        raise ValueError("sample_rate should be greater than 0")

    return sample_rate


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
