from .defaults import OVERLAP
from ._sanitisation import sanitise_arg as san


def sanitise_hann_grain_len_interval_len(grain_len, interval_len):
    san("grain_len")

    if interval_len is None:
        interval_len, remainder = divmod(grain_len, OVERLAP)

        if remainder != 0:
            raise ValueError(
                f"'grain_len' ({grain_len}) is not divisible by default "
                f"overlap ({OVERLAP}); either change 'grain_len' or provide "
                "'interval_len'"
            )
    else:
        san("interval_len")

        if interval_len >= grain_len:
            raise ValueError("'interval_len' should be less than grain_len")

        if grain_len % interval_len != 0:
            raise ValueError(
                f"'grain_len' ({grain_len}) should be divisible by "
                f"'interval_len' ({interval_len})"
            )

    return grain_len, interval_len
