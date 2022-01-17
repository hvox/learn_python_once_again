from collections import namedtuple
NamedTuple = lambda flds: namedtuple('Σ', flds)
class Point(NamedTuple('x y')):
    pass
print(Point(1, 2))
