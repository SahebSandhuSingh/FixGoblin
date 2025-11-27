# DSL Parser Module - Quick Reference

## Overview

The `dsl_parser.py` module provides a simple, production-ready parser for DSL configuration files used by the FixGoblin debugging pipeline. It allows you to control which debugging rules are applied and set optimization parameters.

## Installation

The module is located at:
```
Backend/core/dsl_parser.py
```

No external dependencies required - uses only Python standard library.

## Quick Start

### 1. Create a DSL Configuration File

```dsl
# debug_rules.dsl
allow: range_fix
allow: bounds_check
deny: variable_rename
optimize_efficiency: true
max_patches: 3
```

### 2. Parse the Configuration

```python
from Backend.core.dsl_parser import parse_dsl_config, is_rule_allowed

# Parse configuration file
config = parse_dsl_config("debug_rules.dsl")

# Check if a rule is allowed
if is_rule_allowed("range_fix", config):
    print("Rule is allowed!")
```

## API Reference

### `parse_dsl_config(file_path: str) -> dict`

Parses a DSL configuration file and returns a dictionary.

**Parameters:**
- `file_path` (str): Path to the DSL configuration file

**Returns:**
- Dictionary with keys:
  - `allow` (set): Set of allowed rule names
  - `deny` (set): Set of denied rule names
  - `optimize_efficiency` (bool): Whether to enable efficiency optimizations
  - `max_patches` (int): Maximum number of patches to generate

**Raises:**
- `FileNotFoundError`: If the file does not exist

**Example:**
```python
config = parse_dsl_config("debug_rules.dsl")
print(config["allow"])  # {'range_fix', 'bounds_check'}
print(config["optimize_efficiency"])  # True
```

---

### `is_rule_allowed(rule_name: str, config: dict) -> bool`

Checks if a rule is allowed based on the configuration.

**Logic:**
1. If rule is in `deny` set → return `False`
2. If `allow` set is empty → return `True` (allow all except denied)
3. If rule is in `allow` set → return `True`
4. Otherwise → return `False`

**Parameters:**
- `rule_name` (str): Name of the rule to check
- `config` (dict): Configuration dictionary from `parse_dsl_config()`

**Returns:**
- `bool`: True if rule is allowed, False otherwise

**Example:**
```python
config = {
    "allow": {"range_fix", "bounds_check"},
    "deny": {"variable_rename"}
}

is_rule_allowed("range_fix", config)      # True
is_rule_allowed("variable_rename", config) # False
is_rule_allowed("unknown_rule", config)    # False
```

---

### `validate_config(config: dict) -> bool`

Validates a configuration dictionary structure.

**Parameters:**
- `config` (dict): Configuration dictionary to validate

**Returns:**
- `bool`: True if configuration is valid, False otherwise

**Example:**
```python
if validate_config(config):
    print("Configuration is valid!")
```

---

### `print_config(config: dict) -> None`

Pretty-prints a configuration dictionary to console.

**Parameters:**
- `config` (dict): Configuration dictionary to print

**Example:**
```python
print_config(config)
```

## DSL File Format

### Syntax Rules

1. **Comments**: Lines starting with `#` are ignored
2. **Blank lines**: Empty lines are ignored
3. **Key-value pairs**: Format is `key: value`
4. **Case sensitivity**: Keys are case-insensitive, values are case-sensitive

### Supported Keys

#### `allow: <rule_name>`
Adds a rule to the allowed set. Can be used multiple times.

```dsl
allow: range_fix
allow: bounds_check
allow: logical_patch_1
```

#### `deny: <rule_name>`
Adds a rule to the denied set. Can be used multiple times.

```dsl
deny: variable_rename
deny: code_restructure
```

#### `optimize_efficiency: <boolean>`
Enables or disables efficiency optimizations.

**Accepted values:** `true`, `false`, `yes`, `no`, `1`, `0`, `on`, `off`, `enabled`, `disabled` (case-insensitive)

```dsl
optimize_efficiency: true
```

#### `max_patches: <integer>`
Sets the maximum number of patches to generate per iteration.

```dsl
max_patches: 3
```

### Default Values

If a key is not specified, these defaults are used:

```python
{
    "allow": set(),           # Empty = allow all rules
    "deny": set(),            # Empty = deny no rules
    "optimize_efficiency": False,
    "max_patches": 5
}
```

## Usage Examples

### Example 1: Strict Allow List

Only allow specific patches:

```dsl
# Allow only these patches
allow: range_fix
allow: bounds_check
allow: patch_0

# Optimization settings
optimize_efficiency: true
max_patches: 2
```

Result: Only `range_fix`, `bounds_check`, and `patch_0` are allowed.

### Example 2: Deny List Only

Allow all patches except specific ones:

```dsl
# Deny dangerous operations
deny: variable_rename
deny: code_restructure
deny: full_rewrite

# Settings
optimize_efficiency: false
max_patches: 5
```

Result: All patches are allowed except the three denied ones.

### Example 3: Mixed Configuration

Combine allow and deny lists:

```dsl
# Allow specific patches
allow: range_fix
allow: bounds_check

# But deny this one even if allowed
deny: bounds_check

# Settings
optimize_efficiency: true
max_patches: 3
```

Result: Only `range_fix` is allowed (deny takes precedence over allow).

## Integration with FixGoblin

### In Patch Generator

```python
from Backend.core.dsl_parser import parse_dsl_config, is_rule_allowed

def generate_filtered_patches(error_data, code, dsl_config_path):
    # Load DSL configuration
    config = parse_dsl_config(dsl_config_path)
    
    # Generate all patches
    all_patches = generate_patch_candidates(
        error_data, 
        code,
        optimize_efficiency=config["optimize_efficiency"]
    )
    
    # Filter patches based on DSL rules
    allowed_patches = [
        p for p in all_patches 
        if is_rule_allowed(p["id"], config)
    ]
    
    # Limit to max_patches
    return allowed_patches[:config["max_patches"]]
```

### In Autonomous Repair Loop

```python
from Backend.core.dsl_parser import parse_dsl_config

def autonomous_repair_with_dsl(file_path, dsl_config_path):
    # Load DSL configuration
    config = parse_dsl_config(dsl_config_path)
    
    # Use configuration settings
    return autonomous_repair(
        file_path,
        max_iterations=5,
        optimize_efficiency=config["optimize_efficiency"],
        dsl_config=config
    )
```

## Error Handling

The parser handles errors gracefully:

1. **Unknown keys**: Warns but continues parsing
2. **Invalid boolean values**: Uses default (False) and warns
3. **Invalid integer values**: Uses default (5) and warns
4. **Malformed lines**: Warns and skips line
5. **File not found**: Raises `FileNotFoundError`

All warnings are printed to console with `⚠️` prefix.

## Testing

Run the test suite:

```bash
python3 test_dsl_parser.py
```

Run standalone with a DSL file:

```bash
python3 Backend/core/dsl_parser.py debug_rules.dsl
```

## Best Practices

1. **Always validate after parsing:**
   ```python
   config = parse_dsl_config("debug_rules.dsl")
   if not validate_config(config):
       # Handle invalid configuration
   ```

2. **Use deny list for safety:**
   - Leave `allow` empty to allow all by default
   - Only deny dangerous operations

3. **Start conservative:**
   - Begin with `optimize_efficiency: false`
   - Set lower `max_patches` values
   - Test before enabling aggressive optimizations

4. **Comment your DSL files:**
   - Explain why rules are allowed/denied
   - Document optimization settings

## License

Part of FixGoblin v2.0 - Autonomous Code Repair System
