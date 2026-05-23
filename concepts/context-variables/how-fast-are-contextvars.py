from collections.abc import Generator
from contextlib import contextmanager
from contextvars import ContextVar
from time import monotonic

aboba = ContextVar("aboba", default=0)
global_aboba = 0


def main() -> None:
    n = 1000
    print("# Setting and reading times")
    with timeit("contextvars", "fast?"):
        do_thing_with_contextvars(n)
    with timeit("global vars"):
        do_thing_with_globals(n)
    with timeit("myctxvar v1"):
        do_thing_with_myglobals(n)
    with timeit("myctxvar v2"):
        do_thing_with_myglobals(n)
    print("\n# Just reading")
    with timeit("contextvars"):
        do_reads_with_contextvars(n)
    with timeit("global vars"):
        do_reads_with_globals(n)
    with timeit("myctxvar v1"):
        do_reads_with_myglobals(n)
    with timeit("myctxvar v2"):
        do_reads_with_myglobals_v2(n)


@contextmanager
def timeit(name: str, comment: str = "") -> Generator[None]:
    start_time = monotonic()
    yield None
    dt = 1000_000 * (monotonic() - start_time)
    print(f"{name}: {dt:.9f} μs" + f" <- {comment}" * bool(comment))


def do_thing_with_contextvars(n: int) -> int:
    if n == 0:
        return 0
    counter = aboba.get()
    n1 = (n - 1) // 2
    n2 = n - 1 - n1
    with aboba.set(n1 * 3 % 255):
        counter += do_thing_with_contextvars(n1)
    with aboba.set(n2 * 3 % 255):
        counter += do_thing_with_contextvars(n2)
    return counter


def do_thing_with_globals(n: int) -> int:
    if n == 0:
        return 0
    global global_aboba
    counter = global_aboba
    n1 = (n - 1) // 2
    n2 = n - 1 - n1
    old_global_aboba = global_aboba
    global_aboba = n1 * 3 % 255
    counter += do_thing_with_globals(n1)
    global_aboba = n2 * 3 % 255
    counter += do_thing_with_globals(n2)
    global_aboba = old_global_aboba
    return counter


def do_thing_with_myglobals(n: int) -> int:
    if n == 0:
        return 0
    counter = global_aboba
    n1 = (n - 1) // 2
    n2 = n - 1 - n1
    with set_global_aboba(n1 * 3 % 255):
        counter += do_thing_with_myglobals(n1)
    with set_global_aboba(n2 * 3 % 255):
        counter += do_thing_with_myglobals(n2)
    return counter


def do_thing_with_myglobals_v2(n: int) -> int:
    if n == 0:
        return 0
    counter = get_global_aboba()
    n1 = (n - 1) // 2
    n2 = n - 1 - n1
    with set_global_aboba(n1 * 3 % 255):
        counter += do_thing_with_myglobals_v2(n1)
    with set_global_aboba(n2 * 3 % 255):
        counter += do_thing_with_myglobals_v2(n2)
    return counter


@contextmanager
def set_global_aboba(new_aboba_value: int) -> Generator[None]:
    global global_aboba
    old_global_aboba = global_aboba
    try:
        global_aboba = new_aboba_value
        yield None
    finally:
        global_aboba = old_global_aboba


def do_reads_with_contextvars(n: int) -> int:
    if n == 0:
        return 0
    counter = aboba.get()
    n1 = (n - 1) // 2
    n2 = n - 1 - n1
    counter += do_reads_with_contextvars(n1)
    counter += do_reads_with_contextvars(n2)
    return counter


def do_reads_with_globals(n: int) -> int:
    if n == 0:
        return 0
    counter = global_aboba
    n1 = (n - 1) // 2
    n2 = n - 1 - n1
    counter += do_reads_with_globals(n1)
    counter += do_reads_with_globals(n2)
    return counter


def do_reads_with_myglobals(n: int) -> int:
    if n == 0:
        return 0
    counter = global_aboba
    n1 = (n - 1) // 2
    n2 = n - 1 - n1
    counter += do_reads_with_myglobals(n1)
    counter += do_reads_with_myglobals(n2)
    return counter


def do_reads_with_myglobals_v2(n: int) -> int:
    if n == 0:
        return 0
    counter = get_global_aboba()
    n1 = (n - 1) // 2
    n2 = n - 1 - n1
    counter += do_reads_with_myglobals_v2(n1)
    counter += do_reads_with_myglobals_v2(n2)
    return counter


def get_global_aboba() -> int:
    return global_aboba


if __name__ == "__main__":
    main()
