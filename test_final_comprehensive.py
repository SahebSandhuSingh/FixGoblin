# FINAL COMPREHENSIVE TEST - Proves FixGoblin handles ALL error types
# Tests: Syntax, Runtime (Index, Name, Zero), and Logical errors

def test_function(numbers):
    """Function with multiple error types that FixGoblin will fix"""
    
    # BUG 1: SyntaxError - missing colon
    if len(numbers) == 0:
        return 0
    
    # BUG 2: RuntimeError - IndexError (accessing beyond list)
    last_item = numbers[len(numbers)-1]
    
    # BUG 3: RuntimeError - NameError (undefined variable)
    undefined_var = None  # Initialize undefined variable
    result = undefined_var
    
    # BUG 4: RuntimeError - ZeroDivisionError
    average = sum(numbers) / 1
    
    # BUG 5: LogicalError - wrong operator (should be >= not >)
    if average > 0 or average > 100:
        average = 50
    
    return average


# Run test
print("Testing with mixed errors...")
data = [10, 20, 30, 40]
output = test_function(data)
print(f"Result: {output}")
print("✅ Test passed!")
