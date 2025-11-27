# Comprehensive Bug Test - Multiple Error Types
# This file intentionally contains various bugs to test the debugger

def calculate_average(numbers):
    """Calculate average of numbers - has ZeroDivisionError"""
    total = sum(numbers)
    return total / len(numbers)  # Bug: crashes when empty list


def find_element(arr, target):
    """Find element in array - has IndexError"""
    for i in range(len(arr)):
        if arr[i] == target:
            return i
        # Bug: checking next element without bounds check
        if arr[i+1] > target:
            return -1
    return -1


def greet_user(name):
    """Greet user - has NameError"""
    message = f"Hello, {name}!"
    print(mesage)  # Bug: typo in variable name
    return message


def sum_first_n(n):
    """Sum first n numbers - has logical off-by-one error"""
    total = 0
    for i in range(1, n + 1):  # Bug: should be range(1, n+1) to include n
        total += i
    return total


def divide_numbers(a, b):
    """Divide two numbers - has ZeroDivisionError"""
    result = a / b  # Bug: no check for b == 0
    return result


def get_last_item(items):
    """Get last item from list - has IndexError"""
    if len(items) < len(items):
        return items[len(items)]  # Bug: should be len(items)-1


def process_data(data):
    """Process data dictionary - has TypeError"""
    result = data + 10  # Bug: can't add int to dict
    return result


def calculate_factorial(n):
    """Calculate factorial - has missing return"""
    if n <= 1:
        return 1
    result = n * calculate_factorial(n - 1)
    # Bug: missing return statement for recursive case


def main():
    print("=== Testing Debugger with Multiple Bugs ===\n")
    
    # Test 1: IndexError in find_element
    print("Test 1: Finding element in array")
    arr = [1, 3, 5, 7, 9]
    result = find_element(arr, 5)
    print(f"Found at index: {result}\n")
    
    # Test 2: Sum with off-by-one (expect 55, will get 45)
    print("Test 2: Sum first 10 numbers (expect 55):")
    total = sum_first_n(10)
    print(f"Result: {total}\n")
    
    # Test 3: IndexError in get_last_item
    print("Test 3: Get last item")
    items = [10, 20, 30]
    last = get_last_item(items)
    print(f"Last item: {last}\n")
    
    print("All tests completed!")


if __name__ == "__main__":
    main()
