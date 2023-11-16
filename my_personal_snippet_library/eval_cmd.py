import subprocess


def eval_cmd(cmd: str | list, into: str | bytes | None = None, **kwargs):
    kwargs.setdefault("text", True)
    check = kwargs.pop("check", True)
    kwargs["stdout"] = subprocess.PIPE
    inp = into.encode("utf-8") if isinstance(into, str) else into
    args = list(cmd.split(" ") if isinstance(cmd, str) else map(str, cmd))
    return subprocess.run(args, check=check, input=inp, **kwargs).stdout


if __name__ == "__main__":
    print(eval_cmd(f"cat {__file__}"))
