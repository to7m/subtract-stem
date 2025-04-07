def sanitise_pad_lens(self, pad_len, left_pad_len, right_pad_len):
    if pad_len is None:
        yield san("left_pad_len")
        yield san("right_pad_len")
    else:
        if None in (left_pad_len, right_pad_len):
            raise TypeError(
                "if 'pad_len' is provided, neither 'left_pad_len' nor "
                "'right_pad_len' should be provided"
            )

        yield san("pad_len")
        yield pad_len
