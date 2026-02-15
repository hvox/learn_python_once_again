from typing import Any, Callable
from math import inf
from itertools import product


def roy_floyd_warshall_list2d_backend[
    T
](graph: dict[T, dict[T, float]],) -> dict[tuple[T, T], float]:
    n = len(graph)
    dists = [[graph[u].get(v, inf) if u != v else 0 for v in graph] for u in graph]
    for t, u, v in product(range(n), repeat=3):
        dists[u][v] = min(dists[u][v], dists[u][t] + dists[t][v])
    return {(u, v): dist for u, u_dists in zip(graph, dists) for v, dist in zip(graph, u_dists)}


def roy_floyd_warshall_listkey_backend[
    T
](graph: dict[T, dict[T, float]],) -> dict[tuple[T, T], float]:
    vertices = list(graph)
    n = len(vertices)
    dists = [[graph[u].get(v, inf) if u != v else 0 for v in vertices] for u in vertices]
    for t, u, v in product(range(n), repeat=3):
        dists[u][v] = min(dists[u][v], dists[u][t] + dists[t][v])
    return {
        (u, v): dist for u, u_dists in zip(vertices, dists) for v, dist in zip(vertices, u_dists)
    }


def roy_floyd_warshall_in_dicts(graph: dict[Any, dict[Any, float]]) -> dict[tuple[Any, Any], float]:
    dists = {(u, v): graph[u].get(v, inf) if u != v else 0 for u, v in product(graph, repeat=2)}
    for t, u, v in product(graph, repeat=3):
        dists[u, v] = min(dists[u, v], dists[u, t] + dists[t, v])
    return dists


def roy_floyd_warshall_intkeys(graph: dict[int, dict[int, float]]) -> list[list[float]]:
    n = len(graph)
    dists = [[graph[u].get(v, inf) if u != v else 0 for v in range(n)] for u in range(n)]
    for t, u, v in product(range(n), repeat=3):
        dists[u][v] = min(dists[u][v], dists[u][t] + dists[t][v])
    return dists


def roy_floyd_warshall_intkeys_dict(
    graph: dict[int, dict[int, float]],
) -> dict[tuple[int, int], float]:
    n = len(graph)
    dists = [[graph[u].get(v, inf) if u != v else 0 for v in range(n)] for u in range(n)]
    for t, u, v in product(range(n), repeat=3):
        dists[u][v] = min(dists[u][v], dists[u][t] + dists[t][v])
    return {(u, v): dist for u, u_dists in enumerate(dists) for v, dist in enumerate(u_dists)}


def roy_floyd_warshall_intkeys_flat(graph: dict[int, dict[int, float]]) -> list[float]:
    n = len(graph)
    dists = [graph[u].get(v, inf) if u != v else 0 for u in range(n) for v in range(n)]
    for t, u, v in product(range(n), repeat=3):
        dists[u * n + v] = min(dists[u * n + v], dists[u * n + t] + dists[t * n + v])
    return dists


IMPLEMENTATIONS: list[Callable[[dict[int, dict[int, float]]], Any]] = [
    roy_floyd_warshall_intkeys,
    roy_floyd_warshall_intkeys_dict,
    roy_floyd_warshall_list2d_backend,
    roy_floyd_warshall_listkey_backend,
    roy_floyd_warshall_intkeys_flat,
    roy_floyd_warshall_in_dicts,
]


def main() -> None:
    from random import randint
    from time import monotonic as time_now

    for n in [50, 100, 200, 400]:
        print(f"  n = {n}")
        graph: dict[int, dict[int, float]] = {
            u: {v: randint(1, n**2) / n**2 for v in range(n) if randint(1, n) >= n**0.5}
            for u in range(n)
        }
        for f in IMPLEMENTATIONS:
            t0 = time_now()
            len(f(graph))
            t1 = time_now()
            dt = t1 - t0
            print(f"{dt=:.3f} {f.__name__}")


if __name__ == "__main__":
    main()
