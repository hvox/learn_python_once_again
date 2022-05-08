import ctypes
from pathlib import Path
here = Path(__file__).resolve().parent
lib = ctypes.CDLL(here / "code.lib")
lib.f()
