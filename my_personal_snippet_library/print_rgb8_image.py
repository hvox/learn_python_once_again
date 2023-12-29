from chunked import chunked


def print_rgb8_image(image: list[list[list[int] | None]]):
    if len(image) % 2 == 1:
        image = image + [[None] * len(image[0])]
    lines = []
    for line1, line2 in chunked(image, 2):
        line = []
        for rgb1, rgb2 in zip(line1, line2):
            if rgb1:
                code1 = ";".join(map(str, rgb1))
                code2 = ("48;2;" + ";".join(map(str, rgb2))) if rgb2 else "49"
                line.append(f"\x1b[38;2;{code1};{code2}m▄")
            elif rgb2:
                code = ";".join(map(str, rgb2))
                line.append(f"\x1b[38;2;{code};49m▀")
            else:
                line.append("\x1b[49m ")
        lines.append("".join(line) + "\x1b[0m")
    print("\n".join(reversed(lines)))


if __name__ == "__main__":
    import os
    import random

    w, h = os.get_terminal_size()
    h *= 2
    image = [[None] * w for _ in range(h)]
    x0, y0 = w / 2, h / 2
    for x in range(w):
        for y in range(h):
            dist = ((x - x0) ** 2 + (y - y0) ** 2) ** 0.5
            p = (max(dist / max(w / 2, h / 2) - 0.1, 0) / 0.9) ** 1
            if random.random() > p:
                r = round((1 - abs(y - y0) / h * 2) * 255)
                g = 255 - round(p * 255)
                b = round((1 - abs(x - x0) / w * 2) * 255)
                image[y][x] = [r, g, b]
    print_rgb8_image(image)
