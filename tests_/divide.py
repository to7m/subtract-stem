import subtract_stem_lib as ssl


def safe_divide():
    ssl.safe_divide(3, 7, max_abs_result=9)


def all_divide():
    safe_divide()
