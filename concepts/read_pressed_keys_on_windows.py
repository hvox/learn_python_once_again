import msvcrt
import sys
import time

CONTROL_CODES = {
    b"\x7f": "backspace",
    b"\x1b": "escape",
    b"\x1b[3~": "delete",
    b"\xe0S": "delete",
    b"\x00S": "delete",
    b"\x1b[2~": "insert",
    b"\xe0R": "insert",
    b"\x00R": "insert",
    b"\x1b[A": "up",
    b"\xe0H": "up",
    b"\x00H": "up",
    b"\x1b[D": "left",
    b"\xe0K": "left",
    b"\x00K": "left",
    b"\x1b[B": "down",
    b"\xe0P": "down",
    b"\x00P": "down",
    b"\x1b[C": "right",
    b"\xe0M": "right",
    b"\x00M": "right",
    b"\x1b[E": "five",
    b"\x1b[G": "five",
    b"\x1b[H": "home",
    b"\x1b[1~": "home",
    b"\xe0G": "home",
    b"\x00G": "home",
    b"\x1b[F": "end",
    b"\x1b[4~": "end",
    b"\xe0O": "end",
    b"\x00O": "end",
    b"\x1b[5~": "pg_up",
    b"\xe0I": "pg_up",
    b"\x00I": "pg_up",
    b"\x1b[6~": "pg_down",
    b"\xe0Q": "pg_down",
    b"\x00Q": "pg_down",
    b"\x1bOP": "f1",
    b"\x1b[[A": "f1",
    b"\x00;": "f1",
    b"\x1bOQ": "f2",
    b"\x1b[[B": "f2",
    b"\x00<": "f2",
    b"\x1bOR": "f3",
    b"\x1b[[C": "f3",
    b"\x00=": "f3",
    b"\x1bOS": "f4",
    b"\x1b[[D": "f4",
    b"\x00>": "f4",
    b"\x1b[15~": "f5",
    b"\x1b[[E": "f5",
    b"\x00?": "f5",
    b"\x1b[17~": "f6",
    b"\x00@": "f6",
    b"\x1b[18~": "f7",
    b"\x00A": "f7",
    b"\x1b[19~": "f8",
    b"\x00B": "f8",
    b"\x1b[20~": "f9",
    b"\x00C": "f9",
    b"\x1b[21~": "f10",
    b"\x00D": "f10",
    b"\x1b[23~": "f11",
    b"\xe0\x85": "f11",
    b"\x1b[24~": "f12",
    b"\xe0\x86": "f12",
}


def next_codepoint(bs: bytes) -> tuple[str, bytes]:
    if not bs or (i := bin(bs[0])[2:].zfill(8).find("0")) not in (0, 2, 3, 4):
        return "", bs
    length = (0, 2, 3, 4).index(i) + 1
    if length > len(bs):
        return "", bs
    return bs[:length].decode(), bs[length:]


class NonblockingKeyReader:
    def __init__(self):
        assert sys.stdin.isatty()
        self.buffer = b""

    def __enter__(self):
        return self

    def read_key(self):
        while len(self.buffer) < 5 and msvcrt.kbhit():
            self.buffer += msvcrt.getch()
        for size in range(len(self.buffer), 0, -1):
            if (code := self.buffer[:size]) in CONTROL_CODES:
                self.buffer = self.buffer[size:]
                return CONTROL_CODES[code]
        char, self.buffer = next_codepoint(self.buffer)
        return char

    def wait_key(self, timeout: float | None = None):
        t0 = time.monotonic()
        while timeout is None or time.monotonic() - t0 < timeout:
            if key := self.read_key():
                return key
            time.sleep(0.001)
        return self.read_key()

    def read_keys(self):
        while key := self.read_key():
            yield key

    def __exit__(self, *_):
        pass


with NonblockingKeyReader() as key_reader:
    while True:
        if key := key_reader.wait_key(timeout=5.0):
            print("You pressed " + repr(key))
        else:
            print("You haven't pressed anything in last five seconds...")
