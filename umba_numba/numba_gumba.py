from time import time
from random import randint
from numba import njit
from numba.typed import List


def product1(xs):
    p = True
    result = 1.0
    for x in xs:
        if p:
            result *= x
        else:
            result /= x
        p ^= True
    return result


product2 = njit(product1)
for name, f, argtype in [("python", product1, list), ("numba", product2, List)]:
    print(name)
    for _ in range(5):
        argument = argtype([randint(1, 1000) for _ in range(2**14)])
        t = time()
        result = f(argument)
        print(f"δτ = {time() - t:.6f}")
