"""
Java Patch Generator
===================
Generates fix patches for common Java errors.
"""

import re
import difflib
from typing import List, Dict


def generate_java_patches(error_data: Dict, code: str) -> List[Dict]:
    """
    Generate patch candidates for Java errors.
    
    Args:
        error_data: Dictionary with error_type, line_number, error_message
        code: Current Java code
        
    Returns:
        List of patch dictionaries with id, description, patched_code, diff
    """
    
    error_type = error_data.get('error_type', '')
    line_num = error_data.get('line_number', 0)
    error_msg = error_data.get('error_message', '').lower()
    
    patches = []
    
    # Missing semicolon
    if 'expected' in error_msg and ';' in error_msg:
        patches.extend(_fix_missing_semicolon(code, line_num))
    
    # Missing parenthesis
    if 'expected' in error_msg and ')' in error_msg:
        patches.extend(_fix_missing_parenthesis(code, line_num))
    
    # Missing brace
    if 'expected' in error_msg and ('{' in error_msg or '}' in error_msg):
        patches.extend(_fix_missing_brace(code, line_num))
    
    # Cannot find symbol
    if 'cannot find symbol' in error_msg:
        patches.extend(_fix_cannot_find_symbol(code, line_num, error_msg))
    
    # Incompatible types
    if 'incompatible types' in error_msg:
        patches.extend(_fix_incompatible_types(code, line_num, error_msg))
    
    # Missing return statement
    if 'missing return statement' in error_msg:
        patches.extend(_fix_missing_return(code, line_num))
    
    # Possible loss of precision
    if 'possible lossy conversion' in error_msg or 'possible loss of precision' in error_msg:
        patches.extend(_fix_lossy_conversion(code, line_num, error_msg))
    
    # Unreachable statement
    if 'unreachable statement' in error_msg:
        patches.extend(_fix_unreachable_statement(code, line_num))
    
    return patches


def _fix_missing_semicolon(code: str, line_num: int) -> List[Dict]:
    """Add missing semicolon at end of line"""
    lines = code.split('\n')
    if 0 < line_num <= len(lines):
        target_line = lines[line_num - 1]
        
        # Don't add semicolon if line ends with {, }, or already has ;
        if not target_line.rstrip().endswith(('{', '}', ';', '//')):
            patched_lines = lines.copy()
            patched_lines[line_num - 1] = target_line.rstrip() + ';'
            patched_code = '\n'.join(patched_lines)
            
            return [{
                'id': 'add_semicolon',
                'description': f'Add missing semicolon at line {line_num}',
                'patched_code': patched_code,
                'diff': _generate_diff(code, patched_code)
            }]
    
    return []


def _fix_missing_parenthesis(code: str, line_num: int) -> List[Dict]:
    """Add missing closing parenthesis"""
    lines = code.split('\n')
    if 0 < line_num <= len(lines):
        target_line = lines[line_num - 1]
        
        # Count parentheses
        open_count = target_line.count('(')
        close_count = target_line.count(')')
        
        if open_count > close_count:
            patched_lines = lines.copy()
            patched_lines[line_num - 1] = target_line.rstrip() + ')'
            patched_code = '\n'.join(patched_lines)
            
            return [{
                'id': 'add_closing_paren',
                'description': f'Add missing closing parenthesis at line {line_num}',
                'patched_code': patched_code,
                'diff': _generate_diff(code, patched_code)
            }]
    
    return []


def _fix_missing_brace(code: str, line_num: int) -> List[Dict]:
    """Add missing closing brace"""
    lines = code.split('\n')
    patches = []
    
    # Count braces in entire code
    open_count = code.count('{')
    close_count = code.count('}')
    
    if open_count > close_count:
        # Add closing brace at end
        patched_code = code.rstrip() + '\n}'
        patches.append({
            'id': 'add_closing_brace',
            'description': f'Add missing closing brace',
            'patched_code': patched_code,
            'diff': _generate_diff(code, patched_code)
        })
    
    return patches


def _fix_cannot_find_symbol(code: str, line_num: int, error_msg: str) -> List[Dict]:
    """Fix undeclared variable or typo"""
    patches = []
    lines = code.split('\n')
    
    if 0 < line_num <= len(lines):
        target_line = lines[line_num - 1]
        
        # Extract variable name from error message
        symbol_match = re.search(r'symbol:\s+\w+\s+(\w+)', error_msg)
        if symbol_match:
            symbol = symbol_match.group(1)
            
            # Try to find similar variable names (typo fix)
            all_vars = re.findall(r'\b[a-zA-Z_]\w*\b', code)
            similar = difflib.get_close_matches(symbol, all_vars, n=3, cutoff=0.7)
            
            for suggestion in similar:
                if suggestion != symbol:
                    patched_lines = lines.copy()
                    patched_lines[line_num - 1] = target_line.replace(symbol, suggestion)
                    patched_code = '\n'.join(patched_lines)
                    
                    patches.append({
                        'id': f'fix_typo_{symbol}_to_{suggestion}',
                        'description': f'Fix typo: {symbol} → {suggestion} at line {line_num}',
                        'patched_code': patched_code,
                        'diff': _generate_diff(code, patched_code)
                    })
            
            # Try to declare the variable
            indent = len(target_line) - len(target_line.lstrip())
            declaration = ' ' * indent + f'int {symbol};\n'
            
            patched_lines = lines.copy()
            patched_lines.insert(line_num - 1, declaration)
            patched_code = '\n'.join(patched_lines)
            
            patches.append({
                'id': f'declare_{symbol}',
                'description': f'Declare variable {symbol} before line {line_num}',
                'patched_code': patched_code,
                'diff': _generate_diff(code, patched_code)
            })
    
    return patches


def _fix_incompatible_types(code: str, line_num: int, error_msg: str) -> List[Dict]:
    """Fix type mismatch with casting"""
    patches = []
    lines = code.split('\n')
    
    if 0 < line_num <= len(lines):
        target_line = lines[line_num - 1]
        
        # Extract types from error message
        type_match = re.search(r'required:\s+(\w+).*found:\s+(\w+)', error_msg)
        if type_match:
            required_type = type_match.group(1)
            found_type = type_match.group(2)
            
            # Try casting
            if '=' in target_line:
                parts = target_line.split('=', 1)
                if len(parts) == 2:
                    lhs = parts[0]
                    rhs = parts[1].strip()
                    
                    patched_lines = lines.copy()
                    patched_lines[line_num - 1] = f"{lhs}= ({required_type}) {rhs}"
                    patched_code = '\n'.join(patched_lines)
                    
                    patches.append({
                        'id': 'add_type_cast',
                        'description': f'Cast {found_type} to {required_type} at line {line_num}',
                        'patched_code': patched_code,
                        'diff': _generate_diff(code, patched_code)
                    })
    
    return patches


def _fix_missing_return(code: str, line_num: int) -> List[Dict]:
    """Add missing return statement"""
    lines = code.split('\n')
    patches = []
    
    # Find the method signature to determine return type
    method_line = None
    for i in range(line_num - 1, -1, -1):
        if re.search(r'\b(public|private|protected)?\s*\w+\s+\w+\s*\(', lines[i]):
            method_line = lines[i]
            break
    
    if method_line:
        # Extract return type
        type_match = re.search(r'\b(public|private|protected)?\s*(\w+)\s+\w+\s*\(', method_line)
        if type_match:
            return_type = type_match.group(2)
            
            # Determine default return value
            default_returns = {
                'int': 'return 0;',
                'double': 'return 0.0;',
                'float': 'return 0.0f;',
                'long': 'return 0L;',
                'boolean': 'return false;',
                'String': 'return "";',
                'void': 'return;'
            }
            
            return_stmt = default_returns.get(return_type, 'return null;')
            
            # Find indent level
            indent = 0
            for i in range(line_num - 1, -1, -1):
                if '{' in lines[i]:
                    indent = len(lines[i]) - len(lines[i].lstrip()) + 4
                    break
            
            patched_lines = lines.copy()
            patched_lines.insert(line_num, ' ' * indent + return_stmt)
            patched_code = '\n'.join(patched_lines)
            
            patches.append({
                'id': 'add_return_statement',
                'description': f'Add missing return statement at line {line_num}',
                'patched_code': patched_code,
                'diff': _generate_diff(code, patched_code)
            })
    
    return patches


def _fix_lossy_conversion(code: str, line_num: int, error_msg: str) -> List[Dict]:
    """Fix lossy type conversion"""
    patches = []
    lines = code.split('\n')
    
    if 0 < line_num <= len(lines):
        target_line = lines[line_num - 1]
        
        # Extract types
        type_match = re.search(r'from\s+(\w+)\s+to\s+(\w+)', error_msg)
        if type_match:
            from_type = type_match.group(1)
            to_type = type_match.group(2)
            
            # Add explicit cast
            if '=' in target_line:
                parts = target_line.split('=', 1)
                if len(parts) == 2:
                    lhs = parts[0]
                    rhs = parts[1].strip()
                    
                    patched_lines = lines.copy()
                    patched_lines[line_num - 1] = f"{lhs}= ({to_type}) {rhs}"
                    patched_code = '\n'.join(patched_lines)
                    
                    patches.append({
                        'id': 'explicit_cast',
                        'description': f'Add explicit cast from {from_type} to {to_type} at line {line_num}',
                        'patched_code': patched_code,
                        'diff': _generate_diff(code, patched_code)
                    })
    
    return patches


def _fix_unreachable_statement(code: str, line_num: int) -> List[Dict]:
    """Remove unreachable statement"""
    lines = code.split('\n')
    
    if 0 < line_num <= len(lines):
        patched_lines = lines.copy()
        # Comment out the unreachable line
        patched_lines[line_num - 1] = '// ' + lines[line_num - 1]
        patched_code = '\n'.join(patched_lines)
        
        return [{
            'id': 'remove_unreachable',
            'description': f'Comment out unreachable statement at line {line_num}',
            'patched_code': patched_code,
            'diff': _generate_diff(code, patched_code)
        }]
    
    return []


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
