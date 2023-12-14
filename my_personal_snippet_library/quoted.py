def quoted(string: str):
    table = {'"': '\\"', "\\": "\\\\", "\n": "\\n", "\r": "\\r", "\t": "\\t"}
    return '"' + string.translate(str.maketrans(table)) + '"'


if __name__ == "__main__":
    for s in "aboba dbl\" sngl' 2'\"'".split():
        print(quoted(s))
