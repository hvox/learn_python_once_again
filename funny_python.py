from functools import cache

@cache
def sum(*xs):
    result = 0
    for x in xs:
        result += x
    return [result]

print('2 + 2 =', sum(2, 2))
sum(2, 2)[0] = 5
print('2 + 2 =', sum(2, 2))
