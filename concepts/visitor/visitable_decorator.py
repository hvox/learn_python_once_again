from inspect import getmodule
import re


def camel_to_snake(camel):
    delimiter = r"[a-z][A-Z]|[A-Z][A-Z][a-z]"
    return re.sub(delimiter, lambda x: x[0][0] + "_" + x[0][1:], camel).lower()


def visitable(cls):
    method_suffix = "_" + camel_to_snake(cls.__name__)

    def visit_by(self, visit, *args):
        visitor = getattr(visit, "__self__", getmodule(visit))
        # visit = getattr(visitor, visit.__func__.__name__ + method_suffix)
        visit = getattr(visitor, visit.__name__ + method_suffix)
        return visit(self, *args)

    cls.visit_by = visit_by
    return cls
