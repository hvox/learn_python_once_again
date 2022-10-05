from fractions import Fraction
from itertools import islice


class Rational(Fraction):
    def digits(self):
        numerator, denominator = self.as_integer_ratio()
        integer, fractional = divmod(numerator, denominator)
        yield integer
        while fractional:
            fractional *= 10
            integer, fractional = divmod(fractional, denominator)
            yield integer
        yield from iter(int, None)

    def __format__(self, fmt):
        if not fmt:
            return str(self)
        assert fmt[0] == "."
        precision = int(fmt[1:-1] if fmt[-1] == "f" else fmt[1:])
        *digits, last = list(islice(self.digits(), 2 + precision))
        digits[-1] += last >= 5
        while fmt[-1] != "f" and len(digits) > 2 and digits[-1] == 0:
            digits.pop()
        return str(digits[0]) + "." + "".join(map(str, digits[1:]))
