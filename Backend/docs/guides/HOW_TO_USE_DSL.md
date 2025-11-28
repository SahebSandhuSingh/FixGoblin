# How to Use the DSL Configuration System

## Quick Start for Users

The DSL configuration system lets you control which debugging rules FixGoblin applies to your code. Here's how to use it:

### 1️⃣ **Basic Usage (No Configuration)**

Just run FixGoblin normally - it uses sensible defaults:

```bash
python3 fixgoblin.py buggy_code.py
```

This allows **all** repair strategies and uses default settings.

---

### 2️⃣ **Using a Configuration File**

Create a DSL file to control behavior:

**Step 1: Create `my_rules.dsl`**
```dsl
# My debugging rules
allow: range_fix
allow: bounds_check
allow: logical_patch_1

deny: variable_rename

optimize_efficiency: true
max_patches: 3
```

**Step 2: Run with configuration**
```bash
python3 fixgoblin_dsl.py buggy_code.py --config my_rules.dsl
```

---

### 3️⃣ **Common Use Cases**

#### **🔒 Conservative Mode** (Only Safe Fixes)
```dsl
# conservative_rules.dsl
allow: range_fix
allow: bounds_check
allow: patch_0

deny: variable_rename
deny: code_restructure

optimize_efficiency: false
max_patches: 2
```

Use it:
```bash
python3 fixgoblin_dsl.py important_code.py --config conservative_rules.dsl
```

---

#### **⚡ Aggressive Mode** (Try Everything)
```dsl
# aggressive_rules.dsl
# Allow all rules (empty allow list = allow all)

# Only deny extremely risky operations
deny: full_rewrite

optimize_efficiency: true
max_patches: 10
```

Use it:
```bash
python3 fixgoblin_dsl.py experimental_code.py --config aggressive_rules.dsl
```

---

#### **🎯 Logical Errors Only**
```dsl
# logical_only_rules.dsl
allow: logical_patch_1
allow: wrong_comparison
allow: wrong_operator
allow: missing_percentage_conversion

optimize_efficiency: false
max_patches: 3
```

Use it:
```bash
python3 fixgoblin_dsl.py logic_bug.py --config logical_only_rules.dsl
```

---

### 4️⃣ **Viewing Configuration**

Before running, check what a DSL file does:

```bash
python3 fixgoblin_dsl.py --show-config debug_rules.dsl
```

Output:
```
============================================================
DSL CONFIGURATION: debug_rules.dsl
============================================================

📋 Allowed Rules: 5
   ✓ bounds_check
   ✓ logical_patch_1
   ✓ patch_0
   ✓ patch_1
   ✓ range_fix

🚫 Denied Rules: 2
   ✗ code_restructure
   ✗ variable_rename

⚡ Optimize Efficiency: True
🔢 Max Patches: 3
============================================================
```

---

### 5️⃣ **Complete Workflow Example**

Let's fix `test_logical_errors.py` with custom rules:

**Step 1: Create configuration**
```bash
cat > my_logical_rules.dsl << 'EOF'
# Configuration for logical error fixes
allow: logical_patch_1
allow: wrong_comparison
allow: wrong_operator
allow: missing_percentage_conversion

optimize_efficiency: false
max_patches: 5
EOF
```

**Step 2: Preview the configuration**
```bash
python3 fixgoblin_dsl.py --show-config my_logical_rules.dsl
```

**Step 3: Run the repair**
```bash
python3 fixgoblin_dsl.py test_logical_errors.py --config my_logical_rules.dsl
```

**Step 4: Check results**
```bash
python3 test_logical_errors.py
```

---

## 📚 Command Reference

### Standard FixGoblin (No DSL)
```bash
python3 fixgoblin.py <file.py> [--optimize] [--max-iterations N]
```

### FixGoblin with DSL
```bash
python3 fixgoblin_dsl.py <file.py> --config <dsl_file> [OPTIONS]
```

**Options:**
- `--config FILE` or `-c FILE` - Use DSL configuration file
- `--max-iterations N` - Maximum repair attempts (default: 5)
- `--show-config FILE` - Display configuration and exit

---

## 🎓 Understanding DSL Files

### DSL Syntax

```dsl
# Comments start with #

# Allow specific rules (whitelist mode)
allow: rule_name_1
allow: rule_name_2

# Deny specific rules (blacklist)
deny: dangerous_rule

# Boolean settings (true/false, yes/no, 1/0)
optimize_efficiency: true

# Integer settings
max_patches: 3
```

### How Rules Work

**Scenario 1: Empty Allow List**
```dsl
# No allow rules = allow everything
deny: variable_rename
```
✅ Result: All rules allowed **except** `variable_rename`

**Scenario 2: Explicit Allow List**
```dsl
allow: range_fix
allow: bounds_check
```
✅ Result: **Only** `range_fix` and `bounds_check` allowed

**Scenario 3: Conflict Resolution**
```dsl
allow: bounds_check
deny: bounds_check
```
✅ Result: `deny` wins - rule is **denied**

---

## 🛠️ Available Patch Types

Common patch IDs you can allow/deny:

### Correctness Patches
- `patch_0` - Primary fix (e.g., len(array)-1)
- `patch_1` - Alternative fix (e.g., boundary check)
- `patch_2` - Secondary alternative
- `range_fix` - Fix range/index errors
- `bounds_check` - Add boundary validation

### Logical Patches
- `logical_patch_1` - General logical fixes
- `wrong_comparison` - Fix comparison operators
- `wrong_operator` - Fix arithmetic operators
- `missing_percentage_conversion` - Fix percentage calculations
- `missing_return_statement` - Add missing returns
- `potential_off_by_one` - Fix off-by-one errors

### Transformation Patches
- `variable_rename` - Rename variables
- `code_restructure` - Restructure code blocks
- `full_rewrite` - Complete function rewrite

---

## 💡 Best Practices

### ✅ DO
1. **Start conservative** - Begin with a strict allow list
2. **Test incrementally** - Add one rule at a time
3. **Comment your DSL** - Explain why rules are allowed/denied
4. **Version control DSL files** - Track configuration changes
5. **Use descriptive names** - `production_rules.dsl`, `testing_rules.dsl`

### ❌ DON'T
1. **Don't allow all in production** - Always have some restrictions
2. **Don't skip testing** - Verify repairs work correctly
3. **Don't ignore warnings** - Parser warnings indicate issues
4. **Don't use extreme values** - Keep `max_patches` reasonable (3-10)

---

## 🔧 Troubleshooting

### "Configuration file not found"
```bash
# Check file path
ls -la *.dsl

# Use absolute path
python3 fixgoblin_dsl.py code.py --config /full/path/to/rules.dsl
```

### "No patches generated"
Your allow list might be too restrictive:
```dsl
# Too restrictive - only one rule
allow: range_fix

# Better - allow multiple relevant rules
allow: range_fix
allow: bounds_check
allow: patch_0
allow: patch_1
```

### "Rule not being applied"
Check if it's in the deny list:
```bash
# Show current configuration
python3 fixgoblin_dsl.py --show-config my_rules.dsl
```

---

## 📝 Example DSL Files

### Production Use
```dsl
# production_rules.dsl
# Conservative rules for production code

allow: range_fix
allow: bounds_check
allow: patch_0
allow: logical_patch_1

deny: variable_rename
deny: code_restructure
deny: full_rewrite

optimize_efficiency: false
max_patches: 2
```

### Development Use
```dsl
# dev_rules.dsl
# More permissive for development

allow: range_fix
allow: bounds_check
allow: logical_patch_1
allow: wrong_comparison
allow: wrong_operator
allow: patch_0
allow: patch_1
allow: patch_2

deny: full_rewrite

optimize_efficiency: true
max_patches: 5
```

### Testing Use
```dsl
# test_rules.dsl
# Allow all rules for testing

# Empty allow = allow everything
deny: full_rewrite

optimize_efficiency: true
max_patches: 10
```

---

## 🚀 Integration Examples

### In CI/CD Pipeline
```bash
#!/bin/bash
# fix_bugs.sh

# Use strict rules in CI
python3 fixgoblin_dsl.py src/main.py --config ci_rules.dsl --max-iterations 3

# Check if repair was successful
if [ $? -eq 0 ]; then
    echo "✅ Repair successful"
    python3 -m pytest tests/
else
    echo "❌ Repair failed"
    exit 1
fi
```

### In Makefile
```makefile
.PHONY: fix-strict fix-aggressive

fix-strict:
	python3 fixgoblin_dsl.py src/*.py --config strict_rules.dsl

fix-aggressive:
	python3 fixgoblin_dsl.py src/*.py --config aggressive_rules.dsl
```

### In Python Script
```python
from Backend.core.dsl_parser import parse_dsl_config, is_rule_allowed

# Load configuration
config = parse_dsl_config("my_rules.dsl")

# Use in your code
if config["optimize_efficiency"]:
    run_optimization_passes()

# Filter patches
patches = [p for p in all_patches if is_rule_allowed(p["id"], config)]
```

---

## 📖 Additional Resources

- **Full API Documentation**: `Backend/docs/DSL_PARSER_GUIDE.md`
- **Test Suite**: `test_dsl_parser.py`
- **Example Configs**: `debug_rules.dsl`, `debug_rules_minimal.dsl`
- **Module Source**: `Backend/core/dsl_parser.py`

---

## 🆘 Need Help?

Run with `--help`:
```bash
python3 fixgoblin_dsl.py --help
```

View configuration:
```bash
python3 fixgoblin_dsl.py --show-config your_rules.dsl
```

Test parser directly:
```bash
python3 Backend/core/dsl_parser.py your_rules.dsl
```
