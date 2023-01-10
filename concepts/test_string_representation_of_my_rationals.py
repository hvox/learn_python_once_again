from rationals_using_inheritance_from_fractions import Rational
from itertools import product as iproduct
import pytest

FLOATS = [1, 123, 123456.7, 123.4567, 123 * 10**10, "0.0000000123"]
# [[fill]align][sign][#][0][width][grouping_option][.precision]
FILL_CHARACTERS = ["", "0", " ", "=", "α"]
ALIGN_OPTIONS = ["", "<", ">", "=", "^"]
ALIGNMENT_OPTIONS = [""] + list(map("".join, iproduct(FILL_CHARACTERS, ALIGN_OPTIONS[1:])))
SIGN_OPTIONS = ["", "+", "-", " "]
ALTERNATIVE_FORM_OPTIONS = ["", "#"]
ZERO_PADDING_OPTIONS = ["", "0"]
WIDTH_OPTIONS = ["", "0", "3", "10", "64"]
GROUPING_OPTIONS = ["", "_", ","]
PRECISION_OPTIONS = ["", "0", "3", "10"]
FLOAT_PRESENTATION_TYPES = "eEfFgGn%"
INT_PRESENTATION_TYPES = "bcdoxXn"

FLOAT_FORMAT_SPECIFICATIONS = list(map("".join, iproduct(
    # [[fill]align][sign][#][0][width][grouping_option][.precision]
    ALIGNMENT_OPTIONS,  # fill character and alignment options
    ["", "+", "-", " "],  # sign
    ["", "#"],  # alternative form [#]
    ["", "0"],  # leading zero
    ["", "0", "3", "10", "64"],  # desired minimum width
    [""],  # ["", "_", ","],  # grouping optin
    ["", ".0", ".3", ".7"],  # precision
    "eEfF"  # "eEfFgGn%",  # presentation types
)))
FLOAT_FORMAT_TESTS = list(iproduct(FLOATS, FLOAT_FORMAT_SPECIFICATIONS))


@pytest.mark.parametrize("number, fmt", FLOAT_FORMAT_TESTS)
def test_format(number, fmt):
    ratio_str = f"{Rational.from_float(number):{fmt}}"
    float_str = f"{float(number):{fmt}}"
    assert ratio_str == float_str


def manually_test_float_format_without_pytest():
    for i, _ in enumerate(FLOAT_FORMAT_TESTS):
        number, fmt = FLOAT_FORMAT_TESTS[i * 257 % len(FLOAT_FORMAT_TESTS)]
        print(f" test {i+1} / {len(FLOAT_FORMAT_TESTS)} ".center(80, "="))
        float_str = f"{float(number):{fmt}}"
        ratio_str = f"{Rational.from_float(number):{fmt}}"
        print(repr(ratio_str), repr(float_str))
        assert ratio_str == float_str


if __name__ == "__main__":
    manually_test_float_format_without_pytest()
