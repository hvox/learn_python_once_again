# Inspired by Yahor, I made this simple maze generator.
import random, sys

DIRECTIONS = ((0, 2), (-2, 0), (0, -2), (2, 0))
BLOCKS = ["  ", "\u2588" * 2]
show = lambda *strings: print(*strings) or input()

n = (int(sys.argv[1])) if len(sys.argv) > 1 else 10
random.seed(int(sys.argv[2]) if len(sys.argv) > 2 else None)
walls = [[1 for _ in range(n * 2 + 1)] for _ in range(n * 2 + 1)]
show("\n".join("".join(BLOCKS[c] for c in row) for row in walls))
queue = [(1, -1)]
while queue:
    x1, y1 = queue[-1]
    next_moves = [
        (x2, y2)
        for x2, y2 in ((x1 + dx, y1 + dy) for dx, dy in DIRECTIONS)
        if (0 <= x2 < len(walls) and 0 <= y2 < len(walls) and walls[x2][y2])
    ]
    if next_moves:
        x2, y2 = random.choice(next_moves)
        walls[x2][y2] = walls[(x1 + x2) // 2][(y1 + y2) // 2] = 0
        queue.append((x2, y2))
        show("\n".join("".join(BLOCKS[c] for c in row) for row in walls))
    else:
        queue.pop()
        if len(queue) > 1:
            i = random.randint(0, len(queue) - 1)
            queue[i], queue[-1] = queue[-1], queue[i]
walls[~1][~0] = 0
while not show("\n".join("".join(BLOCKS[c] for c in row) for row in walls)):
    pass
