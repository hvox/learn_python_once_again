#!/usr/bin/env python3.10
import os
import sys
import png
import select
import contextlib

try:
    import termios
except ModuleNotFoundError:
    termios = None

UPPER_BLOCK, FULL_BLOCK = "\u2580\u2588"


def get_background_color(timeout=0.1, default_color=(7710, 8738, 10794)):
    # TODO: use more pythonic way to handle optional imports
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


class ByteArray2d:
    def __init__(self, width: int, height: int):
        self.width, self.height = width, height
        self.elements = bytearray(width * height)

    def __getitem__(self, index: tuple[int, int]) -> int:
        x, y = index[0] % self.width, index[1] % self.height
        return self.elements[y * self.width + x]

    def __setitem__(self, index: tuple[int, int], value: int):
        x, y = index[0] % self.width, index[1] % self.height
        self.elements[y * self.width + x] = value


def print_image(pixels: ByteArray2d, palette: list[tuple[int, int, int]]):
    colors = [f"8;2;{r};{g};{b}m" for r, g, b in palette]
    bts, w, h = pixels.elements, pixels.width, pixels.height
    for y in range(h - 2, 0, -2):
        for bottom, top in zip(bts[y * w - w: y * w], bts[y * w: y * w + w]):
            top, bottom = colors[top], colors[bottom]
            block = " " if top == bottom else UPPER_BLOCK
            top = "9m" if top == bottom else top
            print("\x1b[3" + top + "\x1b[4" + bottom + block, end="")
        print("\x1b[1;39m\x1b[1;49m")


def load_image(path: str) -> tuple[ByteArray2d, list[tuple[int, ...]]]:
    width, height, rows, info = png.Reader(path).read()
    assert info["bitdepth"] == 8 and info["alpha"]
    image, palette = ByteArray2d(width, height), {}
    for y, row in enumerate(map(tuple, rows)):
        for x, color in enumerate(row[i:i+4] for i in range(0, len(row), 4)):
            color_index = palette.setdefault(color, len(palette))
            image.elements[(height - y - 1) * width + x] = color_index
    return image, palette


def blend(x: tuple[int, ...], y: tuple[int, ...], alpha: int):
    return tuple((x * alpha + y * (255 - alpha)) // 255 for x, y in zip(x, y))


if __name__ == "__main__":
    background = tuple(round(x / 257) for x in get_background_color())
    for path in sys.argv[1:]:
        pixels, palette = load_image(path)
        palette = [blend((r, g, b), background, a) for r, g, b, a in palette]
        print_image(pixels, palette)
