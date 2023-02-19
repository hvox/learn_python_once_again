from fractions import Fraction
from itertools import zip_longest, product
from math import gcd
from os import get_terminal_size


def farey_sequence(n: int):
    # https://en.wikipedia.org/wiki/Farey_sequence
    (a, b, c, d) = (0, 1, 1, n)
    yield Fraction(a, b)
    while c <= n:
        k = (n + b) // d
        (a, b, c, d) = (c, d, k * c - a, k * d - b)
        yield Fraction(a, b)


def calkin_wilf_tree(n: int, root=(1, 1)):
    # https://en.wikipedia.org/wiki/Calkin-Wilf_tree
    x, y = root
    if n > 1:
        yield from calkin_wilf_tree(n - 1, (x, x + y))
    yield Fraction(x, y)
    if n > 1:
        yield from calkin_wilf_tree(n - 1, (x + y, y))


def calkin_wilf_left_subtree(n: int):
    yield Fraction(0)
    yield from list(calkin_wilf_tree(n))[: 2 ** (n - 1)]


def stern_brocot_tree(n: int):
    # https://en.wikipedia.org/wiki/Stern-Brocot_tree
    tree = [(0, 1), (1, 1)]
    for _ in range(1, n):
        tree = sum(([(x + z, y + w), (z, w)] for (x, y), (z, w) in zip(tree, tree[1:])), [tree[0]])
    yield from (Fraction(x, y) for x, y in tree)


def khamkou_tree_v1(n: int, left=(0, 1), center=(1, 1), right=(1, 0)):
    if n > 1:
        left_center = tuple(x + y for x, y in zip(left, center))
        yield from khamkou_tree_v1(n - 1, (left[0] * 2, left[1] * 2), left_center, center)
    yield Fraction(*center)
    if n > 1:
        right_center = tuple(x + y for x, y in zip(center, right))
        yield from khamkou_tree_v1(n - 1, center, right_center, (right[0] * 2, right[1] * 2))


def khamkou_left_subtree_v1(n: int):
    yield Fraction(0)
    yield from list(khamkou_tree_v1(n))[: 2 ** (n - 1)]


def khamkou_tree_v2(n: int, left=(0, 1), right=(1, 0), priorities=(1, 1)):
    center = tuple(sum((p + 1) // 2 * w for p, w in zip(priorities, (x, y))) for x, y in zip(left, right))
    center = (center[0] // gcd(*center), center[1] // gcd(*center))
    if n > 1:
        yield from khamkou_tree_v2(n - 1, left, center, (priorities[0] * 2, 1))
    yield Fraction(*center)
    if n > 1:
        yield from khamkou_tree_v2(n - 1, center, right, (1, priorities[1] * 2))


def khamkou_left_subtree_v2(n: int):
    yield Fraction(0)
    yield from list(khamkou_tree_v2(n))[: 2 ** (n - 1)]


def khamkou_tree_v3(n: int, left=(0, 1), right=(1, 0), priorities=(1, 1)):
    center = tuple(sum(2**max(p - 3, 0) * w for p, w in zip(priorities, (x, y))) for x, y in zip(left, right))
    center = (center[0] // gcd(*center), center[1] // gcd(*center))
    if n > 1:
        yield from khamkou_tree_v3(n - 1, left, center, (priorities[0] + 1, 1))
    yield Fraction(*center)
    if n > 1:
        yield from khamkou_tree_v3(n - 1, center, right, (1, priorities[1] + 1))


def khamkou_left_subtree_v3(n: int):
    yield Fraction(0)
    yield from list(khamkou_tree_v3(n))[: 2 ** (n - 1)]


def khamkou_tree_v4(n: int, left=(0, 1), right=(1, 0), balance=0):
    center = tuple(x * 2**max(0, -balance) + y * 2**max(0, balance) for x, y in zip(left, right))
    if n > 1:
        yield from khamkou_tree_v4(n - 1, left, center, min(balance - 1, 0))
    yield Fraction(*center)
    if n > 1:
        yield from khamkou_tree_v4(n - 1, center, right, max(balance + 1, 0))


def khamkou_left_subtree_v4(n: int):
    yield Fraction(0)
    yield from list(khamkou_tree_v4(n))[: 2 ** (n - 1)]


def khamkou_tree_v5(n: int):
    def p(x):
        return 2 ** max(x, 0)
    tree = [(0, 1, 0), (1, 0, 0)]
    for _ in range(n):
        tree = list(map(lambda x: x, sum((
            [(x0 * p(p0) + x1 * p(p1), y0 * p(p0) + y1 * p(p1), 0), (x1, y1, p1 + 1)]
            for ((x0, y0, p0), (x1, y1, p1)) in zip(tree, tree[1:])
        ), [tree[0][:2] + (tree[0][2] + 1,)])))
    yield from (Fraction(x, y) for x, y, _ in tree[:~0])


def khamkou_left_subtree_v5(n: int):
    yield from list(khamkou_tree_v5(n))[: 2 ** (n - 1) + 1]


def khamkou_230218_for_left_subtree(binary_code: str) -> Fraction:
    def lsb(x: int) -> int:
        return x & -x
    if not binary_code:
        return Fraction(1, 2)
    alpha, beacon, direction = 2, [1, 2], binary_code[0]
    star = [1, 1] if direction == "1" else [0, 1]
    for code in binary_code[1:]:
        if alpha % 2 == 1:
            beacon, star = (
                [x + alpha * y for x, y in zip(beacon, star)],
                [x + (alpha + (-1)**(code != direction)) * y for x, y in zip(beacon, star)]
            )
            alpha, direction = 2, code
        elif "1" not in bin(alpha + 2)[3:]:
            if code == direction:
                alpha += 2 ** len(bin(alpha + 2)[3:])
            else:
                alpha = (alpha + 2) * 3 // 4 - 2
        else:
            if code == direction:
                alpha += lsb(alpha + 2) // 2
            else:
                alpha -= lsb(alpha + 2) // 2 if alpha != 2 else 1
    return Fraction(*[x + alpha * y for x, y in zip(beacon, star)])


def khamkou_230218(binary_code: str) -> Fraction:
    def inv(code: str) -> str:
        return "".join("1" if char == "0" else "0" for char in code)
    assert all(char in "01" for char in binary_code)
    if len(binary_code) < 2:
        return Fraction({"0": -1, "": 0, "1": 1}[binary_code])
    r = binary_code
    sign = +1 if binary_code[0] == "1" else -1
    binary_code = binary_code[1:] if binary_code[0] == "1" else inv(binary_code[1:])
    inversed = binary_code[0] == "1"
    binary_code = inv(binary_code[1:]) if inversed else binary_code[1:]
    x = khamkou_230218_for_left_subtree(binary_code)
    return sign * (1 / x if inversed else x)


def khamkou_230218_left_subtree(n: int):
    def get_codes(n: int):
        if n <= 0:
            return
        yield from ("0" + code for code in (get_codes(n - 1)))
        yield ""
        yield from ("1" + code for code in (get_codes(n - 1)))

    yield Fraction(0)
    for code in get_codes(n - 1):
        yield khamkou_230218("10" + code)
    yield Fraction(1)


def print_table(rows: list[str], sep=" "):
    line_width = get_terminal_size().columns
    lengths = [max(len(x) for x in column if x) for column in zip_longest(*rows)]
    for row in rows:
        line = sep.join(x + " " * (lengths[i] - len(x)) for i, x in enumerate(row))
        print(line if len(line) <= line_width else line[:line_width-3].rstrip() + "...")


trees = [
    ("Farey", farey_sequence),
    ("Calkin-Wilf", calkin_wilf_left_subtree),
    ("Stern-Brocot", stern_brocot_tree),
    ("Khamkou(V1)", khamkou_left_subtree_v1),
    ("Khamkou(V2)", khamkou_left_subtree_v2),
    ("Khamkou(V3)", khamkou_left_subtree_v3),
    ("Khamkou(V4)", khamkou_left_subtree_v4),  # my favorite
    ("Khamkou(V5)", khamkou_left_subtree_v5),
    ("[23-02-18]", khamkou_230218_left_subtree),
]
for n in range(1, 11):
    print(f"\n  n = {n}")
    table = []
    fails = []
    set_fails = []
    for tree_name, f in trees:
        tree = list(f(n))
        table.append([tree_name + ":"] + list(map(str, tree)))
        if not set(farey_sequence(n)) <= set(tree):
            fails.append(tree_name)
        if len(set(tree)) != len(tree):
            set_fails.append(tree_name)
    if fails:
        print("Failed Farey test:", ", ".join(fails))
    if set_fails:
        print("Failed element uniqueness test:", ", ".join(fails))
    print_table(table, "  ")
