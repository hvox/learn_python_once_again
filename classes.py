from collections import namedtuple
NamedTuple = lambda flds: namedtuple('Σ', flds)
class Point(NamedTuple('x y')):
    pass
print(Point(1, 2))

from dataclasses import make_dataclass
Dataclass = lambda flds: make_dataclass('ξ', flds.split())
class Point(Dataclass('x y')):
    pass
print(Point(1, 2))

from dataclasses import dataclass
@dataclass
class Point:
    x: int
    y: int
print(Point(1, 2))
