"""Rational numbers."""
# TODO: the __index__ for integer numbers!
import itertools
import math
import numbers

__all__ = ["Rational"]


def parse_ratio(s):
    s = s.strip().replace("_", "").replace(" ", "")
    sign = [1, -1][s[0] == "-"]
    s = s.removeprefix("-").removeprefix("+")
    if "/" in s:
        numerator, denominator = map(int, s.strip().split("/", 1))
    elif "." in s:
        numerator = int(s.replace(".", ""))
        denominator = 10 ** (len(s) - s.index(".") - 1)
        print(s, "->", numerator, "/", denominator)
    else:
        numerator, denominator = int(s), 1
    return (sign * numerator, denominator)


def as_integer_ratio(number):
    if isinstance(number, numbers.Real):
        return number.as_integer_ratio()
    return parse_ratio(number)


class Rational(numbers.Rational):
    """Rational numbers that don't care about python compatibility"""

    __slots__ = ("_numerator", "_denominator")

    @property
    def sign(self):
        return [-1, 0, 1][(self._numerator >= 0) + (self.numerator > 0)]

    @property
    def numerator(self):
        return self._numerator

    @property
    def denominator(self):
        return self._denominator

    def __init__(self, numerator=0, denominator=1):
        numerator, denominator = (
            x * y for x, y in zip(as_integer_ratio(numerator), reversed(as_integer_ratio(denominator)))
        )
        if denominator < 0:
            numerator, denominator = -numerator, -denominator
        gcd = math.gcd(numerator, denominator)
        self._numerator = numerator // gcd
        self._denominator = denominator // gcd

    def as_integer_ratio(self):
        return (self.numerator, self.denominator)

    def round(self, epsilon=1):
        return self // epsilon * epsilon

    def __repr__(self):
        return f'{self.__class__.__qualname__}("{str(self)}")'

    def digits(self, precision: None | int = None):
        if precision is not None:
            *digits, last = itertools.islice(self.digits(), 2 + precision)
            digits[-1] += last >= 5
            yield from digits
            return
        numerator, denominator = self.as_integer_ratio()
        while numerator:
            yield numerator // denominator
            numerator = numerator % denominator * 10
        yield from iter(int, None)

    def __str__(self):
        if self.denominator == 1:
            return str(self.numerator)
        denominator = self.denominator
        fives = 0
        while denominator % 5 == 0:
            denominator //= 5
            fives += 1
        twos = 0
        while denominator % 2 == 0:
            denominator //= 2
            twos += 1
        if denominator == 1:
            tail_len = max(fives, twos)
            shift = 10 ** tail_len // self.denominator
            digits = str(abs(self.numerator) * shift).zfill(1 + tail_len)
            integer, fractional = digits[:-tail_len], digits[-tail_len:]
            return "-" * (self.numerator < 0) + integer + "." + fractional
        else:
            return f"{self.numerator}/{self.denominator}"

    def __format__(self, fmt):
        print("__format__", repr(fmt))
        if not fmt:
            return str(self)
        assert fmt[0] == "."
        if fmt[-1] == "f":
            digits = list(map(str, list(self.digits(int(fmt[1:-1])))))
            return digits[0] + "." + "".join(digits[1:])
        digits = list(map(str, list(self.digits(int(fmt[1:])))))
        return digits[0] + "." + digits[1] + "".join(digits[2:]).rstrip("0")

    def __add__(self, other):
        x, y = as_integer_ratio(self)
        z, w = as_integer_ratio(other)
        return __class__(x * w + z * y, y * w)

    def __radd__(self, other):
        return self.__class__.__add__(other, self)

    def __sub__(self, other):
        x, y = as_integer_ratio(self)
        z, w = as_integer_ratio(other)
        return __class__(x * w - z * y, y * w)

    def __rsub__(self, other):
        return self.__class__.__sub__(other, self)

    def __mul__(self, other):
        x, y = as_integer_ratio(self)
        z, w = as_integer_ratio(other)
        return self.__class__(x * z, y * w)

    def __rmul__(self, other):
        return self.__class__.__mul__(other, self)

    def __truediv__(self, other):
        x, y = as_integer_ratio(self)
        z, w = as_integer_ratio(other)
        return __class__(x * w, y * z)

    def __rtruediv__(self, other):
        return self.__class__.__truediv__(other, self)

    def __floordiv__(self, other):
        x, y = as_integer_ratio(self)
        z, w = as_integer_ratio(other)
        return x * w // (y * z)

    def __rfloordiv__(self, other):
        return self.__class__.__floordiv__(other, self)

    def __divmod__(self, other):
        x, y = as_integer_ratio(self)
        z, w = as_integer_ratio(other)
        return divmod(x * w, y * z)

    def __rdivmod__(self, other):
        return self.__class__.__divmod__(other, self)

    def __mod__(self, other):
        x, y = as_integer_ratio(self)
        z, w = as_integer_ratio(other)
        return __class__(x * w % (y * z), y * z)

    def __rmod__(self, other):
        return self.__class__.__mod__(other, self)

    def __pow__(self, other):
        x, y = as_integer_ratio(self)
        z, w = as_integer_ratio(other)
        if w & (w - 1) or z * (x.bit_length() + y.bit_length()) > 1048576:
            return __class__((x / y) ** (z / w))
        numerator, denominator = x**z, y**z
        while w > 1:
            numerator_sqrt = math.isqrt(numerator)
            if numerator_sqrt * numerator_sqrt != numerator:
                return __class__((numerator / denominator) ** (1 / w))
            denominator_sqrt = math.isqrt(denominator)
            if denominator_sqrt * denominator_sqrt != denominator:
                return __class__((numerator / denominator) ** (1 / w))
            numerator, denominator = numerator_sqrt, denominator_sqrt
            w //= 2
        return __class__(numerator, denominator)

    def __rpow__(self, other):
        return self.__class__.__pow__(other, self)

    def __pos__(self):
        return self.__class__(self.numerator, self.denominator)

    def __neg__(self):
        return self.__class__(-self.numerator, self.denominator)

    def __abs__(self):
        return self.__class__(abs(self.numerator), self.denominator)

    def __int__(self):
        return self.sign * (abs(self.numerator) // self.denominator)

    def __trunc__(self):
        return self.sign * (abs(self.numerator) // self.denominator)

    def __floor__(a):
        return a.numerator // a.denominator

    def __ceil__(self):
        return -(-self.numerator // self.denominator)

    def __round__(self, ndigits=None):
        if ndigits is None:
            integer, fractional = divmod(self.numerator, self.denominator)
            return integer + (fractional * 2 >= self.denominator)
        return self.round(__class__(10) ** ndigits)

    def __hash__(self):
        return hash(self.as_integer_ratio())

    def __eq__(self, other):
        return self.as_integer_ratio() == other.as_integer_ratio()

    def __lt__(self, other):
        (x, y), (z, w) = as_integer_ratio(self), as_integer_ratio(other)
        return x * w < y * z

    def __gt__(self, other):
        (x, y), (z, w) = as_integer_ratio(self), as_integer_ratio(other)
        return x * w > y * z

    def __le__(self, other):
        (x, y), (z, w) = as_integer_ratio(self), as_integer_ratio(other)
        return x * w <= y * z

    def __ge__(self, other):
        (x, y), (z, w) = as_integer_ratio(self), as_integer_ratio(other)
        return x * w >= y * z

    def __bool__(self):
        return self != 0

    def __reduce__(self):
        return (__class__, self.as_integer_ratio())

    def __copy__(self):
        return self

    def __deepcopy__(self, _):
        return self
