from itertools import zip_longest


def transpose(matrix: list[list]) -> list[list]:
    return list(map(list, zip_longest(*matrix, fillvalue=None)))


if __name__ == "__main__":
    matrix = [[1, 2], [3, 4]]
    for row in transpose(matrix):
        print(row)
