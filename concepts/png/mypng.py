#!/usr/bin/env python3
import zlib
from sys import stderr, argv
from pathlib import Path
from enum import IntEnum
from struct import unpack


class PNGError(Exception):
    pass


def error(error_msg):
    raise PNGError("Bad " + error_msg)


def assure(condition: bool, error_msg: str):
    if not condition:
        error(error_msg)


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


def read_png(buf: bytes):
    chunks = read_chunks(buf)
    typ, data = next(chunks)
    assure(typ == b"IHDR", "first chunk: it should be IHDR")
    width, height, depth, clr_typ = read_header(data)
    if clr_typ == ColorType.INDEX:
        _, data = next_chunk(chunks, b"PLTE")
        palette = read_palette(data)
        _, data = next_chunk(chunks, b"IDAT")
        pixels = read_pixel_data(width, height, clr_typ, depth, data)
        for line in pixels:
            for x, index in enumerate(line):
                line[x] = palette[index[0]]
    else:
        _, data = next_chunk(chunks, b"IDAT")
        pixels = read_pixel_data(width, height, clr_typ, depth, data)
    return pixels


def read_chunks(buf: bytes):
    assure(buf[:8] == b"\x89PNG\r\n\x1a\n", "png signature")
    assure(len(buf) >= 42, "file size: the file is almost empty")
    i = 8
    while i < len(buf):
        assure(len(buf) - i >= 12, "chunk size")
        length, typ = unpack(">I4s", buf[i: i + 8])
        assure(len(buf) - i >= 12 + length, f"{typ} chunk size")
        data = buf[i + 8: i + 8 + length]
        i += 12 + length
        crc = unpack(">I", buf[i - 4: i])[0]
        assure(crc == zlib.crc32(typ + data), f"{typ} chunk CRC")
        if typ == "IEND":
            break
        yield typ, data
    else:
        error("chunks: there must be IEND chunk at the end")
    yield typ, data


def next_chunk(chunks, desired_chunks: bytes):
    desired_chunks_set = set(desired_chunks.split(b" "))
    for typ, data in chunks:
        if typ in desired_chunks_set:
            return typ, data
        assure(typ[0] & 1 << 5, f"chunk: {typ}. Expected {desired_chunks.decode()}")
    error("chunk order: unexpected end of file")


def read_header(data: bytes):
    assure(len(data) == 13, "IHDR: it should be exactly 25 bytes long")
    width, height, depth, clr_typ, compression, filtr, interlace = unpack(">IIBBBBB", data)
    assure(1 <= width <= 2**31 - 1, "width: it should be between 1 and 2^31-1")
    assure(1 <= height <= 2**31 - 1, "height: it should be between 1 and 2^31-1")
    assure(clr_typ in (0, 2, 3, 4, 6), "color type")
    clr_typ = ColorType(clr_typ)
    assure(depth in clr_typ.allowed_depths, "bit depth")
    assure(compression == 0, "compression method: it should be 0")
    assure(filtr == 0, "filter method: it should be 0")
    # TODO: support Adam7 interlace
    assert interlace == 0, "TODO: support Adam7 interlace"
    return (width, height, depth, clr_typ)


def read_palette(data: bytes):
    assure(len(data) % 3 == 0, "palette: it should have integer number of colors")
    return [data[i: i + 3] for i in range(0, len(data), 3)]


def read_pixel_data(width: int, height: int, clr_typ: int, depth: int, data: bytes):
    # TODO errors?
    data = zlib.decompress(data)
    bits_per_pixel = depth * clr_typ.channels
    d = bytes_per_pixel = (bits_per_pixel + 7) // 8
    line_length = (bits_per_pixel * width + 7) // 8 + 1
    fltrs = [data[i] for i in range(0, len(data), line_length)]
    lines = [bytearray(data[i + 1: i + line_length]) for i in range(0, len(data), line_length)]
    for y, (fltr, line) in enumerate(zip(fltrs, lines)):
        print(f"{y}:f{fltr} " + " ".join(
                line[i: i + bytes_per_pixel].hex() for i in range(0, len(line), bytes_per_pixel)
        ))
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


for png_path in argv[1:]:
    if len(argv[1:]) > 1:
        print("\n> " + png_path)
    for line in read_png(Path(png_path).read_bytes()):
        s = " ".join(pixel.hex() for pixel in line)
        print(s if len(s) < 160 else s[:157] + "...")
