#!/usr/bin/env python3
"""
syntax_fixer.py - Rule-based Python Syntax Error Detection and Patching

This module provides deterministic, explainable syntax error detection and repair
using Python's built-in compile() function and rule-based pattern matching.

IMPORTANT POLICY:
- NO AUTOMATIC ML TRAINING on error cases
- NO REMOTE SERVICE CALLS or LLM integration
- LOG ONLY for manual review and future rule expansion
- All patches are deterministic, safe, and human-reviewable

Author: FixGoblin Team
License: MIT
"""

import re
import json
import difflib
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime


# ============================================================================
# MAIN API FUNCTIONS
# ============================================================================

def analyze_syntax(code: str) -> Dict:
    """
    Analyze Python code for syntax errors using built-in compile().
    
    NO TRAINING / NO ML / NO REMOTE CALLS - Pure static analysis only.
    
    Args:
        code: Python source code as string
        
    Returns:
        Dictionary with keys:
            - ok (bool): True if no syntax errors
            - error_type (str|None): Classified error category
            - lineno (int|None): Line number of error
            - col_offset (int|None): Column offset of error
            - message (str|None): Original error message
            - faulty_line (str|None): The exact line containing the error
            
    Example:
        >>> result = analyze_syntax("if x = 5:\\n    print(x)")
        >>> result['ok']
        False
        >>> result['error_type']
        'assignment_in_condition'
    """
    try:
        compile(code, '<string>', 'exec')
        return {
            "ok": True,
            "error_type": None,
            "lineno": None,
            "col_offset": None,
            "message": None,
            "faulty_line": None
        }
    except (SyntaxError, IndentationError) as e:
        # Extract error details
        lineno = e.lineno or 0
        col_offset = e.offset or 0
        message = str(e.msg) if e.msg else str(e)
        
        # Get the faulty line from the code
        lines = code.splitlines()
        faulty_line = None
        if lineno > 0 and lineno <= len(lines):
            faulty_line = lines[lineno - 1]
        elif e.text:
            faulty_line = e.text.rstrip()
        
        # Classify the error
        error_type = classify_syntax_error(message, faulty_line, lineno, code)
        
        return {
            "ok": False,
            "error_type": error_type,
            "lineno": lineno,
            "col_offset": col_offset,
            "message": message,
            "faulty_line": faulty_line
        }


def generate_syntax_patches(
    code: str,
    analysis: Dict,
    allow_auto_fix: bool = True,
    max_candidates: int = 3,
    dsl_config: Optional[Dict] = None
) -> List[Dict]:
    """
    Generate rule-based syntax fix patch candidates.
    
    NO TRAINING / NO ML / NO REMOTE CALLS - Only deterministic rule application.
    
    Args:
        code: Original Python source code
        analysis: Result from analyze_syntax()
        allow_auto_fix: If False, only suggest edits without modifying code
        max_candidates: Maximum number of patch candidates to generate
        dsl_config: Optional DSL configuration (e.g., {"deny": {"guess_fix"}})
        
    Returns:
        List of patch dictionaries with keys:
            - id (str): Unique patch identifier
            - description (str): Human-readable patch description
            - patched_code (str): Code after applying patch
            - diff (str): Unified diff showing changes
            - applied_safely (bool): Whether patch is considered safe
            
    Example:
        >>> analysis = analyze_syntax("if x = 5:\\n    print(x)")
        >>> patches = generate_syntax_patches(code, analysis)
        >>> len(patches) > 0
        True
    """
    if analysis.get("ok", True):
        return []  # No patches needed for valid code
    
    # Parse DSL config
    denied_fixes = set()
    if dsl_config and "deny" in dsl_config:
        denied_fixes = set(dsl_config["deny"])
    
    error_type = analysis.get("error_type", "other_syntax")
    lineno = analysis.get("lineno", 0)
    faulty_line = analysis.get("faulty_line")
    
    patches = []
    
    # Generate patches based on error type (deterministic rules only)
    if error_type == "missing_colon" and "missing_colon_fix" not in denied_fixes:
        patches.extend(_fix_missing_colon(code, lineno, faulty_line))
    
    elif error_type == "unmatched_paren" and "paren_fix" not in denied_fixes:
        patches.extend(_fix_unmatched_paren(code, lineno, faulty_line, analysis))
    
    elif error_type == "assignment_in_condition" and "condition_fix" not in denied_fixes:
        patches.extend(_fix_assignment_in_condition(code, lineno, faulty_line))
    
    elif error_type == "unterminated_string" and "string_fix" not in denied_fixes:
        patches.extend(_fix_unterminated_string(code, lineno, faulty_line))
    
    elif error_type == "indentation" and "indent_fix" not in denied_fixes:
        patches.extend(_fix_indentation(code, lineno, faulty_line))
    
    elif error_type == "unexpected_eof" and "eof_fix" not in denied_fixes:
        patches.extend(_fix_unexpected_eof(code, lineno, faulty_line))
    
    # Always add conservative fallback: comment out + marker
    if "fallback_comment" not in denied_fixes:
        patches.append(_create_fallback_patch(code, lineno, faulty_line))
    
    # Limit to max_candidates
    patches = patches[:max_candidates]
    
    # Generate patch metadata
    for idx, patch_data in enumerate(patches, 1):
        patch_id = f"patch_{idx}"
        patched_code = patch_data["patched_code"]
        
        # If allow_auto_fix is False, mark as suggestion only
        if not allow_auto_fix:
            patch_data["applied_safely"] = False
            patch_data["description"] = "[SUGGESTION ONLY] " + patch_data["description"]
        
        # Generate unified diff
        diff = make_unified_diff(code, patched_code)
        
        # Build final patch dictionary
        patches[idx - 1] = {
            "id": patch_id,
            "description": patch_data["description"],
            "patched_code": patched_code,
            "diff": diff,
            "applied_safely": patch_data.get("applied_safely", True)
        }
    
    return patches


def apply_patch_in_memory(original: str, patched: str) -> str:
    """
    Helper to return patched code result.
    
    This is a simple pass-through function used internally by patch generators.
    No training or ML involved.
    
    Args:
        original: Original source code (unused, kept for API compatibility)
        patched: Patched source code
        
    Returns:
        The patched code string
    """
    return patched


def make_unified_diff(
    original: str,
    patched: str,
    filename: str = "file.py"
) -> str:
    """
    Generate unified diff between original and patched code.
    
    Pure deterministic diff generation - no training or ML.
    
    Args:
        original: Original source code
        patched: Patched source code
        filename: Filename to display in diff headers
        
    Returns:
        Unified diff string
    """
    original_lines = original.splitlines(keepends=True)
    patched_lines = patched.splitlines(keepends=True)
    
    diff = difflib.unified_diff(
        original_lines,
        patched_lines,
        fromfile=f"a/{filename}",
        tofile=f"b/{filename}",
        lineterm=""
    )
    
    return "".join(diff)


def log_syntax_case(
    analysis: Dict,
    candidates: List[Dict],
    log_path: str = "syntax_error_log.json"
) -> None:
    """
    Log syntax error case and generated patches for manual review.
    
    IMPORTANT: This function ONLY LOGS data. NO TRAINING / NO ML / NO AUTO-LEARNING.
    Logs are for manual human review and future rule expansion.
    
    Args:
        analysis: Result from analyze_syntax()
        candidates: List of patch candidates from generate_syntax_patches()
        log_path: Path to JSON log file (append-only)
        
    Side Effects:
        Appends entry to log file on disk
    """
    log_file = Path(log_path)
    
    # Create log entry
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "analysis": analysis,
        "num_candidates": len(candidates),
        "candidates": [
            {
                "id": c["id"],
                "description": c["description"],
                "applied_safely": c["applied_safely"]
            }
            for c in candidates
        ],
        "note": "LOG ONLY - No automatic training or ML performed"
    }
    
    # Append to log file
    try:
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        else:
            logs = []
        
        logs.append(log_entry)
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
    
    except Exception as e:
        # Fail gracefully - logging should not break main flow
        print(f"Warning: Could not write to log file {log_path}: {e}")


# ============================================================================
# ERROR CLASSIFICATION (Rule-based pattern matching)
# ============================================================================

def classify_syntax_error(
    message: str,
    faulty_line: Optional[str],
    lineno: int,
    full_code: str
) -> str:
    """
    Classify syntax error into a rule-based category.
    
    Pure pattern matching - NO ML / NO TRAINING.
    
    Args:
        message: Error message from SyntaxError
        faulty_line: The line containing the error
        lineno: Line number of error
        full_code: Full source code
        
    Returns:
        Error category string (one of the predefined categories)
    """
    msg_lower = message.lower()
    
    # Missing colon (if, for, while, def, class, etc.)
    if "expected ':'" in msg_lower or "invalid syntax" in msg_lower:
        if faulty_line:
            stripped = faulty_line.strip()
            # Check for control flow keywords without colons
            if re.match(r'^(if|elif|else|for|while|def|class|try|except|finally|with)\b', stripped):
                if not stripped.endswith(':'):
                    return "missing_colon"
    
    # Assignment in condition (= instead of ==)
    if "invalid syntax" in msg_lower and faulty_line:
        # Look for "if x = " pattern
        if re.search(r'\bif\s+\w+\s*=\s*[^=]', faulty_line):
            return "assignment_in_condition"
        if re.search(r'\belif\s+\w+\s*=\s*[^=]', faulty_line):
            return "assignment_in_condition"
        if re.search(r'\bwhile\s+\w+\s*=\s*[^=]', faulty_line):
            return "assignment_in_condition"
    
    # Unmatched parentheses/brackets
    if any(x in msg_lower for x in ["unmatched", "')'", "'('", "closing parenthesis"]):
        return "unmatched_paren"
    if "unexpected eof" in msg_lower and _has_unclosed_brackets(full_code):
        return "unmatched_paren"
    
    # Unterminated string
    if any(x in msg_lower for x in ["unterminated string", "eol while scanning string"]):
        return "unterminated_string"
    
    # Indentation errors
    if "indent" in msg_lower or "expected an indented block" in msg_lower:
        return "indentation"
    
    # Unexpected EOF
    if "unexpected eof" in msg_lower:
        return "unexpected_eof"
    
    # Default fallback
    return "other_syntax"


def _has_unclosed_brackets(code: str) -> bool:
    """Check if code has unclosed parentheses/brackets/braces."""
    stack = []
    pairs = {'(': ')', '[': ']', '{': '}'}
    
    # Simple check ignoring strings (not perfect but good enough for classification)
    for char in code:
        if char in pairs:
            stack.append(char)
        elif char in pairs.values():
            if not stack:
                return True
            if pairs.get(stack[-1]) == char:
                stack.pop()
            else:
                return True
    
    return len(stack) > 0


# ============================================================================
# PATCH GENERATORS (Deterministic rule-based fixes)
# ============================================================================

def _fix_missing_colon(code: str, lineno: int, faulty_line: Optional[str]) -> List[Dict]:
    """Generate patch for missing colon in control flow statements."""
    if not faulty_line:
        return []
    
    lines = code.splitlines()
    if lineno < 1 or lineno > len(lines):
        return []
    
    # Add colon at end of line
    fixed_line = faulty_line.rstrip() + ":"
    lines[lineno - 1] = fixed_line
    patched_code = "\n".join(lines)
    
    return [{
        "description": f"Add missing colon at end of line {lineno}",
        "patched_code": patched_code,
        "applied_safely": True
    }]


def _fix_assignment_in_condition(code: str, lineno: int, faulty_line: Optional[str]) -> List[Dict]:
    """Generate patch for assignment (=) instead of comparison (==) in condition."""
    if not faulty_line:
        return []
    
    lines = code.splitlines()
    if lineno < 1 or lineno > len(lines):
        return []
    
    # Replace single = with == in condition context
    # Be conservative: only replace if it looks like "if x = value"
    fixed_line = re.sub(
        r'(\b(?:if|elif|while)\s+\w+\s*)=(\s*[^=])',
        r'\1==\2',
        faulty_line
    )
    
    if fixed_line != faulty_line:
        lines[lineno - 1] = fixed_line
        patched_code = "\n".join(lines)
        
        return [{
            "description": f"Replace assignment (=) with comparison (==) in condition at line {lineno}",
            "patched_code": patched_code,
            "applied_safely": True
        }]
    
    return []


def _fix_unmatched_paren(code: str, lineno: int, faulty_line: Optional[str], analysis: Dict) -> List[Dict]:
    """Generate patch for unmatched parentheses/brackets."""
    lines = code.splitlines()
    patches = []
    
    # Strategy 1: Try to close on the faulty line
    if faulty_line:
        # Count unclosed brackets on this line
        balance = {'(': 0, '[': 0, '{': 0}
        pairs = {'(': ')', '[': ']', '{': '}'}
        
        for char in faulty_line:
            if char in balance:
                balance[char] += 1
            elif char == ')':
                balance['('] -= 1
            elif char == ']':
                balance['['] -= 1
            elif char == '}':
                balance['{'] -= 1
        
        # Add closing brackets if needed
        closing = ""
        if balance['('] > 0:
            closing += ')' * balance['(']
        if balance['['] > 0:
            closing += ']' * balance['[']
        if balance['{'] > 0:
            closing += '}' * balance['{']
        
        if closing and lineno > 0 and lineno <= len(lines):
            lines_copy = lines.copy()
            lines_copy[lineno - 1] = faulty_line.rstrip() + closing
            patched_code = "\n".join(lines_copy)
            
            patches.append({
                "description": f"Close unmatched brackets at line {lineno}",
                "patched_code": patched_code,
                "applied_safely": True
            })
    
    # Strategy 2: Add closing brackets at end of file
    if not patches:
        # Calculate overall bracket balance
        balance = {'(': 0, '[': 0, '{': 0}
        for line in lines:
            for char in line:
                if char in balance:
                    balance[char] += 1
                elif char == ')':
                    balance['('] -= 1
                elif char == ']':
                    balance['['] -= 1
                elif char == '}':
                    balance['{'] -= 1
        
        closing = ""
        if balance['('] > 0:
            closing += ')' * balance['(']
        if balance['['] > 0:
            closing += ']' * balance['[']
        if balance['{'] > 0:
            closing += '}' * balance['{']
        
        if closing:
            lines_copy = lines.copy()
            lines_copy.append(closing)
            patched_code = "\n".join(lines_copy)
            
            patches.append({
                "description": f"Close unmatched brackets at end of file",
                "patched_code": patched_code,
                "applied_safely": True
            })
    
    return patches


def _fix_unterminated_string(code: str, lineno: int, faulty_line: Optional[str]) -> List[Dict]:
    """Generate patch for unterminated string literals."""
    if not faulty_line:
        return []
    
    lines = code.splitlines()
    if lineno < 1 or lineno > len(lines):
        return []
    
    # Try to detect which quote type is missing
    quote_type = None
    if faulty_line.count('"') % 2 == 1:
        quote_type = '"'
    elif faulty_line.count("'") % 2 == 1:
        quote_type = "'"
    elif '"""' in faulty_line or "'''" in faulty_line:
        # Multi-line string - add closing triple quotes on new line
        if '"""' in faulty_line:
            quote_type = '"""'
        else:
            quote_type = "'''"
        
        lines_copy = lines.copy()
        lines_copy.insert(lineno, quote_type)
        patched_code = "\n".join(lines_copy)
        
        return [{
            "description": f"Close unterminated multi-line string at line {lineno}",
            "patched_code": patched_code,
            "applied_safely": True
        }]
    
    if quote_type:
        fixed_line = faulty_line.rstrip() + quote_type
        lines[lineno - 1] = fixed_line
        patched_code = "\n".join(lines)
        
        return [{
            "description": f"Close unterminated string with {quote_type} at line {lineno}",
            "patched_code": patched_code,
            "applied_safely": True
        }]
    
    return []


def _fix_indentation(code: str, lineno: int, faulty_line: Optional[str]) -> List[Dict]:
    """Generate patch for indentation errors."""
    lines = code.splitlines()
    if lineno < 1 or lineno > len(lines):
        return []
    
    patches = []
    
    # Strategy 1: Align with previous non-empty line
    if lineno > 1:
        # Find previous non-empty line
        prev_lineno = lineno - 1
        while prev_lineno > 0 and not lines[prev_lineno - 1].strip():
            prev_lineno -= 1
        
        if prev_lineno > 0:
            prev_line = lines[prev_lineno - 1]
            prev_indent = len(prev_line) - len(prev_line.lstrip())
            
            # Check if previous line is a control flow header
            if prev_line.strip().endswith(':'):
                # Indent one level deeper (4 spaces)
                target_indent = prev_indent + 4
            else:
                # Same indentation as previous
                target_indent = prev_indent
            
            if faulty_line:
                content = faulty_line.lstrip()
                fixed_line = ' ' * target_indent + content
                lines_copy = lines.copy()
                lines_copy[lineno - 1] = fixed_line
                patched_code = "\n".join(lines_copy)
                
                patches.append({
                    "description": f"Fix indentation at line {lineno} to match context",
                    "patched_code": patched_code,
                    "applied_safely": True
                })
    
    # Strategy 2: Remove all indentation (dedent completely)
    if faulty_line and faulty_line != faulty_line.lstrip():
        lines_copy = lines.copy()
        lines_copy[lineno - 1] = faulty_line.lstrip()
        patched_code = "\n".join(lines_copy)
        
        patches.append({
            "description": f"Remove indentation at line {lineno}",
            "patched_code": patched_code,
            "applied_safely": False  # Less safe - might break logic
        })
    
    return patches


def _fix_unexpected_eof(code: str, lineno: int, faulty_line: Optional[str]) -> List[Dict]:
    """Generate patch for unexpected EOF errors."""
    lines = code.splitlines()
    
    # Check if there are unclosed control structures
    # Look for lines ending with ':' that might need bodies
    needs_body = False
    last_header_idx = -1
    
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if stripped.endswith(':') and re.match(r'^(if|elif|else|for|while|def|class|try|except|finally|with)\b', stripped):
            # Check if next line is indented (has a body)
            if idx + 1 < len(lines):
                next_line = lines[idx + 1]
                if next_line.strip() and not next_line.startswith(' ') and not next_line.startswith('\t'):
                    needs_body = True
                    last_header_idx = idx
            else:
                needs_body = True
                last_header_idx = idx
    
    if needs_body and last_header_idx >= 0:
        lines_copy = lines.copy()
        header_line = lines[last_header_idx]
        indent = len(header_line) - len(header_line.lstrip())
        # Add a pass statement
        lines_copy.insert(last_header_idx + 1, ' ' * (indent + 4) + 'pass')
        patched_code = "\n".join(lines_copy)
        
        return [{
            "description": f"Add 'pass' statement to complete control structure at line {last_header_idx + 1}",
            "patched_code": patched_code,
            "applied_safely": True
        }]
    
    return []


def _create_fallback_patch(code: str, lineno: int, faulty_line: Optional[str]) -> Dict:
    """
    Create conservative fallback patch: comment out faulty line + add marker.
    
    This is always safe and human-reviewable.
    """
    lines = code.splitlines()
    
    if lineno < 1 or lineno > len(lines):
        # Can't locate line - return code unchanged with warning comment
        patched_code = "# FIXGOBLIN: syntax error detected but line not found\n" + code
        return {
            "description": "Add warning comment (line not found)",
            "patched_code": patched_code,
            "applied_safely": True
        }
    
    # Comment out the faulty line
    original_line = lines[lineno - 1]
    indent = len(original_line) - len(original_line.lstrip())
    
    lines[lineno - 1] = ' ' * indent + f"# FIXGOBLIN: syntax unclear — please review"
    lines.insert(lineno, ' ' * indent + f"# Original: {original_line.strip()}")
    
    patched_code = "\n".join(lines)
    
    return {
        "description": f"Comment out faulty line {lineno} with manual review marker (safe fallback)",
        "patched_code": patched_code,
        "applied_safely": True
    }


# ============================================================================
# EXAMPLE USAGE & TESTS
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("syntax_fixer.py - Rule-based Syntax Error Detection & Patching")
    print("NO TRAINING / NO ML / NO REMOTE CALLS - Deterministic rules only")
    print("=" * 70)
    print()
    
    # Test cases
    test_cases = [
        # Missing colon
        ("if x > 5\n    print('hello')", "missing_colon"),
        
        # Assignment in condition
        ("if x = 5:\n    print(x)", "assignment_in_condition"),
        
        # Unmatched parenthesis
        ("result = (1 + 2\nprint(result)", "unmatched_paren"),
        
        # Unterminated string
        ('message = "Hello world\nprint(message)', "unterminated_string"),
        
        # Indentation error
        ("def foo():\nprint('no indent')", "indentation"),
        
        # Unexpected EOF
        ("if True:", "unexpected_eof"),
    ]
    
    for idx, (buggy_code, expected_type) in enumerate(test_cases, 1):
        print(f"Test Case {idx}: {expected_type}")
        print("-" * 70)
        print("Buggy Code:")
        print(buggy_code)
        print()
        
        # Analyze
        analysis = analyze_syntax(buggy_code)
        print(f"Analysis: {analysis}")
        print()
        
        # Generate patches
        patches = generate_syntax_patches(buggy_code, analysis, max_candidates=2)
        print(f"Generated {len(patches)} patch(es):")
        for patch in patches:
            print(f"  - {patch['id']}: {patch['description']}")
            print(f"    Safe: {patch['applied_safely']}")
        print()
        
        # Show first patch
        if patches:
            print("First Patch Code:")
            print(patches[0]['patched_code'])
            print()
            print("Diff:")
            print(patches[0]['diff'])
        
        # Log the case (NO TRAINING - just logging)
        log_syntax_case(analysis, patches, log_path="syntax_error_examples.json")
        
        print("=" * 70)
        print()
    
    print("✓ All test cases completed.")
    print("✓ Cases logged to syntax_error_examples.json (NO TRAINING performed)")
    print("✓ Review logs manually to expand rules in future versions")
