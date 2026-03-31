from contextvars import ContextVar

active_prefix = ContextVar("active_prefix", default="> ")


def show(*values: str):
    print(active_prefix.get() + " ".join(map(str, values)))


def main() -> None:
    show("hello here #1")
    with active_prefix.set("$ "):
        show("hello #2")
        do_something(3)
    show("hello here #4")
    do_something(5)
    show("hello here #6")


def do_something(x: object) -> None:
    active_prefix.set("!> ")
    show(f"hello #{x}")


if __name__ == "__main__":
    main()
