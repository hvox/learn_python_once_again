def ljust_all(elements: list[object], fillchar: str = " ") -> list[str]:
    strings = list(map(str, elements))
    width = max(map(len, strings))
    return [string.ljust(width, fillchar) for string in strings]


if __name__ == "__main__":
    row = ["aboba", "ohea", "bubububub"]
    for x in ljust_all(row, "-"):
        print("  " + x)
