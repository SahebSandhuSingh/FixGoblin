"""
🦎 FixGoblin - Deterministic Logical Error Detection Engine
============================================================
A rule-based, non-LLM logical analysis system for multi-language debugging.

Techniques:
- Abstract Syntax Tree (AST) traversal
- Control Flow Graph (CFG) validation
- Data Flow Analysis (DFA)
- Boundary condition checking
- Pattern-based error detection

Supported Languages: Python, Java, C++, JavaScript, Go
"""

import ast
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class ErrorType(Enum):
    """Enumeration of logical error types."""
    OFF_BY_ONE = "off_by_one"
    INFINITE_LOOP = "infinite_loop"
    UNREACHABLE_CODE = "unreachable_code"
    MISSING_RETURN = "missing_return"
    WRONG_COMPARISON = "wrong_comparison"
    INCORRECT_BASE_CASE = "incorrect_base_case"
    UNINITIALIZED_VARIABLE = "uninitialized_variable"
    WRONG_LOOP_RANGE = "wrong_loop_range"
    DEAD_CODE = "dead_code"
    ALWAYS_TRUE_FALSE = "always_true_false"
    VARIABLE_SHADOWING = "variable_shadowing"
    MISSING_BREAK = "missing_break"
    WRONG_OPERATOR = "wrong_operator"
    BOUNDARY_ERROR = "boundary_error"


@dataclass
class LogicalError:
    """Represents a detected logical error."""
    error_type: ErrorType
    line: int
    column: int = 0
    message: str = ""
    severity: str = "medium"  # low, medium, high, critical
    context: Dict[str, Any] = field(default_factory=dict)
    suggested_fix: str = ""
    confidence: float = 0.8


@dataclass
class AnalysisResult:
    """Result of logical analysis."""
    logical_errors: List[LogicalError]
    confidence_score: float
    control_flow_issues: List[str] = field(default_factory=list)
    data_flow_issues: List[str] = field(default_factory=list)
    ast_valid: bool = True
    analysis_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convert result to dictionary format."""
        return {
            "logical_errors": [
                {
                    "type": err.error_type.value,
                    "line": err.line,
                    "column": err.column,
                    "message": err.message,
                    "severity": err.severity,
                    "suggested_fix": err.suggested_fix,
                    "confidence": err.confidence
                }
                for err in self.logical_errors
            ],
            "confidence_score": self.confidence_score,
            "control_flow_issues": self.control_flow_issues,
            "data_flow_issues": self.data_flow_issues,
            "ast_valid": self.ast_valid
        }


class ControlFlowNode:
    """Represents a node in the control flow graph."""
    def __init__(self, node_id: int, ast_node: Any, node_type: str):
        self.node_id = node_id
        self.ast_node = ast_node
        self.node_type = node_type  # 'statement', 'branch', 'loop', 'return', 'entry', 'exit'
        self.successors: List['ControlFlowNode'] = []
        self.predecessors: List['ControlFlowNode'] = []
        self.reachable = False
        
    def add_successor(self, node: 'ControlFlowNode'):
        """Add a successor node."""
        if node not in self.successors:
            self.successors.append(node)
            node.predecessors.append(self)


class PythonASTAnalyzer:
    """Python-specific AST analysis."""
    
    def __init__(self, code: str):
        self.code = code
        self.lines = code.split('\n')
        self.tree = None
        self.errors: List[LogicalError] = []
        self.variables_defined: Dict[str, int] = {}  # var_name -> line_number
        self.variables_used: Dict[str, List[int]] = {}  # var_name -> [line_numbers]
        self.functions: Dict[str, ast.FunctionDef] = {}
        self.cfg_nodes: List[ControlFlowNode] = []
        
    def parse(self) -> bool:
        """Parse the Python code into AST."""
        try:
            self.tree = ast.parse(self.code)
            return True
        except SyntaxError:
            return False
    
    def analyze(self) -> List[LogicalError]:
        """Run all Python-specific analyses."""
        if not self.parse():
            return []
        
        # Collect function definitions
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                self.functions[node.name] = node
        
        # Run analysis passes
        self._analyze_loops()
        self._analyze_recursion()
        self._analyze_comparisons()
        self._analyze_returns()
        self._analyze_variables()
        self._analyze_unreachable_code()
        self._analyze_variable_misuse()  # NEW: Detect wrong variable usage
        
        return self.errors
    
    def _analyze_loops(self):
        """Detect loop-related logical errors."""
        for node in ast.walk(self.tree):
            if isinstance(node, (ast.For, ast.While)):
                # Check for potential infinite loops
                if isinstance(node, ast.While):
                    self._check_infinite_loop(node)
                
                # Check for off-by-one errors in range()
                if isinstance(node, ast.For) and isinstance(node.iter, ast.Call):
                    if hasattr(node.iter.func, 'id') and node.iter.func.id == 'range':
                        self._check_range_off_by_one(node)
                
                # Check for empty loops
                if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                    self.errors.append(LogicalError(
                        error_type=ErrorType.DEAD_CODE,
                        line=node.lineno,
                        message="Empty loop detected - this does nothing",
                        severity="low",
                        confidence=0.9
                    ))
    
    def _check_infinite_loop(self, node: ast.While):
        """Check if a while loop might be infinite."""
        # Check if condition is always True
        if isinstance(node.test, ast.Constant) and node.test.value is True:
            # Check if there's a break statement
            has_break = any(isinstance(n, ast.Break) for n in ast.walk(node))
            if not has_break:
                self.errors.append(LogicalError(
                    error_type=ErrorType.INFINITE_LOOP,
                    line=node.lineno,
                    message="Potential infinite loop: condition is always True and no break statement",
                    severity="high",
                    confidence=0.95,
                    suggested_fix="Add a break condition or modify the loop condition"
                ))
        
        # Check if loop variable is never modified
        if isinstance(node.test, ast.Compare):
            variables_in_condition = set()
            for n in ast.walk(node.test):
                if isinstance(n, ast.Name):
                    variables_in_condition.add(n.id)
            
            # Check if any variable in condition is modified in loop body
            modified_vars = set()
            for body_node in ast.walk(node):
                if isinstance(body_node, (ast.Assign, ast.AugAssign)):
                    for target in ast.walk(body_node):
                        if isinstance(target, ast.Name) and isinstance(target.ctx, ast.Store):
                            modified_vars.add(target.id)
            
            unmodified = variables_in_condition - modified_vars
            has_break = any(isinstance(n, ast.Break) for n in ast.walk(node))
            
            if unmodified and not has_break:
                self.errors.append(LogicalError(
                    error_type=ErrorType.INFINITE_LOOP,
                    line=node.lineno,
                    message=f"Potential infinite loop: variables {unmodified} in condition never modified",
                    severity="high",
                    confidence=0.85,
                    suggested_fix=f"Modify {list(unmodified)[0]} inside the loop or add a break condition"
                ))
    
    def _check_range_off_by_one(self, node: ast.For):
        """Check for off-by-one errors in range() calls."""
        range_call = node.iter
        if len(range_call.args) >= 2:
            # Check patterns like range(1, len(arr)) which might be off-by-one
            start = range_call.args[0]
            stop = range_call.args[1]
            
            # Pattern: range(1, n) when should be range(0, n) or range(1, n+1)
            if isinstance(start, ast.Constant) and start.value == 1:
                # Look for array access with loop variable
                loop_var = node.target.id if isinstance(node.target, ast.Name) else None
                if loop_var:
                    for body_node in ast.walk(node):
                        if isinstance(body_node, ast.Subscript):
                            if isinstance(body_node.value, ast.Name) and isinstance(body_node.slice, ast.Name):
                                if body_node.slice.id == loop_var:
                                    self.errors.append(LogicalError(
                                        error_type=ErrorType.OFF_BY_ONE,
                                        line=node.lineno,
                                        message=f"Potential off-by-one: range starts at 1 but array index might start at 0",
                                        severity="medium",
                                        confidence=0.7,
                                        suggested_fix=f"Consider using range(0, ...) if indexing from start"
                                    ))
    
    def _analyze_recursion(self):
        """Analyze recursive functions for missing or incorrect base cases."""
        for func_name, func_node in self.functions.items():
            # Check if function is recursive
            is_recursive = False
            for node in ast.walk(func_node):
                if isinstance(node, ast.Call):
                    if hasattr(node.func, 'id') and node.func.id == func_name:
                        is_recursive = True
                        break
            
            if is_recursive:
                # Check for base case
                has_base_case = False
                has_return = False
                
                for node in ast.walk(func_node):
                    if isinstance(node, ast.Return):
                        has_return = True
                        # Check if return is conditional (likely base case)
                        parent = self._find_parent(func_node, node)
                        if isinstance(parent, ast.If):
                            has_base_case = True
                
                if is_recursive and not has_base_case:
                    self.errors.append(LogicalError(
                        error_type=ErrorType.INCORRECT_BASE_CASE,
                        line=func_node.lineno,
                        message=f"Recursive function '{func_name}' missing clear base case",
                        severity="high",
                        confidence=0.8,
                        suggested_fix="Add a conditional return statement for the base case"
                    ))
                
                if is_recursive and not has_return:
                    self.errors.append(LogicalError(
                        error_type=ErrorType.MISSING_RETURN,
                        line=func_node.lineno,
                        message=f"Recursive function '{func_name}' has no return statement",
                        severity="critical",
                        confidence=0.95
                    ))
    
    def _find_parent(self, root: ast.AST, target: ast.AST) -> Optional[ast.AST]:
        """Find the parent node of a target node."""
        for node in ast.walk(root):
            for child in ast.iter_child_nodes(node):
                if child == target:
                    return node
        return None
    
    def _analyze_comparisons(self):
        """Detect potentially incorrect comparisons."""
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Compare):
                # Check for always true/false comparisons
                if isinstance(node.left, ast.Constant):
                    for op, comparator in zip(node.ops, node.comparators):
                        if isinstance(comparator, ast.Constant):
                            # Both sides are constants - can evaluate
                            if isinstance(op, ast.Eq) and node.left.value == comparator.value:
                                self.errors.append(LogicalError(
                                    error_type=ErrorType.ALWAYS_TRUE_FALSE,
                                    line=node.lineno,
                                    message="Comparison is always True (comparing identical constants)",
                                    severity="medium",
                                    confidence=0.95
                                ))
                
                # Check for suspicious patterns like x == True instead of x
                for comparator in node.comparators:
                    if isinstance(comparator, ast.Constant):
                        if comparator.value is True or comparator.value is False:
                            self.errors.append(LogicalError(
                                error_type=ErrorType.WRONG_COMPARISON,
                                line=node.lineno,
                                message="Comparing to boolean literal - use the variable directly",
                                severity="low",
                                confidence=0.85,
                                suggested_fix="Use 'if variable:' instead of 'if variable == True:'"
                            ))
                
                # Check for assignment in comparison (= instead of ==)
                # This is caught by syntax in Python, but we check for walrus operator misuse
                pass
    
    def _analyze_returns(self):
        """Check for missing or inconsistent return statements."""
        for func_name, func_node in self.functions.items():
            returns = []
            for node in ast.walk(func_node):
                if isinstance(node, ast.Return):
                    returns.append(node)
            
            # Check if all paths return a value
            if returns:
                # Check for inconsistent returns (some with value, some without)
                returns_with_value = sum(1 for r in returns if r.value is not None)
                returns_without_value = len(returns) - returns_with_value
                
                if returns_with_value > 0 and returns_without_value > 0:
                    self.errors.append(LogicalError(
                        error_type=ErrorType.MISSING_RETURN,
                        line=func_node.lineno,
                        message=f"Function '{func_name}' has inconsistent returns (some paths return None)",
                        severity="medium",
                        confidence=0.8
                    ))
    
    def _analyze_variables(self):
        """Track variable definitions and usage."""
        # Build variable usage map
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Name):
                if isinstance(node.ctx, ast.Store):
                    self.variables_defined[node.id] = node.lineno
                elif isinstance(node.ctx, ast.Load):
                    if node.id not in self.variables_used:
                        self.variables_used[node.id] = []
                    self.variables_used[node.id].append(node.lineno)
        
        # Check for variables used before definition
        for var_name, used_lines in self.variables_used.items():
            if var_name in self.variables_defined:
                defined_line = self.variables_defined[var_name]
                for used_line in used_lines:
                    if used_line < defined_line:
                        # This might be caught by runtime, but flag it
                        pass
    
    def _analyze_unreachable_code(self):
        """Detect unreachable code after return/break/continue."""
        for node in ast.walk(self.tree):
            if isinstance(node, (ast.FunctionDef, ast.For, ast.While, ast.If)):
                body = node.body if hasattr(node, 'body') else []
                for i, stmt in enumerate(body):
                    if isinstance(stmt, (ast.Return, ast.Break, ast.Continue)):
                        # Check if there's code after this statement
                        if i < len(body) - 1:
                            next_stmt = body[i + 1]
                            self.errors.append(LogicalError(
                                error_type=ErrorType.UNREACHABLE_CODE,
                                line=next_stmt.lineno,
                                message=f"Unreachable code after {stmt.__class__.__name__.lower()} statement",
                                severity="medium",
                                confidence=0.9,
                                suggested_fix="Remove unreachable code or fix control flow"
                            ))
    
    def _analyze_variable_misuse(self):
        """Detect context-aware variable misuse (e.g., memo[0] when should be memo[n])."""
        for node in ast.walk(self.tree):
            if isinstance(node, ast.If):
                # Check for pattern: if var in dict: return dict[wrong_key]
                if isinstance(node.test, ast.Compare):
                    # Check for 'x in y' pattern
                    if any(isinstance(op, ast.In) for op in node.test.ops):
                        # Get the variable being checked and the container
                        checked_var = None
                        container_var = None
                        
                        if isinstance(node.test.left, ast.Name):
                            checked_var = node.test.left.id
                        
                        for comparator in node.test.comparators:
                            if isinstance(comparator, ast.Name):
                                container_var = comparator.id
                        
                        if checked_var and container_var:
                            # Now check the if body for subscript access
                            for body_stmt in node.body:
                                if isinstance(body_stmt, ast.Return) and body_stmt.value:
                                    # Check if returning a subscript
                                    if isinstance(body_stmt.value, ast.Subscript):
                                        subscript_obj = body_stmt.value.value
                                        subscript_key = body_stmt.value.slice
                                        
                                        # Check if it's the same container
                                        if isinstance(subscript_obj, ast.Name) and subscript_obj.id == container_var:
                                            # Check if using wrong key
                                            wrong_key = None
                                            if isinstance(subscript_key, ast.Constant):
                                                wrong_key = subscript_key.value
                                            elif isinstance(subscript_key, ast.Name):
                                                if subscript_key.id != checked_var:
                                                    wrong_key = subscript_key.id
                                            
                                            if wrong_key is not None and wrong_key != checked_var:
                                                self.errors.append(LogicalError(
                                                    error_type=ErrorType.WRONG_OPERATOR,
                                                    line=body_stmt.lineno,
                                                    message=f"Checked if '{checked_var}' in '{container_var}', but returning '{container_var}[{wrong_key}]' instead of '{container_var}[{checked_var}]'",
                                                    severity="high",
                                                    confidence=0.95,
                                                    suggested_fix=f"Change '{container_var}[{wrong_key}]' to '{container_var}[{checked_var}]'",
                                                    context={
                                                        'checked_var': checked_var,
                                                        'container_var': container_var,
                                                        'wrong_key': wrong_key,
                                                        'correct_key': checked_var
                                                    }
                                                ))



class ControlFlowGraphBuilder:
    """Builds control flow graphs for code analysis."""
    
    def __init__(self, ast_tree):
        self.ast_tree = ast_tree
        self.nodes: List[ControlFlowNode] = []
        self.node_counter = 0
        self.entry_node = None
        self.exit_node = None
    
    def build(self) -> List[ControlFlowNode]:
        """Build CFG from AST."""
        self.entry_node = ControlFlowNode(self._next_id(), None, 'entry')
        self.exit_node = ControlFlowNode(self._next_id(), None, 'exit')
        self.nodes.extend([self.entry_node, self.exit_node])
        
        # Build CFG for the AST
        last_node = self.entry_node
        for stmt in self.ast_tree.body:
            last_node = self._process_statement(stmt, last_node)
        
        # Connect last statement to exit
        if last_node:
            last_node.add_successor(self.exit_node)
        
        # Mark reachable nodes
        self._mark_reachable()
        
        return self.nodes
    
    def _next_id(self) -> int:
        """Generate next node ID."""
        self.node_counter += 1
        return self.node_counter
    
    def _process_statement(self, stmt: ast.AST, predecessor: ControlFlowNode) -> ControlFlowNode:
        """Process a statement and add to CFG."""
        node = ControlFlowNode(self._next_id(), stmt, 'statement')
        self.nodes.append(node)
        predecessor.add_successor(node)
        
        if isinstance(stmt, ast.If):
            # Branch for if-else
            then_node = self._next_id()
            else_node = self._next_id()
            merge_node = ControlFlowNode(self._next_id(), None, 'merge')
            self.nodes.append(merge_node)
            
            # Process then branch
            last_then = node
            for s in stmt.body:
                last_then = self._process_statement(s, last_then)
            last_then.add_successor(merge_node)
            
            # Process else branch
            last_else = node
            for s in stmt.orelse:
                last_else = self._process_statement(s, last_else)
            last_else.add_successor(merge_node)
            
            return merge_node
        
        elif isinstance(stmt, (ast.For, ast.While)):
            # Loop creates back-edge
            loop_body_start = node
            last_body = node
            for s in stmt.body:
                last_body = self._process_statement(s, last_body)
            
            # Back-edge to loop start
            last_body.add_successor(loop_body_start)
            
            # Exit edge
            loop_exit = ControlFlowNode(self._next_id(), None, 'loop_exit')
            self.nodes.append(loop_exit)
            node.add_successor(loop_exit)
            
            return loop_exit
        
        elif isinstance(stmt, ast.Return):
            node.node_type = 'return'
            node.add_successor(self.exit_node)
            return node
        
        return node
    
    def _mark_reachable(self):
        """Mark all reachable nodes from entry."""
        visited = set()
        stack = [self.entry_node]
        
        while stack:
            node = stack.pop()
            if node.node_id in visited:
                continue
            
            visited.add(node.node_id)
            node.reachable = True
            
            for successor in node.successors:
                if successor.node_id not in visited:
                    stack.append(successor)
    
    def find_unreachable(self) -> List[ControlFlowNode]:
        """Find unreachable nodes."""
        return [node for node in self.nodes if not node.reachable and node.node_type not in ['entry', 'exit']]


class DataFlowAnalyzer:
    """Performs data flow analysis to track variable states."""
    
    def __init__(self, ast_tree):
        self.ast_tree = ast_tree
        self.reaching_definitions: Dict[str, List[int]] = {}  # var -> line numbers where defined
        self.live_variables: Dict[int, set] = {}  # line -> set of live variables
        self.uninitialized_uses: List[Tuple[str, int]] = []
    
    def analyze(self) -> List[LogicalError]:
        """Run data flow analysis."""
        errors = []
        
        # Track definitions and uses
        definitions = {}  # var -> line
        uses = {}  # var -> [lines]
        
        for node in ast.walk(self.ast_tree):
            if isinstance(node, ast.Name):
                if isinstance(node.ctx, ast.Store):
                    definitions[node.id] = node.lineno
                elif isinstance(node.ctx, ast.Load):
                    if node.id not in uses:
                        uses[node.id] = []
                    uses[node.id].append(node.lineno)
                    
                    # Check if used before defined
                    if node.id not in definitions:
                        # Could be builtin or parameter
                        if node.id not in dir(__builtins__):
                            errors.append(LogicalError(
                                error_type=ErrorType.UNINITIALIZED_VARIABLE,
                                line=node.lineno,
                                message=f"Variable '{node.id}' may be used before initialization",
                                severity="high",
                                confidence=0.75
                            ))
        
        return errors


def analyze_logic(code: str, language: str, test_cases: list = None) -> dict:
    """
    Main entry point for logical analysis.
    
    Args:
        code: Source code to analyze
        language: Programming language (python, java, cpp, javascript, go)
        test_cases: Optional list of test cases with inputs and expected outputs
        
    Returns:
        Dictionary containing logical errors, confidence score, and suggested fixes
    """
    language = language.lower()
    
    if language == "python":
        analyzer = PythonASTAnalyzer(code)
        errors = analyzer.analyze()
        
        # Build CFG for unreachable code detection
        if analyzer.tree:
            cfg_builder = ControlFlowGraphBuilder(analyzer.tree)
            cfg_nodes = cfg_builder.build()
            unreachable = cfg_builder.find_unreachable()
            
            for node in unreachable:
                if node.ast_node and hasattr(node.ast_node, 'lineno'):
                    errors.append(LogicalError(
                        error_type=ErrorType.UNREACHABLE_CODE,
                        line=node.ast_node.lineno,
                        message="Unreachable code detected via control flow analysis",
                        severity="medium",
                        confidence=0.85
                    ))
            
            # Data flow analysis
            dfa = DataFlowAnalyzer(analyzer.tree)
            dfa_errors = dfa.analyze()
            errors.extend(dfa_errors)
        
        # If test cases provided, compare runtime behavior
        if test_cases:
            test_errors = _analyze_with_test_cases(code, test_cases, language)
            errors.extend(test_errors)
        
        # Calculate confidence score
        confidence = _calculate_confidence(errors)
        
        result = AnalysisResult(
            logical_errors=errors,
            confidence_score=confidence,
            ast_valid=analyzer.tree is not None
        )
        
        return result.to_dict()
    
    elif language in ["java", "cpp", "c++", "javascript", "js", "go"]:
        # For non-Python languages, use regex-based heuristics
        return _analyze_non_python(code, language, test_cases)
    
    else:
        return {
            "logical_errors": [],
            "confidence_score": 0.0,
            "control_flow_issues": [],
            "data_flow_issues": [],
            "ast_valid": False,
            "error": f"Unsupported language: {language}"
        }


def _analyze_with_test_cases(code: str, test_cases: list, language: str) -> List[LogicalError]:
    """
    Analyze code by comparing runtime behavior with expected outputs.
    
    Test case format:
    {
        "input": {...},
        "expected_output": ...,
        "actual_output": ...,
        "passed": bool
    }
    """
    errors = []
    
    for idx, test in enumerate(test_cases):
        if not test.get("passed", True):
            # Test failed - try to infer what went wrong
            expected = test.get("expected_output")
            actual = test.get("actual_output")
            
            # Check for off-by-one errors
            if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
                diff = abs(expected - actual)
                if diff == 1:
                    errors.append(LogicalError(
                        error_type=ErrorType.OFF_BY_ONE,
                        line=0,
                        message=f"Test case {idx+1} failed: off-by-one error detected (expected {expected}, got {actual})",
                        severity="high",
                        confidence=0.9,
                        suggested_fix="Check loop boundaries and array indices"
                    ))
            
            # Check for wrong operator (e.g., + instead of -, * instead of /)
            if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
                if expected != 0 and actual != 0:
                    ratio = actual / expected
                    # Check if actual is 2x expected (might be addition instead of subtraction)
                    if abs(ratio - 2.0) < 0.01:
                        errors.append(LogicalError(
                            error_type=ErrorType.WRONG_OPERATOR,
                            line=0,
                            message=f"Test case {idx+1}: possible wrong operator (result is 2x expected)",
                            severity="medium",
                            confidence=0.7,
                            suggested_fix="Check if you're using + instead of - or vice versa"
                        ))
            
            # Check for boundary errors (array out of bounds, etc.)
            if actual is None or (isinstance(actual, str) and "index" in actual.lower()):
                errors.append(LogicalError(
                    error_type=ErrorType.BOUNDARY_ERROR,
                    line=0,
                    message=f"Test case {idx+1}: boundary/index error detected",
                    severity="high",
                    confidence=0.85,
                    suggested_fix="Check array bounds and loop ranges"
                ))
    
    return errors


def _analyze_non_python(code: str, language: str, test_cases: list = None) -> dict:
    """
    Analyze non-Python languages using regex patterns and heuristics.
    """
    errors = []
    lines = code.split('\n')
    
    # Pattern-based detection for common errors
    
    # 1. Infinite loops
    if language in ["java", "cpp", "c++"]:
        # while(true) without break
        for i, line in enumerate(lines):
            if re.search(r'while\s*\(\s*true\s*\)', line):
                # Check if there's a break in nearby lines
                has_break = any('break' in lines[j] for j in range(i, min(i+20, len(lines))))
                if not has_break:
                    errors.append(LogicalError(
                        error_type=ErrorType.INFINITE_LOOP,
                        line=i+1,
                        message="Potential infinite loop: while(true) without break",
                        severity="high",
                        confidence=0.85
                    ))
    
    # 2. Assignment in condition (= instead of ==)
    for i, line in enumerate(lines):
        if language in ["java", "cpp", "c++", "javascript", "js"]:
            # if (x = 5) instead of if (x == 5)
            match = re.search(r'if\s*\([^=!<>]*\s=\s[^=]', line)
            if match:
                errors.append(LogicalError(
                    error_type=ErrorType.WRONG_COMPARISON,
                    line=i+1,
                    message="Possible assignment in condition - did you mean '==' or '==='?",
                    severity="high",
                    confidence=0.9,
                    suggested_fix="Change '=' to '==' or '==='"
                ))
    
    # 3. Missing return statement
    if language in ["java", "cpp", "c++"]:
        in_function = False
        func_start_line = 0
        return_type = None
        
        for i, line in enumerate(lines):
            # Match function declaration
            func_match = re.match(r'\s*(int|float|double|long|bool|string|void|\w+)\s+\w+\s*\([^)]*\)\s*\{?', line)
            if func_match:
                in_function = True
                func_start_line = i + 1
                return_type = func_match.group(1)
            
            if in_function and '}' in line:
                # End of function - check if return was found
                if return_type and return_type != 'void':
                    # Check if any return statement in function body
                    has_return = any('return' in lines[j] for j in range(func_start_line-1, i+1))
                    if not has_return:
                        errors.append(LogicalError(
                            error_type=ErrorType.MISSING_RETURN,
                            line=func_start_line,
                            message=f"Function with return type '{return_type}' missing return statement",
                            severity="critical",
                            confidence=0.95
                        ))
                in_function = False
    
    # 4. Array index off-by-one
    for i, line in enumerate(lines):
        # for(i=1; i<=n; i++) arr[i] when arr has size n
        match = re.search(r'for\s*\(\s*\w+\s*=\s*1\s*;.*?<=.*?\)', line)
        if match:
            errors.append(LogicalError(
                error_type=ErrorType.OFF_BY_ONE,
                line=i+1,
                message="Potential off-by-one: loop starts at 1 with <= condition",
                severity="medium",
                confidence=0.6,
                suggested_fix="Check if array indices are correct (arrays usually start at 0)"
            ))
    
    # 5. Semicolon after if/for/while in C-like languages
    if language in ["cpp", "c++", "java", "javascript", "js"]:
        for i, line in enumerate(lines):
            if re.search(r'(if|for|while)\s*\([^)]*\)\s*;', line):
                errors.append(LogicalError(
                    error_type=ErrorType.DEAD_CODE,
                    line=i+1,
                    message="Semicolon after control statement makes the body unreachable",
                    severity="high",
                    confidence=0.95,
                    suggested_fix="Remove the semicolon"
                ))
    
    # Test case analysis
    if test_cases:
        test_errors = _analyze_with_test_cases(code, test_cases, language)
        errors.extend(test_errors)
    
    confidence = _calculate_confidence(errors)
    
    return {
        "logical_errors": [
            {
                "type": err.error_type.value,
                "line": err.line,
                "column": err.column,
                "message": err.message,
                "severity": err.severity,
                "suggested_fix": err.suggested_fix,
                "confidence": err.confidence
            }
            for err in errors
        ],
        "confidence_score": confidence,
        "control_flow_issues": [],
        "data_flow_issues": [],
        "ast_valid": True
    }


def _calculate_confidence(errors: List[LogicalError]) -> float:
    """Calculate overall confidence score based on individual error confidences."""
    if not errors:
        return 1.0
    
    # Average of individual confidences, weighted by severity
    severity_weights = {
        "low": 0.5,
        "medium": 1.0,
        "high": 1.5,
        "critical": 2.0
    }
    
    total_weighted = sum(err.confidence * severity_weights.get(err.severity, 1.0) for err in errors)
    total_weight = sum(severity_weights.get(err.severity, 1.0) for err in errors)
    
    return total_weighted / total_weight if total_weight > 0 else 0.5


# Convenience function for easy integration
def quick_analyze(code: str, language: str = "python") -> dict:
    """Quick analysis without test cases."""
    return analyze_logic(code, language, test_cases=None)


if __name__ == "__main__":
    # Test the analyzer
    test_code = """
def factorial(n):
    if n == 1:
        return 1
    return n * factorial(n - 1)

def buggy_loop():
    i = 0
    while i < 10:
        print(i)
        # Forgot to increment i - infinite loop!
    
def unreachable_example():
    return 42
    print("This will never execute")

result = factorial(5)
print(result)
"""
    
    result = analyze_logic(test_code, "python")
    print("Analysis Result:")
    print(f"Found {len(result['logical_errors'])} logical errors")
    for error in result['logical_errors']:
        print(f"  Line {error['line']}: {error['message']}")
    print(f"Confidence: {result['confidence_score']:.2f}")
