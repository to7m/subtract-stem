from fractions import Fraction

from .sanitisation import sanitise_args


DEFAULT_START_ADD = Fraction(1)
DEFAULT_SIDE_WINNER_MUL = Fraction(3)
DEFAULT_MIN_DIFF = Fraction(1, 1_000_000_000)


def hone_in_high(
    scoring_function, *,
    start_val=Fraction(0), start_add=DEFAULT_START_ADD,
    min_diff=DEFAULT_MIN_DIFF, side_winner_mul=DEFAULT_SIDE_WINNER_MUL,
    logger=None
):
    (
        scoring_function,
        start_val, start_add,
        min_diff, side_winner_mul,
        logger
    ) = sanitise_args({
        "scoring_function": scoring_function,
        "start_val": start_val, "start_add": start_add,
        "min_diff": min_diff, "side_winner_mul": side_winner_mul,
        "logger": logger
    }).values()

    val_a = start_val
    val_b = start_val + start_add
    scoring_function_logger = logger(val_being_scored=val_a)
    score_a = scoring_function(val_a, logger=scoring_function_logger)
    scoring_function_logger = logger(val_being_scored=val_b)
    score_b = scoring_function(val_b, logger=scoring_function_logger)

    if score_b > score_a:
        val_c = val_b + (val_b - val_a) * side_winner_mul
    else:
        val_c = val_a + (val_a - val_b) * side_winner_mul

    logger(val_being_scored=val_c)
    score_c = scoring_function(val_c, logger=scoring_function_logger)

    while True:
        (val_a, score_a), (val_b, score_b), (val_c, score_c) \
            = sorted([(val_a, score_a), (val_b, score_b), (val_c, score_c)])

        _, runner_up, winner = "".join(
            char for _, char in
            sorted([(score_a, 'a'), (score_b, 'b'), (score_c, 'c')])
        )

        if abs(val_c - val_a) < min_diff:
            return {'a': val_a, 'b': val_b, 'c': val_c}[winner]

        if winner == 'a':
            val_b, val_c = val_a, val_b
            score_b, score_c = score_a, score_b

            val_a = val_b + (val_b - val_c) * side_winner_mul
            scoring_function_logger = logger(val_being_scored=val_a)
            score_a = scoring_function(val_a, logger=scoring_function_logger)
        elif winner == 'c':
            val_a, val_b = val_b, val_c
            score_a, score_b = score_b, score_c

            val_c = val_b + (val_b - val_a) * side_winner_mul
            scoring_function_logger = logger(val_being_scored=val_c)
            score_c = scoring_function(val_c, logger=scoring_function_logger)
        else:
            if runner_up == 'a':
                val_c = val_b
                score_c = score_b
            else:
                val_a = val_b
                score_a = score_b

            val_b = (val_a + val_c) / 2
            scoring_function_logger = logger(val_being_scored=val_b)
            score_b = scoring_function(val_b, logger=scoring_function_logger)
