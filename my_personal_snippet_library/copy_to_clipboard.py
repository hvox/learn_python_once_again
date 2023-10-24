import contextlib
import subprocess
import sys
from base64 import b64encode


def copy_to_clipboard(message: str, stdout=sys.stdout):
    with contextlib.suppress(ImportError):
        table = __import__("pd").DataFrame([message])
        table.to_clipboard(excel=False, index=False, header=False)
        return
    with contextlib.suppress(OSError):
        cmd = ["/usr/bin/xsel", "-ib"]
        subprocess.run(cmd, check=True, input=message.encode("utf-8"))
        return
    if stdout.isatty():
        encoded = b64encode(message.encode("utf-8")).decode("ascii")
        print(f"\x1b]52;c;{encoded}\x07", file=stdout)
    print("Copy this:\n" + message, file=stdout)


if __name__ == "__main__":
    copy_to_clipboard("Hello from copy-to-clipboard tool!")
