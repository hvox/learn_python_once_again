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


def read_keys(is_interrupted: list[bool], key_buffer: queue.Queue):
    assert sys.stdin.isatty(), "Stdin does not look like TTY..."
    while not is_interrupted[0]:
        if msvcrt.kbhit():
            char = msvcrt.getwch()
            key_buffer.put(char)
        else:
            time.sleep(0.0001)


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
