import itertools


def add(u: list[int], v: list[int]) -> list[int]:
    return [x + y for x, y in itertools.zip_longest(u, v, fillvalue=0)]


def substract(u: list[int], v: list[int]) -> list[int]:
    return [x - y for x, y in itertools.zip_longest(u, v, fillvalue=0)]


def karatsuba(u: list[int], v: list[int]) -> list[int]:
    if len(u) <= 1 or len(v) <= 1:
        return [x * y for x in u for y in v]
    split_size = min(len(u), len(v)) // 2
    u_low, u_high = u[:split_size], u[split_size:]
    v_low, v_high = v[:split_size], v[split_size:]
    w2 = karatsuba(u_high, v_high)
    w1 = karatsuba(add(u_low, u_high), add(v_low, v_high))
    w0 = karatsuba(u_low, v_low)
    w1 = add(substract(substract(w1, w0), w2), w0[split_size:])
    return w0[:split_size] + w1[:split_size] + add(w2, w1[split_size:])


def karatsuba_v2(u: list[int], v: list[int]) -> list[int]:
    if len(u) <= 16 or len(v) <= 16:
        return simple_multiply(u, v)
    split_size = min(len(u), len(v)) // 2
    u_low, u_high = u[:split_size], u[split_size:]
    v_low, v_high = v[:split_size], v[split_size:]
    w2 = karatsuba_v2(u_high, v_high)
    w1 = karatsuba_v2(add(u_low, u_high), add(v_low, v_high))
    w0 = karatsuba_v2(u_low, v_low)
    w1 = add(substract(substract(w1, w0), w2), w0[split_size:])
    return w0[:split_size] + w1[:split_size] + add(w2, w1[split_size:])


def simple_multiply(u: list[int], v: list[int]) -> list[int]:
    w = [0] * (len(u) + len(v) - 1)
    for i, x in enumerate(u):
        for j, y in enumerate(v):
            w[i + j] += x * y
    return w


if __name__ == "__main__":
    from time import monotonic as time
    from random import randint
    print(" power : karatsuba  karatsuba_v2  simple_multiplication")
    for n in range(100):
        u, v = ([randint(1, 255) for _ in range(2**n)] for _ in range(2))
        t0 = time()
        w2 = karatsuba(u, v)
        t1 = time()
        w3 = karatsuba_v2(u, v)
        t2 = time()
        w1 = simple_multiply(u, v)
        t3 = time()
        print(f"  {n:3}  : {t1-t0:0.7f} vs {t2-t1:0.7f} vs {t3-t2:0.7f}")
        assert w1 == w2
"""
 power : karatsuba  karatsuba_v2  simple_multiplication
    0  : 0.0000018 vs 0.0000024 vs 0.0000007
    1  : 0.0000111 vs 0.0000020 vs 0.0000011
    2  : 0.0000182 vs 0.0000029 vs 0.0000024
    3  : 0.0000720 vs 0.0000068 vs 0.0000062
    4  : 0.0001599 vs 0.0000211 vs 0.0000207
    5  : 0.0008481 vs 0.0001498 vs 0.0001657
    6  : 0.0014706 vs 0.0002384 vs 0.0003051
    7  : 0.0047293 vs 0.0008840 vs 0.0011801
    8  : 0.0127625 vs 0.0022910 vs 0.0048878
    9  : 0.0394435 vs 0.0067772 vs 0.0211794
   10  : 0.1157558 vs 0.0207869 vs 0.0852257
   11  : 0.3458520 vs 0.0613387 vs 0.3433293
   12  : 1.0447428 vs 0.1866067 vs 1.4672110
   13  : 3.2930124 vs 0.5868493 vs 6.1812129
   14  : 9.8191791 vs 1.7013226 vs 24.606330
   15  : 29.997886 vs 5.2912729 vs 103.86575
   16  : 91.714347 vs 16.086948 vs 457.54030
   17  : 274.00968 vs 48.865228 vs 1993.0935
   18  : 801.75741 vs 149.10361 vs 9168.3369
"""
