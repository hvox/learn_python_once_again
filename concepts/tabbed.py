from typing import Any


class TabbedText:
    def __init__(self, source: str | list[str]):
        if isinstance(source, list):
            self.blocks = source
            return
        if source[-1:] != "\n":
            source += "\n"
        blocks = []
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

    def __getitem__(self, name: str):
        for i, line in enumerate(self.blocks):
            if line == name:
                if not isinstance(self.blocks[i+1], list):
                    self.blocks.insert(i + 1, [])
                return TabbedText(self.blocks[i+1])
        raise KeyError(name)

    def __setitem__(self, name: str, value: list[Any]):
        for i, line in enumerate(self.blocks):
            if line == name:
                if not isinstance(self.blocks[i+1], list):
                    self.blocks.insert(i + 1, ())
                self.blocks[i + 1] = value
                return
        self.blocks.append(name)
        self.blocks.append(value)

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
            for line in TabbedText.block_to_str(item).split("\n"):
                # if any(char != "\t" for char in line):
                #     line = "\t" + line
                # lines.append(line)
                lines.append(("\t" + line) if line != "" else "")
        return "\n".join(lines)