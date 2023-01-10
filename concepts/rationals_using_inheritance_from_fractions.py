from __future__ import annotations
from re import fullmatch
from fractions import Fraction
from itertools import islice
from functools import update_wrapper
from typing import NamedTuple, Self, Any

__all__ = ["Rational"]


class Rational(Fraction):
    @classmethod
    def from_float(cls, number: float) -> Self:
        result: Any = cls(number).limit_denominator(10**9)
        return result

    @property
    def sign(self) -> Self:
        return self.__class__((self > 0) - (self < 0))

    @property
    def abs(self) -> Self:
        return abs(self)

    def ilog(self, base: Rational) -> Self:
        result, log = Rational("1"), 0
        if base < 1:
            base **= - 1
            self **= -1
        if self < 1:
            while result > self.abs:
                result /= base
                log -= 1
        else:
            while result * base <= self.abs:
                result *= base
                log += 1
        return log

    def digits(self, precision: None | int = None):
        if precision is not None:
            *digits, last = islice(self.digits(), 2 + precision)
            digits[-1] += last >= 5
            yield from digits
            return
        numerator, denominator = self.as_integer_ratio()
        while numerator:
            yield numerator // denominator
            numerator = numerator % denominator * 10
        yield from iter(int, None)

    def __str__(self) -> str:
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

    def __format__(self, format_specification: str) -> str:
        fmt = Format.parse(format_specification)
        print(f"number={self!s}   format={fmt!r}")
        if fmt.typ in "fF":
            digits = list(map(str, self.digits(fmt.precision)))
            print("digits:", digits)
            string = digits[0] + "." + "".join(digits[1:])
            if not fmt.alt:
                string = string.removesuffix(".")
            print("string:", string)
        elif fmt.typ in "eE":
            exponent = int(self.ilog(Rational("10")))
            number = self / Rational("10") ** exponent
            string = f"{number:{fmt.alt}.{fmt.precision}f}{fmt.typ}{exponent:+03d}"
        if self.sign == -1:
            string = "-" + string
        elif fmt.sign == "+":
            string = "+" + string
        elif fmt.sign == " ":
            string = " " + string
        print(f"with sign: {string!r}")
        if fmt.align == "<":
            string = string.ljust(fmt.width, fmt.fill)
        elif fmt.align == ">":
            string = string.rjust(fmt.width, fmt.fill)
        elif fmt.align == "^":
            padding = max(0, fmt.width - len(string))
            string = fmt.fill * (padding // 2) + string + fmt.fill * ((padding + 1) // 2)
        elif fmt.align == "=":
            if string[0] in "+- ":
                string = string[0] + string[1:].rjust(fmt.width - 1, fmt.fill)
            else:
                string = string.rjust(fmt.width, fmt.fill)
        return string


# https://docs.python.org/3/library/string.html#format-specification-mini-language
FORMAT_SPECIFICATION_LANGUAGE = r'(([\s\S])?([<>=\^]))?([\+\- ])?(#)?(0)?(\d*)([,_])?(\.(\d*))?([eEfF])?'


class Format(NamedTuple):
    fill: str
    align: str
    sign: str
    alt: str
    zero_padding: str
    width: int
    grouping_option: str
    precision: int
    typ: str

    @classmethod
    def parse(cls, string: str) -> Self:
        if match := fullmatch(FORMAT_SPECIFICATION_LANGUAGE, string):
            options = match.group(2, 3, 4, 5, 6, 7, 8, 10, 11)
            print(string, "->", options)
            zero_padding = options[4] or ""
            fill = options[0] or ("0" if zero_padding else " ")
            align = options[1] or ("=" if zero_padding else ">")
            sign = options[2] or "-"
            alt = options[3] or ""
            width = int(options[5] or "0")
            grouping_option = options[6] or "."
            typ = options[8] or "d"
            precision = int(options[7] or ("6" if typ in "eEfF" else "-1"))
            return cls(fill, align, sign, alt, zero_padding, width, grouping_option, precision, typ)
        raise ValueError(f"{string!r} is not valid format specification")


def update_method(cls, method_name: str):
    def wrapper(*args, **kwargs):
        result = f(*args, **kwargs)
        return cls(result)
    f = getattr(cls, method_name)
    update_wrapper(wrapper, f)
    setattr(cls, method_name, wrapper)
    return wrapper


for method in [
    "__trunc__", "__floor__", "__ceil__", "__round__", "limit_denominator",
    "__add__", "__radd__", "__sub__", "__rsub__", "__mul__", "__rmul__",
    "__truediv__", "__rtruediv__", "__floordiv__", "__rfloordiv__",
    "__divmod__", "__rdivmod__", "__mod__", "__rmod__", "__pow__",
    "__rpow__", "__pos__", "__neg__", "__abs__", "__int__",
]:
    update_method(Rational, method)
