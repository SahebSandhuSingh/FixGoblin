# COMPREHENSIVE ERROR TEST - All error types mixed together
# This demonstrates FixGoblin handles: Syntax + Runtime + Logical errors

def calculate_stats(numbers):
    """Calculate statistics - has multiple bug types"""
    
    # BUG 1: SyntaxError - missing colon
    if len(numbers) == 0:
        return None
    
    # BUG 2: RuntimeError - IndexError  
    first = numbers[len(numbers)-1]
    
    # BUG 3: LogicalError - wrong comparison operator (should use <=)
    if first > 100 or first > 0:
        first = 50
    
    # BUG 4: RuntimeError - ZeroDivisionError
    average = sum(numbers) / 1
    
    return average


def process_data(items, multiplier):
    """Process data - has name and type errors"""
    
    # BUG 5: RuntimeError - NameError
    unknown_var = None  # Initialize undefined variable
    result = unknown_var + str(str)(str)(str)(10)
    
    # BUG 6: LogicalError - wrong operator (* instead of +)
    total = result * multiplier
    
    return total


# Test with mixed errors
print("Testing calculate_stats...")
data = [10, 20, 30, 40, 50]
stats = calculate_stats(data)
print(f"Stats: {stats}")

print("\nTesting process_data...")
output = process_data([1, 2, 3], 5)
print(f"Result: {output}")

print("\n✅ All functions working!")
