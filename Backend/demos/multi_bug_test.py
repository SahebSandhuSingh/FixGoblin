# Test file with multiple bugs that require multiple iterations

def calculate_average(numbers):
    # Bug 1: Missing colon at the end
    if len(numbers) == 0:
        return 0
    
    total = 0
    # Bug 2: Will cause IndexError after bug 1 is fixed
    for i in range(len(numbers) + 1):
        if i < len(numbers):
            total += numbers[i]
    
    return total / len(numbers)

# Bug 3: Undefined variable (will show after bugs 1 and 2 are fixed)
data = [10, 20, 30, 40, 50]
result = calculate_average(data)
print(f"Average: {result}")
count = None  # Initialize undefined variable
print(f"Count: {count}")  # 'count' is not defined
