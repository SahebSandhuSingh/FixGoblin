"""
Complete 4-Step Autonomous Debugging System
============================================
Integrates: Sandbox → Error Parser → Patch Generator → Patch Optimizer
"""

from sandbox_runner import run_in_sandbox
from error_parser import parse_error
from patch_generator import generate_patch_candidates
from patch_optimizer import select_best_patch, apply_patch_to_file
import sys


def autonomous_debug(file_path: str, auto_apply: bool = False, optimize_efficiency: bool = False) -> bool:
    """
    Complete autonomous debugging pipeline.
    
    Args:
        file_path: Path to buggy code file
        auto_apply: If True, automatically apply the best patch
        optimize_efficiency: If True, also generate efficiency improvement patches
        
    Returns:
        True if bug was fixed, False otherwise
    """
    
    print("=" * 70)
    print("🤖 AUTONOMOUS DEBUGGING SYSTEM - FixGoblin")
    print("=" * 70)
    print(f"\n📁 Target File: {file_path}")
    if optimize_efficiency:
        print("⚡ Efficiency optimization: ENABLED")
    print()
    
    # Read original code
    try:
        with open(file_path, 'r') as f:
            original_code = f.read()
    except FileNotFoundError:
        print(f"❌ Error: File '{file_path}' not found.")
        return False
    
    # ================================================================
    # STEP 1: SANDBOX EXECUTION
    # ================================================================
    print("\n" + "▶" * 35)
    print("STEP 1: SANDBOX EXECUTION")
    print("▶" * 35)
    
    sandbox_result = run_in_sandbox(file_path)
    
    print(f"\nLanguage: {sandbox_result['language']}")
    print(f"Return Code: {sandbox_result['returncode']}")
    
    if sandbox_result['returncode'] == 0:
        print("\n✅ Code executed successfully! No bugs detected.")
        if sandbox_result['stdout']:
            print(f"\nOutput:\n{sandbox_result['stdout']}")
        return True
    
    print("\n❌ Execution failed with errors.")
    print(f"\nStderr Preview:")
    stderr_preview = sandbox_result['stderr'][:300]
    print(stderr_preview + ("..." if len(sandbox_result['stderr']) > 300 else ""))
    
    # ================================================================
    # STEP 2: ERROR PARSING
    # ================================================================
    print("\n" + "▶" * 35)
    print("STEP 2: ERROR ANALYSIS")
    print("▶" * 35)
    
    error_analysis = parse_error(sandbox_result, original_code)
    
    if not error_analysis['error_type']:
        print("\n❌ Could not parse error information.")
        return False
    
    print(f"\n🐛 Bug Identified:")
    print(f"   Type: {error_analysis['error_type']}")
    print(f"   Line: {error_analysis['line_number']}")
    print(f"   Message: {error_analysis['error_message']}")
    print(f"   Faulty Code: {error_analysis['faulty_snippet']}")
    
    # ================================================================
    # STEP 3: PATCH GENERATION
    # ================================================================
    print("\n" + "▶" * 35)
    print("STEP 3: PATCH GENERATION")
    print("▶" * 35)
    
    patches = generate_patch_candidates(error_analysis, original_code, optimize_efficiency=optimize_efficiency)
    
    if not patches:
        print("\n❌ No patch candidates could be generated.")
        return False
    
    correctness_count = sum(1 for p in patches if p.get('patch_type') == 'correctness')
    efficiency_count = sum(1 for p in patches if p.get('patch_type') == 'efficiency')
    
    print(f"\n✨ Generated {len(patches)} patch candidate(s):")
    if efficiency_count > 0:
        print(f"   - {correctness_count} correctness patches")
        print(f"   - {efficiency_count} efficiency patches")
    for i, patch in enumerate(patches, 1):
        patch_type_label = f" [{patch.get('patch_type', 'correctness').upper()}]" if optimize_efficiency else ""
        print(f"   {i}. [{patch['id']}]{patch_type_label} {patch['description']}")
    
    # ================================================================
    # STEP 4: PATCH OPTIMIZATION
    # ================================================================
    print("\n" + "▶" * 35)
    print("STEP 4: PATCH OPTIMIZATION")
    print("▶" * 35)
    
    best_patch = select_best_patch(patches, original_code, run_in_sandbox)
    
    if not best_patch:
        print("\n❌ No suitable patch found.")
        return False
    
    # ================================================================
    # RESULTS & APPLICATION
    # ================================================================
    print("\n" + "=" * 70)
    print("📋 FINAL RESULTS")
    print("=" * 70)
    
    print(f"\n🏆 Best Patch: {best_patch['id']}")
    print(f"Description: {best_patch['description']}")
    print(f"Score: {best_patch['score']} points")
    
    print(f"\n📝 Diff:")
    print("-" * 70)
    print(best_patch['diff'])
    print("-" * 70)
    
    # Check if patch actually works
    if best_patch['score_breakdown']['success']:
        print("\n✅ This patch fixes the bug!")
        
        if auto_apply:
            print("\n🔧 Applying patch to file...")
            if apply_patch_to_file(best_patch, file_path, backup=True):
                print(f"\n✅ File patched successfully!")
                print(f"💡 Original backed up with .bak extension")
                
                # Verify the fix
                print("\n🔍 Verifying fix...")
                verify_result = run_in_sandbox(file_path)
                if verify_result['returncode'] == 0:
                    print("✅ Verification passed! Bug is fixed.")
                    if verify_result['stdout']:
                        print(f"\nOutput:\n{verify_result['stdout']}")
                    return True
                else:
                    print("⚠️ Verification failed. Bug may not be fully fixed.")
                    return False
            else:
                print("❌ Failed to apply patch.")
                return False
        else:
            print("\n💡 Run with --apply flag to automatically apply the patch.")
            return False
    else:
        print("\n⚠️ Best patch still has issues (but reduces errors).")
        print("Manual intervention may be required.")
        return False


def main():
    """Command-line interface."""
    if len(sys.argv) < 2:
        print("FixGoblin - Autonomous Debugging System")
        print("=" * 70)
        print("\nUsage:")
        print("  python3 fixgoblin.py <file_path>                    # Analyze only")
        print("  python3 fixgoblin.py <file_path> --apply            # Analyze and fix")
        print("  python3 fixgoblin.py <file_path> --optimize         # Include efficiency patches")
        print("  python3 fixgoblin.py <file_path> --apply --optimize # Fix with optimization")
        print("\nFlags:")
        print("  --apply, -a      Automatically apply the best patch")
        print("  --optimize, -o   Generate efficiency improvement patches")
        print("\nExamples:")
        print("  python3 fixgoblin.py user.py")
        print("  python3 fixgoblin.py user.py --apply")
        print("  python3 fixgoblin.py user.py --apply --optimize")
        sys.exit(1)
    
    file_path = sys.argv[1]
    auto_apply = "--apply" in sys.argv or "-a" in sys.argv
    optimize_efficiency = "--optimize" in sys.argv or "-o" in sys.argv
    
    success = autonomous_debug(file_path, auto_apply=auto_apply, optimize_efficiency=optimize_efficiency)
    
    print("\n" + "=" * 70)
    if success:
        print("🎉 DEBUGGING COMPLETE - Bug Fixed!")
    else:
        print("⚠️ DEBUGGING INCOMPLETE - Manual Review Needed")
    print("=" * 70 + "\n")
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
