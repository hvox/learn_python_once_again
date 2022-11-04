import random
from time import monotonic as time


def is_sorted(array: list):
    return not any(x > y for x, y in zip(array, array[1:]))


def gitalev_sort(array: list):
    i = 0
    while i < len(array) - 1:
        if array[i] > array[i + 1]:
            array[i], array[i + 1] = array[i + 1], array[i]
            if i > 0:
                i -= 1
        else:
            i += 1


def simplest_sort(array: list):
    n = len(array)
    for i, j in ((i, j) for i in range(n) for j in range(i, n)):
        if array[i] > array[j]:
            array[i], array[j] = array[j], array[i]


SORTING_METHODS = {
    "simple": simplest_sort,
    "Gitalev": gitalev_sort,
}
n = 10**3
for name, sort in SORTING_METHODS.items():
    array = [x for x in range(1, 1 + n)]
    random.shuffle(array)
    t0 = time()
    sort(array)
    t1 = time()
    print(f"{name:>8}: ", t1 - t0)
    assert is_sorted(array)
