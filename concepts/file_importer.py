from collections import namedtuple
from inspect import currentframe
from os import getcwd
from pathlib import Path
from typing import Any, Callable, Generic, TypeVar

T = TypeVar("T")


class Files(Generic[T]):
    def __init__(self, loader: Callable[[Path], T]):
        self.load = loader
        self.cache: dict[Path, T] = {}

    def __getitem__(self, local_path: str) -> T:
        frame: Any = currentframe()
        root = Path(frame.f_back.f_globals.get("__file__", getcwd() + "/x")).resolve().parent
        # TODO: search for path from parent directory too
        path = root.joinpath(*local_path.split("/"))
        if path not in self.cache:
            self.cache[path] = self.load(path)
        return self.cache[path]

    def __setitem__(self, local_path: str, data: T):
        frame: Any = currentframe()
        root = Path(frame.f_back.f_globals.get("__file__", getcwd() + "/x")).resolve().parent
        path = root.joinpath(*local_path.split("/"))
        self.cache[path] = data


def read_bytes(path: Path) -> bytes:
    return path.read_bytes()


def read_text(path: Path) -> str:
    return read_bytes(path).decode("utf-8")


def read_lines(path: Path) -> list[str]:
    return read_text(path).removesuffix("\n").split("\n")


def read_grid(path: Path) -> list[list[str]]:
    return [list(map(descape, line.split("\t"))) for line in read_lines(path)]


def read_table(path: Path) -> list[tuple[str, ...]]:
    header, *rows = read_grid(path)
    fields = [field.lower().replace(" ", "_") for field in header]
    RowType = namedtuple("", fields)  # type: ignore
    return [RowType(*row) for row in rows]


def read_dict(path: Path) -> dict[str, tuple[str, ...]]:
    (_, *header), *rows = read_grid(path)
    fields = [field.lower().replace(" ", "_") for field in header]
    ValueType = namedtuple("", fields)  # type: ignore
    return {key: ValueType(*info) for key, *info in rows}


# TODO: finde better name for that function
def descape(source: str) -> str:
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


BINARIES: Files[bytes] = Files(read_bytes)
TEXTS: Files[str] = Files(read_text)
LISTS: Files[list[str]] = Files(read_lines)
GRIDS: Files[list[list[str]]] = Files(read_grid)
TABLES: Files[list[tuple[str, ...]]] = Files(read_table)
DICTS: Files[dict[str, tuple[str, ...]]] = Files(read_dict)
