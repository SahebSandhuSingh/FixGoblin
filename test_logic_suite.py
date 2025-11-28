"""
Test Suite for Logical Analyzer
================================
Tests various logical errors to verify detection accuracy.
"""

# TEST 1: Dictionary key mismatch (like fibonacci bug)
def cache_lookup(key, cache={}):
    if key in cache:
        return cache[0]  # BUG: Should be cache[key]
    
    result = compute(key)
    cache[key] = result
    return result

def compute(x):
    return x * 2


# TEST 2: Loop variable never modified (infinite loop)
def countdown():
    counter = 10
    while counter > 0:
        print(counter)
        # BUG: Forgot counter -= 1
    return "Done"


# TEST 3: Missing recursion base case
def factorial(n):
    # BUG: No base case for n <= 1
    return n * factorial(n - 1)


# TEST 4: Off-by-one error in array access
def sum_elements(arr):
    total = 0
    # BUG: Starting at 1 instead of 0
    for i in range(1, len(arr)):
        total += arr[i]
    return total


# TEST 5: Unreachable code after return
def early_exit(x):
    if x > 0:
        return "positive"
    return "non-positive"
    print("This never runs")  # BUG: Unreachable


# TEST 6: Wrong comparison (redundant boolean check)
def is_active(status):
    # BUG: Comparing boolean to True
    if status == True:
        return "active"
    return "inactive"


# TEST 7: Always true condition
def filter_data(items):
    result = []
    for item in items:
        # BUG: 10 > 5 is always true
        if 10 > 5:
            result.append(item)
    return result


# TEST 8: Inconsistent return statements
def classify(value):
    if value > 0:
        return "positive"
    elif value < 0:
        return "negative"
    # BUG: Missing return for value == 0


# TEST 9: Variable used in wrong context
def lookup_user(user_id, database={}):
    if user_id in database:
        return database["admin"]  # BUG: Should be database[user_id]
    return None


# TEST 10: Wrong loop range causing skip
def process_all(data):
    # BUG: range(1, n) skips first element at index 0
    for i in range(1, len(data)):
        print(f"Processing: {data[i]}")


print("Run: python3 fixgoblin.py test_logic_suite.py")
print("\nExpected detections:")
print("1. Dictionary key mismatch in cache_lookup (cache[0] vs cache[key])")
print("2. Infinite loop in countdown (counter never modified)")
print("3. Missing base case in factorial")
print("4. Off-by-one in sum_elements (starts at 1)")
print("5. Unreachable code in early_exit")
print("6. Wrong comparison in is_active (== True)")
print("7. Always true condition in filter_data (10 > 5)")
print("8. Missing return in classify (value == 0)")
print("9. Dictionary key mismatch in lookup_user")
print("10. Off-by-one in process_all (starts at 1)")
