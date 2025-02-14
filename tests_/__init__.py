from .hone_in import test_hone_in
from .divide import safe_divide, ataabtrnfatbaa, all_divide
from .io import test_io
from .grains import test_grains
from .transforms import test_spectra, test_spectra_buffer, all_transforms


def all_tests():
    test_hone_in()
    all_divide()
    test_io()
    test_grains()
    all_transforms()
