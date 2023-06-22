import sys


def debug(message: str = "Invalid input", file=sys.stderr):
    if getattr(debug, "enabled", False):
        prefix = "\x1b[1;93m[info]\x1b[0m" if file.isatty() else "[info]"
        print(prefix, message, file=file)


if __name__ == "__main__":
    setattr(debug, "enabled", True)
    debug("aboba")
