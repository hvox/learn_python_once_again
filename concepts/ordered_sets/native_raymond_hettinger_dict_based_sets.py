# This is the most trivial way to implement sets using native python dicts
from collections.abc import MutableSet
from typing import Any, Iterable, Iterator, TypeVar

T = TypeVar("T")


class OrderedSet(MutableSet[T]):
    def __init__(self, iterable: Iterable[T] = None):
        self.elements: dict[T, None] = {}
        if iterable:
            for element in iterable:
                self.add(element)

    def __contains__(self, element: Any) -> bool:
        return element in self.elements

    def __iter__(self) -> Iterator[T]:
        yield from self.elements

    def __len__(self) -> int:
        return len(self.elements)

    def __str__(self) -> str:
        return f"OrderedSet({list(self)})"

    def add(self, element: T) -> None:
        self.elements[element] = None

    def update(self, elements: Iterable[T]) -> None:
        for x in elements:
            self.add(x)

    def discard(self, element: T) -> None:
        try:
            del self.elements[element]
        except KeyError:
            pass


if __name__ == "__main__":
    s: OrderedSet[str] = OrderedSet("abracadaba")
    t: OrderedSet[str] = OrderedSet("simsalabim")
    print(s | t)
    print(s & t)
    print(s - t)
