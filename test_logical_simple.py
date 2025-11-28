"""
Simple Logical Error Demo
==========================
Demonstrates key logical errors detected by the deterministic analyzer.
"""

def infinite_loop_demo():
    """Infinite loop - variable never modified"""
    counter = 0
    while counter < 10:
        print("Stuck!")
        # BUG: Forgot to increment counter
    return "Done"


def off_by_one_demo():
    """Off-by-one error in array indexing"""
    numbers = [10, 20, 30, 40, 50]
    total = 0
    # BUG: Starting at index 1 instead of 0
    for i in range(1, len(numbers)):
        total += numbers[i]
    return total


def missing_base_case():
    """Recursive function without base case"""
    def countdown(n):
        print(n)
        # BUG: No base case - will recurse forever
        return countdown(n - 1)
    
    return countdown(10)


def unreachable_code_demo():
    """Code after return statement"""
    value = 42
    return value
    print("This never executes")  # BUG: Unreachable
    value = value + 1  # BUG: Unreachable


def always_true_condition():
    """Condition that's always true"""
    result = []
    for i in range(5):
        # BUG: 10 > 5 is always true
        if 10 > 5:
            result.append(i)
    return result


def wrong_comparison_demo():
    """Comparing boolean to True unnecessarily"""
    is_valid = True
    # BUG: Redundant comparison to True
    if is_valid == True:
        return "Valid"
    return "Invalid"


def inconsistent_returns():
    """Function with inconsistent return values"""
    def check_value(x):
        if x > 0:
            return "positive"
        elif x < 0:
            return "negative"
        # BUG: Missing return for x == 0
    
    return check_value(0)


if __name__ == "__main__":
    print("🧠 Logical Error Detection Demo")
    print("=" * 50)
    print("\nRun: python fixgoblin.py test_logical_simple.py")
    print("\nExpected detections:")
    print("✓ Infinite loop (counter never incremented)")
    print("✓ Off-by-one error (range starts at 1)")
    print("✓ Missing recursion base case")
    print("✓ Unreachable code after return")
    print("✓ Always-true condition (10 > 5)")
    print("✓ Redundant boolean comparison")
    print("✓ Missing return statement")
