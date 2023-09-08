def rjust_all(elements: list[object], fillchar: str = " ") -> list[str]:
    strings = list(map(str, elements))
    width = max(map(len, strings))
    return [string.rjust(width, fillchar) for string in strings]


if __name__ == "__main__":
    row = ["aboba", "ohea", "bubububub"]
    for x in rjust_all(row, "-"):
        print("  " + x)
