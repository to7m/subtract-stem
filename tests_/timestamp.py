import subtract_stem_lib as ssl


def test_timestamp():
    timestamps_and_strs = [
        (ssl.Timestamp.from_total_seconds(-7.25), "-(7+1/4s)"),
        (
            ssl.Timestamp.from_total_seconds(
                100, reference_point="NEW_INTERMEDIATE_END"
            ),
            "NEW_INTERMEDIATE_END+1m40s"
        ),
        (ssl.Timestamp.from_total_seconds(10000.5), "2h46m40+1/2s"),
        (ssl.Timestamp.from_str("7:6:5.4"), "7h6m5+2/5s"),
        (
            ssl.Timestamp.from_str("DELAY_STEM - (3h1_7m4+1/19s)"),
            "DELAY_STEM-(3h17m4+1/19s)"
        ),
        (ssl.Timestamp.from_str("OLD_STEM_END"), "OLD_STEM_END"),
        (ssl.Timestamp.from_str("-(3m4s)"), "-3m4s"),
        (ssl.Timestamp.from_str("-(3:4)"), "-3m4s")
    ]

    for timestamp, str_ in timestamps_and_strs:
        if str(timestamp) != str_:
            raise Exception("test_failed")
