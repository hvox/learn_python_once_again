#!/usr/bin/env python3.10
import os
import sys
import random
import png
import select
import contextlib
try:
    import termios
except ModuleNotFoundError:
    termios = None

FULL_BLOCK = "\u2588"


def get_background_color(timeout=0.1, default_color=(7710, 8738, 10794)):
    if not termios:
        return (3084, 3084, 3084)
    stdin_fd = sys.stdin.fileno()
    prev_flags = termios.tcgetattr(stdin_fd)
    flags = prev_flags.copy()
    flags[3] &= ~termios.ICANON & ~termios.ECHO
    termios.tcsetattr(stdin_fd, termios.TCSANOW, flags)
    sys.stdout.write("\x1b]11;?\x07")
    sys.stdout.flush()
    if select.select([sys.stdin], [], [], timeout)[0] != [sys.stdin]:
        termios.tcsetattr(stdin_fd, termios.TCSADRAIN, prev_flags)
        return default_color
    color = os.read(stdin_fd, 24)[9:23]
    termios.tcsetattr(stdin_fd, termios.TCSADRAIN, prev_flags)
    with contextlib.suppress(ValueError):
        color = tuple(int(color, 16) for color in color.decode().split("/"))
        if len(color) == 3 and all(0 <= x <= 65535 for x in color):
            return color


def index_to_permutation(permutation_size: int, index: int):
    if permutation_size == 0:
        return []
    p = index_to_permutation(permutation_size - 1, index // permutation_size)
    p.insert(index % permutation_size, len(p))
    return p


def apply_permutation(permutation: list[int], arg: list):
    result = [None] * len(permutation)
    for i, x in enumerate(arg):
        result[permutation[i]] = x
    return result


def print_color(red: int, green: int, blue: int):
    print(end=f"\x1b[38;2;{red};{green};{blue}m" + FULL_BLOCK * 2)


def print_rgba(red: int, green: int, blue: int, alpha: int, back: list[int]):
    background = tuple(round(x * (255 - alpha) / 255) for x in back)
    red = round(red * alpha / 255) + background[0]
    blue = round(blue * alpha / 255) + background[2]
    green = round(green * alpha / 255) + background[1]
    print(end=f"\x1b[38;2;{red};{green};{blue}m" + FULL_BLOCK * 2)


def print_random_colors():
    perm = index_to_permutation(3, random.randint(0, 5))
    base_color = random.randint(0, 255)
    for x in range(0, 256, 8):
        for y in range(0, 256, 8):
            print_color(*apply_permutation(perm, (x, y, base_color)))
        print("\x1b[1;39m")


def load_png(path: str):
    width, height, rows, info = png.Reader(path).read()
    assert info["bitdepth"] == 8 and info["alpha"]
    image = [[None] * width for _ in range(height)]
    for y, row in enumerate(rows):
        for x, pixel in enumerate(row[i:i+4] for i in range(0, len(row), 4)):
            image[y][x] = tuple(pixel)
    return width, height, image


background = tuple(round(x / 257) for x in get_background_color())
for path in sys.argv[1:]:
    width, height, pixels = load_png(path)
    print("width:", width, " height:", height)
    for row in pixels:
        for red, green, blue, alpha in row:
            print_rgba(red, green, blue, alpha, background)
        print("\x1b[1;39m")
