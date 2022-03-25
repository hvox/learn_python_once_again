dict1 = {
    0: "hello, world!",
    1: "ohnter antohrea ntheorant rhoetar hoetrn",
    2: "ntohera",
    3: None,
    4: "to be continued",
}
dict1[3] = dict1
print(f"{dict1=}")

dict2 = {0: "hello, world!", 1: "ohnter antohrea ntheorant rhoetar hoetrn"}
dict2 |= {2: "ntohera", 3: None, 4: "to be continued"}
dict2[3] = dict2
print(f"{dict2=}")
