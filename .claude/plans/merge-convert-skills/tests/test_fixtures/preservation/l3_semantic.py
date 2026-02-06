"""L3 (Semantic) equivalence test fixtures.

These functions are designed to test semantic equivalence:
same I/O behavior for all inputs.
"""


def factorial(n: int) -> int:
    """Calculate factorial recursively."""
    if n <= 1:
        return 1
    return n * factorial(n - 1)


def is_palindrome(s: str) -> bool:
    """Check if string is a palindrome."""
    s = s.lower().replace(" ", "")
    return s == s[::-1]


def binary_search(arr: list[int], target: int) -> int:
    """Binary search returning index or -1."""
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1


def merge_sorted(a: list[int], b: list[int]) -> list[int]:
    """Merge two sorted lists."""
    result = []
    i = j = 0
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            result.append(a[i])
            i += 1
        else:
            result.append(b[j])
            j += 1
    result.extend(a[i:])
    result.extend(b[j:])
    return result


def flatten(nested: list) -> list:
    """Flatten a nested list."""
    result = []
    for item in nested:
        if isinstance(item, list):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result


def count_words(text: str) -> dict[str, int]:
    """Count word occurrences."""
    counts: dict[str, int] = {}
    for word in text.lower().split():
        word = word.strip(".,!?;:")
        if word:
            counts[word] = counts.get(word, 0) + 1
    return counts


def fizzbuzz(n: int) -> list[str]:
    """Generate FizzBuzz sequence."""
    result = []
    for i in range(1, n + 1):
        if i % 15 == 0:
            result.append("FizzBuzz")
        elif i % 3 == 0:
            result.append("Fizz")
        elif i % 5 == 0:
            result.append("Buzz")
        else:
            result.append(str(i))
    return result


def gcd(a: int, b: int) -> int:
    """Calculate greatest common divisor."""
    while b:
        a, b = b, a % b
    return a


def lcm(a: int, b: int) -> int:
    """Calculate least common multiple."""
    return abs(a * b) // gcd(a, b)
