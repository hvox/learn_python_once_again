from collections.abc import Iterable
import random
import dataclasses


@dataclasses.dataclass
class Obstacle:
    x1: int
    y1: int
    x2: int
    y2: int


def generate(w: int, h: int, obstatcles: Iterable[Obstacle] = ()) -> list[int]:
    active_cells = [True] * w * h
    active_walls = [True] * w * h * 2
    for obstacle in obstatcles:
        for x in range(obstacle.x1, obstacle.x2):
            for y in range(obstacle.y1, obstacle.y2):
                active_cells[x + w * y] = False
    walls: list[tuple[int, int, int]] = []
    for x in range(w - 1):
        for y in range(h):
            walls.append((x, y, 0))
    for x in range(w):
        for y in range(h - 1):
            walls.append((x, y, 1))
    random.shuffle(walls)

    disjoint_sets = list(range(w * h))

    def get_set(i: int) -> int:
        if disjoint_sets[i] != i:
            disjoint_sets[i] = get_set(disjoint_sets[i])
        return disjoint_sets[i]

    for x1, y1, direction in walls:
        x2 = x1 + (1 - direction)
        y2 = y1 + (0 + direction)
        if not active_cells[x1 + y1 * w]:
            continue
        if x2 >= w or y2 >= h or not active_cells[x2 + y2 * w]:
            continue
        u = get_set(x1 + y1 * w)
        v = get_set(x2 + y2 * w)
        if u == v:
            continue
        disjoint_sets[u] = v
        active_walls[(x1 + y1 * w) * 2 + direction] = False
    maze = [
        1 * active_walls[2 * x + 2 * y * w + 0]
        + 2 * active_walls[2 * x + 2 * y * w + 1]
        + 4 * (x == 0 or active_walls[2 * (x - 1) + 2 * y * w + 0])
        + 8 * (y == 0 or active_walls[2 * x + 2 * (y - 1) * w + 1])
        for y in range(h)
        for x in range(w)
    ]
    return maze


w, h = 10, 10
maze = generate(w, h, [Obstacle(0, 0, 2, 2), Obstacle(3, 3, 10, 6)])
for y in reversed(range(h)):
    row: list[str] = []
    for x in range(w):
        row.append("╬╣╦╗╠║╔╥╩╝═╡╚╨╞?"[maze[x + y * w]])
    print("".join(row))
