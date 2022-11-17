# bins - idea for package name if I ever put this thing on pypy
from collections.abc import Hashable, MutableSequence, MutableSet, Sequence, Set
from typing import Any, Iterable, Iterator, Self, TypeVar, overload
from random import randint

T = TypeVar("T")


class OrderedSet(Set[T]):
    __slots__ = ("elements",)

    def __init__(self, iterable: Iterable[T] = ()):
        self.elements: dict[T, None] = dict.fromkeys(iterable)

    def __contains__(self, element: Any) -> bool:
        return element in self.elements

    def __iter__(self) -> Iterator[T]:
        return iter(self.elements)

    def __len__(self) -> int:
        return len(self.elements)

    def __repr__(self) -> str:
        return f"OrderedSet({list(self.elements)})"


class MutableOrderedSet(OrderedSet[T], MutableSet[T]):
    def add(self, element: T) -> None:
        self.elements[element] = None

    def update(self, elements: Iterable[T]) -> None:
        for x in elements:
            self.add(x)

    def discard(self, element: T) -> None:
        self.elements.pop(element, None)

    def remove(self, element: T) -> None:
        del self.elements[element]


class GrowableOrderedSet(OrderedSet[T]):
    __slots__ = ("values", "indexes")

    def __init__(self, iterable: Iterable[T] = ()):
        elements = dict.fromkeys(iterable)
        self.values: list[T] = list(elements)
        self.indexes: dict[T, int] = {v: i for i, v in enumerate(elements)}

    def add(self, element: T) -> None:
        if element not in self.indexes:
            self.values.append(element)
            self.indexes[element] = len(self.indexes)

    def __contains__(self, element: Any) -> bool:
        return element in self.indexes

    def __iter__(self) -> Iterator[T]:
        return iter(self.values)

    def __len__(self) -> int:
        return len(self.values)

    def __repr__(self) -> str:
        return f"OrderedSet({self.values})"


class FrozenOrderedSet(OrderedSet[T], Hashable):
    def __hash__(self) -> int:
        return hash(tuple(self.elements))


class IndexedSet(Sequence[T], Set[T]):
    __slots__ = ("indexes", "values")

    def __init__(self, iterable: Iterable[T] = ()):
        elements = dict.fromkeys(iterable)
        self.values: list[T] = list(elements)
        self.indexes: dict[T, int] = {v: i for i, v in enumerate(elements)}

    def __contains__(self, element: Any) -> bool:
        return element in self.indexes

    def __iter__(self) -> Iterator[T]:
        return iter(self.values)

    def __len__(self) -> int:
        return len(self.values)

    def __repr__(self) -> str:
        return f"IndexedSet({self.values})"

    @overload
    def __getitem__(self, i: int) -> T:
        ...

    @overload
    def __getitem__(self, i: slice) -> Self:
        ...

    def __getitem__(self, i: int | slice) -> T | Self:
        if isinstance(i, int):
            return self.values[i]
        start = i.start if i.start is not None else 0
        stop = i.stop if i.stop is not None else len(self.values) - 1
        step = i.step if i.step is not None else 1
        return IndexedSet(self.values[i] for i in range(start, stop, step))

    def index(self, value: T, start: int = 0, stop: int = 2**32) -> int:
        i = self.indexes.get(value, -1)
        return i if start <= i < stop else -1


class FrozenIndexedSet(IndexedSet[T], Hashable):
    def __hash__(self) -> int:
        return hash(tuple(self.values))


class MutableIndexedSet(IndexedSet[T], MutableSequence[T], MutableSet[T]):
    def __delitem__(self, i: int | slice) -> None:
        if isinstance(i, int):
            return self.remove(self.values[i])
        start = i.start if i.start is not None else 0
        stop = i.stop if i.stop is not None else len(self.values) - 1
        step = i.step if i.step is not None else 1
        for i in range(start, stop, step) if step < 0 else reversed(range(start, stop, step)):
            self.remove(self.values[i])

    @overload
    def __setitem__(self, i: int, value: T) -> None:
        ...

    @overload
    def __setitem__(self, i: slice, iterable: Iterable[T]) -> None:
        ...

    def __setitem__(self, i: int | slice, vals: Any) -> None:
        match i:
            case int(i):
                new_value, old_value = vals, self.values[i]
                if new_value != old_value:
                    if new_value in self.indexes:
                        raise ValueError(f"{new_value!r} is already in the set")
                    del self.indexes[old_value]
                    self.values[i] = new_value
                    self.indexes[new_value] = i
            case i:
                start = i.start if i.start is not None else 0
                stop = i.stop if i.stop is not None else len(self.values) - 1
                step = i.step if i.step is not None else 1
                slice_size, new_values = (stop - start) // step, list(vals)
                if slice_size != len(new_values):
                    raise ValueError(
                        f"attempt to assign sequence of size {len(new_values)} "
                        f"to extended slice of size {slice_size}"
                    )
                for i in range(start, stop, step):
                    del self.indexes[self.values[i]]
                for i, value in zip(range(start, stop, step), new_values):
                    if value in self.indexes:
                        raise ValueError(f"{value!r} is already in the set")
                    self.values[i] = value
                    self.indexes[value] = i

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

    def freeze(self) -> FrozenIndexedSet[T]:
        frozen_set: FrozenIndexedSet[T] = FrozenIndexedSet()
        frozen_set.values, frozen_set.indexes = self.values, self.indexes
        self.values, self.indexes = [], {}
        return frozen_set


U32_MAX = 2**32 - 1
INT_TO_ID = 1777797467
ID_TO_INT = pow(INT_TO_ID, -1, U32_MAX + 1)


class Storage(MutableSequence[T]):
    __slots__ = ("values", "ids", "id_generation_seed")

    def __init__(self, iterable: Iterable[T] = (), seed: int | None = None):
        if isinstance(iterable, dict) and seed is not None:
            self.ids = MutableIndexedSet(iterable.keys())
            self.values = list(iterable.values())
            self.id_generation_seed = seed & U32_MAX
            return
        if seed is None:
            seed = randint(0, U32_MAX)
        else:
            seed = (1 + seed % U32_MAX) * INT_TO_ID & U32_MAX
        self.values = list(iterable)
        seeds = range(seed, len(self.values) + seed)
        self.ids = MutableIndexedSet(i * INT_TO_ID & U32_MAX for i in seeds)
        self.id_generation_seed = seed + len(self.values)

    def __len__(self) -> int:
        return len(self.values)

    def __iter__(self) -> Iterator[T]:
        return iter(self.values)

    def items(self) -> Iterator[tuple[int, T]]:
        for i, value in enumerate(self.values):
            yield self.ids[i], value

    def insert(self, i: int, value: T) -> None:
        if i != self.id_generation_seed * INT_TO_ID & U32_MAX:
            raise IndexError("Random access insertion is not possible")
        self.push(value)

    def append(self, value: T) -> None:
        self.push(value)

    def push(self, value) -> int:
        i = self.id_generation_seed * INT_TO_ID & U32_MAX
        self.id_generation_seed += 1
        self.values.append(value)
        self.ids.push(i)
        return i

    def __delitem__(self, i: int | slice) -> None:
        if not isinstance(i, int):
            raise TypeError("Indexing <storage_object> by slice is not possible")
        if i not in self.ids:
            raise IndexError("Invalid ID was provided")
        self.values[self.ids.index(i)] = self.values.pop()
        self.ids.remove(i)

    def __str__(self):
        return "[" + " ".join(f"{i:08x}:{v!r}" for i, v in self.items()) + "]"

    def __repr__(self):
        seed = f"{self.id_generation_seed:#010x}"
        items = ", ".join(f"{i:#010x}:{v!r}" for i, v in self.items())
        return "Storage({" + items + "}, " + f"seed={seed})"

    @overload
    def __getitem__(self, i: int) -> T:
        ...

    @overload
    def __getitem__(self, i: slice) -> Self:
        ...

    def __getitem__(self, i: int | slice) -> T | Self:
        if not isinstance(i, int):
            raise TypeError("Indexing <storage_object> by slice is not possible")
        return self.values[self.ids.index(i)]

    @overload
    def __setitem__(self, i: int, value: T) -> None:
        ...

    @overload
    def __setitem__(self, i: slice, iterable: Iterable[T]) -> None:
        ...

    def __setitem__(self, i: int | slice, value: Any) -> None:
        if not isinstance(i, int):
            raise TypeError("Indexing <storage_object> by slice is not possible")
        self.values[self.ids.index(i)] = value

    def index(self, value: T, start: int = 0, stop: int = 2**32) -> int:
        return self.ids[self.values.index(value, start, stop)]
