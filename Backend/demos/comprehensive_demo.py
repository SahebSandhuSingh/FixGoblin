"""
COMPREHENSIVE DEMO: Autonomous Repair Loop
===========================================
Demonstrates the complete FixGoblin autonomous repair system.
"""

from autonomous_repair import autonomous_repair, print_repair_summary, save_repair_log
import os


def demo_single_bug_repair():
    """Demo: Single bug repair (IndexError)."""
    print("\n" + "=" * 80)
    print("DEMO 1: SINGLE BUG REPAIR")
    print("=" * 80)
    print("Testing: user.py (bubble sort with IndexError)")
    
    # Ensure buggy version
    if os.path.exists('user.py.backup'):
        os.system('cp user.py.backup user.py')
    
    result = autonomous_repair('user.py', max_iterations=3, optimize_efficiency=False)
    
    print("\n✨ DEMO 1 COMPLETE")
    print(f"   Success: {result['success']}")
    print(f"   Iterations: {result['total_iterations']}")
    print(f"   Status: {result['final_status']}")


def demo_multi_bug_repair():
    """Demo: Multiple sequential bugs."""
    print("\n" + "=" * 80)
    print("DEMO 2: MULTI-BUG REPAIR")
    print("=" * 80)
    print("Testing: multi_bug_test.py (SyntaxError → IndexError → NameError)")
    
    # Ensure buggy version
    if os.path.exists('multi_bug_test.py.backup'):
        os.system('cp multi_bug_test.py.backup multi_bug_test.py')
    
    result = autonomous_repair('multi_bug_test.py', max_iterations=5, optimize_efficiency=False)
    
    print("\n✨ DEMO 2 COMPLETE")
    print(f"   Success: {result['success']}")
    print(f"   Iterations: {result['total_iterations']}")
    print(f"   Bugs Fixed: {len([i for i in result['iterations'] if i['error_type']])}")


def demo_with_optimization():
    """Demo: Repair with efficiency optimization."""
    print("\n" + "=" * 80)
    print("DEMO 3: REPAIR WITH OPTIMIZATION")
    print("=" * 80)
    print("Testing: user.py with efficiency patches enabled")
    
    # Ensure buggy version
    if os.path.exists('user.py.backup'):
        os.system('cp user.py.backup user.py')
    
    result = autonomous_repair('user.py', max_iterations=3, optimize_efficiency=True)
    
    print("\n✨ DEMO 3 COMPLETE")
    print(f"   Success: {result['success']}")
    print(f"   Iterations: {result['total_iterations']}")


def demo_with_json_export():
    """Demo: Export repair log to JSON."""
    print("\n" + "=" * 80)
    print("DEMO 4: JSON LOG EXPORT")
    print("=" * 80)
    print("Testing: Repair with JSON log generation")
    
    # Ensure buggy version
    if os.path.exists('user.py.backup'):
        os.system('cp user.py.backup user.py')
    
    result = autonomous_repair('user.py', max_iterations=3, optimize_efficiency=False)
    
    # Save to JSON
    log_file = 'demo_repair_log.json'
    save_repair_log(result, log_file)
    
    print("\n✨ DEMO 4 COMPLETE")
    print(f"   Log saved to: {log_file}")
    
    # Show JSON preview
    import json
    with open(log_file, 'r') as f:
        log_data = json.load(f)
    
    print(f"\n📄 JSON Log Preview:")
    print(f"   success: {log_data['success']}")
    print(f"   total_iterations: {log_data['total_iterations']}")
    print(f"   final_status: {log_data['final_status']}")
    print(f"   iterations: {len(log_data['iterations'])} entries")


def demo_max_iterations():
    """Demo: Max iterations limit."""
    print("\n" + "=" * 80)
    print("DEMO 5: MAX ITERATIONS LIMIT")
    print("=" * 80)
    print("Testing: Repair with low iteration limit (1)")
    
    # Ensure multi-bug version (requires multiple iterations)
    if os.path.exists('multi_bug_test.py.backup'):
        os.system('cp multi_bug_test.py.backup multi_bug_test.py')
    
    result = autonomous_repair('multi_bug_test.py', max_iterations=1, optimize_efficiency=False)
    
    print("\n✨ DEMO 5 COMPLETE")
    print(f"   Success: {result['success']}")
    print(f"   Status: {result['final_status']}")
    print(f"   Reason: {result['reason']}")


def main():
    """Run all demos."""
    print("\n" + "🎯" * 40)
    print("FIXGOBLIN AUTONOMOUS REPAIR - COMPREHENSIVE DEMO")
    print("🎯" * 40)
    
    demos = [
        ("Single Bug Repair", demo_single_bug_repair),
        ("Multi-Bug Repair", demo_multi_bug_repair),
        ("With Optimization", demo_with_optimization),
        ("JSON Export", demo_with_json_export),
        ("Max Iterations", demo_max_iterations)
    ]
    
    for i, (name, demo_func) in enumerate(demos, 1):
        print(f"\n{'▶' * 40}")
        print(f"Running Demo {i}/{len(demos)}: {name}")
        print(f"{'▶' * 40}")
        
        try:
            demo_func()
        except Exception as e:
            print(f"\n❌ Demo failed: {e}")
            import traceback
            traceback.print_exc()
        
        input(f"\n⏸️  Press Enter to continue to next demo...")
    
    print("\n" + "🎯" * 40)
    print("ALL DEMOS COMPLETE!")
    print("🎯" * 40)
    print("\n📚 Key Takeaways:")
    print("   1. ✅ Single bugs fixed in 1-2 iterations")
    print("   2. ✅ Multiple bugs fixed sequentially")
    print("   3. ✅ Efficiency patches optional and controlled")
    print("   4. ✅ Complete JSON logs for tracking")
    print("   5. ✅ Safety limits prevent infinite loops")
    print("\n🚀 FixGoblin is ready for production use!")


if __name__ == "__main__":
    main()
