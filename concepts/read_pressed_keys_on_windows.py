import contextlib
import msvcrt
import os
import queue
import sys
import threading
import time


class KeyReader:
    def __init__(self):
        self.unix_mode = os.name != "nt"
        assert not self.unix_mode
        self.pressed_keys = queue.Queue()
        self._thread = None
        self._cmnctn = None

    @property
    def running(self):
        return self._thread is not None

    def start(self):
        assert not self.running, "Can't start running key reader"
        self._cmnctn = [False]
        self._thread = threading.Thread(
            target=read_keys, args=[self._cmnctn, self.pressed_keys]
        )
        self._thread.start()

    def get_key(self, block=True, timeout=None):
        # This code is here for Windows compatibility.
        # Other OSes are ok with native queue.get(), but on Windows we should
        # emulate blocking queue.get(block=True) since native queue.get() goes
        # into an uninterruptible wait on an underlying lock.
        # https://docs.python.org/3/library/queue.html#queue.Queue.get
        if not block:
            return self.pressed_keys.get(False)
        deadline = time.monotonic() + (timeout or float("inf"))
        while (timeout := deadline - time.monotonic()) > 0.001:
            with contextlib.suppress(queue.Empty):
                return self.pressed_keys.get(timeout=0.001)
        return self.pressed_keys.get(timeout=timeout)

    def stop(self):
        assert self.running, "Can't stop stopped key reader"
        self._cmnctn[0] = True
        self._thread.join()
        self._thread = None

    def __enter__(self) -> "KeyReader":
        self.start()
        return self

    def __exit__(self, *_):
        self.stop()

    def __del__(self):
        assert not self.running, "You forgot to stop key reader"


INPUT_SEQUENCES = {
    "S": "delete",
    "R": "insert",
    "H": "up",
    "K": "left",
    "P": "down",
    "M": "right",
    "G": "home",
    "O": "end",
    "I": "pg_up",
    "Q": "pg_down",
    ";": "f1",
    "<": "f2",
    "=": "f3",
    ">": "f4",
    "?": "f5",
    "@": "f6",
    "A": "f7",
    "B": "f8",
    "C": "f9",
    "D": "f10",
    "\x85": "f11",
    "\x86": "f12",
}


def read_keys(is_interrupted: list[bool], key_buffer: queue.Queue):
    assert sys.stdin.isatty(), "Stdin does not look like TTY..."
    while not is_interrupted[0]:
        if msvcrt.kbhit():
            char = msvcrt.getwch()
            if char in "\x00\xe0":
                char = msvcrt.getwch()
                char = INPUT_SEQUENCES.get(char, char)
            key_buffer.put({"\x1b": "escape", "\r": "\n"}.get(char, char))
        else:
            time.sleep(0.001)


def main():
    with KeyReader() as key_reader:
        while True:
            key = key_reader.get_key()
            print("You pressed " + repr(key))
            if key == "q":
                break
    print(repr(input(">>> ")))


if __name__ == "__main__":
    main()
