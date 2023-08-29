from re import compile as re
from math import gcd
CLASSES = {"b1x1": {"disply: block", "aspect-ratio: 1/1", "width: aboba"}}
TAGS = {""}
GENERATORS = {}


def css_class(pattern: str):
    def decorator(f):
        GENERATORS[re(pattern)] = f
        return f
    return decorator


@css_class(r"b\d+x\d+")
def block_with_fixed_ration(class_name: str, **_):
    w, h = map(int, class_name[1:].split("x"))
    if w / h > 16 / 9:
        h, w = 180, (w * 180 + h - 1) // h
    else:
        w, h = 320, (h * 320 + w - 1) // w
    attrs = {
        "display: block",
        "position: relative",
        f"aspect-ratio: {w//gcd(w,h)}/{h//gcd(w,h)}",
        f"width: min(100%, clamp({w}px, (90vh - {2*h-1}px) * 99999, "
        + f"clamp({2*w}px, (90vh - {3*h-1}px) * 99999, {3*w}px)))",
    }
    return {f".{class_name}": attrs}


def stringify_css(css: dict[str, set[str]]) -> str:
    lines = []
    for selector, attrs in css.items():
        attrs = [p + ";" for p in sorted(attrs)]
        if len(selector) + sum(map(len, attrs)) < 80:
            lines.append(f"{selector}" + " { " + " ".join(attrs) + " }")
            continue
        lines.append(f"{selector}" + " {")
        lines.extend(f"\t{attr}" for attr in attrs)
        lines.append("}")
    return "\n".join(lines)


print(stringify_css(block_with_fixed_ration("b1x1")))


def compose_css(selectors: list[str]):
    recipes = []
    for selector in selectors:
        if selector in CLASSES:
            recipes.append(selector)
    css = []
    for cls in recipes:
        attrs = [p + ";" for p in sorted(CLASSES[cls])]
        if len(cls) + sum(map(len, attrs)) < 80:
            css.append(f".{cls}" + " { " + " ".join(attrs) + " }")
        else:
            css.append(f".{cls}" + " {")
            css.extend(f"\t{attr};" for attr in attrs)
            css.append("}")
    return css


# if __name__ == "__main__":
#     while True:
#         selectors = []
#         while selector := input("> "):
#             selectors.append(selector)
#         for line in compose_css(selectors):
#             print(line)
