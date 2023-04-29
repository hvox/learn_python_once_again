#!/usr/bin/env python3
from pathlib import Path
from struct import pack
from sys import argv
from zlib import compress, crc32


def make_chunk(typ: bytes, data: bytes):
    return pack(">I4s", len(data), typ) + data + crc32(typ + data).to_bytes(4, "big")


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
chunks = [
    (b"IHDR", pack(">IIBBBBB", 1, 1, 8, 0, 0, 0, 0)),
    (b"IDAT", compress(bytes([0, 0]), 9)),
    (b"IEND", b""),
]
Path(argv[1]).write_bytes(PNG_SIGNATURE + b"".join(make_chunk(*ch) for ch in chunks))
for typ, data in [(b"SIGN", PNG_SIGNATURE)] + chunks:
    print(typ.decode(), ":", data.hex(" "))
