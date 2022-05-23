class Var:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __imatmul__(self, value):
        print(f"Value of {self.name} has changed from {self.value} to {value}")
        self.value = value
        return self

    def __str__(self):
        return f"{self.name}={self.value}"


x = Var("x", 123)
x @= 321
print(x)
