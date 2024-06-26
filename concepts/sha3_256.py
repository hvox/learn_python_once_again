from itertools import islice, zip_longest


def sha3_256(message: str | bytes):
    # https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.202.pdf
    b, r = 1600, 1088

    data = bytearray(message if isinstance(message, bytes) else message.encode("utf-8"))
    if len(data) == r // 8 - 1:
        data.append(0x06 | 0x80)
    else:
        data.extend([0x06] + [0] * (r // 8 - (len(data) + 2) % (r // 8)) + [0x80])
    bits = [byte >> shift & 1 for byte in data for shift in range(8)]

    state = [0] * b
    for window in chunked(bits, r):
        state = [x ^ y for x, y in zip_longest(state, window, fillvalue=0)]
        for round in range(24):
            state = permutate(state, b, round)
    hash = [sum(state[8 * i + j] << j for j in range(8)) for i in range(32)]
    return bytes(hash)


def permutate(state: list[int], b: int, round: int):
    A = [[sum(state[shift + 64 * (x + 5 * y)] << shift for shift in range(64)) for y in range(5)] for x in range(5)]

    # Theta
    C = [xor(A[x][y] for y in range(5)) for x in range(5)]
    D = [C[(x - 1) % 5] ^ u64_rotl(C[(x + 1) % 5]) for x in range(5)]
    A = [[A[x][y] ^ D[x] for y in range(5)] for x in range(5)]

    # Rho
    offsets = [0, 1, 62, 28, 27, 36, 44, 6, 55, 20, 3, 10, 43, 25, 39, 41, 45, 15, 21, 8, 18, 2, 61, 56, 14]
    A = [[u64_rotl(A[x][y], offsets[x + y * 5]) for y in range(5)] for x in range(5)]

    # Pi
    A = [[A[(x + 3 * y) % 5][x] for y in range(5)] for x in range(5)]

    # Chi
    A = [[A[x][y] ^ ((A[(x + 1) % 5][y] ^ 0xFFFFFFFFFFFFFFFF) & A[(x + 2) % 5][y]) for y in range(5)] for x in range(5)]

    # Iota
    ROUND_CONSTANTS = [
        *[0x0000000000000001, 0x0000000000008082, 0x800000000000808A, 0x8000000080008000],
        *[0x000000000000808B, 0x0000000080000001, 0x8000000080008081, 0x8000000000008009],
        *[0x000000000000008A, 0x0000000000000088, 0x0000000080008009, 0x000000008000000A],
        *[0x000000008000808B, 0x800000000000008B, 0x8000000000008089, 0x8000000000008003],
        *[0x8000000000008002, 0x8000000000000080, 0x000000000000800A, 0x800000008000000A],
        *[0x8000000080008081, 0x8000000000008080, 0x0000000080000001, 0x8000000080008008],
    ]
    A[0][0] ^= ROUND_CONSTANTS[round]
    return [A[i // 64 % 5][i // 64 // 5] >> (i % 64) & 1 for i in range(b)]


def chunked(iterable, n: int):
    it = iter(iterable)
    while chunk := list(islice(it, n)):
        yield chunk


def xor(iterable) -> int:
    result = 0
    for x in iterable:
        result ^= x
    return result


def u64_rotl(number: int, n: int = 1) -> int:
    for _ in range(n % 64):
        number = sum(divmod(number << 1, 2**64))
    return number


assert "a7ffc6f8bf1ed76651c14756a061d662f580ff4de43b49fa82d80a4b80f8434a" == sha3_256("").hex()
assert "f7b9aac9823678ed5504a4b48141a1790749d57cfa6dfb0a1f92a01d046578c9" == sha3_256("aboba").hex()
assert "6fef857c4ad7eed256b41638414db9331938e50d697696e8665b49a1077ea783" == sha3_256("\n" * 2048).hex()
