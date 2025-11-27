"""
DSL Parser Test Suite
=====================
Demonstrates usage of the DSL parser module.
"""

import sys
import os

# Add Backend/core to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Backend', 'core'))

from dsl_parser import (
    parse_dsl_config,
    is_rule_allowed,
    validate_config,
    print_config
)


def test_dsl_parser():
    """Test the DSL parser with various scenarios."""
    
    print("=" * 70)
    print("DSL PARSER TEST SUITE")
    print("=" * 70)
    
    # Test 1: Parse existing DSL file
    print("\n📝 Test 1: Parsing debug_rules.dsl")
    print("-" * 70)
    
    try:
        config = parse_dsl_config("debug_rules.dsl")
        print("✅ File parsed successfully!")
        print_config(config)
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 2: Validate configuration
    print("\n📝 Test 2: Validating configuration")
    print("-" * 70)
    
    is_valid = validate_config(config)
    if is_valid:
        print("✅ Configuration is valid!")
    else:
        print("❌ Configuration validation failed!")
        return False
    
    # Test 3: Test rule checking
    print("\n📝 Test 3: Testing rule checking")
    print("-" * 70)
    
    test_cases = [
        ("range_fix", True, "In allow set"),
        ("bounds_check", True, "In allow set"),
        ("variable_rename", False, "In deny set"),
        ("unknown_rule", False, "Not in allow set"),
        ("logical_patch_1", True, "In allow set"),
    ]
    
    all_passed = True
    for rule_name, expected, reason in test_cases:
        result = is_rule_allowed(rule_name, config)
        status = "✅" if result == expected else "❌"
        print(f"{status} {rule_name}: {result} (expected {expected}) - {reason}")
        if result != expected:
            all_passed = False
    
    if not all_passed:
        print("\n❌ Some rule checks failed!")
        return False
    
    print("\n✅ All rule checks passed!")
    
    # Test 4: Test with empty allow set (should allow all except denied)
    print("\n📝 Test 4: Testing with empty allow set")
    print("-" * 70)
    
    config_empty_allow = {
        "allow": set(),
        "deny": {"variable_rename"},
        "optimize_efficiency": False,
        "max_patches": 5
    }
    
    print("Configuration: allow=empty, deny={'variable_rename'}")
    test_rules = ["range_fix", "variable_rename", "any_other_rule"]
    for rule in test_rules:
        allowed = is_rule_allowed(rule, config_empty_allow)
        status = "✅ ALLOWED" if allowed else "❌ DENIED"
        print(f"   {rule}: {status}")
    
    # Test 5: Test configuration access
    print("\n📝 Test 5: Accessing configuration values")
    print("-" * 70)
    
    print(f"Optimize Efficiency: {config['optimize_efficiency']}")
    print(f"Max Patches: {config['max_patches']}")
    print(f"Number of allowed rules: {len(config['allow'])}")
    print(f"Number of denied rules: {len(config['deny'])}")
    
    # Test 6: Error handling
    print("\n📝 Test 6: Error handling")
    print("-" * 70)
    
    try:
        print("Attempting to parse non-existent file...")
        parse_dsl_config("non_existent_file.dsl")
        print("❌ Should have raised FileNotFoundError!")
        return False
    except FileNotFoundError:
        print("✅ FileNotFoundError raised as expected!")
    
    print("\n" + "=" * 70)
    print("🎉 ALL TESTS PASSED!")
    print("=" * 70)
    return True


def test_integration_example():
    """Show how to integrate DSL parser with debugging pipeline."""
    
    print("\n\n" + "=" * 70)
    print("INTEGRATION EXAMPLE")
    print("=" * 70)
    
    print("\n# Step 1: Load configuration from DSL file")
    print("config = parse_dsl_config('debug_rules.dsl')")
    
    config = parse_dsl_config("debug_rules.dsl")
    
    print("\n# Step 2: Use configuration in debugging pipeline")
    print("patches = generate_all_patches(error_data, code)")
    print("filtered_patches = [p for p in patches if is_rule_allowed(p['id'], config)]")
    
    # Simulate patch filtering
    all_patches = [
        {"id": "range_fix", "description": "Fix range error"},
        {"id": "bounds_check", "description": "Add bounds check"},
        {"id": "variable_rename", "description": "Rename variable"},
        {"id": "unknown_patch", "description": "Unknown patch"},
    ]
    
    print("\n# Step 3: Filter patches based on allow/deny rules")
    filtered_patches = [
        p for p in all_patches 
        if is_rule_allowed(p['id'], config)
    ]
    
    print(f"\nOriginal patches: {len(all_patches)}")
    for p in all_patches:
        allowed = is_rule_allowed(p['id'], config)
        status = "✅" if allowed else "❌"
        print(f"  {status} {p['id']}: {p['description']}")
    
    print(f"\nFiltered patches: {len(filtered_patches)}")
    for p in filtered_patches:
        print(f"  ✅ {p['id']}: {p['description']}")
    
    print(f"\n# Step 4: Apply optimization settings")
    print(f"optimize_efficiency = {config['optimize_efficiency']}")
    print(f"max_patches = {config['max_patches']}")
    
    if config['optimize_efficiency']:
        print("✅ Efficiency optimizations ENABLED")
    
    if len(filtered_patches) > config['max_patches']:
        print(f"⚠️  Limiting to {config['max_patches']} patches (from {len(filtered_patches)})")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    success = test_dsl_parser()
    
    if success:
        test_integration_example()
        sys.exit(0)
    else:
        sys.exit(1)
