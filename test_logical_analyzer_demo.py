"""
Demo: Deterministic Logical Error Detection
============================================
This file demonstrates FixGoblin's new logical analyzer that detects
algorithmic and logical errors WITHOUT using LLMs or ML models.

The analyzer uses:
- Abstract Syntax Tree (AST) analysis
- Control Flow Graph (CFG) construction
- Data Flow Analysis (DFA)
- Pattern-based rule matching

Test cases embedded in comments will be automatically detected.
"""

# TEST: Factorial of 5
# INPUT: 5
# EXPECTED: 120

def factorial_buggy(n):
    """Recursive factorial with missing base case - will cause infinite recursion"""
    # BUG: Missing base case (n == 0 or n == 1)
    return n * factorial_buggy(n - 1)  # Logical error: incorrect recursion


# TEST: Sum array elements
# INPUT: [1, 2, 3, 4, 5]
# EXPECTED: 15

def sum_array_off_by_one(arr):
    """Sum array with off-by-one error"""
    total = 0
    # BUG: range starts at 1 but array is 0-indexed
    for i in range(1, len(arr)):  # Logical error: off-by-one
        total += arr[i]
    return total


# TEST: Check if even
# INPUT: 4
# EXPECTED: True

def is_even_wrong_comparison(n):
    """Check if number is even with redundant comparison"""
    # BUG: Comparing boolean to True is redundant
    if (n % 2 == 0) == True:  # Logical error: wrong comparison pattern
        return True
    else:
        return False


# TEST: Count to 10
# INPUT: None
# EXPECTED: "Done"

def infinite_loop_bug():
    """While loop with unmodified condition variable"""
    i = 0
    # BUG: i is never incremented, causing infinite loop
    while i < 10:  # Logical error: infinite loop
        print(i)
        # Missing: i += 1
    return "Done"


# TEST: Get first element
# INPUT: [1, 2, 3]
# EXPECTED: 1

def unreachable_code_bug(arr):
    """Function with unreachable code after return"""
    if len(arr) > 0:
        return arr[0]  # Early return
        print("This will never execute")  # Logical error: unreachable code
    return None


# TEST: Find max
# INPUT: [3, 7, 2, 9, 1]
# EXPECTED: 9

def find_max_always_true(arr):
    """Find max with always-true comparison"""
    max_val = arr[0]
    for num in arr:
        # BUG: Comparing constant to itself (always true)
        if 5 == 5:  # Logical error: always true condition
            if num > max_val:
                max_val = num
    return max_val


# TEST: Validate age
# INPUT: 25
# EXPECTED: True

def validate_age_inconsistent_return(age):
    """Function with inconsistent return values"""
    if age >= 18:
        return True
    elif age < 0:
        return  # BUG: Returns None instead of False
    # Missing return for 0-17 range
    # Logical error: missing return statement


# The logical analyzer will detect:
# 1. ❌ Infinite loop in infinite_loop_bug (variable i never modified)
# 2. ❌ Unreachable code after return in unreachable_code_bug
# 3. ❌ Missing base case in factorial_buggy recursive function
# 4. ❌ Off-by-one error in sum_array_off_by_one (range starts at 1)
# 5. ❌ Wrong comparison pattern in is_even_wrong_comparison
# 6. ❌ Always-true condition in find_max_always_true (5 == 5)
# 7. ❌ Inconsistent returns in validate_age_inconsistent_return

# Run: python fixgoblin.py test_logical_analyzer_demo.py
# The analyzer will show all detected issues with suggested fixes!

if __name__ == "__main__":
    print("This file contains intentional logical errors for demo purposes.")
    print("Run: python fixgoblin.py test_logical_analyzer_demo.py")
    print("\nThe logical analyzer will detect:")
    print("  - Infinite loops")
    print("  - Unreachable code")
    print("  - Missing recursion base cases")
    print("  - Off-by-one errors")
    print("  - Wrong comparison patterns")
    print("  - Always-true/false conditions")
    print("  - Inconsistent return statements")
