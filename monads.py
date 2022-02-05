from dataclasses import dataclass
from typing import Any


@dataclass
class Maybe:
    value: Any

    def __init__(self, *values):
        if len(values) == 1:
            self.value = tuple(values)
        else:
            self.value = None

    def bind(self, f):
        if self.value is None:
            return Maybe()
        value = f(self.value[0]).value
        if value is None:
            return Maybe()
        return Maybe(value[0])
