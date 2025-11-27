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
    DOES NOT modify any files - only evaluates in-memory.
    
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
    
    # Run patched code (IN-MEMORY ONLY - no file modification)
    patched_result = _run_code_in_sandbox(patch['patched_code'], run_in_sandbox)
    
    # Initialize score breakdown
    score_info = {
        "returncode": patched_result['returncode'],
        "success": patched_result['returncode'] == 0,
        "no_errors_bonus": 0,
        "priority_bonus": 0,
        "error_reduction_bonus": 0,
        "new_errors_penalty": 0,
        "diff_size_penalty": 0,
        "output_bonus": 0,
        "total_score": 0
    }
    
    # SCORING CRITERIA (Improved scoring system for consistency)
    
    # 1. No errors after patch (HIGHEST PRIORITY: +100 points)
    if patched_result['returncode'] == 0:
        score_info["no_errors_bonus"] = 100
        print(f"      ✓ No errors (returncode 0): +100")
    
    # 2. Patch ID priority bonus (prefer patch_0 which is usually the best/simplest fix)
    if patch['id'] == 'patch_0':
        score_info["priority_bonus"] = 30
        print(f"      ✓ Priority patch (patch_0): +30")
    
    # 3. Error reduction (compare error counts: +20 per error reduced)
    baseline_errors = _count_error_lines(baseline_result['stderr'])
    patched_errors = _count_error_lines(patched_result['stderr'])
    
    if patched_errors < baseline_errors:
        reduction = baseline_errors - patched_errors
        score_info["error_reduction_bonus"] = reduction * 20
        print(f"      ✓ Reduced {reduction} errors: +{reduction * 20}")
    elif patched_errors > baseline_errors:
        increase = patched_errors - baseline_errors
        score_info["new_errors_penalty"] = -increase * 50
        print(f"      ✗ Introduced {increase} new errors: -{increase * 50}")
    
    # 4. Check for new error types (SEVERE penalty - these cascade into more bugs)
    baseline_error_type = _extract_error_type(baseline_result['stderr'])
    patched_error_type = _extract_error_type(patched_result['stderr'])
    
    if (patched_error_type and baseline_error_type and 
        patched_error_type != baseline_error_type):
        # UnboundLocalError and SyntaxError are especially bad (chain reaction bugs)
        if patched_error_type in ['UnboundLocalError', 'SyntaxError']:
            score_info["new_errors_penalty"] -= 100
            print(f"      ✗ Changed to {patched_error_type} (cascading bug): -100")
        else:
            score_info["new_errors_penalty"] -= 50
            print(f"      ✗ Changed error type ({baseline_error_type} → {patched_error_type}): -50")
    
    # 5. Diff size penalty (prefer minimal changes: -10 per extra line after 3)
    lines_changed = _count_diff_lines(patch['diff'])
    if lines_changed > 3:
        penalty = (lines_changed - 3) * 10
        score_info["diff_size_penalty"] = -penalty
        print(f"      ✗ Large diff ({lines_changed} lines): -{penalty}")
    elif lines_changed <= 2:
        bonus = 10
        score_info["diff_size_penalty"] = bonus
        print(f"      ✓ Minimal change ({lines_changed} lines): +{bonus}")
    
    # 6. Bonus for stdout output (code ran far enough to produce output)
    if patched_result['stdout'] and not baseline_result['stdout']:
        score_info["output_bonus"] = 15
        print(f"      ✓ Generated output: +15")
    
    # Calculate total score
    score_info["total_score"] = sum([
        score_info["no_errors_bonus"],
        score_info.get("priority_bonus", 0),
        score_info["error_reduction_bonus"],
        score_info["new_errors_penalty"],
        score_info["diff_size_penalty"],
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
#  FILE APPLICATION UTILITY
# ============================================================

def apply_patch_to_file(best_patch: Dict[str, Any], file_path: str, auto_apply: bool = True) -> Dict[str, Any]:
    """
    Apply the selected patch to the actual file (or return in-memory result).
    
    Safety Rules:
    - NEVER modifies files during optimization loop
    - Only writes to file AFTER best patch is chosen
    - Creates backup before any modification
    
    Args:
        best_patch: Best patch dictionary selected by optimizer
        file_path: Path to file to patch
        auto_apply: If False, only return patched code without modifying file.
                   If True, write to file and create backup.
        
    Returns:
        Dictionary containing:
            - best_patch: The patch object
            - patched_code: The patched code (always returned)
            - applied: True if file was modified, False otherwise
            - backup_path: Path to backup file (if auto_apply=True)
            - original_path: Path to original file
    """
    
    result = {
        "best_patch": best_patch,
        "patched_code": best_patch['patched_code'],
        "applied": False,
        "backup_path": None,
        "original_path": file_path
    }
    
    # If auto_apply is False, return patched code without touching files
    if not auto_apply:
        print("\n📋 Patch generated (auto_apply=False)")
        print("   File NOT modified. Use auto_apply=True to apply changes.")
        return result
    
    # auto_apply is True - proceed with file modification
    try:
        file_path_obj = pathlib.Path(file_path)
        
        # Verify file exists
        if not file_path_obj.exists():
            print(f"\n❌ Error: File '{file_path}' not found.")
            return result
        
        # Create backup file
        backup_path = file_path_obj.with_suffix(file_path_obj.suffix + '.backup')
        
        # Read original content
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Write backup
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
        
        result['backup_path'] = str(backup_path)
        print(f"\n📦 Backup created: {backup_path}")
        
        # Write patched code to original file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(best_patch['patched_code'])
        
        result['applied'] = True
        print(f"✅ Patch applied to: {file_path}")
        
        return result
        
    except Exception as e:
        print(f"\n❌ Failed to apply patch: {e}")
        return result


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
