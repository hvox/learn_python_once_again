import msvcrt
import queue
import os
import time
import sys
import threading


class KeyReader:
    def __init__(self):
        self.unix_mode = os.name != "nt"
        assert not self.unix_mode
        self.pressed_keys = queue.Queue()
        self._thread = None

    @property
    def running(self):
        return self._thread is not None

    def start(self):
        assert not self.running, "Can't start running key reader"
        self._interrupted = [False]
        self._thread = threading.Thread(
            target=read_keys, args=[self._interrupted, self.pressed_keys]
        )
        self._thread.start()

    def stop(self):
        assert self.running, "Can't stop stopped key reader"
        self._interrupted[0] = True
        self._thread.join()
        self._thread = None

    def __enter__(self) -> "KeyReader":
        self.start()
        return self

    def __exit__(self, *_):
        self.stop()

    def __del__(self):
        assert not self.running, "You forgot to stop key reader"


def read_keys(interrupted: list[bool], key_buffer: queue.Queue):
    assert sys.stdin.isatty(), "Stdin does not look like TTY..."
    while not interrupted[0]:
        if msvcrt.kbhit():
            char = msvcrt.getwch()
            key_buffer.put(char)
        else:
            time.sleep(0.0001)


with KeyReader() as key_reader:
    while True:
        key = key_reader.pressed_keys.get()
        print("You pressed " + repr(key))
        if key == "q":
            break
print(repr(input(">>> ")))
