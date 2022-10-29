import typing
import itertools
import contextlib


class Iter:
    def __init__(self, *args):
        match args:
            case [iterable] if isinstance(iterable, typing.Iterable):
                self._iterator = iter(iterable)
            case [start, end, step]:
                self._iterator = range(start, end + step, step)
            case [start, end]:
                self._iterator = range(start, end + 1, 1)
            case [end]:
                self._iterator = range(1, end + 1, 1)

    def __getitem__(self, index):
        return next(itertools.islice(self._iterator, index, index + 1))

    def __call__(self, f=None, *args, **kwargs):
        return f(self, *args, **kwargs) if f else (None, self.last())[1]

    def __iter__(self):
        yield from self._iterator

    def __next__(self):
        return next(self._iterator)

    def __mult__(self, other):
        return Iter(itertools.product(self._iterator, other))

    def __pow__(self, n):
        return Iter(itertools.product(self._iterator, repeat=n))

    def next(self, default=StopIteration()):
        with contextlib.suppress(StopIteration):
            return next(self._iterator)
        if isinstance(default, Exception):
            raise default
        return default

    def next_chunk(self, size=2):
        return tuple(itertools.islice(self._iterator, size))

    def count(self):
        return itertools.count(self)

    def last(self, default=StopIteration()):
        with contextlib.suppress(ValueError):
            value = next(self._iterator)
            for value in self._iterator:
                pass
            return value
        if isinstance(default, Exception):
            raise default
        return default

    def advance_by(self, n):
        for _ in range(n):
            next(self._iterator)
        return self

    def step_by(self, step):
        def generator():
            yield next(self._iterator)
            while True:
                yield self[step - 1]

        return Iter(generator())

    def chain(self, other: typing.Iterable):
        return itertools.chain(self._iterator, other)

    def zip(self, other: typing.Iterable):
        return Iter(zip(self._iterator, other))

    def unzip(self):
        return list(map(list, zip(*self._iterator)))

    def intersperse(self, separator):
        def generator():
            with contextlib.suppress(StopIteration):
                yield next(self._iterator)
                for element in self._iterator:
                    yield separator
                    yield element
        return Iter(generator())

    def map(self, f):
        return Iter(map(f, self._iterator))

    def filter(self, predicate):
        return Iter(element for element in self if predicate(element))

    def cat(self):
        return Iter(x for xs in self._iterator for x in xs)

    def enumerate(self, start=0):
        return Iter(enumerate(self, start=start))

    def skip_while(self, predicate):
        return Iter(itertools.skip_while(self, predicate))

    def take_while(self, predicate):
        return Iter(itertools.takewhile(self, predicate))

    def skip(self, n):
        return Iter(itertools.skip(self._iterator, n))

    def take(self, n):
        return Iter(itertools.islice(self, 0, n))

    def scan(self, initial, f):
        def generator():
            state = initial
            for x in self._iterator:
                state = f(state, x)
                yield state
        return Iter(generator())

    def partition(self, f):
        parts = {}
        for x in self._iterator:
            parts.setdefault(f(x), []).append(x)
        return parts

    def fold(self, initial, f):
        value = initial
        for x in self._iterator:
            value = f(value, x)
        return value

    def all(self, predicate=bool):
        return all(map(predicate, self))

    def any(self, predicate=bool):
        return any(map(predicate, self))

    def cycle(self):
        return Iter(itertools.cycle(self))

    def rev(self):
        return Iter(reversed(self._iterator))

    def smap(self, f):
        return Iter(itertools.starmap(f, self._iterator))


# TODO: peakable iterator: https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.peekable
