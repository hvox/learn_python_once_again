from collections.abc import Iterator
from typing import override


class BinaryIndexedTree:
    nodes: list[int]

    def __init__(self, elements: list[int]):
        # one redundant zero for indexation from 1
        self.nodes = [0] * (len(elements) + 1)
        for i, value in enumerate(elements, 1):
            j = (i & (-i)) // 2
            while j:
                value += self.nodes[i - j]
                j //= 2
            self.nodes[i] = value

    def prefix_sum(self, length: int = 0) -> int:
        result = 0
        while length:
            result += self.nodes[length]
            length -= length & (-length)
        return result

    def sum(self, start: int, end: int) -> int:
        # alternative: difference of prefix sums
        i, j, result = start, end + 1, 0
        while j > i:
            result += self.nodes[j]
            j -= j & (-j)
        while i > j:
            result -= self.nodes[i]
            i -= i & (-i)
        return result

    def __getitem__(self, index: int) -> int:
        return self.sum(index, index)

    def __setitem__(self, index: int, value: int) -> None:
        delta = value - self[index]
        index += 1
        while index < len(self.nodes):
            self.nodes[index] += delta
            index += index & (-index)

    def __iter__(self) -> Iterator[int]:
        for i, value in enumerate(self.nodes[1:], 1):
            j = (i & (-i)) // 2
            while j:
                value -= self.nodes[i - j]
                j //= 2
            yield value

    def __len__(self) -> int:
        return len(self.nodes) - 1

    @override
    def __repr__(self) -> str:
        return f"{self.__class__.__qualname__}({list(self)})"
