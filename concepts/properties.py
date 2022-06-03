from functools import cache


class A:
    def __init__(self, value):
        self.value = value

    @property
    def twice(self):
        print("twice() was called!")
        return self.value * 2

    @property
    @cache
    def triple(self):
        print("triple() was called!")
        return self.value * 3


a = A(123)
for i in range(1, 4):
    print(f"{i=} {a.twice=}")
for i in range(1, 4):
    print(f"{i=} {a.triple=}")
