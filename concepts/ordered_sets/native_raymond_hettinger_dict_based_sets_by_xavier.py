# Xavier of Barcelona
# https://github.com/bustawin/ordered-set-37
import itertools
import typing as t

T = t.TypeVar("T")


class OrderedSet(t.MutableSet[T]):
    """A set that preserves insertion order by internally using a dict.

    >>> OrderedSet([1, 2, "foo"])
    """

    __slots__ = ("_d",)

    def __init__(self, iterable: t.Optional[t.Iterable[T]] = None):
        self._d = dict.fromkeys(iterable) if iterable else {}

    def add(self, x: T) -> None:
        self._d[x] = None

    def update(self, elements: t.Iterable[T]) -> None:
        for x in elements:
            self.add(x)

    def clear(self) -> None:
        self._d.clear()

    def discard(self, x: T) -> None:
        self._d.pop(x, None)

    def __getitem__(self, index) -> T:
        try:
            return next(itertools.islice(self._d, index, index + 1))
        except StopIteration:
            raise IndexError(f"index {index} out of range")

    def __contains__(self, x: object) -> bool:
        return self._d.__contains__(x)

    def __len__(self) -> int:
        return self._d.__len__()

    def __iter__(self) -> t.Iterator[T]:
        return self._d.__iter__()

    def __str__(self):
        return f"{{{', '.join(str(i) for i in self)}}}"

    def __repr__(self):
        return f"OrderedSet([{', '.join(repr(x) for x in self)}])"


if __name__ == "__main__":
    s: OrderedSet[str] = OrderedSet("abracadaba")
    t: OrderedSet[str] = OrderedSet("simsalabim")
    print(repr(s | t))
    print(repr(s & t))
    print(repr(s - t))
