#!/usr/bin/env python3
import pathlib
import sys


def exec(code, scope=None, access=None):
    scope = {} if scope is None else scope
    access = {"__builtins__": {}, "print": print} | (access or {})
    __builtins__.exec(code, access, scope)
    return scope


def eval(code, scope=None, access=None):
    scope = {} if scope is None else scope
    access = {"__builtins__": {}, "print": print} | (access or {})
    return __builtins__.eval(code, access, scope)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        for path in sys.argv[1:]:
            exec(pathlib.Path(path).read_text())
    else:
        scope = {}
        while True:
            src = input("> ")
            try:
                try:
                    print(repr(eval(src, scope)))
                except SyntaxError:
                    exec(src, scope)
            except Exception as e:
                print(repr(e))
