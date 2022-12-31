from rationals import Rational

while True:
    x = Rational(input(">>> "))
    print("x =", x)
    print("repr(x) =", repr(x))
    print("float(x) =", float(x))
    print("x.as_integer_ration() =", x.as_integer_ratio())
    print()
