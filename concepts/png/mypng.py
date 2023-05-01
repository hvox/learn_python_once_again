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


Palette = list[tuple[float, float, float, float]]


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
    trns_index = find_chunk(chunks, 1, "tRNS", strict=False)
    idat_index = find_chunk(chunks, 1, "IDAT", strict=True)
    gamma = decode_gama(chunks[gama_index][1]) if gama_index != -1 else None
    transparent = decode_trns(chunks[trns_index][1], colors) if trns_index != -1 else None
    if colors is None:
        assure(plte_index != -1, "color type")
        colors = decode_plte(chunks[plte_index][1])
        alphas = chunks[trns_index][1] if trns_index != -1 else []
        for i, ((r, g, b, _), alpha) in enumerate(zip(colors, alphas)):
            colors[i] = (r, g, b, alpha / 255)
    channels = len(colors) if isinstance(colors, str) else 1
    pixel_data: Any = decode_idat(chunks[idat_index][1], w, h, bitdepth, channels)
    # TODO: my array type, that does not require value for initialization
    pixels = FloatArray("f", new_array("f32", [0] * w * h * 4))
    if not isinstance(colors, str):
        for i, color_index in enumerate(pixel_data):
            pixels[4 * i: 4 * i + 4] = colors[color_index]
    else:
        one = 2**bitdepth - 1
        for i in range(w * h):
            clr = tuple(pixel_data[i * channels: (i + 1) * channels])
            match tuple(x / one for x in pixel_data[i * channels: (i + 1) * channels]):
                case r, g, b, a:
                    pixels[4 * i: 4 * i + 4] = (r, g, b, a)
                case r, g, b:
                    pixels[4 * i: 4 * i + 4] = (r, g, b, float(clr != transparent))
                case l, a:
                    pixels[4 * i: 4 * i + 4] = (l, l, l, a)
                case (l,):
                    pixels[4 * i: 4 * i + 4] = (l, l, l, float(clr * 3 != transparent))
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
    return [(r / 255, g / 255, b / 255, 1.0) for r, g, b in (data[i: i + 3] for i in range(0, len(data), 3))]


def decode_trns(data: bytes, colors: str) -> tuple[int, int, int]:
    if not isinstance(colors, str):
        return None
    if colors in ("LA", "RGBA"):
        raise PNGError("tRNS is incompatible with color type")
    assure(len(data) * 2 == len(colors), "tRNS chunk")
    clr: Any = unpack(">SSS", data) if colors == "RGB" else unpack(">S", data) * 3
    return clr


def decode_idat(data: bytes, width: int, height: int, bitdepth: int, channels: int) -> Any:
    # TODO: raise PNGError on errors?
    data = bytearray(decompress(data))
    bits_per_pixel = bitdepth * channels
    d = bytes_per_pixel = (bits_per_pixel + 7) // 8
    line_length = (bits_per_pixel * width + 7) // 8 + 1
    for y in range(height):
        fltr = data[y * line_length]
        if fltr == 0:  # None
            pass
        elif fltr == 1:  # Sub
            for x, i in enumerate(range(y * line_length + 1, (y + 1) * line_length)):
                data[i] = (data[i] + (data[i - d] if x >= d else 0)) % 256
        elif fltr == 2:  # Up
            for x, i in enumerate(range(y * line_length + 1, (y + 1) * line_length)):
                data[i] = (data[i] + (data[i - line_length] if y > 0 else 0)) % 256
        elif fltr == 3:  # Avg
            for x, i in enumerate(range(y * line_length + 1, (y + 1) * line_length)):
                left = data[i - d] if x >= d else 0
                up = data[i - line_length] if y > 0 else 0
                data[i] = (data[i] + (left + up) // 2) % 256
        elif fltr == 4:  # Peach
            for x, i in enumerate(range(y * line_length + 1, (y + 1) * line_length)):
                left = data[i - d] if x >= d else 0
                up = data[i - line_length] if y > 0 else 0
                upleft = data[i - line_length - d] if y > 0 and x >= d else 0
                p = left + up - upleft
                peach = (
                    left if abs(p - up) >= abs(p - left) <= abs(p - upleft)
                    else up if abs(p - up) <= abs(p - upleft)
                    else upleft
                )
                data[i] = (data[i] + peach) % 256
    pixels = new_array("u16" if bitdepth > 8 else "u8", [0] * height * width * channels)
    if bits_per_pixel < 8:
        assert channels == 1
        for y in range(height):
            for x in range(width):
                i = x * bits_per_pixel + (height - y - 1) * line_length * 8 + 8
                pixels[x + y * width] = data[i // 8] >> (7 - (i % 8)) & ((1 << bits_per_pixel) - 1)
    else:
        assert bitdepth % 8 == 0
        for y in range(height):
            for x in range(width):
                for channel in range(channels):
                    i = (x + y * width) * channels + channel
                    j = x * bytes_per_pixel + (height - y - 1) * line_length + 1
                    pixels[i] = int.from_bytes(data[j: j + bitdepth // 8], "big")
    return pixels


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


C_TYPES: dict[str, str] = {
    f"{typ}{size}": next(ch for ch in codes if array(ch).itemsize * 8 >= size)
    for typ, codes, sizes in [
        ("u", "BHILQ", [8, 16, 32, 64]),
        ("i", "bhilq", [8, 16, 32, 64]),
        ("f", "fd", [32, 64]),
        # TODO: add bools
    ]
    for size in sizes
}


def new_array(typ: str, content):
    return array(C_TYPES[typ], content)


def is_sorted(elements, ignore=()):
    xs = [x for x in elements if x not in ignore]
    return xs == list(sorted(xs))
