"""
Patch Optimizer Module
======================
Evaluates and ranks patch candidates to select the best fix.
Tests each patch in sandbox without modifying original files.
"""

import tempfile
import pathlib
from typing import List, Dict, Any, Callable, Optional


def select_best_patch(
    patch_candidates: List[Dict[str, Any]], 
    original_code: str,
    run_in_sandbox: Callable
) -> Optional[Dict[str, Any]]:
    """
    Evaluate all patch candidates and select the best one.
    
    Args:
        patch_candidates: List of patch dictionaries from patch generator
        original_code: Original source code as string
        run_in_sandbox: Function that takes file_path and returns sandbox result
        
    Returns:
        Best patch dictionary with added 'all_scored_patches' key, or None if no patches work
    """
    
    if not patch_candidates:
        return None
    
    print("\n" + "=" * 70)
    print("PATCH OPTIMIZER: Evaluating Candidates")
    print("=" * 70)
    
    # Get baseline error info from original code
    baseline_result = _run_code_in_sandbox(original_code, run_in_sandbox)
    baseline_score = _calculate_baseline_score(baseline_result)
    
    print(f"\n📊 Baseline (Original Code):")
    print(f"   Return Code: {baseline_result['returncode']}")
    print(f"   Errors in stderr: {_count_error_lines(baseline_result['stderr'])}")
    
    # Evaluate each patch
    scored_patches = []
    
    for i, patch in enumerate(patch_candidates, 1):
        print(f"\n🔬 Testing Patch {i}/{len(patch_candidates)}: {patch['id']}")
        print(f"   Description: {patch['description']}")
        
        score_info = _evaluate_patch(
            patch, 
            original_code,
            baseline_result,
            run_in_sandbox
        )
        
        scored_patches.append({
            **patch,
            "score": score_info["total_score"],
            "score_breakdown": score_info
        })
        
        print(f"   Score: {score_info['total_score']} points")
        print(f"   Return Code: {score_info['returncode']}")
        if score_info['success']:
            print(f"   ✅ PATCH WORKS!")
        else:
            print(f"   ❌ Still has errors")
    
    # Sort by score (highest first)
    scored_patches.sort(key=lambda x: x["score"], reverse=True)
    
    # Select best patch
    best_patch = scored_patches[0].copy()
    best_patch['all_scored_patches'] = scored_patches  # Add all patches for comparison
    
    print("\n" + "=" * 70)
    print("🏆 BEST PATCH SELECTED")
    print("=" * 70)
    print(f"ID: {best_patch['id']}")
    print(f"Description: {best_patch['description']}")
    print(f"Final Score: {best_patch['score']} points")
    print(f"\nScore Breakdown:")
    for key, value in best_patch['score_breakdown'].items():
        if key != 'total_score':
            print(f"   {key}: {value}")
    print("=" * 70)
    
    return best_patch


def _run_code_in_sandbox(code: str, run_in_sandbox: Callable) -> Dict[str, Any]:
    """
    Write code to temporary file and run it in sandbox.
    
    Args:
        code: Source code to execute
        run_in_sandbox: Sandbox execution function
        
    Returns:
        Sandbox result dictionary
    """
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_path = f.name
    
    try:
        # Run in sandbox
        result = run_in_sandbox(temp_path)
        return result
    finally:
        # Clean up temp file
        try:
            pathlib.Path(temp_path).unlink()
        except:
            pass


def _evaluate_patch(
    patch: Dict[str, Any],
    original_code: str,
    baseline_result: Dict[str, Any],
    run_in_sandbox: Callable
) -> Dict[str, Any]:
    """
    Evaluate a single patch candidate.
    
    Args:
        patch: Patch dictionary
        original_code: Original source code
        baseline_result: Sandbox result from original code
        run_in_sandbox: Sandbox execution function
        
    Returns:
        Dictionary with score breakdown
    """
    
    # Run patched code
    patched_result = _run_code_in_sandbox(patch['patched_code'], run_in_sandbox)
    
    # Initialize score breakdown
    score_info = {
        "returncode": patched_result['returncode'],
        "success": patched_result['returncode'] == 0,
        "error_reduction": 0,
        "no_errors": 0,
        "new_errors_penalty": 0,
        "code_change_penalty": 0,
        "total_score": 0
    }
    
    # SCORING CRITERIA
    
    # 1. No errors after patch (highest priority)
    if patched_result['returncode'] == 0:
        score_info["no_errors"] = 50
        print(f"      ✓ No errors: +50")
    
    # 2. Error reduction (compare error counts)
    baseline_errors = _count_error_lines(baseline_result['stderr'])
    patched_errors = _count_error_lines(patched_result['stderr'])
    
    if patched_errors < baseline_errors:
        reduction = baseline_errors - patched_errors
        score_info["error_reduction"] = reduction * 10
        print(f"      ✓ Reduced {reduction} errors: +{reduction * 10}")
    elif patched_errors > baseline_errors:
        increase = patched_errors - baseline_errors
        score_info["new_errors_penalty"] = -increase * 10
        print(f"      ✗ Introduced {increase} new errors: -{increase * 10}")
    
    # 3. Check for new error types
    baseline_error_type = _extract_error_type(baseline_result['stderr'])
    patched_error_type = _extract_error_type(patched_result['stderr'])
    
    if (patched_error_type and baseline_error_type and 
        patched_error_type != baseline_error_type):
        score_info["new_errors_penalty"] -= 15
        print(f"      ✗ Changed error type ({baseline_error_type} → {patched_error_type}): -15")
    
    # 4. Minimal code changes (prefer smaller diffs)
    lines_changed = _count_diff_lines(patch['diff'])
    if lines_changed > 5:
        penalty = (lines_changed - 5) * 2
        score_info["code_change_penalty"] = -penalty
        print(f"      ✗ Large change ({lines_changed} lines): -{penalty}")
    elif lines_changed <= 2:
        score_info["code_change_penalty"] = 5
        print(f"      ✓ Minimal change ({lines_changed} lines): +5")
    
    # 5. Bonus for stdout output (code ran far enough to produce output)
    if patched_result['stdout'] and not baseline_result['stdout']:
        score_info["output_bonus"] = 10
        print(f"      ✓ Generated output: +10")
    
    # Calculate total score
    score_info["total_score"] = sum([
        score_info["no_errors"],
        score_info["error_reduction"],
        score_info["new_errors_penalty"],
        score_info["code_change_penalty"],
        score_info.get("output_bonus", 0)
    ])
    
    return score_info


def _calculate_baseline_score(baseline_result: Dict[str, Any]) -> int:
    """Calculate baseline score for original code."""
    if baseline_result['returncode'] == 0:
        return 100  # Original code works
    else:
        return 0  # Original code has errors


def _count_error_lines(stderr: str) -> int:
    """Count number of error-related lines in stderr."""
    if not stderr:
        return 0
    
    error_keywords = ['Error', 'Exception', 'Traceback', 'Warning']
    count = 0
    
    for line in stderr.split('\n'):
        if any(keyword in line for keyword in error_keywords):
            count += 1
    
    return count


def _extract_error_type(stderr: str) -> Optional[str]:
    """Extract the error type from stderr."""
    if not stderr:
        return None
    
    import re
    
    # Look for error types like "IndexError:", "SyntaxError:", etc.
    lines = stderr.split('\n')
    for line in reversed(lines):
        match = re.search(r'(\w+(?:Error|Exception|Warning)):', line)
        if match:
            return match.group(1)
    
    return None


def _count_diff_lines(diff: str) -> int:
    """Count number of changed lines in unified diff."""
    if not diff:
        return 0
    
    changed_lines = 0
    for line in diff.split('\n'):
        if line.startswith('+') and not line.startswith('+++'):
            changed_lines += 1
        elif line.startswith('-') and not line.startswith('---'):
            changed_lines += 1
    
    return changed_lines


# ============================================================
#  ADDITIONAL UTILITY: Apply Best Patch to File
# ============================================================

def apply_patch_to_file(patch: Dict[str, Any], file_path: str, backup: bool = True) -> bool:
    """
    Apply the selected patch to the actual file.
    
    Args:
        patch: Patch dictionary with 'patched_code'
        file_path: Path to file to patch
        backup: Whether to create a backup file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        file_path_obj = pathlib.Path(file_path)
        
        # Create backup if requested
        if backup:
            backup_path = file_path_obj.with_suffix(file_path_obj.suffix + '.bak')
            with open(file_path, 'r') as f:
                backup_content = f.read()
            with open(backup_path, 'w') as f:
                f.write(backup_content)
            print(f"📦 Backup created: {backup_path}")
        
        # Write patched code
        with open(file_path, 'w') as f:
            f.write(patch['patched_code'])
        
        print(f"✅ Patch applied to: {file_path}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to apply patch: {e}")
        return False


# ============================================================
#  TEST/DEMO
# ============================================================

if __name__ == "__main__":
    # Mock test
    print("Patch Optimizer Module")
    print("=" * 70)
    print("This module is designed to be imported and used with:")
    print("  - sandbox_runner.run_in_sandbox()")
    print("  - patch_generator.generate_patch_candidates()")
    print("\nSee test_optimizer.py for complete integration test.")
