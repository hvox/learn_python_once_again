from itertools import islice


def chunked(iterable, n: int):
    it = iter(iterable)
    while chunk := list(islice(it, n)):
        yield chunk


if __name__ == "__main__":
    for w in chunked(range(1, 10), 3):
        print(w)
