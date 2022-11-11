from functools import cached_property


class A:
    def __init__(self, value):
        self.value = value

    @property
    def twice(self):
        print("twice() was called!")
        return self.value * 2

    @cached_property
    def triple(self):
        print("triple() was called!")
        return self.value * 3


a = A(123)
for i in range(1, 4):
    print(f"{i=} {a.twice=}")
for i in range(1, 4):
    print(f"{i=} {a.triple=}")
