number_of_iterations = 0


def prefix_function(s: str) -> list[int]:
    dp = [0] * len(s)
    for i in range(1, len(s)):
        j = dp[i - 1]
        while j and s[j] != s[i]:
            j = dp[j - 1]
        dp[i] = j + (s[j] == s[i])
    return dp


def find(haystack: str, needle: str, default: None = None) -> int | None:
    s = needle + haystack
    dp = prefix_function(s)
    for i in range(len(needle) * 2 - 1, len(s)):
        if dp[i] >= len(needle):
            return 1 + i - len(needle) * 2
    return default


while True:
    s1 = input("haystack: ")
    s2 = input("  needle: ")
    print(find(s1, s2))
