import array
from itertools import chain
from typing import Iterable, Self, TypeVar, overload

T = TypeVar("T")


def windows(elements: Iterable[T], n: int) -> Iterable[list[T]]:
    it = iter(elements)
    while window := [x for _, x in zip(range(n), it)]:
        yield window


class BitArray:
    def __init__(self, content: Iterable[int] = ()):
        self.size, self.data = 0, array.array("B")
        for byte in windows(content, 8):
            self.data.append(sum(b << i for i, b in enumerate(byte)))
            self.size += len(byte)

    def append(self, value: int):
        if self.size % 8 == 0:
            self.data.append(value)
        else:
            self.data[self.size // 8] |= value << (self.size % 8)
        self.size += 1

    def extend(self, values: Iterable[int]):
        for value in values:
            self.append(value)

    def zfill(self, length: int | None = None) -> Self:
        if length is None:
            length = (self.size + 7) // 8 * 8
        zeros = (0 for _ in range(max(0, length - self.size)))
        return self.__class__(chain(self, zeros))

    @classmethod
    def from_unsigned(cls, number: int, bits: int = 8) -> Self:
        self = cls.from_bytes(number.to_bytes((bits + 7) // 8, "little"))
        self.size = bits
        return self

    def to_unsigned(self) -> int:
        return sum(x << i for i, x in enumerate(self))

    @classmethod
    def from_bytes(cls, data: bytes):
        self = cls()
        self.size = len(data) * 8
        self.data = array.array("B", data)
        return self

    def to_bytes(self) -> bytes:
        assert self.size % 8 == 0
        return bytes(self.data)

    @overload
    def __getitem__(self, i: int) -> int:
        ...

    @overload
    def __getitem__(self, i: slice) -> Self:
        ...

    def __getitem__(self, i: int | slice) -> int | Self:
        if isinstance(i, int):
            return self.data[i // 8] >> (i % 8) & 1
        start = 0 if i.start is None else i.start
        stop = self.size if i.stop is None else i.stop
        assert i.step is None or i.step == 1
        return self.__class__((self[j] for j in range(start, stop)))

    def __setitem__(self, i: int, value: int):
        assert 0 <= i < self.size and 0 <= value <= 1
        i, shift = divmod(i, 8)
        self.data[i] = self.data[i] & (~(1 << shift)) | (value << shift)

    def __iter__(self):
        yield from (self.data[i // 8] >> (i % 8) & 1 for i in range(self.size))

    def __repr__(self):
        return f"{self.__class__.__qualname__}({list(self)})"

    def __str__(self):
        return "[" + "".join("01"[x] for x in self) + "]"

    def __len__(self) -> int:
        return self.size
