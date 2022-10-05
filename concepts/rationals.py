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
        assert fmt[0] == "." and fmt[-1] == "f"
        *digits, last = list(islice(self.digits(), 2 + int(fmt[1:-1])))
        digits[-1] += last >= 5
        return str(digits[0]) + "." + "".join(map(str, digits[1:]))
