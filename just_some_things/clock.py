import time

CHARS = " 0123456789:"
CHARS_ART = """
     █▀█ ▀█  ▀▀█ ▀▀█ █ █ █▀▀ █▀▀ ▀▀█ █▀█ █▀█  ▄ :
     █ █  █  █▀▀ ▀▀█ ▀▀█ ▀▀█ █▀█  █  █▀█ ▀▀█  ▄ :
     ▀▀▀ ▀▀▀ ▀▀▀ ▀▀▀   ▀ ▀▀▀ ▀▀▀  ▀  ▀▀▀ ▀▀▀    :
"""
CHARS_ART = CHARS_ART.strip("\n").split("\n")


def pretty_print(message: str):
    digits = [CHARS.find(c) for c in message]
    print("\033[A" * 4)
    for y in range(3):
        row = "".join(
            CHARS_ART[y][4 * digits[x // 4] + x % 4]
            for x in range(len(digits) * 4)
        )
        print(" " + row)


print("\033[?25l\n\n\n")
running = True
while running:
    try:
        pretty_print(time.strftime("%H:%M:%S", time.localtime()))
        time.sleep(1)
    except KeyboardInterrupt or Exception:
        print("\033[?25h")
        running = False
