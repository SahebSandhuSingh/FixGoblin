"""
🦎 FixGoblin - Test Case Validator
====================================
Executes code against test cases and compares outputs to trigger logical analysis.
"""

import json
import subprocess
import tempfile
import os
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import re


@dataclass
class TestCase:
    """Represents a single test case."""
    test_id: int
    description: str
    input_data: Any
    expected_output: Any
    timeout: int = 5
    
    def to_dict(self) -> dict:
        return {
            "test_id": self.test_id,
            "description": self.description,
            "input": self.input_data,
            "expected_output": self.expected_output
        }


@dataclass
class TestResult:
    """Result of running a test case."""
    test_case: TestCase
    passed: bool
    actual_output: Any
    execution_time: float
    error_message: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "test_id": self.test_case.test_id,
            "description": self.test_case.description,
            "input": self.test_case.input_data,
            "expected_output": self.test_case.expected_output,
            "actual_output": self.actual_output,
            "passed": self.passed,
            "execution_time": self.execution_time,
            "error_message": self.error_message
        }


class TestCaseValidator:
    """Validates code against test cases and triggers logical analysis."""
    
    def __init__(self, language: str = "python"):
        self.language = language.lower()
        self.test_results: List[TestResult] = []
    
    def run_tests(self, code: str, test_cases: List[TestCase]) -> List[TestResult]:
        """
        Run code against all test cases.
        
        Args:
            code: Source code to test
            test_cases: List of test cases
            
        Returns:
            List of test results
        """
        self.test_results = []
        
        for test_case in test_cases:
            result = self._run_single_test(code, test_case)
            self.test_results.append(result)
        
        return self.test_results
    
    def _run_single_test(self, code: str, test_case: TestCase) -> TestResult:
        """Run a single test case."""
        import time
        
        start_time = time.time()
        
        try:
            if self.language == "python":
                actual_output, error = self._run_python_test(code, test_case)
            elif self.language in ["java"]:
                actual_output, error = self._run_java_test(code, test_case)
            elif self.language in ["cpp", "c++"]:
                actual_output, error = self._run_cpp_test(code, test_case)
            elif self.language in ["javascript", "js"]:
                actual_output, error = self._run_js_test(code, test_case)
            else:
                actual_output = None
                error = f"Unsupported language: {self.language}"
            
            execution_time = time.time() - start_time
            
            # Compare outputs
            passed = self._compare_outputs(test_case.expected_output, actual_output)
            
            return TestResult(
                test_case=test_case,
                passed=passed,
                actual_output=actual_output,
                execution_time=execution_time,
                error_message=error
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return TestResult(
                test_case=test_case,
                passed=False,
                actual_output=None,
                execution_time=execution_time,
                error_message=str(e)
            )
    
    def _run_python_test(self, code: str, test_case: TestCase) -> Tuple[Any, Optional[str]]:
        """Run Python code with test input."""
        # Create a test wrapper
        test_wrapper = f"""
{code}

# Test execution
import json
test_input = {repr(test_case.input_data)}

# Try to call the main function with test input
try:
    if callable(globals().get('main')):
        result = main(test_input)
    elif callable(globals().get('solution')):
        result = solution(test_input)
    elif callable(globals().get('solve')):
        result = solve(test_input)
    else:
        # Look for any function that's not a builtin
        user_functions = [name for name in dir() if callable(globals()[name]) and not name.startswith('_')]
        if user_functions:
            result = globals()[user_functions[0]](test_input)
        else:
            result = None
    
    print("__RESULT__:", json.dumps(result))
except Exception as e:
    print("__ERROR__:", str(e))
"""
        
        # Write to temp file and execute
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_wrapper)
            temp_file = f.name
        
        try:
            result = subprocess.run(
                ['python3', temp_file],
                capture_output=True,
                text=True,
                timeout=test_case.timeout
            )
            
            output = result.stdout
            error = result.stderr
            
            # Parse result
            if "__RESULT__:" in output:
                result_line = [line for line in output.split('\n') if "__RESULT__:" in line][0]
                result_str = result_line.split("__RESULT__:")[1].strip()
                actual_output = json.loads(result_str)
                return actual_output, None
            elif "__ERROR__:" in output:
                error_line = [line for line in output.split('\n') if "__ERROR__:" in line][0]
                error_msg = error_line.split("__ERROR__:")[1].strip()
                return None, error_msg
            else:
                return None, error if error else "No output"
                
        except subprocess.TimeoutExpired:
            return None, f"Timeout ({test_case.timeout}s exceeded)"
        except Exception as e:
            return None, str(e)
        finally:
            os.unlink(temp_file)
    
    def _run_java_test(self, code: str, test_case: TestCase) -> Tuple[Any, Optional[str]]:
        """Run Java code with test input."""
        # For Java, we need to compile and run
        # This is a simplified version - production would need more robust handling
        return None, "Java test execution not yet implemented"
    
    def _run_cpp_test(self, code: str, test_case: TestCase) -> Tuple[Any, Optional[str]]:
        """Run C++ code with test input."""
        return None, "C++ test execution not yet implemented"
    
    def _run_js_test(self, code: str, test_case: TestCase) -> Tuple[Any, Optional[str]]:
        """Run JavaScript code with test input."""
        test_wrapper = f"""
{code}

// Test execution
const testInput = {json.dumps(test_case.input_data)};

try {{
    let result;
    if (typeof main === 'function') {{
        result = main(testInput);
    }} else if (typeof solution === 'function') {{
        result = solution(testInput);
    }} else if (typeof solve === 'function') {{
        result = solve(testInput);
    }}
    
    console.log('__RESULT__:', JSON.stringify(result));
}} catch (e) {{
    console.log('__ERROR__:', e.message);
}}
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(test_wrapper)
            temp_file = f.name
        
        try:
            result = subprocess.run(
                ['node', temp_file],
                capture_output=True,
                text=True,
                timeout=test_case.timeout
            )
            
            output = result.stdout
            
            if "__RESULT__:" in output:
                result_line = [line for line in output.split('\n') if "__RESULT__:" in line][0]
                result_str = result_line.split("__RESULT__:")[1].strip()
                actual_output = json.loads(result_str)
                return actual_output, None
            elif "__ERROR__:" in output:
                error_line = [line for line in output.split('\n') if "__ERROR__:" in line][0]
                error_msg = error_line.split("__ERROR__:")[1].strip()
                return None, error_msg
            else:
                return None, "No output"
                
        except subprocess.TimeoutExpired:
            return None, f"Timeout ({test_case.timeout}s exceeded)"
        except Exception as e:
            return None, str(e)
        finally:
            os.unlink(temp_file)
    
    def _compare_outputs(self, expected: Any, actual: Any) -> bool:
        """Compare expected and actual outputs."""
        if expected is None or actual is None:
            return expected == actual
        
        # Handle numeric comparisons with tolerance
        if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
            return abs(expected - actual) < 1e-6
        
        # Handle list/array comparisons
        if isinstance(expected, (list, tuple)) and isinstance(actual, (list, tuple)):
            if len(expected) != len(actual):
                return False
            return all(self._compare_outputs(e, a) for e, a in zip(expected, actual))
        
        # Handle dict comparisons
        if isinstance(expected, dict) and isinstance(actual, dict):
            if set(expected.keys()) != set(actual.keys()):
                return False
            return all(self._compare_outputs(expected[k], actual[k]) for k in expected.keys())
        
        # Default comparison
        return expected == actual
    
    def get_failed_tests(self) -> List[TestResult]:
        """Get list of failed test results."""
        return [r for r in self.test_results if not r.passed]
    
    def get_pass_rate(self) -> float:
        """Calculate test pass rate."""
        if not self.test_results:
            return 0.0
        passed = sum(1 for r in self.test_results if r.passed)
        return passed / len(self.test_results)
    
    def format_results(self) -> str:
        """Format test results as a readable string."""
        if not self.test_results:
            return "No tests run"
        
        lines = []
        lines.append(f"\n{'='*60}")
        lines.append(f"TEST RESULTS - {len(self.test_results)} tests")
        lines.append(f"{'='*60}")
        
        for result in self.test_results:
            status = "✅ PASS" if result.passed else "❌ FAIL"
            lines.append(f"\n{status} - Test #{result.test_case.test_id}: {result.test_case.description}")
            lines.append(f"  Input: {result.test_case.input_data}")
            lines.append(f"  Expected: {result.test_case.expected_output}")
            lines.append(f"  Actual: {result.actual_output}")
            lines.append(f"  Time: {result.execution_time:.3f}s")
            if result.error_message:
                lines.append(f"  Error: {result.error_message}")
        
        pass_rate = self.get_pass_rate() * 100
        lines.append(f"\n{'='*60}")
        lines.append(f"Pass Rate: {pass_rate:.1f}% ({sum(1 for r in self.test_results if r.passed)}/{len(self.test_results)})")
        lines.append(f"{'='*60}\n")
        
        return '\n'.join(lines)


def parse_test_cases_from_comments(code: str) -> List[TestCase]:
    """
    Parse test cases from code comments.
    
    Expected format:
    # TEST: description
    # INPUT: {"key": "value"} or [1, 2, 3]
    # EXPECTED: output
    """
    test_cases = []
    lines = code.split('\n')
    
    current_test = {}
    test_id = 1
    
    for line in lines:
        line = line.strip()
        
        if line.startswith('# TEST:') or line.startswith('// TEST:'):
            if current_test:
                # Save previous test
                if 'description' in current_test and 'input' in current_test and 'expected' in current_test:
                    test_cases.append(TestCase(
                        test_id=test_id,
                        description=current_test['description'],
                        input_data=current_test['input'],
                        expected_output=current_test['expected']
                    ))
                    test_id += 1
            
            current_test = {'description': line.split('TEST:')[1].strip()}
        
        elif line.startswith('# INPUT:') or line.startswith('// INPUT:'):
            try:
                input_str = line.split('INPUT:')[1].strip()
                current_test['input'] = json.loads(input_str)
            except:
                current_test['input'] = input_str
        
        elif line.startswith('# EXPECTED:') or line.startswith('// EXPECTED:'):
            try:
                expected_str = line.split('EXPECTED:')[1].strip()
                current_test['expected'] = json.loads(expected_str)
            except:
                current_test['expected'] = expected_str
    
    # Don't forget the last test
    if current_test and 'description' in current_test and 'input' in current_test and 'expected' in current_test:
        test_cases.append(TestCase(
            test_id=test_id,
            description=current_test['description'],
            input_data=current_test['input'],
            expected_output=current_test['expected']
        ))
    
    return test_cases


if __name__ == "__main__":
    # Test the validator
    code = """
def add(x):
    return x + 1

def multiply(x):
    return x * 2
"""
    
    test_cases = [
        TestCase(1, "Add 5", 5, 6),
        TestCase(2, "Add 10", 10, 11),
        TestCase(3, "Multiply 3", 3, 6),
    ]
    
    validator = TestCaseValidator("python")
    results = validator.run_tests(code, test_cases)
    print(validator.format_results())
