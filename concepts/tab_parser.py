from __future__ import annotations
from pathlib import Path

AST = "list[AST | str]"


def split(string: str, line_ending: str = "\n") -> list[str]:
    *values, end = string.split(line_ending)
    if end != "":
        raise ValueError("Input does not have line ending")
    return values


def parse(source: str | list[str]) -> AST:
    lines = source if isinstance(source, list) else split(source)
    ast = node = []
    parents, ast_lvl = None, 0
    for line_number, indented_line in enumerate(lines):
        line = indented_line.lstrip("\t")
        indent = len(indented_line) - len(line)
        while indent > ast_lvl:
            node.append([])
            parents, node = [parents, node], node[-1]
            ast_lvl += 1
        while indent < ast_lvl:
            parents, node = parents
            ast_lvl -= 1
        node.append(line)
    return ast


def prettify(ast: AST, indent: str = "\t"):
    result = []
    for node in ast:
        if isinstance(node, str):
            result.append(node)
            continue
        result += [indent + line for line in prettify(node, indent).split("\n")]
    return "\n".join(result)


ast = parse(Path("../download-and-install").read_text())
print(prettify(ast, " ── "))
