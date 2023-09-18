from typing import TypeVar, Type, get_args


T = TypeVar("T")


def tsv_to_dict(typ: Type[T], string: str) -> dict[str, T]:
    return {
        decode_str(name): decode_tuple(typ, values)
        for name, values in (row.split("\t", 1) for row in string.strip("\n").split("\n"))
    }


def dict_to_tsv(field_names: list[str], dct: dict[str, tuple]) -> str:
    table = ["\t".join(map(encode_str, field_names))]
    for name, obj in dct.items():
        table.append(encode_str(name) + "\t" + encode_tuple(obj))
    return "".join(row + "\n" for row in table)


def encode_tuple(tpl: tuple) -> str:
    return "\t".join(encode_str(x) for x in tpl)


def decode_tuple(typ: Type[T], string: str) -> T:
    valus = map(decode_str, string.split("\t"))
    if hasattr(typ, "__annotations__"):
        return typ(**{name: typ(value) for (name, typ), value in zip(typ.__annotations__.items(), valus)})
    return typ([t(x) for t, x in zip(get_args(typ), valus)])  # type: ignore


def encode_str(string: object) -> str:
    return str(string).replace("\\", "\\\\").replace("\n", "\\n").replace("\t", "\\t").replace("\r", "\\r")


def decode_str(string: str) -> str:
    result, chars = [], iter(string)
    for char in chars:
        result.append({"\\": "\\", "t": "\t", "n": "\n", "r": "\r"}[next(chars)] if char == "\\" else char)
    return "".join(result)
