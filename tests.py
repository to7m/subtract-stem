import sys
from pathlib import Path

from tests_ import all_tests


sys.path.insert(0, Path(__file__).parent)

all_tests()
