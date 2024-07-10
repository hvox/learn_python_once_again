from pathlib import Path
from random import choice
from os import get_terminal_size

words = (Path(__file__).resolve().parent.parent / "data" / "words.txt").read_text().splitlines()
adjectives = (Path(__file__).resolve().parent.parent / "data" / "adjectives.txt").read_text().splitlines()

word = input("> ")
if not word:
    word = choice([w for w in words if 3 <= len(w) <= 4])

while True:
    _, h = get_terminal_size()
    for _ in range(h - 1):
        sentence = (
            " ".join(choice([w for w in adjectives if w.startswith(letter)]) for letter in word[:-1])
            + (" " + choice([w for w in words if w.endswith(word[-1])]))
        ).title()
        print(sentence)
    input()
