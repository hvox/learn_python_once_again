from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Self, TypeAlias


@dataclass
class AST:
    nodes: list[ASTNode]

    @classmethod
    def parse(cls, source: str | list[str]) -> Self:
        lines = source if isinstance(source, list) else split(source)
        ast: Any = []
        parents: Any = None
        node, ast_lvl = ast, 0
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
        return cls(ast)

    def prettify(self, indent: str = "\t"):
        def prettify(ast: list[ASTNode]):
            result = []
            for node in ast:
                if isinstance(node, str):
                    result.append(node)
                    continue
                result += [indent + line for line in prettify(node).split("\n")]
            return "\n".join(result)
        return prettify(self.nodes)

    def __getitem__(self, line: str) -> AST:
        i = self.nodes.index(line) + 1
        if i == len(self.nodes) or not isinstance(self.nodes[i], list):
            self.nodes.insert(i, [])
        group: Any = self.nodes[i]
        return AST(group)

    def __setitem__(self, line: str, value: list[ASTNode]):
        i = self.nodes.index(line) + 1
        if i == len(self.nodes) or not isinstance(self.nodes[i], list):
            self.nodes.insert(i, [])
        self.nodes[i] = value

    def __str__(self):
        return self.prettify("    ")


ASTNode: TypeAlias = "str | list[ASTNode]"


def split(string: str, line_ending: str = "\n") -> list[str]:
    *values, end = string.split(line_ending)
    if end != "":
        raise ValueError("Input does not have line ending")
    return values


ast = AST.parse(Path("../download-and-install").read_text())
print(ast.prettify(" ── "))
