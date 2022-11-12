from typing import TypeVar, Any, Iterator
from collections.abc import MutableSet, Set

T = TypeVar("T")


class MySet(MutableSet[T]):
    def __init__(self, content: set[T]):
        self.content = content

    def __contains__(self, element: Any) -> bool:
        return element in self.content

    def __iter__(self) -> Iterator[T]:
        yield from self.content

    def __len__(self) -> int:
        return len(self.content)

    def add(self, element: T) -> None:
        self.content.add(element)

    def discard(self, element: T) -> None:
        self.content.discard(element)


def f(s: Set[str]) -> str:
    return next(iter(s))


s: MySet[str] = MySet(set())
s.add("hello")
print(f(s))
