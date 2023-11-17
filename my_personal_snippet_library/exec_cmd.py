import subprocess


def exec_cmd(cmd: str | list, into: str | bytes | None = None, **kwargs):
    check = kwargs.pop("check", True)
    inp = into.encode("utf-8") if isinstance(into, str) else into
    args = list(cmd.split(" ") if isinstance(cmd, str) else map(str, cmd))
    return subprocess.run(args, check=check, input=inp, **kwargs)


if __name__ == "__main__":
    exec_cmd(["batcat", __file__])
