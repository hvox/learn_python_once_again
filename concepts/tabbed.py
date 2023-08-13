from typing import Any


Block = str | list["Block"]


class TabbedText:
    def __init__(self, source: Block | None = None, parent: Any = None):
        self.parent = parent
        if source is None:
            source = []
        if isinstance(source, list):
            self.blocks = source
            return
        if source[-1:] != "\n":
            source += "\n"
        blocks: list[str | list[Any]] = []
        stack = [(0, blocks)]
        for tabbed_line in source.split("\n"):
            line = tabbed_line.lstrip("\t")
            tabs = len(tabbed_line) - len(line)
            if line == "":
                stack[-1][1].append(line)
                continue
            if tabs > stack[-1][0]:
                stack.append((tabs, [line]))
                continue
            while tabs < stack[-1][0]:
                group_tabs, group = stack.pop()
                for _ in range(group_tabs - stack[-1][0] - 1):
                    group = [group]
                stack[-1][1].append(group)
            stack[-1][1].append(line)
        self.blocks = blocks[:-1]

    def prepend(self, name, items: list[Any] | None = None):
        block = [] if items is None else items
        self.blocks.insert(0, block)
        self.blocks.insert(0, name)
        return TabbedText(block, self) if items is None else self

    def append(self, name, items: list[Any] | None = None):
        block = [] if items is None else items
        self.blocks.append(name)
        self.blocks.append(block)
        return TabbedText(block, self) if items is None else self

    def __getitem__(self, name: str):
        try:
            i = self.blocks.index(name)
        except ValueError:
            raise KeyError(name)
        if not isinstance(self.blocks[i + 1], list):
            self.blocks.insert(i + 1, [])
        return TabbedText(self.blocks[i + 1], self)

    def __setitem__(self, name: str, value: list[Any]):
        try:
            i = self.blocks.index(name)
        except ValueError:
            self.blocks.append(name)
            self.blocks.append(value)
            return
        if not isinstance(self.blocks[i + 1], list):
            self.blocks.insert(i + 1, [])
        self.blocks[i + 1] = value

    def __repr__(self):
        self_as_string = str(self) + "\n"
        return f"{self.__class__.__name__}({self_as_string!r})"

    def __str__(self):
        return TabbedText.block_to_str(self.blocks)

    @staticmethod
    def block_to_str(block: list[Any]):
        lines = []
        for item in block:
            if isinstance(item, str):
                lines.append(item)
                continue
            if item == []:
                continue
            for line in TabbedText.block_to_str(item).split("\n"):
                # if any(char != "\t" for char in line):
                #     line = "\t" + line
                # lines.append(line)
                lines.append(("\t" + line) if line != "" else "")
        return "\n".join(lines)
