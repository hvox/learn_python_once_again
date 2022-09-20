from ast import literal_eval
from functools import singledispatch


@singledispatch
def sqrt(_):
    raise NotImplementedError()


@sqrt.register
def _(x: int) -> int:
    y = bytearray(x.to_bytes((x.bit_length() + 7) // 8, "little"))
    result, delta = 0, 0
    for i in range(len(y) * 8 - 2, -1, -2):
        delta, result = delta * 4 + ((y[i // 8] >> i % 8) & 3), result * 2
        if (new_delta := delta - (2 * result + 1)) >= 0:
            delta, result = new_delta, result + 1
    return result


@sqrt.register
def _(x: float) -> float:
    return x**0.5


@sqrt.register
def _(s: str) -> str:
    return s[: len(s) // 2]


while True:
    try:
        x = literal_eval(input(">>> "))
        y = sqrt(x)
        print(f"sqrt({x}) = {repr(y)}")
    except ValueError as e:
        print(e)
