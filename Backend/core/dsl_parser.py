"""
DSL Parser Module
=================
Parses a simple DSL configuration file for debugging pipeline rules.

The DSL format supports:
    - allow: rule_name      # Add rule to allowed set
    - deny: rule_name       # Add rule to denied set
    - optimize_efficiency: true/false
    - max_patches: number

Example DSL file (debug_rules.dsl):
    # Configuration for debugging pipeline
    allow: range_fix
    allow: bounds_check
    deny: variable_rename
    optimize_efficiency: true
    max_patches: 3
"""

import os
from typing import Dict, Set, Any


def parse_dsl_config(file_path: str) -> Dict[str, Any]:
    """
    Parse a DSL configuration file and return a configuration dictionary.
    
    Args:
        file_path: Path to the DSL configuration file
        
    Returns:
        Dictionary containing:
            - allow: set of allowed rule names
            - deny: set of denied rule names
            - optimize_efficiency: boolean flag
            - max_patches: integer maximum number of patches
            
    Raises:
        FileNotFoundError: If the file does not exist
        
    Example:
        >>> config = parse_dsl_config("debug_rules.dsl")
        >>> print(config["allow"])
        {'range_fix', 'bounds_check'}
        >>> print(config["optimize_efficiency"])
        True
    """
    # Default configuration
    config = {
        "allow": set(),
        "deny": set(),
        "optimize_efficiency": False,
        "max_patches": 5
    }
    
    # Check if file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"DSL configuration file not found: {file_path}")
    
    # Parse the file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, start=1):
                # Strip whitespace
                line = line.strip()
                
                # Skip blank lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Parse key-value pairs
                if ':' not in line:
                    _warn(f"Line {line_num}: Invalid format (missing ':'): {line}")
                    continue
                
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                
                # Process based on key
                if key == "allow":
                    config["allow"].add(value)
                elif key == "deny":
                    config["deny"].add(value)
                elif key == "optimize_efficiency":
                    config["optimize_efficiency"] = _parse_bool(value, line_num)
                elif key == "max_patches":
                    config["max_patches"] = _parse_int(value, line_num, default=5)
                else:
                    _warn(f"Line {line_num}: Unknown key '{key}' - ignoring")
    
    except Exception as e:
        _warn(f"Error reading DSL file: {e}")
        # Return defaults if file reading fails
        return config
    
    return config


def is_rule_allowed(rule_name: str, config: Dict[str, Any]) -> bool:
    """
    Check if a rule is allowed based on the configuration.
    
    A rule is allowed if:
        1. It is in the 'allow' set (or allow set is empty)
        2. AND it is NOT in the 'deny' set
    
    Args:
        rule_name: Name of the rule to check
        config: Configuration dictionary from parse_dsl_config()
        
    Returns:
        True if the rule is allowed, False otherwise
        
    Example:
        >>> config = {"allow": {"range_fix", "bounds_check"}, "deny": {"variable_rename"}}
        >>> is_rule_allowed("range_fix", config)
        True
        >>> is_rule_allowed("variable_rename", config)
        False
        >>> is_rule_allowed("some_other_rule", config)
        False
    """
    allow_set = config.get("allow", set())
    deny_set = config.get("deny", set())
    
    # If rule is explicitly denied, return False
    if rule_name in deny_set:
        return False
    
    # If allow set is empty, allow all rules (except denied)
    if not allow_set:
        return True
    
    # Otherwise, rule must be in allow set
    return rule_name in allow_set


def _parse_bool(value: str, line_num: int = 0) -> bool:
    """
    Parse a boolean value from string.
    
    Accepts: true, false, yes, no, 1, 0 (case-insensitive)
    
    Args:
        value: String value to parse
        line_num: Line number for error reporting
        
    Returns:
        Boolean value, defaults to False if parsing fails
    """
    value_lower = value.lower()
    
    if value_lower in ('true', 'yes', '1', 'on', 'enabled'):
        return True
    elif value_lower in ('false', 'no', '0', 'off', 'disabled'):
        return False
    else:
        _warn(f"Line {line_num}: Invalid boolean value '{value}' - using default (False)")
        return False


def _parse_int(value: str, line_num: int = 0, default: int = 5) -> int:
    """
    Parse an integer value from string.
    
    Args:
        value: String value to parse
        line_num: Line number for error reporting
        default: Default value if parsing fails
        
    Returns:
        Integer value, defaults to provided default if parsing fails
    """
    try:
        parsed = int(value)
        if parsed < 0:
            _warn(f"Line {line_num}: Negative value '{value}' not allowed - using default ({default})")
            return default
        return parsed
    except ValueError:
        _warn(f"Line {line_num}: Invalid integer value '{value}' - using default ({default})")
        return default


def _warn(message: str) -> None:
    """
    Print a warning message to stderr.
    
    Args:
        message: Warning message to display
    """
    print(f"⚠️  DSL Parser Warning: {message}")


def validate_config(config: Dict[str, Any]) -> bool:
    """
    Validate a configuration dictionary structure.
    
    Args:
        config: Configuration dictionary to validate
        
    Returns:
        True if configuration is valid, False otherwise
    """
    required_keys = {"allow", "deny", "optimize_efficiency", "max_patches"}
    
    # Check all required keys exist
    if not all(key in config for key in required_keys):
        missing = required_keys - set(config.keys())
        _warn(f"Missing required keys: {missing}")
        return False
    
    # Validate types
    if not isinstance(config["allow"], set):
        _warn("'allow' must be a set")
        return False
    
    if not isinstance(config["deny"], set):
        _warn("'deny' must be a set")
        return False
    
    if not isinstance(config["optimize_efficiency"], bool):
        _warn("'optimize_efficiency' must be a boolean")
        return False
    
    if not isinstance(config["max_patches"], int) or config["max_patches"] < 0:
        _warn("'max_patches' must be a non-negative integer")
        return False
    
    return True


def print_config(config: Dict[str, Any]) -> None:
    """
    Pretty-print a configuration dictionary.
    
    Args:
        config: Configuration dictionary to print
    """
    print("=" * 60)
    print("DSL CONFIGURATION")
    print("=" * 60)
    
    print(f"\n📋 Allowed Rules: {len(config['allow'])}")
    if config['allow']:
        for rule in sorted(config['allow']):
            print(f"   ✓ {rule}")
    else:
        print("   (all rules allowed by default)")
    
    print(f"\n🚫 Denied Rules: {len(config['deny'])}")
    if config['deny']:
        for rule in sorted(config['deny']):
            print(f"   ✗ {rule}")
    else:
        print("   (none)")
    
    print(f"\n⚡ Optimize Efficiency: {config['optimize_efficiency']}")
    print(f"🔢 Max Patches: {config['max_patches']}")
    
    print("=" * 60)


# ============================================================
#  COMMAND-LINE INTERFACE (for testing)
# ============================================================

def main():
    """
    Command-line interface for testing the DSL parser.
    
    Usage:
        python3 dsl_parser.py <path_to_dsl_file>
    """
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 dsl_parser.py <path_to_dsl_file>")
        print("\nExample DSL file format:")
        print("  # Debug rules configuration")
        print("  allow: range_fix")
        print("  allow: bounds_check")
        print("  deny: variable_rename")
        print("  optimize_efficiency: true")
        print("  max_patches: 3")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    try:
        # Parse configuration
        config = parse_dsl_config(file_path)
        
        # Validate configuration
        if not validate_config(config):
            print("\n❌ Configuration validation failed!")
            sys.exit(1)
        
        # Print configuration
        print_config(config)
        
        # Test rule checking
        print("\n🧪 Testing rule checking:")
        test_rules = ["range_fix", "bounds_check", "variable_rename", "unknown_rule"]
        for rule in test_rules:
            allowed = is_rule_allowed(rule, config)
            status = "✅ ALLOWED" if allowed else "❌ DENIED"
            print(f"   {rule}: {status}")
        
        print("\n✅ DSL parsing successful!")
        
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
