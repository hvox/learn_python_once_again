from fractions import Fraction
from itertools import zip_longest
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


def khamkou_tree_v5(n: int, left=(0, 1), right=(1, 0), balance=0):
    center = tuple(x * 2**max(0, -balance) + y * 2**max(0, balance) for x, y in zip(left, right))
    if n > 1:
        yield from khamkou_tree_v5(n - 1, left, center, min(balance - 1, 0))
    yield Fraction(*center)
    if n > 1:
        yield from khamkou_tree_v5(n - 1, center, right, max(balance + 1, 0))


def khamkou_left_subtree_v5(n: int):
    yield Fraction(0)
    yield from list(khamkou_tree_v5(n))[: 2 ** (n - 1)]


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
    ("Khamkou(V4)", khamkou_left_subtree_v4),
    # ("Khamkou(V5)", khamkou_left_subtree_v5),
]
for n in range(1, 11):
    print(f"\n  n = {n}")
    table = []
    fails = []
    for tree_name, f in trees:
        tree = list(f(n))
        table.append([tree_name + ":"] + list(map(str, tree)))
        if not set(farey_sequence(n)) <= set(tree):
            fails.append(tree_name)
    if fails:
        print("Failed Farey test:", ", ".join(fails))
    print_table(table, "  ")
