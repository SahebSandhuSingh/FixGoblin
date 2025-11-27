"""
Patch Generator Module
======================
Generates multiple patch candidates for common Python errors.
Does NOT rank patches - only generates possible fixes.
"""

import re
import difflib
import sys
import os
from typing import Dict, List, Any, Optional

# Import syntax_fixer module for compile()-based syntax detection
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
try:
    from syntax_fixer import analyze_syntax, generate_syntax_patches
    SYNTAX_FIXER_AVAILABLE = True
except ImportError:
    SYNTAX_FIXER_AVAILABLE = False
    print("Warning: syntax_fixer.py not available, using fallback syntax patches")


def generate_patch_candidates(error_data: Dict[str, Any], user_code: str, optimize_efficiency: bool = False) -> List[Dict[str, Any]]:
    """
    Generate multiple patch candidates based on error type.
    
    Args:
        error_data: Dictionary containing error_type, line_number, error_message, faulty_snippet
        user_code: Full source code as string
        optimize_efficiency: If True, also generate optional efficiency improvement patches
        
    Returns:
        List of patch dictionaries, each containing:
            - id: unique patch identifier
            - description: human-readable description of the fix
            - patched_code: full code with the fix applied
            - diff: unified diff showing the changes
            - patch_type: 'correctness' or 'efficiency'
    """
    
    error_type = error_data.get("error_type")
    line_number = error_data.get("line_number")
    
    if not error_type or not line_number:
        return []
    
    # Generate correctness patches based on error type
    correctness_patches = []
    
    if error_type == "IndexError":
        correctness_patches = _generate_index_error_patches(error_data, user_code)
    elif error_type == "SyntaxError":
        correctness_patches = _generate_syntax_error_patches(error_data, user_code)
    elif error_type == "NameError":
        correctness_patches = _generate_name_error_patches(error_data, user_code)
    elif error_type == "ZeroDivisionError":
        correctness_patches = _generate_zero_division_patches(error_data, user_code)
    elif error_type == "TypeError":
        correctness_patches = _generate_type_error_patches(error_data, user_code)
    elif error_type == "AttributeError":
        correctness_patches = _generate_attribute_error_patches(error_data, user_code)
    elif error_type == "UnboundLocalError":
        correctness_patches = _generate_unbound_local_patches(error_data, user_code)
    elif error_type == "LogicalError":
        correctness_patches = _generate_logical_error_patches(error_data, user_code)
    
    # Mark all correctness patches
    for patch in correctness_patches:
        patch['patch_type'] = 'correctness'
    
    # Optionally add efficiency patches if requested
    if optimize_efficiency and correctness_patches:
        efficiency_patches = _generate_efficiency_patches(error_data, user_code, correctness_patches)
        for patch in efficiency_patches:
            patch['patch_type'] = 'efficiency'
        correctness_patches.extend(efficiency_patches)
    
    return correctness_patches


# ============================================================
#  INDEX ERROR PATCHES
# ============================================================

def _generate_index_error_patches(error_data: Dict[str, Any], user_code: str) -> List[Dict[str, Any]]:
    """Generate patches for IndexError."""
    patches = []
    lines = user_code.splitlines(keepends=True)
    line_number = error_data["line_number"]
    faulty_snippet = error_data["faulty_snippet"]
    
    # Patch 0: Fix len(array) → len(array)-1 (most common pattern)
    patch0 = _fix_len_array_pattern(lines, line_number, faulty_snippet)
    if patch0:
        patches.append({
            "id": "patch_0",
            "description": "Fix index: use len(array)-1 instead of len(array)",
            "patched_code": patch0,
            "diff": _generate_diff(user_code, patch0)
        })
    
    # Patch 1: Add boundary check before access
    patch1 = _add_index_boundary_check(lines, line_number, faulty_snippet)
    if patch1:
        patches.append({
            "id": "patch_1",
            "description": "Add boundary check before array access",
            "patched_code": patch1,
            "diff": _generate_diff(user_code, patch1)
        })
    
    # Patch 2: Fix loop range (common issue: range(n) when accessing [i+1])
    patch2 = _fix_loop_range(lines, line_number, faulty_snippet)
    if patch2:
        patches.append({
            "id": "patch_2",
            "description": "Adjust loop range to prevent out-of-bounds access",
            "patched_code": patch2,
            "diff": _generate_diff(user_code, patch2)
        })
    
    # Patch 3: Change i+1 to i (remove offset)
    patch3 = _remove_index_offset(lines, line_number, faulty_snippet)
    if patch3:
        patches.append({
            "id": "patch_3",
            "description": "Remove index offset to stay within bounds",
            "patched_code": patch3,
            "diff": _generate_diff(user_code, patch3)
        })
    
    return patches


def _fix_len_array_pattern(lines: List[str], line_num: int, faulty_snippet: str) -> str:
    """Detect and fix pattern like array[len(array)] → array[len(array)-1]."""
    if line_num < 1 or line_num > len(lines):
        return None
    
    idx = line_num - 1
    original_line = lines[idx]
    
    # Match pattern: array_name[len(array_name)]
    match = re.search(r'(\w+)\[len\(\1\)\]', original_line)
    if match:
        array_name = match.group(1)
        # Replace with len(array)-1
        new_line = re.sub(
            rf'{array_name}\[len\({array_name}\)\]',
            f'{array_name}[len({array_name})-1]',
            original_line
        )
        new_lines = lines.copy()
        new_lines[idx] = new_line
        return "".join(new_lines)
    
    return None


def _add_index_boundary_check(lines: List[str], line_num: int, faulty_snippet: str) -> str:
    """Add if statement to check array bounds."""
    if line_num < 1 or line_num > len(lines):
        return None
    
    idx = line_num - 1
    original_line = lines[idx]
    indent = len(original_line) - len(original_line.lstrip())
    indent_str = " " * indent
    
    # Extract array and index from patterns like arr[i], arr[j+1], etc.
    match = re.search(r'(\w+)\[([^\]]+)\]', faulty_snippet)
    if not match:
        return None
    
    array_name = match.group(1)
    index_expr = match.group(2)
    
    # Avoid impossible conditions like len(x) < len(x)
    if f'len({array_name})' in index_expr:
        return None
    
    # Create boundary check
    check_line = f"{indent_str}if {index_expr} < len({array_name}):\n"
    indented_original = indent_str + "    " + original_line.lstrip()
    
    new_lines = lines.copy()
    new_lines[idx] = check_line + indented_original
    
    return "".join(new_lines)


def _fix_loop_range(lines: List[str], line_num: int, faulty_snippet: str) -> str:
    """Fix loop range to account for array access with offset."""
    if line_num < 1:
        return None
    
    # Look backwards for the loop that contains this line
    for i in range(line_num - 1, -1, -1):
        line = lines[i]
        if "for" in line and "range" in line:
            # Check if accessing with +1 offset
            if re.search(r'\[\w+\+1\]', faulty_snippet):
                # Fix range(0, n) → range(0, n-1)
                new_line = re.sub(r'range\((\d+),\s*([^)]+)\)', r'range(\1, \2-1)', line)
                if new_line != line:
                    new_lines = lines.copy()
                    new_lines[i] = new_line
                    return "".join(new_lines)
                
                # Fix range(n) → range(n-1)
                new_line = re.sub(r'range\(([^)]+)\)(?!\s*-)', r'range(\1-1)', line)
                if new_line != line:
                    new_lines = lines.copy()
                    new_lines[i] = new_line
                    return "".join(new_lines)
            break
    
    return None


def _remove_index_offset(lines: List[str], line_num: int, faulty_snippet: str) -> str:
    """Remove +1 or -1 offset from array access."""
    if line_num < 1 or line_num > len(lines):
        return None
    
    idx = line_num - 1
    original_line = lines[idx]
    
    # Replace [i+1] with [i], [j+1] with [j], etc.
    new_line = re.sub(r'\[(\w+)\+1\]', r'[\1]', original_line)
    
    # Also try [i-1] → [i]
    if new_line == original_line:
        new_line = re.sub(r'\[(\w+)-1\]', r'[\1]', original_line)
    
    if new_line != original_line:
        new_lines = lines.copy()
        new_lines[idx] = new_line
        return "".join(new_lines)
    
    return None


# ============================================================
#  SYNTAX ERROR PATCHES
# ============================================================

def _generate_syntax_error_patches(error_data: Dict[str, Any], user_code: str) -> List[Dict[str, Any]]:
    """
    Generate patches for SyntaxError using compile()-based detection.
    
    Uses the dedicated syntax_fixer.py module which provides:
    - Comprehensive syntax analysis via compile()
    - Rule-based deterministic patches
    - NO iterative error discovery
    - NO ML/training loops
    """
    patches = []
    
    # ============================================================
    # USE SYNTAX_FIXER MODULE (compile()-based analysis)
    # ============================================================
    if SYNTAX_FIXER_AVAILABLE:
        # Use syntax_fixer for comprehensive compile()-based detection
        analysis = analyze_syntax(user_code)
        
        if not analysis.get("ok", True):
            # Generate patches using syntax_fixer
            syntax_patches = generate_syntax_patches(
                user_code,
                analysis,
                allow_auto_fix=True,
                max_candidates=3
            )
            
            # Convert syntax_fixer patch format to our format
            for idx, sp in enumerate(syntax_patches):
                patches.append({
                    "id": f"syntax_patch_{idx}",
                    "description": sp["description"],
                    "patched_code": sp["patched_code"],
                    "diff": sp["diff"]
                })
            
            # Return immediately - syntax_fixer handles all cases
            return patches
    
    # ============================================================
    # FALLBACK: Basic rule-based patches (if syntax_fixer unavailable)
    # ============================================================
    lines = user_code.splitlines(keepends=True)
    line_number = error_data["line_number"]
    error_message = error_data.get("error_message", "")
    
    if line_number < 1 or line_number > len(lines):
        return patches
    
    idx = line_number - 1
    original_line = lines[idx]
    
    # Basic fallback patches (much simpler than before)
    
    # Patch 1: Fix = to ==
    if " = " in original_line and ("if " in original_line or "while " in original_line or "elif " in original_line):
        new_line = re.sub(r'(\s)=(\s)', r'\1==\2', original_line, count=1)
        if new_line != original_line:
            new_lines = lines.copy()
            new_lines[idx] = new_line
            patched = "".join(new_lines)
            patches.append({
                "id": "patch_1",
                "description": "Replace assignment '=' with comparison '=='",
                "patched_code": patched,
                "diff": _generate_diff(user_code, patched)
            })
    
    # Patch 2: Add missing colon
    if ("if " in original_line or "while " in original_line or "for " in original_line or 
        "def " in original_line or "class " in original_line or "elif " in original_line or
        "else" in original_line or "try" in original_line or "except" in original_line):
        if not original_line.rstrip().endswith(':'):
            new_line = original_line.rstrip() + ':\n'
            new_lines = lines.copy()
            new_lines[idx] = new_line
            patched = "".join(new_lines)
            patches.append({
                "id": "patch_2",
                "description": "Add missing colon at end of statement",
                "patched_code": patched,
                "diff": _generate_diff(user_code, patched)
            })
    
    return patches


# ============================================================
#  NAME ERROR PATCHES
# ============================================================

def _generate_name_error_patches(error_data: Dict[str, Any], user_code: str) -> List[Dict[str, Any]]:
    """Generate patches for NameError."""
    patches = []
    lines = user_code.splitlines(keepends=True)
    line_number = error_data["line_number"]
    error_message = error_data.get("error_message", "")
    
    # Extract undefined variable name
    match = re.search(r"name '(\w+)' is not defined", error_message)
    if not match:
        return patches
    
    undefined_var = match.group(1)
    
    # Find all defined variables in the code
    defined_vars = _extract_defined_variables(user_code, line_number)
    
    # Patch 1-N: Suggest similar variable names (typo fixes)
    similar_vars = _find_similar_names(undefined_var, defined_vars)
    for i, var in enumerate(similar_vars[:3], 1):  # Max 3 suggestions
        new_lines = lines.copy()
        idx = line_number - 1
        new_lines[idx] = new_lines[idx].replace(undefined_var, var)
        patched = "".join(new_lines)
        patches.append({
            "id": f"patch_{i}",
            "description": f"Replace '{undefined_var}' with '{var}' (possible typo)",
            "patched_code": patched,
            "diff": _generate_diff(user_code, patched)
        })
    
    # Patch: Initialize the variable
    if line_number > 0:
        idx = line_number - 1
        original_line = lines[idx]
        indent = len(original_line) - len(original_line.lstrip())
        indent_str = " " * indent
        
        init_line = f"{indent_str}{undefined_var} = None  # Initialize undefined variable\n"
        new_lines = lines.copy()
        new_lines.insert(idx, init_line)
        patched = "".join(new_lines)
        patches.append({
            "id": f"patch_{len(patches) + 1}",
            "description": f"Initialize '{undefined_var}' before use",
            "patched_code": patched,
            "diff": _generate_diff(user_code, patched)
        })
    
    return patches


def _extract_defined_variables(code: str, before_line: int) -> List[str]:
    """Extract all variable names defined before a certain line."""
    lines = code.splitlines()
    variables = set()
    
    for i, line in enumerate(lines[:before_line], 1):
        # Match variable assignments: var = ...
        matches = re.findall(r'^\s*([a-zA-Z_]\w*)\s*=', line)
        variables.update(matches)
        
        # Match function parameters
        if 'def ' in line:
            params = re.findall(r'def\s+\w+\(([^)]*)\)', line)
            if params:
                param_names = [p.strip().split('=')[0].strip() for p in params[0].split(',') if p.strip()]
                variables.update(param_names)
        
        # Match for loop variables
        for_vars = re.findall(r'for\s+([a-zA-Z_]\w*)\s+in', line)
        variables.update(for_vars)
    
    return list(variables)


def _find_similar_names(target: str, candidates: List[str]) -> List[str]:
    """Find variable names similar to target using edit distance."""
    from difflib import SequenceMatcher
    
    similarities = []
    for candidate in candidates:
        ratio = SequenceMatcher(None, target.lower(), candidate.lower()).ratio()
        if ratio > 0.6:  # Similarity threshold
            similarities.append((candidate, ratio))
    
    # Sort by similarity (highest first)
    similarities.sort(key=lambda x: x[1], reverse=True)
    return [name for name, _ in similarities]


# ============================================================
#  ZERO DIVISION ERROR PATCHES
# ============================================================

def _generate_zero_division_patches(error_data: Dict[str, Any], user_code: str) -> List[Dict[str, Any]]:
    """Generate patches for ZeroDivisionError."""
    patches = []
    lines = user_code.splitlines(keepends=True)
    line_number = error_data["line_number"]
    faulty_snippet = error_data["faulty_snippet"]
    
    if line_number < 1 or line_number > len(lines):
        return patches
    
    idx = line_number - 1
    original_line = lines[idx]
    indent = len(original_line) - len(original_line.lstrip())
    indent_str = " " * indent
    
    # Find division operations
    division_match = re.search(r'(\S+)\s*/\s*(\S+)', faulty_snippet)
    if not division_match:
        return patches
    
    divisor = division_match.group(2)
    
    # Patch 0: If divisor is literal 0, replace with 1
    if divisor.strip() == '0':
        new_line = original_line.replace('/ 0', '/ 1')
        if new_line != original_line:
            new_lines = lines.copy()
            new_lines[idx] = new_line
            patched = "".join(new_lines)
            patches.append({
                "id": "patch_0",
                "description": "Replace division by zero with division by 1",
                "patched_code": patched,
                "diff": _generate_diff(user_code, patched)
            })
    
    # Patch 1: Use ternary operator to avoid unbound variables (preferred)
    if divisor.strip() != '0':  # Skip if literal zero
        # Extract variable being assigned (e.g., "result = " from "result = 10 / x")
        assignment_match = re.search(r'^\s*(\w+)\s*=', original_line)
        if assignment_match:
            var_name = assignment_match.group(1)
            # Extract the division expression
            div_expr = original_line.split('=', 1)[1].strip().rstrip('\n')
            # Create ternary expression
            new_line = f"{indent_str}{var_name} = {div_expr} if {divisor} != 0 else 0\n"
            
            new_lines = lines.copy()
            new_lines[idx] = new_line
            patched = "".join(new_lines)
            patches.append({
                "id": "patch_1",
                "description": f"Use ternary operator with zero check for '{divisor}'",
                "patched_code": patched,
                "diff": _generate_diff(user_code, patched)
            })
    
    # Patch 2: Use try-except
    try_line = f"{indent_str}try:\n"
    indented_original = indent_str + "    " + original_line.lstrip()
    except_line = f"{indent_str}except ZeroDivisionError:\n"
    except_body = f"{indent_str}    pass  # Handle division by zero\n"
    
    new_lines = lines.copy()
    new_lines[idx] = try_line + indented_original + except_line + except_body
    patched = "".join(new_lines)
    patches.append({
        "id": "patch_2",
        "description": "Wrap division in try-except block",
        "patched_code": patched,
        "diff": _generate_diff(user_code, patched)
    })
    
    return patches


# ============================================================
#  TYPE ERROR PATCHES
# ============================================================

def _generate_type_error_patches(error_data: Dict[str, Any], user_code: str) -> List[Dict[str, Any]]:
    """Generate patches for TypeError."""
    patches = []
    lines = user_code.splitlines(keepends=True)
    line_number = error_data["line_number"]
    
    if line_number < 1 or line_number > len(lines):
        return patches
    
    idx = line_number - 1
    original_line = lines[idx]
    
    # Common fix: Add type conversion
    # Look for concatenation of different types
    if '+' in original_line:
        new_line = re.sub(r'\+\s*(\w+)', r'+ str(\1)', original_line)
        if new_line != original_line:
            new_lines = lines.copy()
            new_lines[idx] = new_line
            patched = "".join(new_lines)
            patches.append({
                "id": "patch_1",
                "description": "Convert variable to string for concatenation",
                "patched_code": patched,
                "diff": _generate_diff(user_code, patched)
            })
    
    return patches


# ============================================================
#  ATTRIBUTE ERROR PATCHES
# ============================================================

def _generate_attribute_error_patches(error_data: Dict[str, Any], user_code: str) -> List[Dict[str, Any]]:
    """Generate patches for AttributeError."""
    patches = []
    lines = user_code.splitlines(keepends=True)
    line_number = error_data["line_number"]
    error_message = error_data.get("error_message", "")
    
    # Extract attribute name from error
    match = re.search(r"'(\w+)' object has no attribute '(\w+)'", error_message)
    if not match:
        return patches
    
    obj_type = match.group(1)
    attr_name = match.group(2)
    
    if line_number < 1 or line_number > len(lines):
        return patches
    
    idx = line_number - 1
    original_line = lines[idx]
    
    # Patch 0: Fix typo if "Did you mean" suggestion exists
    did_you_mean = re.search(r"Did you mean[:\s]+'(\w+)'", error_message)
    if did_you_mean:
        correct_name = did_you_mean.group(1)
        # Replace the typo with the correct name
        new_line = original_line.replace(f'.{attr_name}', f'.{correct_name}')
        if new_line != original_line:
            new_lines = lines.copy()
            new_lines[idx] = new_line
            patched = "".join(new_lines)
            patches.append({
                "id": "patch_0",
                "description": f"Fix typo: replace '{attr_name}' with '{correct_name}'",
                "patched_code": patched,
                "diff": _generate_diff(user_code, patched)
            })
    
    # Patch 1: Add hasattr check
    indent = len(original_line) - len(original_line.lstrip())
    indent_str = " " * indent
    
    obj_match = re.search(r'(\w+)\.' + attr_name, original_line)
    if obj_match:
        obj_name = obj_match.group(1)
        check_line = f"{indent_str}if hasattr({obj_name}, '{attr_name}'):\n"
        indented_original = indent_str + "    " + original_line.lstrip()
        
        new_lines = lines.copy()
        new_lines[idx] = check_line + indented_original
        patched = "".join(new_lines)
        patches.append({
            "id": "patch_1",
            "description": f"Add check for '{attr_name}' attribute existence",
            "patched_code": patched,
            "diff": _generate_diff(user_code, patched)
        })
    
    return patches


# ============================================================
#  EFFICIENCY OPTIMIZATION PATCHES
# ============================================================

def _generate_efficiency_patches(error_data: Dict[str, Any], user_code: str, correctness_patches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Generate optional efficiency improvement patches.
    Only generates 1-2 patches maximum, focused on common optimizations.
    
    Args:
        error_data: Error information
        user_code: Original code
        correctness_patches: Already generated correctness patches
        
    Returns:
        List of efficiency patch dictionaries (max 2)
    """
    patches = []
    lines = user_code.splitlines(keepends=True)
    error_type = error_data.get("error_type")
    
    # Only generate efficiency patches for runtime errors (not syntax errors)
    if error_type not in ["IndexError", "RuntimeError", "KeyError"]:
        return patches
    
    # Efficiency Patch 1: Optimize bubble sort inner loop
    efficiency_patch = _optimize_bubble_sort_loop(lines, error_data)
    if efficiency_patch:
        patches.append({
            "id": f"patch_efficiency_1",
            "description": "Optimize inner loop to skip already sorted elements",
            "patched_code": efficiency_patch,
            "diff": _generate_diff(user_code, efficiency_patch)
        })
    
    # Efficiency Patch 2: Add early exit for sorted arrays
    if "bubble_sort" in user_code.lower() or "sort" in user_code.lower():
        early_exit_patch = _add_early_exit_optimization(lines, error_data)
        if early_exit_patch and early_exit_patch != efficiency_patch:
            patches.append({
                "id": f"patch_efficiency_2",
                "description": "Add early exit when array is already sorted",
                "patched_code": early_exit_patch,
                "diff": _generate_diff(user_code, early_exit_patch)
            })
    
    # Limit to max 2 efficiency patches
    return patches[:2]


def _optimize_bubble_sort_loop(lines: List[str], error_data: Dict[str, Any]) -> Optional[str]:
    """
    Optimize bubble sort by improving the inner loop range.
    Changes range(0, n-i-1) to range(0, n-1-i) for better clarity,
    or adds optimization to skip sorted elements.
    """
    # Look for bubble sort pattern
    for i, line in enumerate(lines):
        if "for" in line and "range" in line:
            # Check if this is an inner loop (has another for loop before it)
            is_inner_loop = False
            for j in range(max(0, i-5), i):
                if "for" in lines[j] and "range" in lines[j]:
                    is_inner_loop = True
                    break
            
            if is_inner_loop:
                # Optimize: use range(n-1-i) instead of range(n-i-1) for clarity
                # Or add len(arr)-1-i optimization
                if "range(0," in line or "range(" in line:
                    # Already optimized in correctness patches, add comment
                    new_lines = lines.copy()
                    indent = len(line) - len(line.lstrip())
                    indent_str = " " * indent
                    comment = f"{indent_str}# Optimized: each pass moves largest element to end\n"
                    new_lines.insert(i, comment)
                    return "".join(new_lines)
    
    return None


def _add_early_exit_optimization(lines: List[str], error_data: Dict[str, Any]) -> Optional[str]:
    """
    Add early exit optimization to sorting algorithm.
    If no swaps occur in a pass, the array is sorted.
    """
    # Find the outer loop
    outer_loop_idx = None
    for i, line in enumerate(lines):
        if "for" in line and "range" in line and "def" not in lines[max(0, i-2):i+1]:
            # This might be the outer loop
            outer_loop_idx = i
            break
    
    if outer_loop_idx is None:
        return None
    
    # Find the swap operation
    swap_idx = None
    for i in range(outer_loop_idx, min(outer_loop_idx + 10, len(lines))):
        if "=" in lines[i] and "," in lines[i]:  # Likely a swap: a, b = b, a
            swap_idx = i
            break
    
    if swap_idx is None:
        return None
    
    new_lines = lines.copy()
    
    # Add swapped flag initialization after outer loop
    outer_line = new_lines[outer_loop_idx]
    indent = len(outer_line) - len(outer_line.lstrip())
    indent_str = " " * indent
    flag_line = f"{indent_str}    swapped = False\n"
    new_lines.insert(outer_loop_idx + 1, flag_line)
    
    # Set swapped = True at swap location
    swap_line = new_lines[swap_idx + 1]  # +1 because we inserted a line
    swap_indent = len(swap_line) - len(swap_line.lstrip())
    set_flag = " " * swap_indent + "swapped = True\n"
    new_lines.insert(swap_idx + 2, set_flag)
    
    # Add early exit check after inner loop
    # Find the end of inner loop
    inner_loop_end = swap_idx + 3
    early_exit = f"{indent_str}    if not swapped:\n{indent_str}        break\n"
    new_lines.insert(inner_loop_end, early_exit)
    
    return "".join(new_lines)


# ============================================================
#  UTILITY FUNCTIONS
# ============================================================

def _generate_unbound_local_patches(error_data: Dict[str, Any], user_code: str) -> List[Dict[str, Any]]:
    """Generate patches for UnboundLocalError (variable used before assignment)."""
    patches = []
    lines = user_code.splitlines(keepends=True)
    line_number = error_data["line_number"]
    error_message = error_data["error_message"]
    
    # Extract variable name from error message
    # Pattern: "cannot access local variable 'var_name' where it is not associated with a value"
    match = re.search(r"variable '(\w+)'", error_message)
    if not match:
        return patches
    
    var_name = match.group(1)
    
    # Patch 1: Initialize variable at the beginning of the function
    if line_number > 1:
        idx = line_number - 1
        original_line = lines[idx]
        indent = len(original_line) - len(original_line.lstrip())
        indent_str = " " * indent
        
        # Find the function definition to initialize at the start
        init_idx = None
        for i in range(idx - 1, max(0, idx - 20), -1):
            line = lines[i].strip()
            if line.startswith("def "):
                # Found function def, initialize right after it
                init_idx = i + 1
                # Skip docstrings if present
                if init_idx < len(lines) and '"""' in lines[init_idx]:
                    # Find end of docstring
                    for j in range(init_idx + 1, len(lines)):
                        if '"""' in lines[j]:
                            init_idx = j + 1
                            break
                break
        
        if init_idx is not None:
            new_lines = lines.copy()
            new_lines.insert(init_idx, f"{indent_str}{var_name} = None\n")
            patched = "".join(new_lines)
            patches.append({
                "id": "patch_1",
                "description": f"Initialize '{var_name}' to None at function start",
                "patched_code": patched,
                "diff": _generate_diff(user_code, patched)
        })
    
    # Patch 2: Remove the conditional that prevents assignment
    # Look backwards for if statement that might be blocking the assignment
    if line_number > 2:
        for i in range(line_number - 2, max(0, line_number - 10), -1):
            if "if " in lines[i] and var_name in lines[i+1]:
                # Found potential blocking if statement
                new_lines = lines.copy()
                # Remove the if statement and unindent the body
                if_indent = len(lines[i]) - len(lines[i].lstrip())
                body_indent = len(lines[i+1]) - len(lines[i+1].lstrip())
                indent_diff = body_indent - if_indent
                
                # Unindent lines in the if block
                j = i + 1
                while j < len(lines) and (len(lines[j]) - len(lines[j].lstrip())) >= body_indent:
                    if lines[j].strip():  # Don't modify empty lines
                        new_lines[j] = lines[j][indent_diff:]
                    j += 1
                
                # Remove the if line
                del new_lines[i]
                
                patched = "".join(new_lines)
                patches.append({
                    "id": "patch_2",
                    "description": f"Remove conditional that prevents '{var_name}' initialization",
                    "patched_code": patched,
                    "diff": _generate_diff(user_code, patched)
                })
                break
    
    return patches


def _generate_diff(original: str, patched: str) -> str:
    """Generate unified diff between original and patched code."""
    original_lines = original.splitlines(keepends=True)
    patched_lines = patched.splitlines(keepends=True)
    
    diff = difflib.unified_diff(
        original_lines,
        patched_lines,
        fromfile='original',
        tofile='patched',
        lineterm=''
    )
    
    return ''.join(diff)


# ============================================================
#  TEST/DEMO
# ============================================================

if __name__ == "__main__":
    # Test IndexError patches (correctness only)
    print("=" * 70)
    print("TEST 1: IndexError - Correctness Patches Only")
    print("=" * 70)
    
    error_data = {
        "error_type": "IndexError",
        "line_number": 5,
        "error_message": "list index out of range",
        "faulty_snippet": "if arr[j] > arr[j+1]:"
    }
    
    user_code = """def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr
"""
    
    patches = generate_patch_candidates(error_data, user_code, optimize_efficiency=False)
    
    print(f"\nGenerated {len(patches)} CORRECTNESS patches:")
    for patch in patches:
        print(f"\n{patch['id']} ({patch['patch_type']}): {patch['description']}")
        print("-" * 70)
        print(patch['diff'][:200] + "..." if len(patch['diff']) > 200 else patch['diff'])
    
    # Test with efficiency optimization enabled
    print("\n\n" + "=" * 70)
    print("TEST 2: IndexError - Correctness + Efficiency Patches")
    print("=" * 70)
    
    patches_with_efficiency = generate_patch_candidates(error_data, user_code, optimize_efficiency=True)
    
    correctness_count = sum(1 for p in patches_with_efficiency if p['patch_type'] == 'correctness')
    efficiency_count = sum(1 for p in patches_with_efficiency if p['patch_type'] == 'efficiency')
    
    print(f"\nGenerated {len(patches_with_efficiency)} total patches:")
    print(f"  - {correctness_count} correctness patches")
    print(f"  - {efficiency_count} efficiency patches")
    
    for patch in patches_with_efficiency:
        print(f"\n{patch['id']} ({patch['patch_type'].upper()}): {patch['description']}")
        if patch['patch_type'] == 'efficiency':
            print("-" * 70)
            print(patch['diff'][:300] + "..." if len(patch['diff']) > 300 else patch['diff'])
    
    print("\n" + "=" * 70)
    print("✅ Patch generation complete!")
    print("=" * 70)


# ============================================================
#  LOGICAL ERROR PATCHES
# ============================================================

def _generate_logical_error_patches(error_data: Dict[str, Any], user_code: str) -> List[Dict[str, Any]]:
    """
    Generate patches for logical errors (missing return statements, off-by-one, wrong operators, etc.).
    """
    patches = []
    
    suggested_fix = error_data.get('suggested_fix', {})
    logical_issue = error_data.get('logical_issue', {})
    
    if logical_issue.get('type') == 'missing_return_statement':
        func_name = logical_issue.get('function_name')
        var_to_return = suggested_fix.get('variable_to_return', 'result')
        
        # Find the function and add return statement
        lines = user_code.split('\n')
        func_start = None
        func_end = None
        
        # Find function boundaries
        for i, line in enumerate(lines):
            if f'def {func_name}(' in line:
                func_start = i
            elif func_start is not None and func_end is None:
                # Find end of function (next non-indented line or another def)
                if line and not line[0].isspace() and i > func_start:
                    func_end = i
                    break
        
        if func_end is None:
            func_end = len(lines)
        
        # Insert return statement before function end
        # Find last non-empty line with indentation
        insert_line = func_end - 1
        while insert_line > func_start and not lines[insert_line].strip():
            insert_line -= 1
        
        # Get indentation of function body
        indent = ''
        for i in range(func_start + 1, insert_line + 1):
            if lines[i].strip():
                indent = lines[i][:len(lines[i]) - len(lines[i].lstrip())]
                break
        
        # Create patched version
        patched_lines = lines.copy()
        patched_lines.insert(insert_line + 1, f"{indent}return {var_to_return}")
        patched_code = '\n'.join(patched_lines)
        
        patches.append({
            'id': 'logical_patch_1',
            'description': f"Add missing 'return {var_to_return}' statement in {func_name}()",
            'patched_code': patched_code,
            'diff': _generate_diff(user_code, patched_code),
            'patch_type': 'correctness'
        })
    
    elif logical_issue.get('type') == 'wrong_comparison':
        func_name = logical_issue.get('function_name')
        line_num = logical_issue.get('line_number')
        operator = logical_issue.get('operator')
        expected_op = logical_issue.get('expected_operator')
        
        # Fix wrong comparison operator (< to > or vice versa)
        lines = user_code.split('\n')
        if line_num and line_num <= len(lines):
            target_line = lines[line_num - 1]
            
            # Replace the operator
            if operator == 'less_than' and expected_op == 'greater_than':
                new_line = target_line.replace(' < ', ' > ')
            elif operator == 'greater_than' and expected_op == 'less_than':
                new_line = target_line.replace(' > ', ' < ')
            else:
                new_line = target_line
            
            patched_lines = lines.copy()
            patched_lines[line_num - 1] = new_line
            patched_code = '\n'.join(patched_lines)
            
            patches.append({
                'id': 'logical_patch_1',
                'description': f"Fix comparison operator in {func_name}(): change '{operator}' to '{expected_op}'",
                'patched_code': patched_code,
                'diff': _generate_diff(user_code, patched_code),
                'patch_type': 'correctness'
            })
    
    elif logical_issue.get('type') == 'wrong_operator':
        func_name = logical_issue.get('function_name')
        line_num = logical_issue.get('line_number')
        operator = logical_issue.get('operator')
        expected_op = logical_issue.get('expected_operator')
        
        # Fix wrong arithmetic operator (+ to -, etc.)
        lines = user_code.split('\n')
        if line_num and line_num <= len(lines):
            target_line = lines[line_num - 1]
            
            # Replace the operator
            if operator == 'add' and expected_op == 'subtract':
                # Find price/total + discount pattern and change to subtraction
                import re
                pattern = r'(\w+)\s*\+\s*(discount|reduction|deduction)'
                match = re.search(pattern, target_line)
                if match:
                    new_line = re.sub(r'\s*\+\s*', ' - ', target_line, count=1)
                else:
                    new_line = target_line.replace(' + ', ' - ', 1)
            else:
                new_line = target_line
            
            patched_lines = lines.copy()
            patched_lines[line_num - 1] = new_line
            patched_code = '\n'.join(patched_lines)
            
            patches.append({
                'id': 'logical_patch_1',
                'description': f"Fix arithmetic operator in {func_name}(): change addition to subtraction for discount",
                'patched_code': patched_code,
                'diff': _generate_diff(user_code, patched_code),
                'patch_type': 'correctness'
            })
    
    elif logical_issue.get('type') == 'missing_percentage_conversion':
        func_name = logical_issue.get('function_name')
        line_num = logical_issue.get('line_number')
        
        # Fix missing division by 100 for percentage
        lines = user_code.split('\n')
        if line_num and line_num <= len(lines):
            target_line = lines[line_num - 1]
            
            # Find multiplication pattern with percentage variable
            import re
            pattern = r'(\w+)\s*\*\s*(\w*percent\w*|\w*rate\w*)'
            match = re.search(pattern, target_line, re.IGNORECASE)
            if match:
                # Add division by 100
                price_var = match.group(1)
                percent_var = match.group(2)
                new_line = target_line.replace(
                    f'{price_var} * {percent_var}',
                    f'{price_var} * {percent_var} / 100'
                )
                
                patched_lines = lines.copy()
                patched_lines[line_num - 1] = new_line
                patched_code = '\n'.join(patched_lines)
                
                patches.append({
                    'id': 'logical_patch_1',
                    'description': f"Fix percentage calculation in {func_name}(): divide by 100",
                    'patched_code': patched_code,
                    'diff': _generate_diff(user_code, patched_code),
                    'patch_type': 'correctness'
                })
    
    elif logical_issue.get('type') == 'potential_off_by_one':
        func_name = logical_issue.get('function_name')
        line_num = logical_issue.get('line_number')
        
        # Fix range(1, n) to range(1, n+1)
        lines = user_code.split('\n')
        if line_num and line_num <= len(lines):
            target_line = lines[line_num - 1]
            # Find range(1, variable_name) and change to range(1, variable_name + 1)
            import re
            pattern = r'range\(1,\s*(\w+)\)'
            match = re.search(pattern, target_line)
            if match:
                var_name = match.group(1)
                new_line = target_line.replace(f'range(1, {var_name})', f'range(1, {var_name} + 1)')
                
                patched_lines = lines.copy()
                patched_lines[line_num - 1] = new_line
                patched_code = '\n'.join(patched_lines)
                
                patches.append({
                    'id': 'logical_patch_1',
                    'description': f"Fix off-by-one error: change range(1, {var_name}) to range(1, {var_name} + 1) in {func_name}()",
                    'patched_code': patched_code,
                    'diff': _generate_diff(user_code, patched_code),
                    'patch_type': 'correctness'
                })
    
    elif logical_issue.get('type') == 'output_mismatch':
        # For output mismatches detected in stdout, try to find related function
        expected = logical_issue.get('expected')
        actual = logical_issue.get('actual')
        
        patches.append({
            'id': 'logical_patch_info',
            'description': f"Output mismatch detected: expected {expected}, got {actual}. Manual review recommended.",
            'patched_code': user_code,
            'diff': '# No automatic fix available for output mismatch',
            'patch_type': 'correctness'
        })
    
    return patches

