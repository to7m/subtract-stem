import numpy as np

from .running_eq_profile import GenerateRunningEqProfile


# There's no thread-safe way of doing this so I'm just putting it here to make
# it obvious.
np.seterr(divide="ignore")
