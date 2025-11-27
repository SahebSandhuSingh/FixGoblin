"""
JavaScript Patch Generator
==========================
Generates fix patches for common JavaScript errors.
"""

import re
import difflib
from typing import List, Dict


def generate_js_patches(error_data: Dict, code: str) -> List[Dict]:
    """
    Generate patch candidates for JavaScript errors.
    
    Args:
        error_data: Dictionary with error_type, line_number, error_message
        code: Current JavaScript code
        
    Returns:
        List of patch dictionaries with id, description, patched_code, diff
    """
    
    error_type = error_data.get('error_type', '')
    line_num = error_data.get('line_number', 0)
    error_msg = error_data.get('error_message', '').lower()
    
    patches = []
    
    # Unexpected token
    if 'unexpected token' in error_msg or 'syntaxerror' in error_type.lower():
        patches.extend(_fix_syntax_error(code, line_num, error_msg))
    
    # ReferenceError: X is not defined
    if 'is not defined' in error_msg or 'referenceerror' in error_type.lower():
        patches.extend(_fix_undefined_variable(code, line_num, error_msg))
    
    # TypeError: Cannot read property
    if 'cannot read property' in error_msg or 'typeerror' in error_type.lower():
        patches.extend(_fix_null_reference(code, line_num, error_msg))
    
    # Missing closing bracket/brace/paren
    if 'expected' in error_msg:
        patches.extend(_fix_missing_delimiter(code, line_num, error_msg))
    
    # Assignment in condition
    if '=' in error_msg and '==' in error_msg:
        patches.extend(_fix_assignment_in_condition(code, line_num))
    
    return patches


def _fix_syntax_error(code: str, line_num: int, error_msg: str) -> List[Dict]:
    """Fix common syntax errors"""
    patches = []
    lines = code.split('\n')
    
    if 0 < line_num <= len(lines):
        target_line = lines[line_num - 1]
        
        # Missing semicolon (though JS doesn't strictly require them)
        if not target_line.rstrip().endswith((';', '{', '}', ')', ',')):
            patched_lines = lines.copy()
            patched_lines[line_num - 1] = target_line.rstrip() + ';'
            patched_code = '\n'.join(patched_lines)
            
            patches.append({
                'id': 'add_semicolon',
                'description': f'Add semicolon at line {line_num}',
                'patched_code': patched_code,
                'diff': _generate_diff(code, patched_code)
            })
        
        # Missing closing quote
        quote_count_single = target_line.count("'")
        quote_count_double = target_line.count('"')
        
        if quote_count_single % 2 != 0:
            patched_lines = lines.copy()
            patched_lines[line_num - 1] = target_line.rstrip() + "'"
            patched_code = '\n'.join(patched_lines)
            
            patches.append({
                'id': 'add_closing_quote',
                'description': f"Add missing closing quote at line {line_num}",
                'patched_code': patched_code,
                'diff': _generate_diff(code, patched_code)
            })
        
        if quote_count_double % 2 != 0:
            patched_lines = lines.copy()
            patched_lines[line_num - 1] = target_line.rstrip() + '"'
            patched_code = '\n'.join(patched_lines)
            
            patches.append({
                'id': 'add_closing_double_quote',
                'description': f'Add missing closing double quote at line {line_num}',
                'patched_code': patched_code,
                'diff': _generate_diff(code, patched_code)
            })
    
    return patches


def _fix_undefined_variable(code: str, line_num: int, error_msg: str) -> List[Dict]:
    """Fix undefined variable errors"""
    patches = []
    lines = code.split('\n')
    
    if 0 < line_num <= len(lines):
        target_line = lines[line_num - 1]
        
        # Extract variable name from error message
        var_match = re.search(r"'?(\w+)'?\s+is not defined", error_msg)
        if var_match:
            var_name = var_match.group(1)
            
            # Try to find similar variable names (typo fix)
            all_vars = re.findall(r'\b[a-zA-Z_$][\w$]*\b', code)
            similar = difflib.get_close_matches(var_name, all_vars, n=3, cutoff=0.7)
            
            for suggestion in similar:
                if suggestion != var_name:
                    patched_lines = lines.copy()
                    patched_lines[line_num - 1] = target_line.replace(var_name, suggestion)
                    patched_code = '\n'.join(patched_lines)
                    
                    patches.append({
                        'id': f'fix_typo_{var_name}_to_{suggestion}',
                        'description': f'Fix typo: {var_name} → {suggestion} at line {line_num}',
                        'patched_code': patched_code,
                        'diff': _generate_diff(code, patched_code)
                    })
            
            # Try to declare the variable
            indent = len(target_line) - len(target_line.lstrip())
            declaration = ' ' * indent + f'let {var_name};\n'
            
            patched_lines = lines.copy()
            patched_lines.insert(line_num - 1, declaration)
            patched_code = '\n'.join(patched_lines)
            
            patches.append({
                'id': f'declare_{var_name}',
                'description': f'Declare variable {var_name} before line {line_num}',
                'patched_code': patched_code,
                'diff': _generate_diff(code, patched_code)
            })
    
    return patches


def _fix_null_reference(code: str, line_num: int, error_msg: str) -> List[Dict]:
    """Fix null/undefined property access"""
    patches = []
    lines = code.split('\n')
    
    if 0 < line_num <= len(lines):
        target_line = lines[line_num - 1]
        
        # Extract object name
        obj_match = re.search(r"Cannot read property '(\w+)' of (null|undefined)", error_msg)
        if obj_match:
            prop_name = obj_match.group(1)
            
            # Find the object reference in the line
            obj_ref_match = re.search(r'(\w+)\.' + re.escape(prop_name), target_line)
            if obj_ref_match:
                obj_name = obj_ref_match.group(1)
                
                # Add null check using optional chaining
                patched_lines = lines.copy()
                patched_lines[line_num - 1] = target_line.replace(
                    f'{obj_name}.{prop_name}',
                    f'{obj_name}?.{prop_name}'
                )
                patched_code = '\n'.join(patched_lines)
                
                patches.append({
                    'id': 'add_optional_chaining',
                    'description': f'Add optional chaining for {obj_name}.{prop_name} at line {line_num}',
                    'patched_code': patched_code,
                    'diff': _generate_diff(code, patched_code)
                })
                
                # Alternative: Add explicit null check
                indent = len(target_line) - len(target_line.lstrip())
                null_check = ' ' * indent + f'if ({obj_name}) {{\n'
                closing_brace = ' ' * indent + '}\n'
                
                patched_lines = lines.copy()
                patched_lines[line_num - 1] = ' ' * (indent + 2) + target_line.lstrip()
                patched_lines.insert(line_num - 1, null_check)
                patched_lines.insert(line_num + 1, closing_brace)
                patched_code = '\n'.join(patched_lines)
                
                patches.append({
                    'id': 'add_null_check',
                    'description': f'Add null check for {obj_name} at line {line_num}',
                    'patched_code': patched_code,
                    'diff': _generate_diff(code, patched_code)
                })
    
    return patches


def _fix_missing_delimiter(code: str, line_num: int, error_msg: str) -> List[Dict]:
    """Fix missing closing delimiters"""
    patches = []
    lines = code.split('\n')
    
    if 0 < line_num <= len(lines):
        target_line = lines[line_num - 1]
        
        # Missing closing parenthesis
        if ')' in error_msg or 'paren' in error_msg:
            open_count = target_line.count('(')
            close_count = target_line.count(')')
            
            if open_count > close_count:
                patched_lines = lines.copy()
                patched_lines[line_num - 1] = target_line.rstrip() + ')'
                patched_code = '\n'.join(patched_lines)
                
                patches.append({
                    'id': 'add_closing_paren',
                    'description': f'Add missing closing parenthesis at line {line_num}',
                    'patched_code': patched_code,
                    'diff': _generate_diff(code, patched_code)
                })
        
        # Missing closing brace
        if '}' in error_msg or 'brace' in error_msg:
            open_count = code.count('{')
            close_count = code.count('}')
            
            if open_count > close_count:
                patched_code = code.rstrip() + '\n}'
                
                patches.append({
                    'id': 'add_closing_brace',
                    'description': f'Add missing closing brace',
                    'patched_code': patched_code,
                    'diff': _generate_diff(code, patched_code)
                })
        
        # Missing closing bracket
        if ']' in error_msg or 'bracket' in error_msg:
            open_count = target_line.count('[')
            close_count = target_line.count(']')
            
            if open_count > close_count:
                patched_lines = lines.copy()
                patched_lines[line_num - 1] = target_line.rstrip() + ']'
                patched_code = '\n'.join(patched_lines)
                
                patches.append({
                    'id': 'add_closing_bracket',
                    'description': f'Add missing closing bracket at line {line_num}',
                    'patched_code': patched_code,
                    'diff': _generate_diff(code, patched_code)
                })
    
    return patches


def _fix_assignment_in_condition(code: str, line_num: int) -> List[Dict]:
    """Fix assignment operator in conditional statement"""
    patches = []
    lines = code.split('\n')
    
    if 0 < line_num <= len(lines):
        target_line = lines[line_num - 1]
        
        # Look for single = in if/while conditions
        if re.search(r'\b(if|while)\s*\([^=]*=[^=]', target_line):
            # Replace = with ==
            patched_line = re.sub(r'(\bif|\bwhile)(\s*\([^=]*)=([^=])', r'\1\2==\3', target_line)
            
            patched_lines = lines.copy()
            patched_lines[line_num - 1] = patched_line
            patched_code = '\n'.join(patched_lines)
            
            patches.append({
                'id': 'fix_assignment_in_condition',
                'description': f'Replace assignment = with comparison == at line {line_num}',
                'patched_code': patched_code,
                'diff': _generate_diff(code, patched_code)
            })
    
    return patches


def _generate_diff(original: str, patched: str) -> str:
    """Generate unified diff between original and patched code"""
    original_lines = original.splitlines(keepends=True)
    patched_lines = patched.splitlines(keepends=True)
    
    diff = list(difflib.unified_diff(
        original_lines,
        patched_lines,
        fromfile='original',
        tofile='patched',
        lineterm=''
    ))
    
    return ''.join(diff)
