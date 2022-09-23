#!/usr/bin/env python3
import contextlib
import os
import queue
import select
import sys
import threading
import time


class KeyReader:
    def __init__(self):
        self.unix_mode = os.name != "nt"
        self.pressed_keys = queue.Queue()
        self._thread = None
        self._cmnctr = None
        if self.unix_mode:
            self.get_key = self.pressed_keys.get

    @property
    def running(self):
        return self._thread is not None

    def start(self):
        assert not self.running, "Can't start running key reader"
        assert sys.stdin.isatty(), "Stdin does not look like TTY..."
        self._cmnctr = os.pipe2(os.O_NONBLOCK) if self.unix_mode else [[False]]
        thread_target = unix_read_keys if self.unix_mode else win_read_keys
        self._thread = threading.Thread(
            target=thread_target, args=[self._cmnctr[0], self.pressed_keys]
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
        while (timeout := deadline - time.monotonic()) > 0.002:
            with contextlib.suppress(queue.Empty):
                return self.pressed_keys.get(timeout=0.001)
        return self.pressed_keys.get(timeout=timeout)

    def stop(self):
        assert self.running, "Can't stop stopped key reader"
        if self.unix_mode:
            os.write(self._cmnctr[1], b"\x00")
            self._thread.join()
            list(map(os.close, self._cmnctr))
        else:
            self._cmnctr[0][0] = True
            self._thread.join()
        self._thread = None

    def __enter__(self) -> "KeyReader":
        self.start()
        return self

    def __exit__(self, *_):
        self.stop()

    def __del__(self):
        assert not self.running, "You forgot to stop the key reader"


INPUT_SEQUENCES = {
    "\x1b": "escape", "\x7f": "backspace", "\x08": "backspace", "\r": "\n",
    "[3~": "delete", "[2~": "insert", "[A": "up", "[D": "left", "[B": "down",
    "[C": "right", "[E": "five", "[G": "five", "[H": "home", "[1~": "home",
    "[F": "end", "[4~": "end", "[5~": "pageup", "[6~": "pagedown", "OP": "f1",
    "[[A": "f1", "OQ": "f2", "[[B": "f2", "OR": "f3", "[[C": "f3", "OS": "f4",
    "[[D": "f4", "[15~": "f5", "[[E": "f5", "[17~": "f6", "[18~": "f7",
    "[19~": "f8", "[20~": "f9", "[21~": "f10", "[23~": "f11", "[24~": "f12"
}
WINDOWS_INPUT_SEQUENCES = {
    "S": "delete", "R": "insert", "H": "up", "K": "left", "P": "down",
    "M": "right", "G": "home", "O": "end", "I": "pg_up", "Q": "pg_down",
    ";": "f1", "<": "f2", "=": "f3", ">": "f4", "?": "f5", "@": "f6",
    "A": "f7", "B": "f8", "C": "f9", "D": "f10", "\x85": "f11", "\x86": "f12"
}


def parse_input_sequences(chars: str):
    i = 0
    while i < len(chars):
        char = chars[i]
        if char != "\x1b" or i + 1 == len(chars):
            yield INPUT_SEQUENCES.get(char, char)
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


def unix_read_keys(communication_fd: int, key_buffer: queue.Queue):
    import fcntl
    import termios
    stdin_fd = sys.stdin.fileno()
    tty_flags = termios.tcgetattr(stdin_fd)
    fcntl_flags = fcntl.fcntl(stdin_fd, fcntl.F_GETFL)
    (cur_tty_flags := tty_flags.copy())[3] &= ~termios.ICANON & ~termios.ECHO
    termios.tcsetattr(stdin_fd, termios.TCSANOW, cur_tty_flags)
    # Usage select(...) guarantees that read syscall will not block.
    # Thus NONBLOCK is not necessary if os.read() used instead of stdin.read().
    # But I'm just a little shy about using system calls, so I use NONBLOCK.
    fcntl.fcntl(stdin_fd, fcntl.F_SETFL, fcntl_flags | os.O_NONBLOCK)
    rlist = [sys.stdin, communication_fd]
    while select.select(rlist, [], [])[0] == [sys.stdin]:
        for key in parse_input_sequences(sys.stdin.read()):
            key_buffer.put(key)
    termios.tcsetattr(stdin_fd, termios.TCSADRAIN, tty_flags)
    fcntl.fcntl(stdin_fd, fcntl.F_SETFL, fcntl_flags)


def win_read_keys(is_interrupted: list[bool], key_buffer: queue.Queue):
    import msvcrt
    # I am convinced that there is no right way to read keystrokes on windows.
    # The current solution has the following disadvantages:
    #  - Pressing "à" uninterruptible freezes the thread until next keystroke.
    #  - The thread has non-zero CPU usage when nothing is pressed.
    # Any other solution found has far more terrible disadvantages.
    #
    # total_hours_wasted_here = 32
    while not is_interrupted[0]:
        if msvcrt.kbhit():
            char = msvcrt.getwch()
            if char in "\x00\xe0":
                char = msvcrt.getwch()
                char = WINDOWS_INPUT_SEQUENCES.get(char, char)
            else:
                char = INPUT_SEQUENCES.get(char, char)
            key_buffer.put(char)
        else:
            time.sleep(0.001)


def main():
    # This is just a simple example of KeyReader usage
    print(repr(input(">>> ")))
    with KeyReader() as key_reader:
        while True:
            key = key_reader.get_key()
            print("You pressed " + repr(key))
            if key == "q":
                break
    print(repr(input(">>> ")))


if __name__ == "__main__":
    main()
