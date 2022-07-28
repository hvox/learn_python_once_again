class NewInt(int):
    def f(self:int):
        return self ** self
__builtins__.int = NewInt
x = int(input())
print(x.f())
