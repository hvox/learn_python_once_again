import contextlib
import subprocess


def paste_from_clipboard() -> str:
    with contextlib.suppress(ImportError):
        return __import__("pandas").read_clipboard().columns[0]
    with contextlib.suppress(OSError):
        cmd = ["/usr/bin/xsel", "-b"]
        output = subprocess.run(cmd, check=True, stdout=subprocess.PIPE).stdout
        return output.decode("utf-8")
    return input("Paste here: ")


if __name__ == "__main__":
    print("Clipboard:", repr(paste_from_clipboard()))
