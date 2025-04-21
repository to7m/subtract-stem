from operator import lt, gt

from ._sanitisation import sanitise as san


_STRETCH = 10.0
_INSIDE = 0.8


class _Results:
    __slots__ = [
        "low_val", "winning_val", "high_val", "new_val",
        "low_score", "winning_score", "high_score", "new_score",
        "scoring_function", "better_score"
    ]

    def __init__(
        self, *,
        winning_and_new_val, winning_and_new_score,
        scoring_function, better_score
    ):
        self.low_val = self.high_val = self.low_score = self.high_score = None
        self.winning_val = self.new_val = winning_and_new_val
        self.winning_score = self.new_score = winning_and_new_score
        self.scoring_function = scoring_function
        self.better_score = better_score

    def score_new_and_reorder(self):
        self.new_score = self.scoring_function(self.new_val)

        if self.better_score(self.new_score, self.winning_score):
            if self.new_val > self.winning_val:
                self.low_val = self.winning_val
                self.low_score = self.winning_score
            else:
                self.high_val = self.winning_val
                self.high_score = self.winning_score

            self.winning_val = self.new_val
            self.winning_score = self.new_score
        else:
            if self.new_val > self.winning_val:
                self.high_val = self.new_val
                self.high_score = self.new_score
            else:
                self.low_val = self.new_val
                self.low_score = self.new_score

    def get_and_set_new(self):
        if self.low_val is None:
            self.new_val = (
                self.winning_val * _STRETCH + self.high_val * (1 - _STRETCH)
            )
        elif self.high_val is None:
            self.new_val = (
                self.winning_val * _STRETCH + self.low_val * (1 - _STRETCH)
            )
        else:
            if (
                self.high_val - self.winning_val
                > self.winning_val - self.low_val
            ):
                self.new_val = (
                    self.winning_val * _INSIDE + self.high_val * (1 - _INSIDE)
                )
            else:
                self.new_val = (
                    self.winning_val * _INSIDE + self.low_val * (1 - _INSIDE)
                )

    def get_dict(self):
        return {
            position: {
                "val": getattr(self, f"{position}_val"),
                "score": getattr(self, f"{position}_score")
            }
            for position in ["low", "winning", "high", "new"]
        }


def hone_in(
    scoring_function, *,
    first_val=0.0, val_add=1.0, highest_wins=False, min_diff=0.0
):
    _, first_val, val_add, _, min_diff = sanitise_args(
        "scoring_function", "first_val", "val_add", "highest_wins", "min_diff"
    )

    results = _Results(
        winning_and_new_val=first_val,
        winning_and_new_score=scoring_function(first_val),
        scoring_function=scoring_function,
        better_score=gt if highest_wins else lt
    )
    yield results.get_dict()

    results.new_val = first_val + val_add
    results.score_new_and_reorder()
    yield results.get_dict()

    while True:
        if None not in (results.high_val, results.low_val):
            if results.high_val - results.low_val < min_diff:
                return

        results.get_and_set_new()

        if results.new_val in (results.low_val, results.high_val):
            return

        results.score_new_and_reorder()
        yield results.get_dict()
