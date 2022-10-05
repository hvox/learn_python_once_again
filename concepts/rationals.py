from fractions import Fraction
from itertools import islice


class Rational(Fraction):
    def digits(self, precision: None | int = None):
        if precision is not None:
            *digits, last = list(islice(self.digits(), 2 + precision))
            digits[-1] += last >= 5
            yield from digits
            return
        numerator, denominator = self.as_integer_ratio()
        while numerator:
            yield numerator // denominator
            numerator = numerator % denominator * 10
        yield from iter(int, None)

    def __format__(self, fmt):
        if not fmt:
            return str(self)
        assert fmt[0] == "."
        if fmt[-1] == "f":
            digits = list(map(str, list(self.digits(int(fmt[1:-1])))))
            return digits[0] + "." + "".join(digits[1:])
        digits = list(map(str, list(self.digits(int(fmt[1:])))))
        return digits[0] + "." + digits[1] + "".join(digits[2:]).rstrip("0")

    def __round__(self, ndigits=None):
        if ndigits is None:
            return round(Fraction(self))
        numerator, denominator = self.as_integer_ratio()
        number = round(Fraction(numerator * 4 + 1, denominator * 4), ndigits)
        return number if ndigits is None else __class__(number)
