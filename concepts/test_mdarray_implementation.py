import array
import sys
import time
import numpy

from collections import namedtuple

ARRAY_IMPLEMENTATIONS = {}


def mdarray(description: str):
    def f(cls: type):
        ARRAY_IMPLEMENTATIONS[description] = cls

    return f


@mdarray("MD[array.array]")
class ArrayU16V1:
    __slots__ = ("sizes", "elements")
    implementation = "array.array"

    def __init__(self, *sizes: list[int]):
        self.sizes = sizes
        self.elements = array.Array("H", [0] * product(sizes))

    def __getitem__(self, index: tuple[int, ...] | int):
        i, scale = 0, 1
        offsets = index if isinstance(index, tuple) else [index]
        for j, offset in enumerate(reversed(offsets)):
            i += offset * scale
            scale *= self.sizes[~j]
        return self.elements[i]


@mdarray("3DA[array.array]")
class ArrayU16V2:
    __slots__ = ("sizes", "elements")
    implementation = "array.array"

    def __init__(self, *sizes: list[int]):
        assert len(sizes) == 3
        self.sizes = sizes
        self.elements = array.Array("H", [0] * product(sizes))

    def __getitem__(self, index: tuple[int, ...]):
        i, j, k = index
        return self.elements[((i * self.sizes[1] + j) * self.sizes[2]) + k]


@mdarray("numpy.array")
def numpy_array(*sizes: list[int]):
    assert len(sizes) == 3
    return numpy.array(
        [[[0 for _ in range(sizes[2])] for _ in range(sizes[1])] for _ in range(sizes[0])],
        dtype=numpy.uint16,
    )


@mdarray("list[list[list[]]]")
class ArrayU16V3:
    __slots__ = ("w", "h", "d", "elements")
    implementation = "array.array"

    def __init__(self, *sizes: list[int]):
        assert len(sizes) == 3
        self.w, self.h, self.d = sizes
        self.elements = [
            [[0 for _ in range(sizes[2])] for _ in range(sizes[1])] for _ in range(sizes[0])
        ]

    def __getitem__(self, index: tuple[int, ...]):
        i, j, k = index
        return self.elements[i][j][k]


@mdarray("A3[array.array]")
class ArrayU16V4:
    __slots__ = ("w", "h", "d", "elements")
    implementation = "array.array"

    def __init__(self, *sizes: list[int]):
        assert len(sizes) == 3
        self.w, self.h, self.d = sizes
        self.elements = array.Array("H", [0] * product(sizes))

    def __getitem__(self, index: tuple[int, ...]):
        i, j, k = index
        return self.elements[((i * self.h + j) * self.d) + k]


@mdarray("DynA3[array.array]")
class ArrayU16V5:
    __slots__ = ("w", "h", "d", "elements")
    implementation = "array.array"

    def __new__(_, *sizes: list[int]):
        def __init__(self, *sizes: list[int]):
            assert len(sizes) == 3
            self.w, self.h, self.d = sizes
            self.elements = array.Array("H", [0] * product(sizes))

        def __getitem__(self, index: tuple[int, ...]):
            i, j, k = index
            return self.elements[((i * self.h + j) * self.d) + k]

        cls = type(
            "ArrayU16V4",
            (object,),
            {
                "__slots__": ("w", "h", "d", "elements"),
                "__init__": __init__,
                "__getitem__": __getitem__,
            },
        )
        return cls(*sizes)


@mdarray("ClosureA3(array.array)")
class ArrayU16V6:
    __slots__ = ("w", "h", "d", "elements")
    implementation = "array.array"

    def __new__(_, *sizes: list[int]):
        w, h, d = sizes
        array_getitem = array.Array.__getitem__

        def __new__(cls, *args):
            obj = array.Array.__new__(cls, *args)
            obj.getitem = obj.__getitem__
            return obj

        def __getitem__(self, index: tuple[int, ...]):
            i, j, k = index
            return array_getitem(self, ((i * h + j) * d) + k)

        cls = type(
            "Aboba",
            (array.Array,),
            {"__new__": __new__, "__slots__": ("getitem"), "__getitem__": __getitem__},
        )
        # print(sys.getsizeof(array.array("H", [0]*3)))
        # print(sys.getsizeof(cls("H", [0]*3)))
        # print(sys.getsizeof(numpy.array([[[1, 2, 3]]], dtype="uint16")))
        return cls("H", [0] * product(sizes))


@mdarray("ClosureA3[array.array]")
class ArrayU16V7:
    def __new__(_, *sizes: list[int]):
        w, h, d = sizes

        def __init__(self, *sizes: list[int]):
            assert len(sizes) == 3
            self.elements = array.Array("H", [0] * product(sizes))

        def __getitem__(self, index: tuple[int, ...]):
            i, j, k = index
            return self.elements[((i * h + j) * d) + k]

        cls = type(
            "ArrayU16V4",
            (object,),
            {"__slots__": ("elements",), "__init__": __init__, "__getitem__": __getitem__},
        )
        obj = cls(*sizes)
        # print(sys.getsizeof(obj) + sys.getsizeof(array.array("H", [0] * 3)))
        # print(sys.getsizeof(numpy.array([[[1, 2, 3]]], dtype="uint16")))
        return cls(*sizes)


@mdarray("ClosureA3[array.array][][][]")
class ArrayU16V8:
    def __new__(_, *sizes: list[int]):
        w, h, d = sizes

        def A1__init__(self, elements, i):
            self.elements = elements
            self.i = i

        def A1__getitem__(self, index):
            return self.elements[self.i + index]

        Aboba1 = type(
            "Aboba1",
            (object,),
            {"__slots__": ("elements", "i"), "__init__": A1__init__, "__getitem__": A1__getitem__},
        )

        def A2__init__(self, elements, i):
            self.elements = elements
            self.i = i

        def A2__getitem__(self, index):
            return Aboba1(self.elements, self.i + index * d)

        Aboba2 = type(
            "Aboba2",
            (object,),
            {"__slots__": ("elements", "i"), "__init__": A2__init__, "__getitem__": A2__getitem__},
        )

        def __init__(self, *sizes: list[int]):
            assert len(sizes) == 3
            self.elements = array.Array("H", [0] * product(sizes))

        def __getitem__(self, index):
            return Aboba2(self.elements, index * h * d)

        Aboba3 = type(
            "Aboba3",
            (object,),
            {"__slots__": ("elements",), "__init__": __init__, "__getitem__": __getitem__},
        )
        obj = Aboba3(*sizes)
        return obj


def get_dimensions(lst: list):
    if isinstance(lst[0], list):
        return get_dimensions(lst[0]) + 1
    return 1


def product(elements: list):
    result = 1
    for x in elements:
        result *= x
    return result


def test_access_speed(desc: str, Array: type):
    W, H = 640, 360
    array = Array(W, H, 4)
    array_sum = 0
    if desc.endswith("[][][]"):
        t0 = time.monotonic()
        for x in range(W):
            for y in range(H):
                for z in range(4):
                    array_sum += array[x][y][z]
        return time.monotonic() - t0
    t0 = time.monotonic()
    for x in range(W):
        for y in range(H):
            for z in range(4):
                array_sum += array[x, y, z]
    return time.monotonic() - t0


def getsizeof(obj, seen=None):
    """Recursively finds size of objects"""

    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()

    obj_id = id(obj)
    if obj_id in seen:
        return 0

    # Important mark as seen *before* entering recursion to gracefully handle
    # self-referential objects
    seen.add(obj_id)

    if isinstance(obj, dict):
        size += sum([getsizeof(v, seen) for v in obj.values()])
        size += sum([getsizeof(k, seen) for k in obj.keys()])
    elif hasattr(obj, '__dict__'):
        size += getsizeof(obj.__dict__, seen)
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        size += sum([getsizeof(i, seen) for i in obj])

    return size


desc_len = max(map(len, ARRAY_IMPLEMENTATIONS.keys()))
for desc, Array in reversed(ARRAY_IMPLEMENTATIONS.items()):
    t = test_access_speed(desc, Array) * 1000
    print(desc.ljust(desc_len), f"{t:5.1f}ms")
