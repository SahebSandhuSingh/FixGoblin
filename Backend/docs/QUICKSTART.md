# FixGoblin - Quick Start Guide

## 🚀 5-Minute Getting Started

### Prerequisites
- Python 3.7+ installed
- Basic terminal/command-line knowledge

### Installation
```bash
# Clone or download the FixGoblin repository
cd FixGoblin/
```

That's it! No dependencies to install. FixGoblin is **100% offline** and uses only Python standard library.

---

## 🎯 Your First Repair

### Create a buggy file
```python
# test.py
def calculate_sum(numbers):
    total = 0
    for i in range(len(numbers) + 1):  # Bug: off-by-one error
        total += numbers[i]
    return total

print(calculate_sum([1, 2, 3, 4, 5]))
```

### Run autonomous repair
```bash
python3 autonomous_repair.py test.py
```

### Output
```
🤖 AUTONOMOUS REPAIR LOOP - FixGoblin v2.0
================================================================================
📁 Target: test.py
🔄 Max Iterations: 5

▶▶▶▶ ITERATION 1/5 ▶▶▶▶
🔬 Running code in sandbox...
❌ Execution failed with errors
🐛 Parsing error...
   Type: IndexError (Line 4)
🔧 Generating patches...
   Generated 3 patch candidate(s)
🏆 Selecting best patch...
   Selected: patch_2 (Score: 150)
💾 Applying patch to file...
   ✅ Applied: test.py.backup

▶▶▶▶ ITERATION 2/5 ▶▶▶▶
🔬 Running code in sandbox...
✅ CODE RUNS SUCCESSFULLY!

📋 REPAIR SUMMARY
🎯 Final Status: SUCCESS
✅ Success: True
🔄 Total Iterations: 2
```

### Check the fixed code
```bash
cat test.py
```

Fixed version:
```python
def calculate_sum(numbers):
    total = 0
    for i in range(len(numbers) + 1):
        if i < len(numbers):  # ✅ Boundary check added
            total += numbers[i]
    return total

print(calculate_sum([1, 2, 3, 4, 5]))
```

---

## 🎓 Common Use Cases

### 1. Quick Fix (Default)
```bash
python3 autonomous_repair.py your_file.py
```
- Tries up to 5 times
- Generates correctness patches only
- Shows detailed progress

### 2. With Optimization
```bash
python3 autonomous_repair.py your_file.py --optimize
```
- Also generates efficiency patches
- May improve performance
- Slightly longer execution time

### 3. Custom Iteration Limit
```bash
python3 autonomous_repair.py your_file.py --max-iterations 10
```
- For complex bugs
- More repair attempts
- Higher success rate

### 4. Save Repair Log
```bash
python3 autonomous_repair.py your_file.py --log repair.json
```
- Exports complete history
- JSON format
- Good for analysis

### 5. Batch Processing
```bash
for file in *.py; do
    python3 autonomous_repair.py "$file" --log "${file%.py}_repair.json"
done
```

---

## 🛟 Troubleshooting

### Problem: "File not found"
```bash
# Make sure file exists and path is correct
ls your_file.py

# Use absolute path if needed
python3 autonomous_repair.py /absolute/path/to/your_file.py
```

### Problem: Max iterations reached
```bash
# Increase iteration limit
python3 autonomous_repair.py your_file.py --max-iterations 15

# Or check if bug is too complex for automated repair
```

### Problem: Want to undo changes
```bash
# Restore from backup
cp your_file.py.backup your_file.py
```

---

## 📚 What FixGoblin Can Fix

### ✅ Supported Error Types
- **IndexError**: Array out of bounds
- **SyntaxError**: Missing colons, parentheses, operators
- **NameError**: Undefined variables, typos
- **ZeroDivisionError**: Division by zero
- **IndentationError**: Incorrect indentation
- **TypeError**: Type mismatches (partial)

### ❌ Limitations
- Complex logic errors (may require human review)
- API/library compatibility issues
- Performance bottlenecks (unless --optimize used)
- Multi-file dependencies

---

## 🎯 Best Practices

### 1. Start Simple
```bash
# Try default settings first
python3 autonomous_repair.py file.py
```

### 2. Review Changes
```bash
# Check what was fixed
diff file.py.backup file.py
```

### 3. Keep Backups
```bash
# Backup is automatic, but keep originals too
cp important_file.py important_file.py.original
python3 autonomous_repair.py important_file.py
```

### 4. Use Version Control
```bash
# Commit before repair
git commit -am "Before FixGoblin repair"
python3 autonomous_repair.py file.py
git diff  # Review changes
```

---

## 🚀 Next Steps

### Test on provided examples
```bash
# Simple bug
python3 autonomous_repair.py user.py

# Multiple bugs
python3 autonomous_repair.py multi_bug_test.py

# Run comprehensive demo
python3 comprehensive_demo.py
```

### Read documentation
- `README.md` - Complete user guide
- `ARCHITECTURE.md` - System internals
- `SYSTEM_FLOW.md` - Execution flow
- `STEP5_COMPLETE.md` - Implementation details

### Explore options
```bash
# See all available flags
python3 autonomous_repair.py --help
```

---

## 💡 Pro Tips

1. **Always check the diff**: Review what was changed
2. **Test after repair**: Run your test suite
3. **Iterate if needed**: Increase max-iterations for complex bugs
4. **Use --log**: Track repair history for learning
5. **Backup everything**: Automatic backups are created, but keep originals

---

## 🎉 You're Ready!

You now know how to:
- ✅ Run autonomous repair on buggy code
- ✅ Use different repair modes
- ✅ Review and verify fixes
- ✅ Troubleshoot common issues

**Start fixing bugs automatically! 🤖**

---

## 📞 Need Help?

- Check `README.md` for detailed documentation
- Review `ARCHITECTURE.md` for technical details
- Run `comprehensive_demo.py` for examples
- Look at test files (`user.py`, `multi_bug_test.py`)

**Happy debugging! ✨**
