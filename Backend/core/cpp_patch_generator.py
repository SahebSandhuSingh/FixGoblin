"""
C++ Patch Generator
===================
Generates fix patches for common C++ syntax and runtime errors.
"""

import re
from typing import Dict, List, Any
import difflib


def generate_cpp_patches(error_data: Dict[str, Any], code: str) -> List[Dict[str, Any]]:
    """
    Generate patch candidates for C++ errors.
    
    Args:
        error_data: Dictionary with error_type, line_number, error_message
        code: Full C++ source code
        
    Returns:
        List of patch dictionaries
    """
    error_type = error_data.get("error_type")
    error_message = error_data.get("error", "")
    
    patches = []
    
    # Missing semicolon
    if "expected ';'" in error_message or "expected ';' at end" in error_message:
        patches.extend(_fix_missing_semicolon(error_data, code))
    
    # Missing parentheses
    elif "expected ')'" in error_message or "expected '('" in error_message:
        patches.extend(_fix_missing_parenthesis(error_data, code))
    
    # Missing braces
    elif "expected '{'" in error_message or "expected '}'" in error_message:
        patches.extend(_fix_missing_brace(error_data, code))
    
    # Undeclared identifier
    elif "undeclared identifier" in error_message or "was not declared" in error_message:
        patches.extend(_fix_undeclared_identifier(error_data, code))
    
    # Type mismatch
    elif "cannot convert" in error_message or "invalid conversion" in error_message:
        patches.extend(_fix_type_mismatch(error_data, code))
    
    # Missing return statement
    elif "non-void function" in error_message and "return" in error_message:
        patches.extend(_fix_missing_return(error_data, code))
    
    # Assignment in condition
    elif "using the result of an assignment" in error_message:
        patches.extend(_fix_assignment_in_condition(error_data, code))
    
    return patches


def _fix_missing_semicolon(error_data: Dict, code: str) -> List[Dict]:
    """Fix missing semicolon errors"""
    patches = []
    line_num = error_data.get("line_number")
    if not line_num:
        return patches
    
    lines = code.split('\n')
    if line_num < 1 or line_num > len(lines):
        return patches
    
    idx = line_num - 1
    line = lines[idx]
    
    # Add semicolon at end of line
    if not line.rstrip().endswith((';', '{', '}')):
        new_line = line.rstrip() + ';'
        if line.endswith('\n'):
            new_line += '\n'
        
        new_lines = lines.copy()
        new_lines[idx] = new_line
        patched_code = '\n'.join(new_lines)
        
        patches.append({
            "id": "cpp_patch_1",
            "description": f"Add missing semicolon at line {line_num}",
            "patched_code": patched_code,
            "diff": _generate_diff(code, patched_code)
        })
    
    return patches


def _fix_missing_parenthesis(error_data: Dict, code: str) -> List[Dict]:
    """Fix missing parenthesis errors"""
    patches = []
    line_num = error_data.get("line_number")
    error_msg = error_data.get("error", "")
    
    if not line_num:
        return patches
    
    lines = code.split('\n')
    if line_num < 1 or line_num > len(lines):
        return patches
    
    idx = line_num - 1
    line = lines[idx]
    
    # Count parentheses
    open_count = line.count('(')
    close_count = line.count(')')
    
    if "expected ')'" in error_msg and open_count > close_count:
        # Add closing parenthesis
        new_line = line.rstrip() + ')'
        if line.endswith('\n'):
            new_line += '\n'
        
        new_lines = lines.copy()
        new_lines[idx] = new_line
        patched_code = '\n'.join(new_lines)
        
        patches.append({
            "id": "cpp_patch_1",
            "description": f"Add missing closing parenthesis at line {line_num}",
            "patched_code": patched_code,
            "diff": _generate_diff(code, patched_code)
        })
    
    return patches


def _fix_missing_brace(error_data: Dict, code: str) -> List[Dict]:
    """Fix missing brace errors"""
    patches = []
    line_num = error_data.get("line_number")
    error_msg = error_data.get("error", "")
    
    if not line_num:
        return patches
    
    lines = code.split('\n')
    if line_num < 1 or line_num > len(lines):
        return patches
    
    idx = line_num - 1
    
    # Add opening brace after control structures
    if "expected '{'" in error_msg:
        # Look for if, for, while, etc.
        if idx > 0:
            prev_line = lines[idx - 1].strip()
            if any(kw in prev_line for kw in ['if', 'for', 'while', 'else']):
                new_lines = lines.copy()
                indent = len(lines[idx - 1]) - len(lines[idx - 1].lstrip())
                new_lines.insert(idx, ' ' * indent + '{')
                new_lines.insert(idx + 2, ' ' * indent + '}')
                patched_code = '\n'.join(new_lines)
                
                patches.append({
                    "id": "cpp_patch_1",
                    "description": f"Add missing braces around line {line_num}",
                    "patched_code": patched_code,
                    "diff": _generate_diff(code, patched_code)
                })
    
    # Add closing brace
    elif "expected '}'" in error_msg or "extraneous closing brace" in error_msg:
        # Find matching opening brace
        brace_count = 0
        for i in range(idx, -1, -1):
            brace_count += lines[i].count('{')
            brace_count -= lines[i].count('}')
        
        if brace_count > 0:
            new_lines = lines.copy()
            indent = len(lines[idx]) - len(lines[idx].lstrip())
            new_lines.insert(idx + 1, ' ' * indent + '}')
            patched_code = '\n'.join(new_lines)
            
            patches.append({
                "id": "cpp_patch_2",
                "description": f"Add missing closing brace after line {line_num}",
                "patched_code": patched_code,
                "diff": _generate_diff(code, patched_code)
            })
    
    return patches


def _fix_undeclared_identifier(error_data: Dict, code: str) -> List[Dict]:
    """Fix undeclared identifier by suggesting similar variables or adding declaration"""
    patches = []
    line_num = error_data.get("line_number")
    error_msg = error_data.get("error", "")
    
    # Extract variable name
    match = re.search(r"'(\w+)'", error_msg)
    if not match or not line_num:
        return patches
    
    var_name = match.group(1)
    lines = code.split('\n')
    
    # Find similar variable names
    declared_vars = set()
    for line in lines[:line_num]:
        # Match variable declarations
        matches = re.findall(r'\b(int|float|double|char|bool|string|auto)\s+(\w+)', line)
        for _, var in matches:
            declared_vars.add(var)
    
    # Find similar names (typo fix)
    from difflib import get_close_matches
    similar = get_close_matches(var_name, declared_vars, n=1, cutoff=0.7)
    
    if similar:
        # Fix typo
        idx = line_num - 1
        new_line = lines[idx].replace(var_name, similar[0])
        new_lines = lines.copy()
        new_lines[idx] = new_line
        patched_code = '\n'.join(new_lines)
        
        patches.append({
            "id": "cpp_patch_1",
            "description": f"Fix typo: replace '{var_name}' with '{similar[0]}' at line {line_num}",
            "patched_code": patched_code,
            "diff": _generate_diff(code, patched_code)
        })
    else:
        # Add declaration
        idx = line_num - 1
        indent = len(lines[idx]) - len(lines[idx].lstrip())
        declaration = ' ' * indent + f'int {var_name}; // TODO: Change type if needed\n'
        new_lines = lines.copy()
        new_lines.insert(idx, declaration)
        patched_code = '\n'.join(new_lines)
        
        patches.append({
            "id": "cpp_patch_2",
            "description": f"Declare variable '{var_name}' before line {line_num}",
            "patched_code": patched_code,
            "diff": _generate_diff(code, patched_code)
        })
    
    return patches


def _fix_type_mismatch(error_data: Dict, code: str) -> List[Dict]:
    """Fix type conversion errors"""
    patches = []
    line_num = error_data.get("line_number")
    error_msg = error_data.get("error", "")
    
    if not line_num:
        return patches
    
    lines = code.split('\n')
    if line_num < 1 or line_num > len(lines):
        return patches
    
    idx = line_num - 1
    line = lines[idx]
    
    # Common fixes: add cast, change type
    if "int" in error_msg and "string" in error_msg:
        # Convert int to string with std::to_string
        new_line = re.sub(r'(\w+)', r'std::to_string(\1)', line, count=1)
        new_lines = lines.copy()
        new_lines[idx] = new_line
        patched_code = '\n'.join(new_lines)
        
        patches.append({
            "id": "cpp_patch_1",
            "description": f"Add std::to_string() conversion at line {line_num}",
            "patched_code": patched_code,
            "diff": _generate_diff(code, patched_code)
        })
    
    return patches


def _fix_missing_return(error_data: Dict, code: str) -> List[Dict]:
    """Fix missing return statement"""
    patches = []
    line_num = error_data.get("line_number")
    
    if not line_num:
        return patches
    
    lines = code.split('\n')
    
    # Find the function and add return statement before closing brace
    for i in range(line_num - 1, max(0, line_num - 20), -1):
        if '{' in lines[i]:
            # Find matching closing brace
            brace_count = 1
            for j in range(i + 1, len(lines)):
                brace_count += lines[j].count('{')
                brace_count -= lines[j].count('}')
                if brace_count == 0:
                    # Insert return before this line
                    indent = len(lines[j]) - len(lines[j].lstrip())
                    new_lines = lines.copy()
                    new_lines.insert(j, ' ' * (indent + 4) + 'return 0; // TODO: Return appropriate value')
                    patched_code = '\n'.join(new_lines)
                    
                    patches.append({
                        "id": "cpp_patch_1",
                        "description": f"Add missing return statement in function",
                        "patched_code": patched_code,
                        "diff": _generate_diff(code, patched_code)
                    })
                    return patches
    
    return patches


def _fix_assignment_in_condition(error_data: Dict, code: str) -> List[Dict]:
    """Fix assignment (=) in condition, should be comparison (==)"""
    patches = []
    line_num = error_data.get("line_number")
    
    if not line_num:
        return patches
    
    lines = code.split('\n')
    if line_num < 1 or line_num > len(lines):
        return patches
    
    idx = line_num - 1
    line = lines[idx]
    
    # Replace = with == in if/while conditions
    if 'if' in line or 'while' in line:
        # Match single = but not == or !=
        new_line = re.sub(r'(\s)=(\s)', r'\1==\2', line)
        if new_line != line:
            new_lines = lines.copy()
            new_lines[idx] = new_line
            patched_code = '\n'.join(new_lines)
            
            patches.append({
                "id": "cpp_patch_1",
                "description": f"Replace assignment '=' with comparison '==' at line {line_num}",
                "patched_code": patched_code,
                "diff": _generate_diff(code, patched_code)
            })
    
    return patches


def _generate_diff(original: str, patched: str) -> str:
    """Generate unified diff"""
    diff = difflib.unified_diff(
        original.splitlines(keepends=True),
        patched.splitlines(keepends=True),
        fromfile='original',
        tofile='patched',
        lineterm=''
    )
    return ''.join(diff)
