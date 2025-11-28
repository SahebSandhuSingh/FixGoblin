"""
Semantic Error Detector
======================
Detects logical/semantic errors by analyzing code patterns and output behavior.
Identifies issues that don't cause runtime errors but produce wrong results.
"""

import ast
import re
from typing import Dict, List, Optional


def detect_semantic_errors(code: str, output: str, error_info: Dict) -> List[Dict]:
    """
    Detect semantic/logical errors in code.
    
    Args:
        code: Source code
        output: Program output
        error_info: Error information from execution
        
    Returns:
        List of detected semantic issues
    """
    
    issues = []
    
    # Check for common semantic errors
    issues.extend(_check_traversal_order(code, output))
    issues.extend(_check_function_name_mismatch(code))
    issues.extend(_check_suspicious_patterns(code))
    issues.extend(_check_common_algorithm_bugs(code))
    
    return issues


def _check_traversal_order(code: str, output: str) -> List[Dict]:
    """Detect tree/graph traversal order mismatches"""
    issues = []
    
    # Check if function name suggests one traversal but implements another
    patterns = {
        'preorder': {
            'wrong': r'def\s+preorder.*?:\s*.*?preorder\([^)]*left[^)]*\).*?append.*?preorder\([^)]*right[^)]*\)',
            'correct': r'def\s+preorder.*?:\s*.*?append.*?preorder\([^)]*left[^)]*\).*?preorder\([^)]*right[^)]*\)',
            'message': 'Function named "preorder" but implements inorder traversal (Left→Root→Right). Should be Root→Left→Right.'
        },
        'inorder': {
            'wrong': r'def\s+inorder.*?:\s*.*?append.*?inorder\([^)]*left[^)]*\).*?inorder\([^)]*right[^)]*\)',
            'correct': r'def\s+inorder.*?:\s*.*?inorder\([^)]*left[^)]*\).*?append.*?inorder\([^)]*right[^)]*\)',
            'message': 'Function named "inorder" but implements preorder traversal (Root→Left→Right). Should be Left→Root→Right.'
        },
        'postorder': {
            'wrong': r'def\s+postorder.*?:\s*.*?postorder\([^)]*left[^)]*\).*?append.*?postorder\([^)]*right[^)]*\)',
            'correct': r'def\s+postorder.*?:\s*.*?postorder\([^)]*left[^)]*\).*?postorder\([^)]*right[^)]*\).*?append',
            'message': 'Function named "postorder" but doesn\'t implement postorder traversal. Should be Left→Right→Root.'
        }
    }
    
    code_clean = re.sub(r'\s+', ' ', code)
    
    for traversal_type, pattern_info in patterns.items():
        if f'def {traversal_type}' in code:
            if re.search(pattern_info['wrong'], code_clean, re.DOTALL):
                issues.append({
                    'type': 'SemanticError',
                    'category': 'traversal_order_mismatch',
                    'severity': 'HIGH',
                    'message': pattern_info['message'],
                    'suggestion': f'Reorder operations in {traversal_type} function to match expected traversal order',
                    'auto_fixable': True
                })
    
    return issues


def _check_function_name_mismatch(code: str) -> List[Dict]:
    """Detect function names that don't match their implementation"""
    issues = []
    
    # Parse AST
    try:
        tree = ast.parse(code)
    except:
        return issues
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            func_name = node.name.lower()
            
            # Check for sorting functions
            if 'sort' in func_name or 'bubble' in func_name:
                # Check if it actually sorts
                has_comparison = any(
                    isinstance(n, ast.Compare) 
                    for n in ast.walk(node)
                )
                has_swap = any(
                    isinstance(n, ast.Assign) and 
                    any(isinstance(t, ast.Subscript) for t in n.targets)
                    for n in ast.walk(node)
                )
                
                if not (has_comparison and has_swap):
                    issues.append({
                        'type': 'SemanticError',
                        'category': 'incomplete_implementation',
                        'severity': 'MEDIUM',
                        'message': f'Function "{func_name}" suggests sorting but may not implement it correctly',
                        'suggestion': 'Verify sorting logic includes comparison and swap operations'
                    })
            
            # Check for search functions
            if 'search' in func_name or 'find' in func_name:
                has_return = any(isinstance(n, ast.Return) for n in ast.walk(node))
                if not has_return:
                    issues.append({
                        'type': 'SemanticError',
                        'category': 'missing_return',
                        'severity': 'HIGH',
                        'message': f'Function "{func_name}" suggests search but has no return statement',
                        'suggestion': 'Add return statement to return search result'
                    })
    
    return issues


def _check_suspicious_patterns(code: str) -> List[Dict]:
    """Detect suspicious code patterns that often indicate bugs"""
    issues = []
    
    lines = code.split('\n')
    
    for i, line in enumerate(lines, 1):
        # Check for loop with no body
        if re.match(r'\s*(for|while)\s+.*:\s*$', line):
            if i < len(lines) and lines[i].strip() == '':
                issues.append({
                    'type': 'SemanticError',
                    'category': 'empty_loop',
                    'severity': 'MEDIUM',
                    'line': i,
                    'message': 'Loop has no body - likely incomplete implementation',
                    'suggestion': 'Add loop body or remove empty loop'
                })
        
        # Check for comparison in assignment context
        if '==' in line and '=' in line and 'if' not in line and 'while' not in line:
            issues.append({
                'type': 'SemanticError',
                'category': 'suspicious_comparison',
                'severity': 'LOW',
                'line': i,
                'message': 'Comparison operator == found outside conditional - might be assignment typo',
                'suggestion': 'Verify if this should be assignment (=) instead'
            })
    
    return issues


def _check_common_algorithm_bugs(code: str) -> List[Dict]:
    """Detect common algorithmic bugs"""
    issues = []
    
    # Off-by-one errors in range
    if re.search(r'range\([^)]*\+\s*1\s*\)', code):
        issues.append({
            'type': 'SemanticError',
            'category': 'potential_off_by_one',
            'severity': 'LOW',
            'message': 'range() with +1 might indicate off-by-one consideration',
            'suggestion': 'Verify loop bounds are correct'
        })
    
    # Wrong operator in calculation
    calc_patterns = [
        (r'discount\s*=.*?\*', 'calculate.*discount', 
         'Discount calculation multiplies instead of expected subtraction'),
        (r'average\s*=.*?[+\-\*](?!\s*/)', 'average',
         'Average calculation missing division operator'),
    ]
    
    for pattern, context, message in calc_patterns:
        if re.search(context, code, re.IGNORECASE) and re.search(pattern, code):
            issues.append({
                'type': 'SemanticError',
                'category': 'wrong_operator',
                'severity': 'MEDIUM',
                'message': message,
                'suggestion': 'Verify mathematical operators match intended calculation'
            })
    
    return issues


def suggest_fixes_for_semantic_errors(issues: List[Dict], code: str) -> List[Dict]:
    """Generate fix suggestions for semantic errors"""
    fixes = []
    
    for issue in issues:
        if issue.get('auto_fixable'):
            if issue['category'] == 'traversal_order_mismatch':
                fixes.append(_fix_traversal_order(code, issue))
    
    return fixes


def _fix_traversal_order(code: str, issue: Dict) -> Dict:
    """Generate fix for traversal order mismatch"""
    
    lines = code.split('\n')
    fixed_lines = []
    in_preorder = False
    indent_level = 0
    
    for i, line in enumerate(lines):
        # Detect preorder function
        if 'def preorder' in line:
            in_preorder = True
            indent_level = len(line) - len(line.lstrip())
            fixed_lines.append(line)
            continue
        
        if in_preorder:
            # Look for the append line
            if '.append(' in line and 'root.val' in line:
                # Found append - move it to top
                append_line = line
                # Look ahead for the recursive calls
                left_call = None
                right_call = None
                
                for j in range(i+1, min(i+10, len(lines))):
                    if '.left' in lines[j] and 'preorder(' in lines[j]:
                        left_call = lines[j]
                    if '.right' in lines[j] and 'preorder(' in lines[j]:
                        right_call = lines[j]
                
                # Reorder: skip this line, we'll insert it before left call
                continue
            
            # Look for left recursive call
            elif '.left' in line and 'preorder(' in line and in_preorder:
                # Insert append before left call
                # Find the append line from previous iteration
                for prev_line in fixed_lines[::-1]:
                    if '.append(' in prev_line and 'root.val' in prev_line:
                        fixed_lines.append(prev_line)
                        break
                fixed_lines.append(line)
                continue
        
        # Check if we're exiting the function
        if in_preorder and line.strip() and not line.startswith(' ' * (indent_level + 4)) and line.strip() != '':
            if not line.strip().startswith('#'):
                in_preorder = False
        
        fixed_lines.append(line)
    
    fixed_code = '\n'.join(fixed_lines)
    
    # Simple fix: just swap the order if it matches the pattern
    if 'def preorder' in code:
        # Find and fix the order
        import re
        # Match the function and reorder
        pattern = r'(def preorder[^:]*:.*?if not root:.*?return)(.*?)(preorder\([^,]+\.left[^)]*\))(.*?)(res\.append\([^)]+\.val\))(.*?)(preorder\([^,]+\.right[^)]*\))'
        
        def reorder_match(m):
            return f'{m.group(1)}{m.group(2)}{m.group(5)}{m.group(4)}{m.group(3)}{m.group(6)}{m.group(7)}'
        
        fixed_code = re.sub(pattern, reorder_match, code, flags=re.DOTALL)
    
    return {
        'id': 'fix_preorder_traversal',
        'description': 'Fix preorder traversal order: Root → Left → Right',
        'patched_code': fixed_code,
        'issue': issue
    }
