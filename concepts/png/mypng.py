#!/usr/bin/env python3
import zlib
from sys import stderr, argv
from pathlib import Path
from enum import IntEnum
from struct import unpack


class ColorType(IntEnum):
    W = 0
    RGB = 2
    INDEX = 3
    WA = 4
    RGBA = 6

    def __init__(self, number: int):
        self.allowed_depths = {
            0: (1, 2, 4, 8, 16),
            2: (8, 16),
            3: (1, 2, 4, 8),
            4: (8, 16),
            6: (8, 16),
        }[number]
        self.channels = [1, 0, 3, 1, 2, 0, 4][number]


SIGNATURE = b"\x89PNG\r\n\x1a\n"
SUPPORTED_CHUNK_TYPES = b"IHDR IEND PLTE IDAT".split()


def read_header(data: bytes):
    width, height, depth, clr_typ, compression, filtr, interlace = unpack(">IIBBBBB", data)
    clr_typ = ColorType(clr_typ)
    assert 1 <= width < 2**31 and 1 <= height < 2**31 and depth in clr_typ.allowed_depths
    assert compression == filtr == 0
    assert interlace == 0  # TODO: support Adam7 thumbnail
    print(width, height, depth, clr_typ.name, compression, filtr, interlace)
    return (width, height, depth, clr_typ)


def read_palette(data: bytes):
    return [data[i: i + 3] for i in range(0, len(data), 3)]


def read_pixels(width: int, height: int, depth: int, clr_typ: int, data: bytes):
    data = zlib.decompress(data)
    bits_per_pixel = depth * clr_typ.channels
    print(bits_per_pixel, data.hex())
    d = bytes_per_pixel = (bits_per_pixel + 7) // 8
    line_length = (bits_per_pixel * width + 7) // 8 + 1
    fltrs = [data[i] for i in range(0, len(data), line_length)]
    lines = [bytearray(data[i + 1: i + line_length]) for i in range(0, len(data), line_length)]
    for y, (fltr, line) in enumerate(zip(fltrs, lines)):
        print(f"{y} {fltr}:{line.hex()}")
        assert 0 <= fltr <= 4
        if fltr == 0:  # None
            pass
        elif fltr == 1:  # Sub
            for x in range(line_length - 1):
                line[x] = (line[x] + (line[x - d] if x >= d else 0)) % 256
        elif fltr == 2:  # Up
            for x in range(line_length - 1):
                line[x] = (line[x] + (lines[y - 1][x] if y > 0 else 0)) % 256
        elif fltr == 3:  # Avg
            for x in range(line_length - 1):
                left = line[x - d] if x >= d else 0
                up = lines[y - 1][x] if y > 0 else 0
                line[x] = (line[x] + (left + up) // 2) % 256
        elif fltr == 4:  # Peach
            for x in range(line_length - 1):
                left = line[x - d] if x >= d else 0
                up = lines[y - 1][x] if y > 0 else 0
                upleft = lines[y - 1][x - d] if y > 0 and x >= d else 0
                p = left + up - upleft
                peach = (
                    left if abs(p - up) >= abs(p - left) <= abs(p - upleft) else
                    up if abs(p - up) <= abs(p - upleft) else upleft
                )
                line[x] = (line[x] + peach) % 256
    if bits_per_pixel < 8:
        lines = [
            bytes(
                line[x // 8] >> (7 - (x % 8)) & ((1 << bits_per_pixel) - 1)
                for x in range(0, width * bits_per_pixel, bits_per_pixel)
            )
            for line in lines
        ]
    pixels = [
        [line[x * bytes_per_pixel: x * bytes_per_pixel + bytes_per_pixel] for x in range(width)]
        for line in lines
    ]
    return pixels


def read_png(png_bytes: bytes):
    assert png_bytes[:8] == SIGNATURE
    i, chunks = 8, []
    while i < len(png_bytes):
        length, typ = unpack(">I4s", png_bytes[i: i + 8])
        data = png_bytes[i + 8: i + 8 + length]
        i += 12 + length
        assert zlib.crc32(typ + data) == unpack(">I", png_bytes[i - 4: i])[0]
        chunks.append((typ, data))
        print(f"{typ.decode()} {data.hex()}")
        if ~typ[0] & 1 << 5 and typ not in SUPPORTED_CHUNK_TYPES:
            print(f"  Unsupported critical chuck: {typ.decode()}", file=stderr)
    assert chunks[0][0] == b"IHDR"
    width, height, depth, clr_typ = read_header(chunks[0][1])
    i, palette = 0, None
    if clr_typ == ColorType.INDEX:
        while chunks[i][0] != b"PLTE":
            i += 1
        palette = read_palette(chunks[i][1])
    while chunks[i][0] != b"IDAT":
        i += 1
    lines = read_pixels(width, height, depth, clr_typ, chunks[i][1])
    image = []
    for y, line in enumerate(lines):
        print("".join([["  ", "██"][bool(x[0])] for x in line]))
        row = []
        for pixel in line:
            if clr_typ == ColorType.INDEX:
                row.append(palette[pixel[0]])
            else:
                row.append(pixel)
        image.append(row)
    return image


for png_path in argv[1:]:
    if len(argv[1:]) > 1:
        print("\n> " + png_path)
    for line in read_png(Path(png_path).read_bytes()):
        s = " ".join(pixel.hex() for pixel in line)
        print(s if len(s) < 160 else s[:157] + "...")
