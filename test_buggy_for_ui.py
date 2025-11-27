"""
Test file with multiple bugs for Streamlit UI testing
This file contains syntax, runtime, and logical errors
"""

def calculate_total(items):
    '''Calculate total price with tax'''
    total = 0
    for item in items
        total += item['price']  # Missing colon on line 8
    
    tax = total * 0.08
    return total + tax


def find_max(numbers):
    '''Find maximum number in list'''
    if len(numbers) = 0:  # Wrong operator (= instead of ==)
        return None
    
    max_val = numbers[0]
    for num in numbers:
        if num < max_val:  # Wrong comparison (< instead of >)
            max_val = num
    
    return max_val


def apply_discount(price, discount_percent):
    '''Apply discount to price'''
    discount = price * discount_percent  # Missing /100
    final_price = price + discount  # Wrong operator (+ instead of -)
    return final_price


# Test cases
print("Test 1: Calculate total")
items = [
    {'name': 'Apple', 'price': 10},
    {'name': 'Banana', 'price': 5}
]
print(f"Total with tax: {calculate_total(items)}")

print("\nTest 2: Find maximum")
numbers = [3, 7, 2, 9, 1]
print(f"Maximum: {find_max(numbers)}")

print("\nTest 3: Apply discount")
original = 100
discount = 20
final = apply_discount(original, discount)
print(f"Original: ${original}, Discount: {discount}%, Final: ${final}")
print(f"Expected: $80, Got: ${final}")
