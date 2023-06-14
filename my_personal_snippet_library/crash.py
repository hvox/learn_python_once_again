import sys


def crash(message: str = "Invalid input", file=sys.stderr):
    prefix = "\x1b[1;91merror\x1b[0m:" if file.isatty() else "error:"
    print(prefix, message, file=file)
    sys.exit(1)


if __name__ == "__main__":
    crash("aboba")
