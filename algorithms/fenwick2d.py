from typing import override


class BinaryIndexedTree2D:
    def __init__(self, array2d: list[list[int]]):
        height = len(array2d)
        width = len(array2d[0])
        self.shape = (height, width)
        self.nodes = [[0] * (width + 1)]
        for x, array_row in enumerate(array2d, 1):
            row = [0] + list(array_row)
            for y, value in enumerate(array_row, 1):
                dy = (y & (-y)) // 2
                while dy:
                    value += row[y - dy]
                    dy //= 2
                row[y] = value
            dx = (x & (-x)) // 2
            while dx:
                row = [x + y for x, y in zip(row, self.nodes[x - dx])]
                dx //= 2
            self.nodes.append(row)

    def sum(self, x1: int, y1: int, x2: int, y2: int) -> int:
        x2 += 1
        result = 0
        while x2 > x1:
            i, j = y1, y2 + 1
            while j > i:
                result += self.nodes[x2][j]
                j -= j & (-j)
            while i > j:
                result -= self.nodes[x2][i]
                i -= i & (-i)
            x2 -= x2 & (-x2)
        while x1 > x2:
            i, j = y1, y2 + 1
            while j > i:
                result -= self.nodes[x1][j]
                j -= j & (-j)
            while i > j:
                result += self.nodes[x1][i]
                i -= i & (-i)
            x1 -= x1 & (-x1)
        return result

    def __getitem__(self, index: tuple[int, int]) -> int:
        x, y = index
        return self.sum(x, y, x, y)

    def __setitem__(self, index: tuple[int, int], value: int) -> None:
        delta = value - self[index]
        x, y0 = (x + 1 for x in index)
        while x < len(self.nodes):
            y = y0
            while y < len(self.nodes[0]):
                self.nodes[x][y] += delta
                y += y & (-y)
            x += x & (-x)

    @override
    def __repr__(self) -> str:
        height, width = self.shape
        lst = [[self[x, y] for y in range(width)] for x in range(height)]
        return f"{self.__class__.__qualname__}({lst})"
