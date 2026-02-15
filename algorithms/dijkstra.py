from queue import PriorityQueue
import random
from math import inf


def dijkstras_algorithm_storing_edges[T](graph: dict[T, set[tuple[T, float]]], s: T, t: T) -> float:
    visited = {}
    Q: PriorityQueue[tuple[float, T, T | None]] = PriorityQueue()
    Q.put((0, s, None))
    while not Q.empty() and t not in visited:
        dist, u, prev = Q.get()
        if u not in visited:
            visited[u] = (dist, prev)
            for v, length in graph[u]:
                Q.put((dist + length, v, u))
    return visited.get(t, (inf, None))[0]


# this is my fastest implementation
def dijkstras_algorithm_storing_edges_to_nonvisited_vertices[
    T
](G: dict[T, set[tuple[T, float]]], s: T, t: T) -> float:
    visited = {}
    Q: PriorityQueue[tuple[float, T, T | None]] = PriorityQueue()
    Q.put((0, s, None))
    while not Q.empty() and t not in visited:
        dist, u, prev = Q.get()
        if u not in visited:
            visited[u] = (dist, prev)
            for v, length in G[u]:
                if v not in visited:
                    Q.put((dist + length, v, u))
    return visited.get(t, (inf, None))[0]


def dijkstras_algorithm_storing_vertices[T](G: dict[T, set[tuple[T, float]]], s: T, t: T) -> float:
    _ = G
    _ = s
    _ = t
    # not implementable in python because PriorityQueue does not have
    # change_priority() method, which is needed to do things...
    raise NotImplementedError("not implementable")
    # visited = {}
    # Q = PriorityQueue()
    # Q.put((0, s, None))
    # while Q and t not in visited:
    #     dist, u, prev = Q.get()
    #     visited[u] = (dist, prev)
    #     for v, length in G[u]:
    #         if v not in visited:
    #             # there should be change priority instead of put()
    #             Q.put((dist + length, v, u))
    # return visited[t][0]


def random_graph(p: int, qn: int) -> dict[int, set[tuple[int, float]]]:
    graph: dict[int, dict[int, float]] = {u: {} for u in range(1, p + 1)}
    while qn > 0:
        qn -= 1
        u = random.randint(1, p)
        v = random.randint(1, p)
        weight = random.randint(1, 99)
        if u != v:
            graph[u][v] = weight
    return {u: set(vs.items()) for u, vs in graph.items()}


def main() -> None:
    ts1: float = 0
    ts2: float = 0
    for i in range(2**5):
        p = 1000
        G = random_graph(p, int(p ** (3 / 2)))
        from time import time

        t0 = time()
        dijkstras_algorithm_storing_edges_to_nonvisited_vertices(G, 1, 2)
        t1 = time() - t0
        ts1 += t1
        print("nvv", t1)

        t0 = time()
        dijkstras_algorithm_storing_edges(G, 1, 2)
        t2 = time() - t0
        ts2 += t2
        print("sda", t2)

        print(f"nvv is {t2 / t1} times faster, than sda.")
    print("-" * 58)
    print(f"usually nvv is {ts2 / ts1} times faster, than sda.")


if __name__ == "__main__":
    main()
