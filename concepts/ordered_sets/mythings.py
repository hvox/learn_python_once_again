from collections.abc import MutableSequence, MutableSet
from typing import Any, Iterable, Iterator, Self, TypeVar, overload

T = TypeVar("T")


class MutablyIterableIndexedSet(MutableSequence[T], MutableSet[T]):
    __slots__ = ("indexes", "values")

    def __init__(self, iterable: Iterable[T] = ()):
        elements = dict.fromkeys(iterable)
        self.values: list[T] = list(elements)
        self.indexes: dict[T, int] = {v: i for i, v in enumerate(elements)}

    def __contains__(self, element: Any) -> bool:
        return element in self.indexes

    def __iter__(self) -> Iterator[T]:
        return iter(self.values)

    def mutable_iter(self) -> Iterator[T]:
        i, values, current = 0, self.values, object()
        while i < len(values):
            if current is not values[i]:
                current = values[i]
                yield current
            else:
                i += 1

    def __len__(self) -> int:
        return len(self.values)

    def __repr__(self) -> str:
        return f"MutablyIterableIndexedSet({self.values})"

    @overload
    def __getitem__(self, i: int) -> T:
        ...

    @overload
    def __getitem__(self, i: slice) -> Self:
        ...

    def __getitem__(self, i: int | slice) -> T | Self:
        if isinstance(i, int):
            return self.values[i]
        raise NotImplementedError("Slice indixing is not yet supported")

    def index(self, value: T, start: int = 0, stop: int = 2**32) -> int:
        i = self.indexes.get(value, -1)
        return i if start <= i < stop else -1

    def __delitem__(self, i: int | slice) -> None:
        if isinstance(i, int):
            return self.remove(self.values[i])
        raise NotImplementedError("Slice indixing is not yet supported")

    @overload
    def __setitem__(self, i: int, value: T) -> None:
        ...

    @overload
    def __setitem__(self, i: slice, iterable: Iterable[T]) -> None:
        ...

    def __setitem__(self, i: int | slice, vals: Any) -> None:
        if isinstance(i, int):
            new_value, old_value = vals, self.values[i]
            if new_value != old_value:
                if new_value in self.indexes:
                    raise ValueError(f"{new_value!r} is already in the set")
                del self.indexes[old_value]
                self.values[i] = new_value
                self.indexes[new_value] = i
        raise NotImplementedError("Slice indixing is not yet supported")

    def insert(self, i: int, element: T) -> None:
        if i == len(self.values):
            if element in self.indexes:
                raise ValueError(f"{element!r} is already in the set")
            return self.add(element)
        old_value = self.values[i]
        if element != old_value:
            if element in self.indexes:
                raise ValueError(f"{element!r} is already in the set")
            self.indexes[old_value] = len(self.values)
            self.values.append(old_value)
            self.indexes[element] = i
            self.values[i] = element

    def add(self, element: T) -> None:
        if element not in self.indexes:
            self.values.append(element)
            self.indexes[element] = len(self.indexes)

    def push(self, element: T) -> int:
        i = self.indexes.get(element, len(self.indexes))
        if i == len(self.values):
            self.values.append(element)
            self.indexes[element] = i
        return i

    def update(self, elements: Iterable[T]) -> None:
        for x in elements:
            self.add(x)

    def discard(self, element: T) -> None:
        if element in self.indexes:
            self.remove(element)

    def remove(self, element: T) -> None:
        i = self.indexes.pop(element)
        if i == len(self.indexes):
            self.values.pop()
        else:
            self.values[i] = self.values.pop()
            self.indexes[self.values[i]] = i


class MutablyIterableIndexedSet2(MutableSequence[T], MutableSet[T]):
    __slots__ = ("indexes", "values")

    def __init__(self, iterable: Iterable[T] = ()):
        elements = dict.fromkeys(iterable)
        self.values: list[T] = list(elements)
        self.indexes: dict[T, int] = {v: i for i, v in enumerate(elements)}

    def __contains__(self, element: Any) -> bool:
        return element in self.indexes

    def __iter__(self) -> Iterator[T]:
        i, values, current = 0, self.values, object()
        while i < len(values):
            if current is not values[i]:
                current = values[i]
                yield current
            else:
                i += 1

    def __len__(self) -> int:
        return len(self.values)

    def __repr__(self) -> str:
        return f"MutablyIterableIndexedSet({self.values})"

    @overload
    def __getitem__(self, i: int) -> T:
        ...

    @overload
    def __getitem__(self, i: slice) -> Self:
        ...

    def __getitem__(self, i: int | slice) -> T | Self:
        if isinstance(i, int):
            return self.values[i]
        raise NotImplementedError("Slice indixing is not yet supported")

    def index(self, value: T, start: int = 0, stop: int = 2**32) -> int:
        i = self.indexes.get(value, -1)
        return i if start <= i < stop else -1

    def __delitem__(self, i: int | slice) -> None:
        if isinstance(i, int):
            return self.remove(self.values[i])
        raise NotImplementedError("Slice indixing is not yet supported")

    @overload
    def __setitem__(self, i: int, value: T) -> None:
        ...

    @overload
    def __setitem__(self, i: slice, iterable: Iterable[T]) -> None:
        ...

    def __setitem__(self, i: int | slice, vals: Any) -> None:
        if isinstance(i, int):
            new_value, old_value = vals, self.values[i]
            if new_value != old_value:
                if new_value in self.indexes:
                    raise ValueError(f"{new_value!r} is already in the set")
                del self.indexes[old_value]
                self.values[i] = new_value
                self.indexes[new_value] = i
        raise NotImplementedError("Slice indixing is not yet supported")

    def insert(self, i: int, element: T) -> None:
        if i == len(self.values):
            if element in self.indexes:
                raise ValueError(f"{element!r} is already in the set")
            return self.add(element)
        old_value = self.values[i]
        if element != old_value:
            if element in self.indexes:
                raise ValueError(f"{element!r} is already in the set")
            self.indexes[old_value] = len(self.values)
            self.values.append(old_value)
            self.indexes[element] = i
            self.values[i] = element

    def add(self, element: T) -> None:
        if element not in self.indexes:
            self.values.append(element)
            self.indexes[element] = len(self.indexes)

    def push(self, element: T) -> int:
        i = self.indexes.get(element, len(self.indexes))
        if i == len(self.values):
            self.values.append(element)
            self.indexes[element] = i
        return i

    def update(self, elements: Iterable[T]) -> None:
        for x in elements:
            self.add(x)

    def discard(self, element: T) -> None:
        if element in self.indexes:
            self.remove(element)

    def remove(self, element: T) -> None:
        i = self.indexes.pop(element)
        if i == len(self.indexes):
            self.values.pop()
        else:
            self.values[i] = self.values.pop()
            self.indexes[self.values[i]] = i
