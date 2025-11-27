"""Final Test - 6 Different Error Types"""

def divide_numbers(a, b):
    """Bug 1: ZeroDivisionError - dividing by zero"""
    result = a / b if b != 0 else 0
    return result

def get_last_element(items):
    """Bug 2: IndexError - accessing beyond list length"""
    return items[len(items)-1]

def greet_user(age):
    """Bug 3: NameError - undefined variable"""
    name = None  # Initialize undefined variable
    return f"Hello {name}, you are {age} years old"

def process_data(text, number):
    """Bug 4: TypeError - concatenating incompatible types"""
    return text + str(number)

def convert_text(message):
    """Bug 5: AttributeError - method typo"""
    return message.upper()

def calculate_total(prices):
    """Bug 6: TypeError - sum on non-numeric"""
    total = sum(prices)
    return total

def main():
    print("=== Final 6 Errors Test ===\n")
    
    print("Test 1: ZeroDivisionError")
    result = divide_numbers(10, 0)
    print(f"Result: {result}")
    
    print("\nTest 2: IndexError")
    my_list = [1, 2, 3, 4, 5]
    last = get_last_element(my_list)
    print(f"Last element: {last}")
    
    print("\nTest 3: NameError")
    greeting = greet_user(30)
    print(greeting)
    
    print("\nTest 4: TypeError")
    output = process_data("Number: ", 42)
    print(output)
    
    print("\nTest 5: AttributeError")
    upper_text = convert_text("hello")
    print(f"Uppercase: {upper_text}")
    
    print("\nTest 6: TypeError")
    items = ["apple", "banana", "cherry"]
    total = calculate_total(items)
    print(f"Total: {total}")
    
    print("\n=== All Tests Complete ===")

if __name__ == "__main__":
    main()
