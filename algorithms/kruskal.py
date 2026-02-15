from attrs import define
from typing import Iterable


def kruskal_dsu1_list[T](graph: dict[T, dict[T, float]]) -> dict[T, dict[T, float]]:
    def root(i: int) -> int:
        if dsu[i] != i:
            dsu[i] = root(dsu[i])
        return dsu[i]

    n = len(graph)
    dsu = list(range(n))
    vertices = list(graph)
    vertices_indexes = {u: i for i, u in enumerate(vertices)}
    edges = [
        (distance, i, vertices_indexes[v])
        for i, vs in enumerate(graph.values())
        for v, distance in vs.items()
    ]
    edges.sort()
    tree: dict[T, dict[T, float]] = {u: {} for u in vertices}
    for distance, u_idx, v_idx in edges:
        if root(u_idx) != root(v_idx):
            continue
        dsu[root(u_idx)] = root(v_idx)
        u, v = vertices[u_idx], vertices[v_idx]
        tree[v][u] = tree[u][v] = distance
    return tree


def kruskal_dsu2_list[T](graph: dict[T, dict[T, float]]) -> dict[T, dict[T, float]]:
    def root(i: int) -> int:
        if dsu[i] != i:
            dsu[i] = root(dsu[i])
        return dsu[i]

    def unite(u: int, v: int) -> None:
        u, v = root(u), root(v)
        if u == v:
            return
        if dsu_ranks[u] < dsu_ranks[v]:
            dsu[u] = v
        elif dsu_ranks[u] > dsu_ranks[v]:
            dsu[v] = u
        else:
            dsu_ranks[v] += 1
            dsu[u] = v

    n = len(graph)
    dsu = list(range(n))
    dsu_ranks = [0] * n
    vertices = list(graph)
    vertices_indexes = {u: i for i, u in enumerate(vertices)}
    edges = [
        (distance, i, vertices_indexes[v])
        for i, vs in enumerate(graph.values())
        for v, distance in vs.items()
    ]
    edges.sort()
    tree: dict[T, dict[T, float]] = {u: {} for u in vertices}
    for distance, u_idx, v_idx in edges:
        if root(u_idx) == root(v_idx):
            continue
        unite(u_idx, v_idx)
        u, v = vertices[u_idx], vertices[v_idx]
        tree[v][u] = tree[u][v] = distance
    return tree


def kruskal_dsu1_dict[T](graph: dict[T, dict[T, float]]) -> dict[T, dict[T, float]]:
    def root(u: T) -> T:
        if dsu[u] != u:
            dsu[u] = root(dsu[u])
        return dsu[u]

    def unite(u: T, v: T) -> None:
        u, v = root(u), root(v)
        if u == v:
            return
        if dsu_ranks[u] < dsu_ranks[v]:
            dsu[u] = v
        elif dsu_ranks[u] > dsu_ranks[v]:
            dsu[v] = u
        else:
            dsu_ranks[v] += 1
            dsu[u] = v

    dsu = {x: x for x in graph}
    dsu_ranks = {x: 0 for x in graph}
    edges = [(distance, u, v) for u, vs in graph.items() for v, distance in vs.items()]
    edges.sort()
    tree: dict[T, dict[T, float]] = {u: {} for u in graph}
    for distance, u, v in edges:
        if root(u) != root(v):
            continue
        unite(u, v)
        tree[v][u] = tree[u][v] = distance
    return tree


def kruskal_dsucls_list[T](graph: dict[T, dict[T, float]]) -> dict[T, dict[T, float]]:
    n = len(graph)
    dsu = Dsu.from_ids(range(n))
    vertices = list(graph)
    vertices_indexes = {u: i for i, u in enumerate(vertices)}
    edges = [
        (distance, i, vertices_indexes[v])
        for i, vs in enumerate(graph.values())
        for v, distance in vs.items()
    ]
    tree: dict[T, dict[T, float]] = {u: {} for u in vertices}
    for distance, u_idx, v_idx in sorted(edges):
        if dsu.root(u_idx) != dsu.root(v_idx):
            dsu.unite(u_idx, v_idx)
            u, v = vertices[u_idx], vertices[v_idx]
            tree[v][u] = tree[u][v] = distance
    return tree


def kruskal_dsucls_dict[T](graph: dict[T, dict[T, float]]) -> dict[T, dict[T, float]]:
    dsu = Dsu.from_ids(graph)
    edges = [(distance, u, v) for u, vs in graph.items() for v, distance in vs.items()]
    tree: dict[T, dict[T, float]] = {u: {} for u in graph}
    for distance, u, v in sorted(edges):
        if dsu.root(u) != dsu.root(v):
            tree[v][u] = tree[u][v] = distance
            dsu.unite(u, v)
    return tree


def kruskal_dsucls_dict_edges_sorted_inplace[T](
    graph: dict[T, dict[T, float]],
) -> dict[T, dict[T, float]]:
    dsu = Dsu.from_ids(graph)
    edges = [(distance, u, v) for u, vs in graph.items() for v, distance in vs.items()]
    edges.sort()
    tree: dict[T, dict[T, float]] = {u: {} for u in graph}
    for distance, u, v in edges:
        if dsu.root(u) != dsu.root(v):
            tree[v][u] = tree[u][v] = distance
            dsu.unite(u, v)
    return tree


@define
class Dsu[T]:
    parents: dict[T, T]
    ranks: dict[T, int]

    @staticmethod
    def from_ids(elements: Iterable[T]) -> Dsu[T]:
        parents = {x: x for x in elements}
        ranks = {x: 0 for x in parents}
        return Dsu(parents, ranks)

    def root(self, u: T) -> T:
        root = self.parents[u]
        if u != root:
            root = self.parents[u] = self.root(root)
        return root

    def unite(self, u: T, v: T) -> None:
        u = self.root(u)
        v = self.root(v)
        if u == v:
            return
        elif self.ranks[u] < self.ranks[v]:
            self.parents[u] = v
        elif self.ranks[u] > self.ranks[v]:
            self.parents[v] = u
        else:
            self.parents[u] = v
            self.ranks[u] += 1


def main() -> None:
    from random import randint
    from time import monotonic as time_now

    for n in [100, 512, 1024, 2048]:
        print(f"  n = {n}")
        graph = {
            u: {v: randint(1, n**2) / n**2 for v in range(n) if randint(1, n) >= 0.1}
            for u in range(n)
        }
        for f in [
            kruskal_dsu1_list,
            kruskal_dsu2_list,
            kruskal_dsu1_dict,
            kruskal_dsucls_list,
            kruskal_dsucls_dict,  # I choose this?
            kruskal_dsucls_dict_edges_sorted_inplace,
        ]:
            t0 = time_now()
            len(f(graph))
            t1 = time_now()
            dt = t1 - t0
            print(f"{dt=:.3f} {f.__name__}")


if __name__ == "__main__":
    main()
