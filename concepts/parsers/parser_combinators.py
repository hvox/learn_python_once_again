from re import compile as compile_regex
from functools import reduce


class Parser:
    def __init__(self, parse=None):
        self.parse = parse

    def __call__(self, source, i=0):
        return self.parse(source, i)

    def __or__(self, other):
        return Parser(lambda s, i: self(s, i) or other(s, i))

    def __and__(self, other):
        left = self.subparsers if isinstance(self, ParserConcat) else [self]
        right = other.subparsers if isinstance(other, ParserConcat) else [other]
        return ParserConcat(left + right)

    def repeate(self):
        def parse(source, i):
            result = []
            while item := self(source, i):
                elem, i = item
                result.append(elem)
            return tuple(result), i

        return Parser(parse)

    def bind(self, f):
        def parse(source, i):
            if parsed := self(source, i):
                value, i = parsed
                return f(value)(source, i)
            return None

        return Parser(parse)

    def map(self, f):
        return self.bind(lambda value: (lambda s, i: (f(value), i)))

    def __imatmul__(self, other):
        self.parse = other
        return self

    def maybe():
        return parser | (lambda s, i: (None, i))


class ParserConcat(Parser):
    def __init__(self, subparsers):
        self.subparsers = subparsers

    def __call__(self, source, i=0):
        result = []
        for parse in self.subparsers:
            if parsed := parse(source, i):
                value, i = parsed
                result.append(value)
                continue
            return None
        return tuple(result), i

    def starmap(self, f):
        return self.bind(lambda sequence: (lambda s, i: (f(*sequence), i)))


def re(pattern):
    regex = compile_regex(pattern)

    def parse(source, i):
        if match := regex.match(source, i):
            return (i, match.group()), match.span()[1]
        return None

    return Parser(parse)


def parsers(count):
    return [Parser(lambda: None) for _ in range(count)]


whitespace = re(r"[ \n\t]+")
comment = re(r"//.*\n")
ignored = (whitespace | comment).repeate()


def token(token_pattern):
    match token_pattern:
        case set(patterns):
            parser = Parser(lambda s, i: None)
            for pattern in patterns:
                parser |= token(pattern)
            return parser
        case str(pattern):
            return (ignored & re(pattern)).starmap(lambda _, token: token)
        case undefined:
            raise TypeError(repr(undefined))
