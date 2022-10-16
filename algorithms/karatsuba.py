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
