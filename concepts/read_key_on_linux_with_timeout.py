#!/usr/bin/env python

import os
import sys
import termios
from select import select


def getchar(timeout: float = 1e9):
    assert sys.stdin.isatty()
    fd = sys.stdin.fileno()
    prev_flags = termios.tcgetattr(fd)
    flags = prev_flags.copy()
    flags[3] &= ~termios.ICANON & ~termios.ECHO
    termios.tcsetattr(fd, termios.TCSANOW, flags)
    char = os.read(fd, 4) if select([sys.stdin], [], [], timeout)[0] else b""
    termios.tcsetattr(fd, termios.TCSADRAIN, prev_flags)
    return char


while True:
    key = getchar(timeout=0.1)
    print(repr(key), "->", repr(key.decode()))
