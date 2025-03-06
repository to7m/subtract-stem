from .timestamp import test_timestamp
from .buffer import test_buffer
from .hone_in import test_hone_in
from .divide import all_divide
from .io import test_io
from .audio_grains import test_audio_grains
from .transforms import test_transforms
from .eq_profiles import all_eq_profiles
from .audio_pair_to_eq_profile import all_audio_pair_to_eq_profile


def all_tests():
    test_timestamp()
    test_buffer()
    test_hone_in()
    all_divide()
    test_io()
    test_audio_grains()
    test_transforms()
    all_eq_profiles()
    all_audio_pair_to_eq_profile()

    print("tests succeeded")
