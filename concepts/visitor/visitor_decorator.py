import re
from functools import update_wrapper
from inspect import getmodule
from typing import TypeVar

T = TypeVar("T")


def get_parent(fun):
    container = getmodule(fun)
    for attribute in fun.__qualname__.split(".")[:-1]:
        container = getattr(container, attribute)
    return container


def camel_to_snake(camel):
    delimiter = r"[a-z][A-Z]|[A-Z][A-Z][a-z]"
    return re.sub(delimiter, lambda x: x[0][0] + "_" + x[0][1:], camel).lower()


def lazy_functoin(function_generator):
    def fun(*args, **kwargs):
        nonlocal fun
        fun = function_generator()
        return fun(*args, **kwargs)
    return lambda *args, **kwargs: fun(*args, **kwargs)


def visitor(fun: T) -> T:
    def generate_visitor():
        visitor_container = get_parent(fun)
        visitor_name = fun.__name__
        def visitor(arg, *args, **kwargs):
            visitor = visitor_name + "_" + camel_to_snake(type(arg).__name__)
            return getattr(visitor_container, visitor)(arg, *args, **kwargs)
        return visitor
    visitor = lazy_functoin(generate_visitor)
    update_wrapper(visitor, fun)
    return visitor


@visitor
def print_the(argument: int) -> str:
    raise NotImplementedError()


def print_the_str(arg: str):
    return f"string: {arg}"


def print_the_int(arg: int):
    return f"integer: {arg}"


print(print_the(123))
