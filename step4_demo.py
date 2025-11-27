"""
Step 4: Patch Optimizer - Comprehensive Demonstration
======================================================
Shows the patch optimizer selecting the best fix from multiple candidates.
"""

from sandbox_runner import run_in_sandbox
from error_parser import parse_error
from patch_generator import generate_patch_candidates
from patch_optimizer import select_best_patch
import sys


def demonstrate_step4(file_path: str, optimize_efficiency: bool = False):
    """
    Demonstrate Step 4: Patch Optimizer in action.
    
    Shows how the optimizer:
    1. Tests each patch candidate in sandbox
    2. Scores based on multiple criteria
    3. Selects the best working patch
    """
    
    print("=" * 70)
    print("STEP 4: PATCH OPTIMIZER - COMPREHENSIVE DEMONSTRATION")
    print("=" * 70)
    print(f"\n📁 Testing File: {file_path}")
    if optimize_efficiency:
        print("⚡ Mode: Correctness + Efficiency Patches")
    else:
        print("🎯 Mode: Correctness Patches Only")
    print()
    
    # Read original code
    with open(file_path, 'r') as f:
        original_code = f.read()
    
    print("=" * 70)
    print("PREREQUISITE: Steps 1-3 (Quick Summary)")
    print("=" * 70)
    
    # Step 1: Run in sandbox
    print("\n[Step 1] Running code in sandbox...")
    sandbox_result = run_in_sandbox(file_path)
    print(f"Result: Return Code {sandbox_result['returncode']}")
    
    if sandbox_result['returncode'] == 0:
        print("✅ No bugs detected!")
        return
    
    # Step 2: Parse error
    print("\n[Step 2] Parsing error...")
    error_analysis = parse_error(sandbox_result, original_code)
    print(f"Error: {error_analysis['error_type']} on line {error_analysis['line_number']}")
    print(f"Message: {error_analysis['error_message']}")
    
    # Step 3: Generate patches
    print("\n[Step 3] Generating patch candidates...")
    patches = generate_patch_candidates(error_analysis, original_code, optimize_efficiency=optimize_efficiency)
    
    correctness_patches = [p for p in patches if p.get('patch_type') == 'correctness']
    efficiency_patches = [p for p in patches if p.get('patch_type') == 'efficiency']
    
    print(f"Generated {len(patches)} patches:")
    print(f"  - {len(correctness_patches)} correctness patches")
    if efficiency_patches:
        print(f"  - {len(efficiency_patches)} efficiency patches")
    
    print("\n" + "=" * 70)
    print("STEP 4: PATCH OPTIMIZER - DETAILED EVALUATION")
    print("=" * 70)
    
    # Show what the optimizer will do
    print("\n🔍 The optimizer will now:")
    print("  1. Test each patch in an isolated sandbox")
    print("  2. Score based on:")
    print("     • Does it fix the bug? (+50 points)")
    print("     • Does it reduce errors? (+10 per error)")
    print("     • Does it introduce new errors? (-10 per error)")
    print("     • Is the change minimal? (+5 for ≤2 lines)")
    print("  3. Select the highest-scoring patch")
    print("\n" + "-" * 70)
    
    # Run the optimizer
    best_patch = select_best_patch(patches, original_code, run_in_sandbox)
    
    # Detailed results
    print("\n" + "=" * 70)
    print("STEP 4 RESULTS: BEST PATCH ANALYSIS")
    print("=" * 70)
    
    if not best_patch:
        print("\n❌ No suitable patch found.")
        return
    
    print(f"\n🏆 Winner: {best_patch['id']}")
    print(f"Type: {best_patch.get('patch_type', 'correctness').upper()}")
    print(f"Description: {best_patch['description']}")
    print(f"Final Score: {best_patch['score']} points")
    
    print(f"\n📊 Detailed Score Breakdown:")
    breakdown = best_patch['score_breakdown']
    print(f"   ✓ No Errors Bonus:        {breakdown.get('no_errors', 0):>3} points")
    print(f"   ✓ Error Reduction:        {breakdown.get('error_reduction', 0):>3} points")
    print(f"   ✓ Code Change Score:      {breakdown.get('code_change_penalty', 0):>3} points")
    print(f"   ✗ New Errors Penalty:     {breakdown.get('new_errors_penalty', 0):>3} points")
    print(f"   {'─' * 40}")
    print(f"   TOTAL:                    {best_patch['score']:>3} points")
    
    if breakdown.get('success'):
        print(f"\n✅ Status: This patch FIXES THE BUG!")
    else:
        print(f"\n⚠️ Status: Partial fix (reduces errors but doesn't eliminate them)")
    
    print(f"\n📝 Code Changes (Unified Diff):")
    print("-" * 70)
    print(best_patch['diff'])
    print("-" * 70)
    
    # Show comparison with other patches
    print(f"\n📈 Comparison with Other Patches:")
    print("-" * 70)
    
    # Get all scored patches from best_patch
    all_scored = best_patch.get('all_scored_patches', [])
    
    if all_scored:
        for i, patch in enumerate(all_scored, 1):
            indicator = "🏆" if patch['id'] == best_patch['id'] else "  "
            patch_type = patch.get('patch_type', 'correctness')[0].upper()
            status = "✅ WORKS" if patch['score_breakdown'].get('success') else "❌ FAILS"
            patch_id = patch['id']
            score = patch['score']
            print(f"{indicator} #{i} [{patch_type}] {patch_id:<25} Score: {score:>4}  {status}")
        print("-" * 70)
        
        # Summary statistics
        working_patches = [p for p in all_scored if p['score_breakdown'].get('success')]
        print(f"\n📊 Summary:")
        print(f"   Total patches tested: {len(all_scored)}")
        print(f"   Working patches: {len(working_patches)}")
        print(f"   Failed patches: {len(all_scored) - len(working_patches)}")
        print(f"   Best score: {all_scored[0]['score']} points")
        if len(working_patches) > 1:
            print(f"   Note: Multiple patches work, selected best/first")
    else:
        print("   (Patch comparison data not available)")
    
    print("\n" + "=" * 70)
    print("STEP 4 COMPLETE: Patch Optimizer Successfully Selected Best Fix")
    print("=" * 70)
    
    return best_patch


def main():
    """Command-line interface for Step 4 demonstration."""
    
    if len(sys.argv) < 2:
        print("Step 4: Patch Optimizer Demonstration")
        print("=" * 70)
        print("\nUsage:")
        print("  python3 step4_demo.py <file_path>")
        print("  python3 step4_demo.py <file_path> --optimize")
        print("\nExample:")
        print("  python3 step4_demo.py user.py")
        print("  python3 step4_demo.py user.py --optimize")
        sys.exit(1)
    
    file_path = sys.argv[1]
    optimize_efficiency = "--optimize" in sys.argv or "-o" in sys.argv
    
    try:
        result = demonstrate_step4(file_path, optimize_efficiency)
        
        if result and result['score_breakdown'].get('success'):
            print("\n✅ Demonstration Complete: Best patch successfully identified!")
            sys.exit(0)
        else:
            print("\n⚠️ Demonstration Complete: Partial success (best effort patch selected)")
            sys.exit(0)
            
    except FileNotFoundError:
        print(f"\n❌ Error: File '{file_path}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
