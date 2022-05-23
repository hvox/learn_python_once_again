from dataclasses import dataclass
from typing import Any
from enum import Enum, auto


class FreerMonadType(Enum):
    Pure = auto()
    Impure = auto()


@dataclass
class FreerMonad:
    type: FreerMonadType
    value: Any

    @staticmethod
    def pure(value):
        return FreerMonad(FreerMonadType.Pure, value)

    @staticmethod
    def fish(x2my, y2mz):
        return lambda x: x2my(x).bind(y2mz)

    def bind(self, f):
        if self.type is FreerMonadType.Pure:
            return f(self.value)
        fx, next_isntr = self.value
        instr = FreerMonad.fish(next_isntr, f)
        return FreerMonad(FreerMonadType.Impure, (fx, instr))


if __name__ == "__main__":
    pure = FreerMonad.pure
    liftF = lambda f: lambda x: FreerMonad(FreerMonadType.Impure, (f(x), pure))
    put = liftF(lambda x: ("put", x))
    get = liftF(lambda _: ("get",))

    just5 = pure(5)
    print(just5)
    put5 = put(5)
    print(put5)
    ask_name = put("So what is your name?").bind(get)
    print(ask_name)
    hello_name = ask_name.bind(lambda name: put(f"Hello, {name}!"))
    print(hello_name)

    def interprete(m):
        if m.type == FreerMonadType.Pure:
            return
        arg = ()
        fx, next_isntr = m.value
        if fx[0] == "put":
            print(fx[1])
        elif fx[0] == "get":
            arg = input()
        else:
            assert False
        return interprete(next_isntr(arg)) if next_isntr else None

    print("intreprete put5")
    interprete(put5)
    print("intreprete hello_name")
    interprete(hello_name)


@dataclass
class FastFreerMonad:
    type: FreerMonadType
    value: Any
    instrs: [Any]

    @staticmethod
    def pure(value):
        return FastFreerMonad(FreerMonadType.Pure, value, None)

    @staticmethod
    def fish(x2my, y2mz):
        return lambda x: x2my(x).bind(y2mz)

    def bind(self, f):
        if self.type is FreerMonadType.Pure:
            return f(self.value)
        instrs = self.instrs + [f]
        return FastFreerMonad(FreerMonadType.Impure, self.value, instrs)


if __name__ == "__main__":
    pure = FastFreerMonad.pure
    liftF = lambda f: lambda *x: FastFreerMonad(
        FreerMonadType.Impure, f(*x), []
    )
    put = liftF(lambda x: ("put", x))
    get = liftF(lambda: ("get",))

    just5 = pure(5)
    print(just5)
    put5 = put(5)
    print(put5)
    ask_name = put("So what is your name?").bind(lambda _: get())
    print(ask_name)
    hello_name = ask_name.bind(lambda name: put(f"Hello, {name}!"))
    print(hello_name)

    def interprete(m):
        if m.type == FreerMonadType.Pure:
            return m.value
        value = m.value
        if value[0] == "put":
            print(value[1])
            value = ()
        elif value[0] == "get":
            value = input()
        else:
            assert False
        instrs = list(reversed(m.instrs))
        while instrs:
            value = interprete(instrs.pop()(value))
        return value

    print("intreprete put5")
    interprete(put5)
    print("intreprete hello_name")
    interprete(hello_name)
