def quoted(string: str):
    table = {"\\": "\\\\", "\n": "\\n", "\r": "\\r", "\t": "\\t"}
    quotes = '"' if "'" in string or '"' not in string else "'"
    trans = str.maketrans(table | {quotes: "\\" + quotes})
    return quotes + string.translate(trans) + quotes


if __name__ == "__main__":
    for s in "aboba dbl\" sngl' 2'\"'".split():
        print(quoted(s))
