# DSL Configuration System - User Guide Summary

## 🎯 What Is This?

The DSL (Domain Specific Language) Configuration System lets you **control which debugging rules** FixGoblin applies to your code. Think of it as a "settings file" for the debugger.

## 🚀 Quick Start (3 Steps)

### 1. Create a Configuration File
```bash
cat > my_rules.dsl << 'EOF'
allow: logical_patch_1
allow: range_fix
optimize_efficiency: true
max_patches: 3
EOF
```

### 2. Run FixGoblin with Config
```bash
python3 fixgoblin_dsl.py buggy_code.py --config my_rules.dsl
```

### 3. Done! ✅

---

## 📖 Three Ways to Use It

### Method 1: No Config (Easiest)
```bash
python3 fixgoblin.py buggy_code.py
```
Uses default settings (allows everything).

### Method 2: With DSL Config (Recommended)
```bash
python3 fixgoblin_dsl.py buggy_code.py --config my_rules.dsl
```
You control exactly which patches are allowed.

### Method 3: Programmatic (Advanced)
```python
from Backend.core.dsl_parser import parse_dsl_config

config = parse_dsl_config("my_rules.dsl")
# Use config in your code
```

---

## 📝 DSL File Format

Super simple - just `key: value` pairs:

```dsl
# This is a comment

# Allow specific patches
allow: logical_patch_1
allow: range_fix

# Deny dangerous operations
deny: variable_rename

# Settings
optimize_efficiency: true
max_patches: 3
```

---

## 🎓 Real Example

**Before (Buggy Code):**
```python
def calculate_total(items):
    total = 0
    for item in items:
        total += item['price']
    # Missing return!
```

**Create Config:**
```bash
cat > fix.dsl << 'EOF'
allow: logical_patch_1
allow: missing_return_statement
max_patches: 3
EOF
```

**Run Repair:**
```bash
python3 fixgoblin_dsl.py buggy_code.py --config fix.dsl
```

**After (Fixed Code):**
```python
def calculate_total(items):
    total = 0
    for item in items:
        total += item['price']
    return total  # ✅ Added!
```

---

## 🛠️ Useful Commands

```bash
# Show what a config file does
python3 fixgoblin_dsl.py --show-config my_rules.dsl

# Get help
python3 fixgoblin_dsl.py --help

# Test the parser
python3 Backend/core/dsl_parser.py my_rules.dsl

# Run test suite
python3 test_dsl_parser.py
```

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `QUICKSTART_DSL.md` | Quick 3-step guide |
| `HOW_TO_USE_DSL.md` | Complete user guide |
| `Backend/docs/DSL_PARSER_GUIDE.md` | Technical API docs |

---

## 🎁 Pre-Made Configs

We provide several ready-to-use configurations:

- **`debug_rules.dsl`** - General purpose
- **`debug_rules_minimal.dsl`** - Minimal restrictions
- **`strict_logical_rules.dsl`** - Only logical fixes

Use them:
```bash
python3 fixgoblin_dsl.py code.py --config debug_rules.dsl
```

---

## ✅ What Users Get

1. **Control** - Choose which patches to allow
2. **Safety** - Deny risky operations
3. **Simplicity** - No coding required
4. **Flexibility** - Works with existing FixGoblin
5. **Documentation** - Comprehensive guides
6. **Examples** - Pre-made configs

---

## 💡 Common Use Cases

### Conservative (Production)
```dsl
allow: range_fix
allow: bounds_check
deny: variable_rename
optimize_efficiency: false
max_patches: 2
```

### Aggressive (Testing)
```dsl
# Allow all (empty allow list)
deny: full_rewrite
optimize_efficiency: true
max_patches: 10
```

### Logical Errors Only
```dsl
allow: logical_patch_1
allow: wrong_comparison
allow: wrong_operator
max_patches: 5
```

---

## 🎯 Bottom Line

**Users can:**
1. Create a simple text file (`.dsl`)
2. Specify which debugging rules to use
3. Run FixGoblin with `--config` flag
4. Get controlled, predictable repairs

**No programming knowledge required!**

---

## 📞 Need Help?

Start here:
1. Read `QUICKSTART_DSL.md` (5 minutes)
2. Try examples with pre-made configs
3. Check `HOW_TO_USE_DSL.md` for details
4. Use `--help` for command reference

---

**Made with ❤️ for FixGoblin v2.0**
