"""
LOGICAL VALIDATION LAYER
=========================
Detects logical errors that don't cause runtime crashes.

This module extends the error detection system to catch:
- Functions that compute values but return None
- Suspicious output patterns (e.g., "None" where values expected)
- Missing return statements
"""

import re
import ast
from typing import Dict, List, Any, Optional


def validate_logic(sandbox_result: Dict[str, Any], source_code: str) -> Dict[str, Any]:
    """
    Validate program logic even when returncode == 0.
    
    Args:
        sandbox_result: Result from sandbox execution
        source_code: Original source code
        
    Returns:
        Dictionary with:
            - is_logically_correct: bool
            - issues: list of detected logical issues
            - suggested_fixes: list of potential fixes
    """
    issues = []
    
    # Only validate if code ran successfully
    if sandbox_result['returncode'] != 0:
        return {
            'is_logically_correct': True,  # Runtime errors take priority
            'issues': [],
            'suggested_fixes': []
        }
    
    # Check 1: Detect "None" in output where values are expected
    stdout = sandbox_result.get('stdout', '')
    none_issues = _detect_suspicious_none_outputs(stdout, source_code)
    issues.extend(none_issues)
    
    # Check 2: Detect functions with missing return statements
    missing_returns = _detect_missing_returns(source_code)
    issues.extend(missing_returns)
    
    # Determine if logically correct
    is_correct = len(issues) == 0
    
    return {
        'is_logically_correct': is_correct,
        'issues': issues,
        'suggested_fixes': _generate_logical_fixes(issues, source_code)
    }


def _detect_suspicious_none_outputs(stdout: str, source_code: str) -> List[Dict[str, Any]]:
    """
    Detect patterns like "result is None" or "Sum: None" in output.
    These suggest missing return statements or logic errors.
    """
    issues = []
    
    # Pattern 1: word + "is" + None
    # Example: "Sum up to 10 is None"
    pattern1 = r'(\w+)\s+(?:is|=|:)\s+None'
    matches1 = re.finditer(pattern1, stdout, re.IGNORECASE)
    
    for match in matches1:
        variable_name = match.group(1).lower()
        # Filter out intentional None (like "Max of []")
        if 'max of []' not in stdout.lower() or variable_name != 'max':
            issues.append({
                'type': 'suspicious_none_output',
                'message': f"Output shows '{match.group(0)}' - possible missing return statement",
                'context': match.group(0),
                'line_number': None
            })
    
    # Pattern 2: Detect mismatch between expected and actual output
    # Example: "Sum of first 10 (expect 55): 45"
    pattern2 = r'\(expect\s+(\d+)\)[:\s]+(\d+)'
    matches2 = re.finditer(pattern2, stdout)
    
    for match in matches2:
        expected = int(match.group(1))
        actual = int(match.group(2))
        if expected != actual:
            issues.append({
                'type': 'output_mismatch',
                'message': f"Expected output {expected} but got {actual} - possible logic error",
                'context': match.group(0),
                'line_number': None,
                'expected': expected,
                'actual': actual
            })
    
    # Pattern 3: Detect "Exception" or "Error" in output (even if code didn't crash)
    if re.search(r'(?:Exception|Error)(?!:)', stdout):
        issues.append({
            'type': 'exception_in_output',
            'message': "Exception or error message in output - possible unhandled edge case",
            'context': 'Exception found in output',
            'line_number': None
        })
    
    return issues


def _detect_missing_returns(source_code: str) -> List[Dict[str, Any]]:
    """
    Use AST to detect functions that:
    - Calculate/accumulate values in local variables
    - Don't return anything (implicit return None)
    - Have off-by-one errors in loops
    """
    issues = []
    
    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        return issues  # Can't analyze if syntax is broken
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Check if function has any explicit return statement
            has_return = any(isinstance(n, ast.Return) and n.value is not None 
                           for n in ast.walk(node))
            
            # Check if function has computation (assignments to local vars)
            has_computation = any(isinstance(n, (ast.AugAssign, ast.Assign)) 
                                for n in ast.walk(node))
            
            # Check for accumulator pattern (total += x, sum += x, etc.)
            # ANY augmented assignment with += operator indicates accumulation
            has_accumulator = False
            accumulator_var = None
            accumulators = []
            for n in ast.walk(node):
                if isinstance(n, ast.AugAssign) and isinstance(n.target, ast.Name):
                    if isinstance(n.op, ast.Add):  # Specifically += operations
                        has_accumulator = True
                        accumulator_var = n.target.id
                        accumulators.append(n.target.id)
            
            # Prefer descriptive names if multiple accumulators found
            if len(accumulators) > 1:
                for var in accumulators:
                    var_lower = var.lower()
                    if any(kw in var_lower for kw in ['total', 'sum', 'count', 'result', 'value']):
                        accumulator_var = var
                        break
            
            # Flag if: computes values but doesn't return
            if has_accumulator and not has_return:
                issues.append({
                    'type': 'missing_return_statement',
                    'message': f"Function '{node.name}' computes values but doesn't return anything",
                    'function_name': node.name,
                    'line_number': node.lineno,
                    'end_line': node.end_lineno,
                    'accumulator_var': accumulator_var
                })
            
            # Check for potential off-by-one errors in range() calls
            if has_return:  # Only check functions that do return
                for n in ast.walk(node):
                    if isinstance(n, ast.For) and isinstance(n.iter, ast.Call):
                        if isinstance(n.iter.func, ast.Name) and n.iter.func.id == 'range':
                            # Check for range(1, n) pattern - common off-by-one
                            if len(n.iter.args) == 2:
                                start_arg = n.iter.args[0]
                                end_arg = n.iter.args[1]
                                # Detect range(1, n) without n+1
                                if (isinstance(start_arg, ast.Constant) and start_arg.value == 1 and
                                    isinstance(end_arg, ast.Name) and 
                                    has_accumulator):
                                    issues.append({
                                        'type': 'potential_off_by_one',
                                        'message': f"Function '{node.name}' uses range(1, n) which excludes n - possible off-by-one error",
                                        'function_name': node.name,
                                        'line_number': n.lineno,
                                        'end_line': node.end_lineno
                                    })
    
    return issues


def _generate_logical_fixes(issues: List[Dict[str, Any]], source_code: str) -> List[Dict[str, Any]]:
    """
    Generate fix suggestions for logical issues.
    """
    fixes = []
    
    for issue in issues:
        if issue['type'] == 'missing_return_statement':
            # Suggest adding return statement
            func_name = issue.get('function_name')
            line_num = issue.get('line_number')
            
            # Try to identify the variable to return
            var_to_return = _identify_return_variable(source_code, func_name)
            
            fixes.append({
                'issue_type': 'missing_return_statement',
                'function_name': func_name,
                'line_number': line_num,
                'suggested_fix': f"Add 'return {var_to_return}' at end of function",
                'variable_to_return': var_to_return
            })
        
        elif issue['type'] == 'potential_off_by_one':
            func_name = issue.get('function_name')
            line_num = issue.get('line_number')
            
            fixes.append({
                'issue_type': 'potential_off_by_one',
                'function_name': func_name,
                'line_number': line_num,
                'suggested_fix': 'Change range(1, n) to range(1, n + 1) to include n in the sum',
                'variable_name': 'n'  # Could be extracted from AST but 'n' is common
            })
        
        elif issue['type'] == 'output_mismatch':
            expected = issue.get('expected')
            actual = issue.get('actual')
            
            fixes.append({
                'issue_type': 'output_mismatch',
                'suggested_fix': f'Output shows expected {expected} but got {actual} - review calculation logic',
                'expected': expected,
                'actual': actual
            })
        
        elif issue['type'] == 'suspicious_none_output':
            fixes.append({
                'issue_type': 'suspicious_none_output',
                'suggested_fix': 'Check for missing return statements in called functions',
                'context': issue.get('context')
            })
    
    return fixes


def _identify_return_variable(source_code: str, func_name: str) -> str:
    """
    Identify which variable should be returned from a function.
    Uses heuristics: look for variables like total, result, sum, etc.
    """
    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        return 'result'
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            # Find accumulator variables
            accumulators = []
            for n in ast.walk(node):
                if isinstance(n, ast.AugAssign) and isinstance(n.target, ast.Name):
                    accumulators.append(n.target.id)
                elif isinstance(n, ast.Assign):
                    for target in n.targets:
                        if isinstance(target, ast.Name):
                            var_name = target.id.lower()
                            if any(kw in var_name for kw in ['total', 'sum', 'result', 'value', 'count', 'output']):
                                accumulators.append(target.id)
            
            # Return most likely candidate
            if accumulators:
                # Prefer 'total', 'result', 'sum' in that order
                for preferred in ['total', 'result', 'sum', 'count', 'value']:
                    for var in accumulators:
                        if preferred in var.lower():
                            return var
                return accumulators[0]  # Return first accumulator found
    
    return 'result'  # Default fallback


def format_logical_error(validation_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format logical validation results as error_data for the patch generator.
    
    Returns format compatible with error_parser output.
    """
    if validation_result['is_logically_correct']:
        return {}
    
    # Prioritize issues: potential_off_by_one > missing_return_statement > output_mismatch > suspicious_none_output
    # Note: off_by_one prioritized over output_mismatch because it has actionable code fix
    priority_types = ['potential_off_by_one', 'missing_return_statement', 'output_mismatch', 'suspicious_none_output']
    
    selected_issue = None
    for priority_type in priority_types:
        for issue in validation_result['issues']:
            if issue['type'] == priority_type:
                selected_issue = issue
                break
        if selected_issue:
            break
    
    # Fallback to first issue if none match priority
    if not selected_issue and validation_result['issues']:
        selected_issue = validation_result['issues'][0]
    
    if not selected_issue:
        return {}
    
    # Find corresponding fix
    suggested_fix = {}
    for fix in validation_result['suggested_fixes']:
        if fix.get('issue_type') == selected_issue['type']:
            suggested_fix = fix
            break
    
    # If no specific fix found, use first available
    if not suggested_fix and validation_result['suggested_fixes']:
        suggested_fix = validation_result['suggested_fixes'][0]
    
    return {
        'error_type': 'LogicalError',
        'line_number': selected_issue.get('line_number') or suggested_fix.get('line_number'),
        'error_message': selected_issue['message'],
        'faulty_snippet': f"Function: {selected_issue.get('function_name', 'unknown')}",
        'logical_issue': selected_issue,
        'suggested_fix': suggested_fix,
        'defined_variables': []
    }
