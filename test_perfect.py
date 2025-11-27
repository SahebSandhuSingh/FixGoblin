def calculate_sum(n):
    """Calculate sum of numbers from 1 to n"""
    total = 0
    for i in range(1, n + 1):
        total += i
    return total

if __name__ == "__main__":
    result = calculate_sum(5)
    print(f"Sum of 1 to 5: {result}")
