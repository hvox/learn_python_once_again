from __future__ import annotations

from array import array
from dataclasses import dataclass, field
from itertools import count
from pathlib import Path
from struct import unpack
from typing import Any, Callable, Literal, NamedTuple, Self, Sequence
from zlib import compress, crc32, decompress

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


class FloatArray(array):
    def __setitem__(self, index: Any, value: Any):
        if isinstance(index, slice) and not isinstance(value, array):
            value = array("f", value)
        array.__setitem__(self, index, value)


@dataclass
class Image:
    width: int
    height: int
    pixels: Sequence[float]

    def __iter__(self):
        yield from (self.width, self.height, self.pixels)

    def __post_init__(self):
        if not isinstance(self.pixels, FloatArray):
            self.pixels = FloatArray("f", self.pixels)


@dataclass
class Chunk:
    typ: str
    position: Literal["begin", "palette", "end"]
    data: bytes


Palette = tuple[tuple[float, float, float, float], ...]


@dataclass
class PNG:
    image: Image
    gamma: float | None = None
    bitdepth: int = 16
    interlacing: bool = False
    colors: Literal["L", "LA", "RGB", "RGBA"] | Palette = "RGBA"
    tags: dict[str, str] = field(default_factory=dict)
    extra_chunks: dict[str, list[Chunk]] = field(default_factory=dict)

    @staticmethod
    def decode(data: bytes, fltr: Callable[[str], bool] | None = None) -> PNG:
        return decode_png(data, fltr)


def decode_png(data: bytes, fltr: Callable[[str], bool] | None = None) -> PNG:
    fltr = (lambda typ: typ[3].islower()) if fltr is None else fltr
    chunks = split_chunks(data)
    w, h, bitdepth, colors = decode_ihdr(chunks[0][1])
    gama_index = find_chunk(chunks, 1, "gAMA", strict=False)
    plte_index = find_chunk(chunks, 1, "PLTE", strict=False)
    idat_index = find_chunk(chunks, 1, "IDAT", strict=True)
    assure(gama_index <= plte_index < idat_index, "chunk ordering")
    gamma = decode_gama(chunks[gama_index][1]) if gama_index != -1 else None
    if colors is None:
        assure(plte_index != -1, "color type")
        colors = decode_plte(chunks[plte_index][1])
    channels = len(colors) if isinstance(colors, str) else 1
    pixels: Any = decode_idat(chunks[idat_index][1], w, h, bitdepth, channels)
    if not isinstance(colors, str):
        pixels = sum((colors[color_index] for color_index in pixels), array("f"))
    image = Image(w, h, pixels)
    png = PNG(image, gamma, bitdepth)
    return png


def decode_ihdr(data: bytes) -> tuple[int, int, int, Any]:
    width, height, depth, clr_typ, compression, filtr, interlace = unpack(">IIBBBBB", data)
    assure(1 <= width <= 2**31 - 1 and 1 <= height <= 2**31 - 1, "image size")
    assure(compression == 0 and filtr == 0 and interlace in (0, 1), "IHDR last bytes")
    assert interlace == 0, "TODO: support Adam7 interlace"
    color_type_is_ok = (  # TODO: Use any(), when mypy is fixed
        clr_typ == 0 and depth in (1, 2, 4, 8, 16),
        clr_typ in (2, 4, 6) and depth in (8, 16),
        clr_typ == 3 and depth in (1, 2, 4, 8),
    )
    assure(any(color_type_is_ok), "image color type")
    colors = ["L", None, "RGB", None, "LA", None, "RGBA"][clr_typ]
    return (width, height, depth, colors)


def decode_gama(data: bytes) -> float:
    gamma = unpack(">I", data)[0] / 100000
    return gamma


def decode_plte(data: bytes) -> Palette:
    assure(len(data) % 3 == 0, "PLTE size")
    return tuple((r / 255, g / 255, b / 255, 1.0) for r, g, b in (data[i: i + 3] for i in range(0, len(data), 3)))


def decode_idat(data: bytes, width: int, height: int, bitdepth: int, channels: int) -> Any:
    # TODO: raise PNGError on errors?
    data = decompress(data)
    bits_per_pixel = bitdepth * channels
    d = bytes_per_pixel = (bits_per_pixel + 7) // 8
    line_length = (bits_per_pixel * width + 7) // 8 + 1
    fltrs = [data[i] for i in range(0, len(data), line_length)]
    lines = [bytearray(data[i + 1: i + line_length]) for i in range(0, len(data), line_length)]
    for y, (fltr, line) in enumerate(zip(fltrs, lines)):
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
                    left
                    if abs(p - up) >= abs(p - left) <= abs(p - upleft)
                    else up
                    if abs(p - up) <= abs(p - upleft)
                    else upleft
                )
                line[x] = (line[x] + peach) % 256
    if bits_per_pixel < 8:
        lines = [
            bytearray(
                line[x // 8] >> (7 - (x % 8)) & ((1 << bits_per_pixel) - 1)
                for x in range(0, width * bits_per_pixel, bits_per_pixel)
            )
            for line in lines
        ]
    pixels = [
        [line[x * bytes_per_pixel: x * bytes_per_pixel + bytes_per_pixel] for x in range(width)]
        for line in lines
    ]
    return bytes(channel for line in pixels for pixel in line for channel in pixel)


def split_chunks(bytes: bytes) -> list[tuple[str, bytes]]:
    assure(bytes[:8] == PNG_SIGNATURE, "PNG Signature")
    i, chunks = 8, []
    while i < len(bytes):
        assure(len(bytes) - i >= 12, "Chunk size")
        length, typ = unpack(">I4s", bytes[i: i + 8])
        assure(is_correct_chunk_type(typ), "chunk type")
        assure(len(bytes) - i >= 12 + length, f"{typ} chunk size")
        data = bytes[i + 8: i + 8 + length]
        i += 12 + length
        crc = unpack(">I", bytes[i - 4: i])[0]
        assure(crc == crc32(typ + data), f"{typ} chunk CRC")
        chunks.append((typ.decode(), data))
    assure(len(chunks) > 0 and chunks[0][0] == "IHDR", "IHDR position")
    assure(chunks[-1][0] == "IEND", "IEND position")
    assure(len(chunks[-1][1]) == 0, "IEND content")
    return chunks


def is_correct_chunk_type(typ: str | bytes):
    if isinstance(typ, str):
        typ = typ.encode("utf-8")
    return len(typ) == 4 and typ.isalpha() and typ[2] & 5


def find_chunk(chunks: list[tuple[str, bytes]], i: int, typ: str, strict=False):
    while i < len(chunks):
        if chunks[i][0] == typ:
            return i
        i += 1
    if strict:
        raise PNGError(f"{typ} chunk not found")
    return -1


class PNGError(Exception):
    @staticmethod
    def blame(error_location: str):
        raise PNGError(f"Incorrect {error_location}")


def assure(condition: bool, error_location: str):
    if not condition:
        raise PNGError.blame(error_location)
