import ctypes

code_in_c = ctypes.CDLL("./code_in_c.so")
code_in_nim = ctypes.CDLL("./code_in_nim.so")
array = (ctypes.c_uint8 * 10)()
for i in range(10):
    array[i] = 10 + i ** 2
print("array:", array)
for lang, lib in (("c", code_in_c), ("nim", code_in_nim)):
    print("---", lang, "---")
    lib.f(id(array), array)
print("array", list(array))
