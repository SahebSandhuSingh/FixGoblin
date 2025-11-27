# 🚀 Quick Start: Using FixGoblin with DSL Configuration

## TL;DR - 3 Simple Steps

```bash
# 1. Create a DSL config file
cat > my_rules.dsl << 'EOF'
allow: logical_patch_1
allow: range_fix
optimize_efficiency: true
max_patches: 3
EOF

# 2. Run FixGoblin with the config
python3 fixgoblin_dsl.py buggy_code.py --config my_rules.dsl

# 3. Done! Your code is fixed ✅
```

---

## Real Example

### Before (Buggy Code):
```python
def calculate_total(items):
    total = 0
    for item in items:
        total += item['price']
    # Missing return!

def apply_discount(price, percent):
    discount = price * percent  # Should divide by 100
    return price + discount      # Should subtract
```

### Create Configuration:
```bash
cat > fix_logical.dsl << 'EOF'
allow: logical_patch_1
allow: missing_return_statement
allow: wrong_operator
allow: missing_percentage_conversion
optimize_efficiency: false
max_patches: 3
EOF
```

### Run Repair:
```bash
python3 fixgoblin_dsl.py demo_buggy_code.py --config fix_logical.dsl
```

### After (Fixed Code):
```python
def calculate_total(items):
    total = 0
    for item in items:
        total += item['price']
    return total  # ✅ Added automatically!

def apply_discount(price, percent):
    discount = price * percent / 100  # ✅ Fixed!
    return price - discount            # ✅ Fixed!
```

---

## Common Workflows

### 1. Fix Logical Errors Only
```dsl
# logical_only.dsl
allow: logical_patch_1
allow: wrong_comparison
allow: wrong_operator
optimize_efficiency: false
max_patches: 5
```

```bash
python3 fixgoblin_dsl.py code.py --config logical_only.dsl
```

---

### 2. Conservative Production Mode
```dsl
# production.dsl
allow: range_fix
allow: bounds_check
deny: variable_rename
deny: code_restructure
optimize_efficiency: false
max_patches: 2
```

```bash
python3 fixgoblin_dsl.py critical_code.py --config production.dsl
```

---

### 3. Aggressive Testing Mode
```dsl
# testing.dsl
# Empty allow = allow all
deny: full_rewrite
optimize_efficiency: true
max_patches: 10
```

```bash
python3 fixgoblin_dsl.py experimental.py --config testing.dsl
```

---

## Useful Commands

### View Configuration Before Using
```bash
python3 fixgoblin_dsl.py --show-config my_rules.dsl
```

### Basic Repair (No Config)
```bash
python3 fixgoblin.py buggy_code.py
```

### With More Iterations
```bash
python3 fixgoblin_dsl.py buggy_code.py --config my_rules.dsl --max-iterations 10
```

---

## Available Patch Types

| Patch ID | Description |
|----------|-------------|
| `logical_patch_1` | General logical fixes |
| `wrong_comparison` | Fix `<` vs `>` operators |
| `wrong_operator` | Fix `+` vs `-` operators |
| `missing_percentage_conversion` | Add `/100` for percentages |
| `missing_return_statement` | Add missing returns |
| `range_fix` | Fix array index errors |
| `bounds_check` | Add boundary validation |
| `patch_0`, `patch_1`, `patch_2` | Generic fixes |

---

## Tips

✅ **DO:**
- Start with a strict allow list
- Test on non-critical code first
- Use `--show-config` to preview

❌ **DON'T:**
- Allow all rules in production
- Skip testing after repair
- Use extreme `max_patches` values

---

## Need Help?

```bash
# Show help
python3 fixgoblin_dsl.py --help

# Test DSL parser
python3 Backend/core/dsl_parser.py my_rules.dsl

# Run full test suite
python3 test_dsl_parser.py
```

---

## Full Documentation

- **Complete Guide**: `HOW_TO_USE_DSL.md`
- **API Reference**: `Backend/docs/DSL_PARSER_GUIDE.md`
- **Examples**: `debug_rules.dsl`, `strict_logical_rules.dsl`
