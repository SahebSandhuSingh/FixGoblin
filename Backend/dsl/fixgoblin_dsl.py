"""
FixGoblin with DSL Configuration Support
=========================================
This example shows how users can use DSL configuration files
to control the debugging pipeline behavior.
"""

import os
import sys

# Add Backend to path
backend_path = os.path.join(os.path.dirname(__file__), 'Backend')
sys.path.insert(0, backend_path)

from core.dsl_parser import parse_dsl_config, is_rule_allowed, print_config
from core.autonomous_repair import autonomous_repair
from core.patch_generator import generate_patch_candidates
from core.patch_optimizer import select_best_patch


def repair_with_dsl_config(file_path: str, dsl_config_path: str = None, max_iterations: int = 5):
    """
    Repair code using DSL configuration to control behavior.
    
    Args:
        file_path: Path to the code file to repair
        dsl_config_path: Path to DSL configuration file (optional)
        max_iterations: Maximum repair iterations
        
    Returns:
        Repair result dictionary
    """
    
    # Load DSL configuration if provided
    if dsl_config_path and os.path.exists(dsl_config_path):
        print(f"📋 Loading DSL configuration from: {dsl_config_path}")
        config = parse_dsl_config(dsl_config_path)
        print_config(config)
        print()
    else:
        # Use defaults if no DSL file provided
        print("📋 No DSL configuration provided - using defaults")
        config = {
            "allow": set(),  # Allow all
            "deny": set(),   # Deny none
            "optimize_efficiency": False,
            "max_patches": 5
        }
    
    # Run autonomous repair with DSL configuration
    result = autonomous_repair(
        file_path=file_path,
        max_iterations=max_iterations,
        optimize_efficiency=config["optimize_efficiency"]
    )
    
    return result


def main():
    """
    Command-line interface for FixGoblin with DSL support.
    
    Usage examples:
        # Use default settings
        python3 fixgoblin_dsl.py buggy_code.py
        
        # Use DSL configuration file
        python3 fixgoblin_dsl.py buggy_code.py --config debug_rules.dsl
        
        # Use DSL config with custom iterations
        python3 fixgoblin_dsl.py buggy_code.py --config debug_rules.dsl --max-iterations 10
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description="FixGoblin with DSL Configuration Support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic repair (no DSL config)
  python3 fixgoblin_dsl.py test_logical_errors.py
  
  # Use DSL configuration
  python3 fixgoblin_dsl.py test_logical_errors.py --config debug_rules.dsl
  
  # Strict mode with specific rules
  python3 fixgoblin_dsl.py buggy_code.py --config strict_rules.dsl --max-iterations 10
  
  # Show available DSL config
  python3 fixgoblin_dsl.py --show-config debug_rules.dsl
        """
    )
    
    parser.add_argument(
        'file_path',
        nargs='?',
        help='Path to the code file to repair'
    )
    
    parser.add_argument(
        '--config', '-c',
        metavar='DSL_FILE',
        help='Path to DSL configuration file (e.g., debug_rules.dsl)'
    )
    
    parser.add_argument(
        '--max-iterations',
        type=int,
        default=5,
        help='Maximum number of repair iterations (default: 5)'
    )
    
    parser.add_argument(
        '--show-config',
        metavar='DSL_FILE',
        help='Display DSL configuration and exit'
    )
    
    args = parser.parse_args()
    
    # Handle --show-config
    if args.show_config:
        if not os.path.exists(args.show_config):
            print(f"❌ Error: Configuration file not found: {args.show_config}")
            sys.exit(1)
        
        print("\n" + "=" * 70)
        print(f"DSL CONFIGURATION: {args.show_config}")
        print("=" * 70)
        
        config = parse_dsl_config(args.show_config)
        print_config(config)
        
        print("\n💡 To use this configuration:")
        print(f"   python3 fixgoblin_dsl.py <file.py> --config {args.show_config}")
        print()
        sys.exit(0)
    
    # Validate file_path
    if not args.file_path:
        parser.print_help()
        sys.exit(1)
    
    if not os.path.exists(args.file_path):
        print(f"❌ Error: File not found: {args.file_path}")
        sys.exit(1)
    
    # Run repair with DSL configuration
    print("=" * 70)
    print("🤖 FixGoblin v2.0 - DSL Configuration Mode")
    print("=" * 70)
    print(f"📁 Target File: {args.file_path}")
    print(f"⚙️  DSL Config: {args.config or 'None (using defaults)'}")
    print(f"🔄 Max Iterations: {args.max_iterations}")
    print("=" * 70)
    print()
    
    result = repair_with_dsl_config(
        file_path=args.file_path,
        dsl_config_path=args.config,
        max_iterations=args.max_iterations
    )
    
    # Exit with appropriate code
    sys.exit(0 if result['success'] else 1)


if __name__ == "__main__":
    main()
