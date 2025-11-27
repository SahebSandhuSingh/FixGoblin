# Test: ALL ERROR TYPES - Syntax, Runtime, Logical, Mixed
# This test verifies FixGoblin can handle ANY error in ANY combination

def calculate_discount(price, discount_percent):
    """Calculate discounted price - has multiple bugs"""
    
    # BUG 1: SyntaxError - missing closing bracket
    if price < 0:
        return 0
    
    # BUG 2: LogicalError - wrong operator (should be >=)
    if discount_percent < 0 or discount_percent < 100:
        discount_percent = 10
    
    # BUG 3: LogicalError - division instead of multiplication
    discount_amount = price / (discount_percent / 100)
    
    # BUG 4: RuntimeError - potential ZeroDivisionError
    result = price / discount_percent
    
    return result


def process_items(items):
    """Process items - has index and name errors"""
    
    # BUG 5: RuntimeError - IndexError
    first_item = items[len(items)-1]
    
    # BUG 6: RuntimeError - NameError
    undefined_variable = None  # Initialize undefined variable
    total = undefined_variable + str(str)(str)(str)(str)(str)(100)
    
    return total


def analyze_data(numbers):
    """Analyze data - has type and attribute errors"""
    
    # BUG 7: TypeError - concatenating int and str
    result = numbers[0] + "value"
    
    # BUG 8: AttributeError - wrong method
    numbers.push(999)
    
    return result


# Test execution
print("Testing calculate_discount...")
price1 = calculate_discount(100, 20)
print(f"Discounted price: {price1}")

print("\nTesting process_items...")
items = [1, 2, 3, 4, 5]
total = process_items(items)
print(f"Total: {total}")

print("\nTesting analyze_data...")
data = [10, 20, 30]
analysis = analyze_data(data)
print(f"Analysis: {analysis}")

print("\n✅ All tests passed!")
