from .defaults import OVERLAP
from ._sanitisation import sanitise_arg as san


def sanitise_hann_inner_grain_len_interval_len(inner_grain_len, interval_len):
    san("inner_grain_len")

    if interval_len is None:
        interval_len, remainder = divmod(inner_grain_len, OVERLAP)

        if remainder != 0:
            raise ValueError(
                f"'inner_grain_len' ({inner_grain_len}) is not divisible by "
                f"default overlap ({OVERLAP}); either change "
                "'inner_grain_len' or provide 'interval_len'"
            )
    else:
        san("interval_len")

        if interval_len >= inner_grain_len:
            raise ValueError(
                "'interval_len' should be less than inner_grain_len"
            )

        if inner_grain_len % interval_len != 0:
            raise ValueError(
                f"'inner_grain_len' ({inner_grain_len}) should be divisible "
                f"by 'interval_len' ({interval_len})"
            )

    return inner_grain_len, interval_len
