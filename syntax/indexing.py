A = ['first', 'second', 'third', 'second from the end', 'last']
# i-th element == element at offset (i-1) from start
assert A[1] == 'second' and A[2] == 'third'
# we can get i-th element from end using NOT of the offset
assert A[~1] == 'second from the end'
