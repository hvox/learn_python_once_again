#!/usr/bin/env python3.10


def str2list(source):
    stack = [[]]
    for char in source:
        match char:
            case " ":
                continue
            case "[":
                stack.append([])
            case "]":
                stack[-2].append(stack.pop())
    return stack[0][0]


print(str2list("[[][[][]][]]"))
