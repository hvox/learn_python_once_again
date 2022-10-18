from math import atan2, tau
from time import sleep

from mouse import get_position

x, y = get_position()
while True:
    x_prev, y_prev = x, y
    x, y = get_position()
    dx, dy = x - x_prev, y - y_prev
    if dx or dy:
        print("→↗↑↖←↙↓↘"[round(atan2(dy, dx) / (-tau / 8))], end="\r")
    sleep(0.02)
