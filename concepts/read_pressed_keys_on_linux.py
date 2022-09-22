#!/usr/bin/env python3
import fcntl
import os
import queue
import select
import sys
import termios
import threading


class KeyReader:
    def __init__(self):
        self.unix_mode = os.name != "nt"
        assert self.unix_mode
        self.pressed_keys = queue.Queue()
        self._thread = None
        self._cmnctr = None

    @property
    def running(self):
        return self._thread is not None

    def start(self):
        assert not self.running, "Can't start running key reader"
        assert self.unix_mode
        self._cmnctr = os.pipe2(os.O_NONBLOCK)
        self._thread = threading.Thread(
            target=read_keys, args=[self._cmnctr[0], self.pressed_keys]
        )
        self._thread.start()

    def stop(self):
        assert self.running, "Can't stop stopped key reader"
        os.write(self._cmnctr[1], b"\x00")
        self._thread.join()
        self._thread = None
        list(map(os.close, self._cmnctr))

    def __enter__(self) -> "KeyReader":
        self.start()
        return self

    def __exit__(self, *_):
        self.stop()

    def __del__(self):
        assert not self.running, "You forgot to stop key reader"


INPUT_SEQUENCES = {
    "[3~": "delete", "[2~": "insert", "[A": "up", "[D": "left", "[B": "down",
    "[C": "right", "[E": "five", "[G": "five", "[H": "home", "[1~": "home",
    "[F": "end", "[4~": "end", "[5~": "pageup", "[6~": "pagedown", "OP": "f1",
    "[[A": "f1", "OQ": "f2", "[[B": "f2", "OR": "f3", "[[C": "f3", "OS": "f4",
    "[[D": "f4", "[15~": "f5", "[[E": "f5", "[17~": "f6", "[18~": "f7",
    "[19~": "f8", "[20~": "f9", "[21~": "f10", "[23~": "f11", "[24~": "f12"
}


def parse_input_sequences(chars: str):
    i = 0
    while i < len(chars):
        char = chars[i]
        if char != "\x1b" or i + 1 == len(chars):
            yield {"\x7f": "backspace", "\x1b": "escape"}.get(char, char)
            i += 1
            continue
        for j in range(i + 5, i + 2, -1):
            if chars[i + 1:j] in INPUT_SEQUENCES:
                yield INPUT_SEQUENCES[chars[i + 1:j]]
                i = j
                break
        else:
            yield "alt+" + chars[i + 1]
            i += 2


def read_keys(communication_fd: int, key_buffer: queue.Queue):
    assert sys.stdin.isatty(), "Stdin does not look like TTY..."
    stdin_fd = sys.stdin.fileno()
    tty_flags = termios.tcgetattr(stdin_fd)
    fcntl_flags = fcntl.fcntl(stdin_fd, fcntl.F_GETFL)
    (cur_tty_flags := tty_flags.copy())[3] &= ~termios.ICANON & ~termios.ECHO
    termios.tcsetattr(stdin_fd, termios.TCSANOW, cur_tty_flags)
    fcntl.fcntl(stdin_fd, fcntl.F_SETFL, fcntl_flags | os.O_NONBLOCK)
    rlist = [sys.stdin, communication_fd]
    while select.select(rlist, [], [])[0] == [sys.stdin]:
        for key in parse_input_sequences(sys.stdin.read()):
            key_buffer.put(key)
    termios.tcsetattr(stdin_fd, termios.TCSADRAIN, tty_flags)
    fcntl.fcntl(stdin_fd, fcntl.F_SETFL, fcntl_flags)


def main():
    with KeyReader() as key_reader:
        while True:
            key = key_reader.pressed_keys.get()
            print("You pressed " + repr(key))
            if key == "q":
                break
    print(repr(input(">>> ")))


if __name__ == "__main__":
    main()
