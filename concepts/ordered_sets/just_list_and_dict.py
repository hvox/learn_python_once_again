# raymond_hettinger_collections?
from collections.abc import MutableSet
from typing import Any, Iterable, Iterator, TypeVar

T = TypeVar("T")


class OrderedSet(MutableSet[T]):
    __slots__ = ("elements", "lookup")

    def __init__(self, iterable: Iterable[T] = ()):
        elements = dict.fromkeys(iterable)
        self.elements: list[T] = list(elements)
        self.lookup: dict[T, int] = {v: i for i, v in enumerate(elements)}

    def __contains__(self, element: Any) -> bool:
        return element in self.lookup

    def __iter__(self) -> Iterator[T]:
        return (self.elements[i] for i in self.lookup.values())

    def __len__(self) -> int:
        return len(self.elements)

    def __repr__(self) -> str:
        return f"OrderedSet({list(self)})"

    def add(self, element: T) -> None:
        if element not in self.lookup:
            self.elements.append(element)
            self.lookup[element] = len(self.lookup)

    def update(self, elements: Iterable[T]) -> None:
        for x in elements:
            self.add(x)

    def discard(self, element: T) -> None:
        if element in self.lookup:
            self.remove(element)

    def remove(self, element: T) -> None:
        i = self.lookup.pop(element)
        if i == len(self.lookup):
            self.elements.pop()
        else:
            self.elements[i] = self.elements.pop()
            self.lookup[self.elements[i]] = i


if __name__ == "__main__":
    s: OrderedSet[str] = OrderedSet("abracadaba")
    t: OrderedSet[str] = OrderedSet("simsalabim")
    print(repr(s | t))
    print(repr(s & t))
    print(repr(s - t))
