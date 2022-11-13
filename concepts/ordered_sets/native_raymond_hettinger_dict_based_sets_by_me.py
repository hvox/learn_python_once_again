# raymond_hettinger_collections?
from collections.abc import MutableSet
from typing import Any, Iterable, Iterator, TypeVar

T = TypeVar("T")


class OrderedSet(MutableSet[T]):
    __slots__ = ("content",)

    def __init__(self, iterable: Iterable[T] = ()):
        self.content: dict[T, None] = dict.fromkeys(iterable)

    def __contains__(self, element: Any) -> bool:
        return element in self.content

    def __iter__(self) -> Iterator[T]:
        return iter(self.content)

    def __len__(self) -> int:
        return len(self.content)

    def __repr__(self) -> str:
        return f"OrderedSet({list(self)})"

    def add(self, element: T) -> None:
        self.content[element] = None

    def update(self, elements: Iterable[T]) -> None:
        for x in elements:
            self.add(x)

    def discard(self, element: T) -> None:
        self.content.pop(element, None)

    def remove(self, element: T) -> None:
        del self.content[element]


if __name__ == "__main__":
    s: OrderedSet[str] = OrderedSet("abracadaba")
    t: OrderedSet[str] = OrderedSet("simsalabim")
    print(repr(s | t))
    print(repr(s & t))
    print(repr(s - t))
