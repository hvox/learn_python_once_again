from typing import TypeVar, Any, Callable


K = TypeVar("K")
V = TypeVar("V")


def dict_min(*dicts: dict[K, V]) -> dict[K, V]:
    result: Any = {}
    for dct in dicts:
        for key, value in dct.items():
            if key in result:
                value = min(value, result[key])
            result[key] = value
    return result


def dict_max(*dicts: dict[K, V]) -> dict[K, V]:
    result: Any = {}
    for dct in dicts:
        for key, value in dct.items():
            if key in result:
                value = max(value, result[key])
            result[key] = value
    return result
