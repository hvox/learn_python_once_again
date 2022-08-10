import sys
import pathlib
import string
import hashlib


def random_number_generator(seed=""):
    seed, counter, buffer = seed.encode(), 0, []

    def f():
        nonlocal buffer, counter
        if not buffer:
            h = hashlib.sha3_512(seed + counter.to_bytes(8, "little")).digest()
            buffer = list(reversed(h))
            counter += 1
        return buffer.pop()

    return f


ONE = "(lambda _,__:().__eq__(__))(((),()),())"

PATH_OPTIONS = (
    ["print", "hello", "destroy", "you", "hacked", "world"]
    + ["the", "python", "lambda", "counter", "_", "god", "home", ""]
    + ["up", "page", "down", "space", "left", "q", "doublewi"]
    + ["bamblbe", "beef", "yahor", "camel", "casecase", "casca"]
    + ["abcdef", "six", "every", "hunt", "book", "return"]
    + ["input", "output", "stdlib", "main", "unwrap", "reduce"]
    + ["printf", "scanf", "macro", "cpp", "zig", "export"]
    + ["unexport", "telegram", "bot", "href", "success", "decrypto"]
    + ["ntfs", "ext", "fuso", "void", "pair", "thair", "korr"]
    + ["solus", "sound", "power_off", "connect", "aliens"]
    + ["planet", "destruction", "rororo", "clock", "timer"]
    + "Ben Kurtovic is clever guy".lower().split()
)


def generate_path(path, rng):
    if len(path) == 1:
        return path[0]
    head, tail = generate_path(path[:-1], rng), path[-1]
    head_index = rng() % 3
    alts = [
        ".".join(
            "__" + PATH_OPTIONS[rng() % len(PATH_OPTIONS)] + "__"
            for _ in range(1 + (rng() % 3))
        )
        for _ in range(2)
    ]
    alts = [
        "lambda "
        + "_" * (1 + (rng() % 10))
        + ":"
        + "_" * (1 + (rng() % 5))
        + "."
        + alt
        for alt in alts
    ]
    alts.insert(head_index, head)
    args = ["_" * (1 + (rng() % 5)) for _ in range(3)]
    while len(set(args)) != 3:
        args = ["_" * (1 + (rng() % 5)) for _ in range(3)]
    return (
        "(lambda "
        + ",".join(args)
        + ":"
        + f"(lambda _:_.{tail})({args[head_index]})"
        + ")("
        + ",".join(alts)
        + ")"
    )


def generate_number(number):
    # assumes _ = 1
    if number < 2:
        return "-".join("_" * (2 - number))
    high = generate_number(number // 2)
    if number % 2:
        return f"(lambda ___,__,_:_+__+__)(lambda: _,{high},_)"
    else:
        return f"(lambda _,__:__+_-__+_)({high},_)"


def generate_chr_name(rng):
    c = generate_path("__name__.__dir__.__class__.__name__".split("."), rng)
    eleven = generate_number(11)
    c = f"({c})[{eleven}]"
    h = generate_path("__name__.__class__.__module__.__doc__".split("."), rng)
    number257 = generate_number(257)
    h = f"({h})[{number257}]"
    r = generate_path(["().__class__", "__eq__", "__class__", "__name__"], rng)
    r = f"({r})[_+_-_]"
    return c + "+" + h + "+" + r


def generate_builtins(rng):
    return generate_path(
        ["(lambda __:__builtins__)(lambda:_)", "__dict__"], rng
    )


def generate_string(string: str, chr_name: str, rng):
    assert len(string)
    result = []
    for char in string:
        number = generate_number(ord(char))
        result.append(f"{chr_name}({number})")
    return "+".join(result)


def generate_program(source: str, rng=None):
    if rng is None:
        rng = random_number_generator()
    src = generate_string(source, "____", rng)
    bltns = generate_builtins(rng)
    chr_name = generate_chr_name(rng)
    exec_name = generate_string("exec", "____", rng)
    the_thing = f"___[{exec_name}]({src})"
    with_chr = f"(lambda __,_,____:{the_thing})(lambda:_,_,___[{chr_name}])"
    return f"(lambda _,___:{with_chr})({ONE},{bltns})"


match sys.argv:
    case _, source:
        print(generate_program(pathlib.Path(source).read_text()))
    case program_path, *_:
        print("USAGE: {program_path} source_to_be_obfuscated")
        exit(1)
