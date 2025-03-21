from fractions import Fraction

from .sanitisation import sanitise_args, sanitise_logger


DEFAULT_START_ADD = Fraction(1)
DEFAULT_SIDE_WINNER_MUL = Fraction(3)
DEFAULT_MIN_DIFF = Fraction(1, 1_000_000_000)


class _HoneInIterator:
    def __init__(
        self, scoring_function, *,
        aim_lowest,
        start_val, start_add,
        min_diff, side_winner_mul,
        logger
    ):
        self._scoring_function = scoring_function
        self._min_diff, self._side_winner_mul = min_diff, side_winner_mul
        self._logger = logger

        self._i = 0

        self._sort_key = self._low_last if aim_lowest else self._high_last

        self._vals_and_scores = []
        self._set_initial_vals_and_scores(
            start_val=start_val, start_add=start_add
        )

    def __iter__(self):
        return self

    def __next__(self):
        if self._check_below_min_diff():
            raise StopIteration

        middle_val = self._vals_and_scores[1][0]
        self._order_by_score()
        winning_val = self._vals_and_scores[2][0]

        del self._vals_and_scores[0]

        if middle_val == winning_val:
            self._new_middle()
        else:
            self._new_side()

        self._order_by_score()
        winning_val_and_score = self._vals_and_scores[2]

        self._order_by_val()

        return winning_val_and_score

    def _low_last(self, val_and_score):
        return -val_and_score[1]

    def _high_last(self, val_and_score):
        return val_and_score[1]

    def _get_score(self, val):
        logger = sanitise_logger(self._logger(
            msg=f"scoring value: {val}",
            iteration=self._i, val=val
        ))
        score = self._scoring_function(val, logger=logger)
        self._logger(
            msg=f"value {val} scored {score}",
            iteration=self._i, val=val, score=score
        )

        self._i += 1

        return score

    def _order_by_score(self):
        self._vals_and_scores.sort(key=self._sort_key)

    def _new_side(self):
        (val_0, val_1), _ = zip(*self._vals_and_scores)
        diff = val_1 - val_0
        val_2 = val_1 + diff * self._side_winner_mul
        self._vals_and_scores.append((val_2, self._get_score(val_2)))

    def _order_by_val(self):
        self._vals_and_scores.sort()

    def _set_initial_vals_and_scores(self, *, start_val, start_add):
        self._vals_and_scores = [
            (start_val, self._get_score(start_val)),
            (start_val + start_add, self._get_score(start_val + start_add))
        ]

        self._order_by_score()
        self._new_side()
        self._order_by_val()

    def _check_below_min_diff(self):
        (val_0, val_1, val_2), _ = zip(*self._vals_and_scores)
        return (
            val_1 - val_0 < self._min_diff
            or val_2 - val_1 < self._min_diff
        )

    def _new_middle(self):
        (val_0, val_1), _ = zip(*self._vals_and_scores)
        val_2 = (val_0 + val_1) / 2
        self._vals_and_scores.append((val_2, self._get_score(val_2)))


def hone_in(
    scoring_function, *,
    aim_lowest=True,
    start_val=Fraction(0), start_add=DEFAULT_START_ADD,
    min_diff=DEFAULT_MIN_DIFF, side_winner_mul=DEFAULT_SIDE_WINNER_MUL,
    logger=None
):
    for winning_val, winning_score in _HoneInIterator(**sanitise_args({
        "scoring_function": scoring_function,
        "aim_lowest": aim_lowest,
        "start_val": start_val, "start_add": start_add,
        "min_diff": min_diff, "side_winner_mul": side_winner_mul,
        "logger": logger
    })):
        pass

    return winning_val, winning_score
