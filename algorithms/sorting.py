import random
from time import monotonic as time
from typing import Any, Callable


def is_sorted(array: list[Any]) -> bool:
    return not any(x > y for x, y in zip(array, array[1:]))


def simplest_sort(array: list[Any]) -> None:
    n = len(array)
    for i, j in ((i, j) for i in range(n) for j in range(i, n)):
        if array[i] > array[j]:
            array[i], array[j] = array[j], array[i]


def gitalev_sort(array: list[Any]) -> None:
    i = 0
    while i < len(array) - 1:
        if array[i] > array[i + 1]:
            array[i], array[i + 1] = array[i + 1], array[i]
            if i > 0:
                i -= 1
        else:
            i += 1


def quicksort(array: list[Any], left: int = 0, right: int = ~0) -> None:
    left %= len(array)
    right %= len(array)
    if right - left < 2:
        array[left : right + 1] = list(sorted(array[left : right + 1]))
        return
    pivot, i = array[left], left
    for j in range(i + 1, right + 1):
        if array[j] <= pivot:
            i += 1
            array[i], array[j] = array[j], array[i]
    array[left], array[i] = array[i], array[left]
    if i > left:
        quicksort(array, left, i - 1)
    if right > i:
        quicksort(array, i + 1, right)


SORTING_METHODS: dict[str, Callable[[list[int]], None]] = {
    "quicksort": quicksort,
    "simple": simplest_sort,
    "Gitalev": gitalev_sort,
}
n = 10**3 * 5
for name, sort in SORTING_METHODS.items():
    array = [x for x in range(1, 1 + n)]
    random.shuffle(array)
    t0 = time()
    sort(array)
    t1 = time()
    print(f"{name:>9}: ", t1 - t0)
    assert is_sorted(array)
