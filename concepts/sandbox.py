#!/usr/bin/env python3
import pathlib
import sys


def exec(code, scope=None, access=None):
    scope = {} if scope is None else scope
    access = {"__builtins__": {}, "print": print} | (access or {})
    __builtins__.exec(code, access, scope)
    return scope


if __name__ == "__main__":
    if sys.argv[1:]:
        for path in sys.argv[1:]:
            exec(pathlib.Path(path).read_text())
    else:
        scope = {}
        while src := input():
            exec(src, scope)
