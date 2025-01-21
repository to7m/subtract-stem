import numpy as np

from .sanitisation import sanitise_arg


class _Resources:
    def __init__(self, safe_divider_for_types):
        ...


class SafeDivider:
    def __init__(self, *, safe_divider_for_types):
        self._safe_divider_for_types = sanitise_arg("safe_divider_for_types")

    @classmethod
    def from_args(cls, a, b, *, max_abs_result, out):
        max_abs_result = sanitise_arg("max_abs_result")

        for name, val in [("a", a), ("b", b), ("out", out)]:
            if not isinstance(val, np.ndarray):
                raise TypeError(f"{name} should be a numpy.ndarray")

        if a.shape != b.shape or a.shape != out.shape:
            raise ValueError("a, b, and out should have the same shape")

        if 



    
    
    
    a, b, *,
        max_abs_result, out
    ):


        self._resources = _Resources(
            **sanitise_args_to_dict(
                "a", "b",
                "max_abs_result", "out"
            )
        ) 
