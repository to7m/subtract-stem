import subtract_stem_lib as ssl


def test_hone_in():
    def scoring_function(x):
        return -((x - 98.7654321) ** 2)

    for results in ssl.hone_in(scoring_function, highest_wins=True):
        pass

    if results["winning"]["val"] != 98.7654321:
        raise Exception("test failed")

    for results in ssl.hone_in(
        scoring_function, highest_wins=True, min_diff=0.001
    ):
        pass

    if abs(98.7654321 - results["winning"]["val"]) > 0.001:
        raise Exception("test failed")
