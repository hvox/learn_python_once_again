import re
from functools import reduce
from inspect import currentframe
from pathlib import Path
from typing import Any, Type, TypeVar

__all__ = ["load"]
T = TypeVar("T")
CAMELCASE_REGEX = re.compile("((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))")


def load(typ: Type[T], relative_path: str | None = None) -> T:
    if relative_path is None:
        relative_path = guess_path(typ)
    path = resolve(relative_path)
    lines = path.read_text().strip("\n").split("\n")
    header, *rows = (list(map(unwrap, line.split("\t"))) for line in lines)
    fields = {h.lower(): i for i, h in enumerate(header)}
    t: Any = typ
    assert t.__origin__ is list
    t = t.__args__[0]
    result: Any = []
    for row in rows:
        attributes: dict[str, Any] = {}
        for field, field_type in t.__annotations__.items():
            attributes[field] = field_type(row[fields[field]])
        result.append(t(**attributes))
    return result


def camel_to_snake(text: str) -> str:
    return CAMELCASE_REGEX.sub(r"_\1", text).lower()


def pluralize(text: str) -> str:
    return text + "s"


def guess_path(t: type) -> str:
    name = camel_to_snake(getattr(t, "__args__", (t,))[0].__name__)
    return pluralize(name.replace("_", " ")).replace(" ", "-") + ".tsv"


def resolve(relative_path: str, callee_lvl: int = 0) -> Path:
    frame: Any = currentframe()
    frame = reduce(lambda x, _: x.f_back, range(callee_lvl + 1), frame)
    root = Path(frame.f_globals["__file__"]).resolve().parent
    path = root.joinpath(*relative_path.split("/"))
    while not path.exists() and root.parent != root:
        root = root.parent
        path = root.joinpath(*relative_path.split("/"))
    if not path.exists():
        raise FileNotFoundError(f"???/{relative_path}")
    return path


def unwrap(source: str) -> str:
    i = 0
    cell_value = []
    while i < len(source):
        if source[i: i + 2] in (r"\t", r"\n", r"\r"):
            cell_value.append({"n": "\n", "t": "\t", "r": "\r"}[source[i + 1]])
            i += 2
        else:
            cell_value.append(source[i])
            i += 1
    return "".join(cell_value)
