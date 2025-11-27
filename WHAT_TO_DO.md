# 🚀 FixGoblin Quick Start Guide

## What Can I Do?

### ✅ **AUTO-REPAIR (Python Only)**
Automatically fixes bugs in Python code:
```bash
python3 fixgoblin.py your_code.py
```

### 🔍 **ERROR DETECTION (All Languages)**
Finds errors in C++, Java, JavaScript, Go, C:
```bash
python3 check_code.py your_code.cpp
python3 check_code.py MyClass.java
python3 check_code.py app.js
```

---

## Option 1: Use Auto-Repair (Python)

**Best for:** Python projects needing automatic bug fixes

```bash
# Create a buggy Python file
cat > buggy.py << 'EOF'
def greet(name):
print("Hello", name)  # Missing indentation
return
EOF

# Auto-fix it
python3 fixgoblin.py buggy.py --max-iterations 5

# See the fixed code
cat buggy.py
```

**What gets fixed automatically:**
- ✓ Indentation errors
- ✓ Syntax errors (missing colons, wrong operators)
- ✓ Runtime errors (IndexError, NameError, etc.)
- ✓ Logic errors (wrong operators, missing returns)

---

## Option 2: Use Error Detection (C++/Java/JS)

**Best for:** Non-Python code - just shows errors

```bash
# Check your C++ code
python3 check_code.py test.cpp

# Check Java
python3 check_code.py MyClass.java

# Check JavaScript
python3 check_code.py app.js
```

**What you get:**
- ✓ Exact line number of error
- ✓ Error type (SyntaxError, CompileError, etc.)
- ✓ Detailed error message
- ✗ NO auto-fix (you fix it yourself)

---

## Option 3: Use Streamlit UI

**Best for:** Visual interface, beginner-friendly

```bash
# Start the web UI
streamlit run streamlit_app.py
```

Then:
1. Upload or paste your **Python** code
2. Click "Start Debugging"
3. See errors fixed automatically
4. Download fixed code

⚠️ **Important:** Streamlit UI only works for Python!

---

## Examples

### Example 1: Fix Python Indentation
```python
# buggy.py
def hello():
print("world")  # Wrong indentation

# Run: python3 fixgoblin.py buggy.py
# Fixed automatically! ✅
```

### Example 2: Check C++ Errors
```cpp
// test.cpp
int main() {
    int x = 5  // Missing semicolon
    return 0;
}

// Run: python3 check_code.py test.cpp
// Shows: "SyntaxError at line 2: expected ';'"
// You fix it manually
```

### Example 3: Use Streamlit
```bash
streamlit run streamlit_app.py
# Open browser at http://localhost:8501
# Paste Python code
# Click "Start Debugging"
# Download fixed version
```

---

## What Should YOU Do?

### If your code is **PYTHON**:
```bash
# Just run this - it will auto-fix everything!
python3 fixgoblin.py your_file.py
```

### If your code is **C++/Java/JavaScript**:
```bash
# This will show you the errors
python3 check_code.py your_file.cpp

# Then you fix them manually based on the error message
```

### If you want a **nice UI**:
```bash
# Only works for Python code
streamlit run streamlit_app.py
```

---

## Common Questions

**Q: Why doesn't my C++ code get auto-fixed?**  
A: Auto-repair only works for Python. For C++, use `check_code.py` to see errors, then fix manually.

**Q: Can I use the Streamlit website for C++?**  
A: No, the website only supports Python auto-repair. Use `check_code.py` for other languages.

**Q: My Python code says "max iterations reached"?**  
A: The code is too complex. Try increasing: `python3 fixgoblin.py file.py --max-iterations 10`

**Q: How do I see what got fixed?**  
A: Check the `.backup` file to compare before/after: `diff file.py.backup file.py`

---

## Quick Commands Reference

```bash
# Python auto-repair
python3 fixgoblin.py code.py

# C++/Java/JS error check
python3 check_code.py code.cpp

# Streamlit UI (Python only)
streamlit run streamlit_app.py

# Increase repair attempts
python3 fixgoblin.py code.py --max-iterations 10

# Enable efficiency optimization
python3 fixgoblin.py code.py --optimize-efficiency
```

---

## Your Specific Case

Your **C++ linked list code is perfect** - no errors! ✅

If the website showed an error, it's because:
- The website tried to auto-repair it as Python
- Auto-repair only works for Python
- Your C++ code is actually fine

**What to do:**
1. Keep using your C++ code as-is (it's correct!)
2. Use `check_code.py` if you want to verify other C++ files
3. Use FixGoblin auto-repair only for Python projects

---

Made with ❤️ by FixGoblin Team
