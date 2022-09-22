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

    @property
    def running(self):
        return self._thread is not None

    def start(self):
        assert not self.running, "Can't start running key reader"
        assert self.unix_mode
        self._pipe = os.pipe2(os.O_NONBLOCK)
        self._thread = threading.Thread(
            target=read_keys, args=[self._pipe[0], self.pressed_keys]
        )
        self._thread.start()

    def stop(self):
        assert self.running, "Can't stop stopped key reader"
        os.write(self._pipe[1], b"\x00")
        self._thread.join()
        self._thread = None
        list(map(os.close, self._pipe))

    def __enter__(self) -> "KeyReader":
        self.start()
        return self

    def __exit__(self, *_):
        self.stop()

    def __del__(self):
        assert not self.running, "You forgot to stop key reader"


def read_keys(communication_fd: int, key_buffer: queue.Queue):
    assert sys.stdin.isatty(), "Stdin does not look like TTY..."
    fd = sys.stdin.fileno()
    tty_flags = termios.tcgetattr(fd)
    fcntl_flags = fcntl.fcntl(fd, fcntl.F_GETFL)
    (cur_tty_flags := tty_flags.copy())[3] &= ~termios.ICANON & ~termios.ECHO
    termios.tcsetattr(fd, termios.TCSANOW, cur_tty_flags)
    fcntl.fcntl(fd, fcntl.F_SETFL, fcntl_flags | os.O_NONBLOCK)
    rlist = [sys.stdin, communication_fd]
    while select.select(rlist, [], [])[0] == [sys.stdin]:
        chars = sys.stdin.read()
        for char in chars:
            key_buffer.put(char)
    termios.tcsetattr(fd, termios.TCSADRAIN, tty_flags)
    fcntl.fcntl(fd, fcntl.F_SETFL, fcntl_flags)


with KeyReader() as key_reader:
    while True:
        key = key_reader.pressed_keys.get()
        print("You pressed " + repr(key))
        if key == "q":
            break
print(repr(input(">>> ")))
