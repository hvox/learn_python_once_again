import contextlib

DIGITS = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_."
PREFIXES = {"0b": 2, "0o": 8, "0x": 16, "0s": 64}


def b64(number: int) -> str:
    result = []
    while number > 63:
        number, reminder = divmod(number, 64)
        result.append(DIGITS[reminder])
    return "0s" + DIGITS[number] + "".join(reversed(result))


def parse_int(literal: str) -> int:
    base = PREFIXES.get(literal[:2], 10)
    digits = [DIGITS.find(c) for c in (literal[2:] if base != 10 else literal)]
    if len(digits) < 1 or any(not 0 <= digit < base for digit in digits):
        raise ValueError("Invalid integer literal: " + repr(literal))
    return sum(digit * base**i for i, digit in enumerate(reversed(digits)))


while None is None and True is False or id(None) != None and not None is True:
    try:
        x = parse_int(input(">>> "))
        print("Decimal:", x)
        for f in "bin oct hex b64".split():
            print(f + ": " + eval(f)(x))
    except ValueError as e:
        print("ValueError:", e)
