#!/usr/bin/env python3
import contextlib
import fcntl
import os
import select
import sys
import termios

CONTROL_CODES = {
    b"\x7f": "backspace",
    b"\x1b": "escape",
    b"\x1b[3~": "delete",
    b"\x1b[2~": "insert",
    b"\x1b[A": "up",
    b"\x1b[D": "left",
    b"\x1b[B": "down",
    b"\x1b[C": "right",
    b"\x1b[E": "five",
    b"\x1b[G": "five",
    b"\x1b[H": "home",
    b"\x1b[1~": "home",
    b"\x1b[F": "end",
    b"\x1b[4~": "end",
    b"\x1b[5~": "pg_up",
    b"\x1b[6~": "pg_down",
    b"\x1bOP": "f1",
    b"\x1b[[A": "f1",
    b"\x1bOQ": "f2",
    b"\x1b[[B": "f2",
    b"\x1bOR": "f3",
    b"\x1b[[C": "f3",
    b"\x1bOS": "f4",
    b"\x1b[[D": "f4",
    b"\x1b[15~": "f5",
    b"\x1b[[E": "f5",
    b"\x1b[17~": "f6",
    b"\x1b[18~": "f7",
    b"\x1b[19~": "f8",
    b"\x1b[20~": "f9",
    b"\x1b[21~": "f10",
    b"\x1b[23~": "f11",
    b"\x1b[24~": "f12",
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
        self.fd = sys.stdin.fileno()
        self.tty_flags = termios.tcgetattr(self.fd)
        self.fcntl_flags = fcntl.fcntl(self.fd, fcntl.F_GETFL)
        cur_tty_flags = self.tty_flags.copy()
        cur_tty_flags[3] &= ~termios.ICANON & ~termios.ECHO
        termios.tcsetattr(self.fd, termios.TCSANOW, cur_tty_flags)
        fcntl.fcntl(self.fd, fcntl.F_SETFL, self.fcntl_flags | os.O_NONBLOCK)
        return self

    def read_key(self):
        if len(self.buffer) < 5:
            with contextlib.suppress(BlockingIOError):
                self.buffer += os.read(self.fd, 5)
        for size in range(len(self.buffer), 0, -1):
            if (code := self.buffer[:size]) in CONTROL_CODES:
                self.buffer = self.buffer[size:]
                return CONTROL_CODES[code]
        char, self.buffer = next_codepoint(self.buffer)
        return char

    def wait_key(self, timeout: float | None = None):
        if key := self.read_key():
            return key
        select.select([sys.stdin], [], [], timeout)
        return self.read_key()

    def read_keys(self):
        while key := self.read_key():
            yield key

    def __exit__(self, *_):
        termios.tcsetattr(self.fd, termios.TCSADRAIN, self.tty_flags)
        fcntl.fcntl(self.fd, fcntl.F_SETFL, self.fcntl_flags)


with NonblockingKeyReader() as key_reader:
    while True:
        if key := key_reader.wait_key(timeout=5.0):
            print("You pressed " + repr(key))
        else:
            print("You haven't pressed anything in last five seconds...")
