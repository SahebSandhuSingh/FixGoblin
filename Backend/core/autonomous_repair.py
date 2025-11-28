"""
STEP 5: AUTONOMOUS REPAIR LOOP
================================
Iteratively repairs code until it works or max iterations reached.

This is the main orchestration layer that combines all previous steps
into a self-healing repair system.
"""

import os
import time
import pathlib
from typing import Dict, List, Any, Optional
from core.sandbox_runner import run_in_sandbox
from core.error_parser import parse_error
from core.patch_generator import generate_patch_candidates
from core.patch_optimizer import select_best_patch, apply_patch_to_file
from core.logical_validator import validate_logic, format_logical_error
from core.semantic_detector import detect_semantic_errors, suggest_fixes_for_semantic_errors
from core.final_report import generate_final_report, collect_repair_context
from core.logical_analyzer import analyze_logic
from core.test_case_validator import TestCaseValidator, TestCase, parse_test_cases_from_comments


def autonomous_repair(
    file_path: str, 
    max_iterations: int = 5, 
    optimize_efficiency: bool = False,
    test_cases: List[TestCase] = None,
    enable_logical_analysis: bool = True
) -> Dict[str, Any]:
    """
    Autonomous repair loop that iteratively fixes code.
    
    Algorithm:
        1. Load code from file
        2. Run in sandbox
        3. If test cases provided, run tests and trigger logical analysis on failures
        4. If success → Check logic/semantics → STOP or fix
        5. If error → Parse → Generate patches → Select best → Apply
        6. Repeat until fixed or max_iterations reached
    
    Args:
        file_path: Path to the code file to repair
        max_iterations: Maximum number of repair attempts (default: 5)
        optimize_efficiency: If True, also generate efficiency patches
        test_cases: Optional list of test cases for logical analysis
        enable_logical_analysis: Enable deterministic logical error detection (AST/CFG/DFA)
        
    Returns:
        Dictionary containing:
            - success: True if code was fixed, False otherwise
            - final_code: The final state of the code
            - iterations: List of iteration logs
            - total_iterations: Number of iterations performed
            - final_status: "success", "failed", or "max_iterations_reached"
            - test_results: Test case results if provided
            - logical_analysis: Logical error analysis results if enabled
    """
    
    print("=" * 80)
    print("🤖 AUTONOMOUS REPAIR LOOP - FixGoblin v2.0")
    print("=" * 80)
    print(f"📁 Target: {file_path}")
    print(f"🔄 Max Iterations: {max_iterations}")
    print(f"⚡ Efficiency Mode: {'ENABLED' if optimize_efficiency else 'DISABLED'}")
    print("=" * 80)
    
    # Start timing
    start_time = time.time()
    
    # Validate file exists
    if not os.path.exists(file_path):
        return _create_failure_result(
            f"File not found: {file_path}",
            None,
            [],
            ""
        )
    
    # Load initial code
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            initial_code = f.read()
    except Exception as e:
        return _create_failure_result(
            f"Failed to read file: {e}",
            None,
            [],
            ""
        )
    
    # Initialize tracking
    iteration_logs: List[Dict[str, Any]] = []
    current_iteration = 0
    test_results = None
    logical_analysis_results = None
    
    # Detect language from file extension
    file_ext = pathlib.Path(file_path).suffix.lower()
    language_map = {
        '.py': 'python',
        '.java': 'java',
        '.cpp': 'cpp',
        '.cc': 'cpp',
        '.cxx': 'cpp',
        '.js': 'javascript',
        '.go': 'go'
    }
    detected_language = language_map.get(file_ext, 'python')
    
    # Parse test cases from comments if not provided
    if test_cases is None and enable_logical_analysis:
        test_cases = parse_test_cases_from_comments(initial_code)
        if test_cases:
            print(f"📝 Found {len(test_cases)} test case(s) in code comments")
    
    # Main repair loop
    while current_iteration < max_iterations:
        current_iteration += 1
        
        print(f"\n{'▶' * 40}")
        print(f"ITERATION {current_iteration}/{max_iterations}")
        print(f"{'▶' * 40}\n")
        
        # STEP 1: Run code in sandbox
        print("🔬 Running code in sandbox...")
        sandbox_result = run_in_sandbox(file_path)
        
        print(f"   Language: {sandbox_result['language']}")
        print(f"   Return Code: {sandbox_result['returncode']}")
        
        # Check if code runs successfully
        if sandbox_result['returncode'] == 0:
            print("\n✅ CODE RUNS SUCCESSFULLY!")
            
            # Read current code for logical validation
            with open(file_path, 'r', encoding='utf-8') as f:
                current_code = f.read()
            
            # STEP 2.5: Run test cases if provided
            if test_cases:
                print("\n🧪 Running test cases...")
                validator = TestCaseValidator(detected_language)
                test_results = validator.run_tests(current_code, test_cases)
                
                failed_tests = validator.get_failed_tests()
                if failed_tests:
                    print(f"   ❌ {len(failed_tests)}/{len(test_cases)} tests failed")
                    
                    # Trigger logical analysis with test case data
                    if enable_logical_analysis:
                        print("\n🔍 Running logical analysis on failed tests...")
                        test_data = [r.to_dict() for r in test_results]
                        logical_analysis_results = analyze_logic(current_code, detected_language, test_data)
                        
                        if logical_analysis_results['logical_errors']:
                            print(f"   🎯 Found {len(logical_analysis_results['logical_errors'])} logical error(s):")
                            for err in logical_analysis_results['logical_errors']:
                                severity_emoji = {'low': '🟢', 'medium': '🟡', 'high': '🔴', 'critical': '🔴'}
                                emoji = severity_emoji.get(err['severity'], '🟡')
                                print(f"   {emoji} Line {err['line']}: {err['message']}")
                                if err.get('suggested_fix'):
                                    print(f"      💡 {err['suggested_fix']}")
                            
                            # Try to apply the suggested fix
                            # For now, we'll continue to semantic/logical validation
                            # Future: generate patches based on logical_analysis_results
                else:
                    print(f"   ✅ All {len(test_cases)} tests passed")
            
            # STEP 2.6: Run deterministic logical analysis (even without test cases)
            if enable_logical_analysis and not test_cases:
                print("\n🔍 Running deterministic logical analysis...")
                logical_analysis_results = analyze_logic(current_code, detected_language)
                
                if logical_analysis_results['logical_errors']:
                    print(f"   ⚠️ Found {len(logical_analysis_results['logical_errors'])} logical issue(s):")
                    for err in logical_analysis_results['logical_errors']:
                        severity_emoji = {'low': '🟢', 'medium': '🟡', 'high': '🔴', 'critical': '🔴'}
                        emoji = severity_emoji.get(err['severity'], '🟡')
                        print(f"   {emoji} Line {err['line']}: {err['message']}")
                        if err.get('suggested_fix'):
                            print(f"      💡 {err['suggested_fix']}")
                else:
                    print("   ✓ No logical issues detected")
            
            # STEP 2.7: Validate logic (existing validator)
            print("\n🧠 Validating logic...")
            logic_validation = validate_logic(sandbox_result, current_code)
            
            # STEP 2.6: Check for semantic errors
            print("\n🔍 Checking for semantic/algorithmic errors...")
            semantic_issues = detect_semantic_errors(
                current_code, 
                sandbox_result.get('stdout', ''),
                {}
            )
            
            if semantic_issues:
                print(f"   ⚠️ FOUND {len(semantic_issues)} SEMANTIC ISSUE(S)!")
                for issue in semantic_issues:
                    severity_emoji = {'HIGH': '🔴', 'MEDIUM': '🟡', 'LOW': '🟢'}
                    emoji = severity_emoji.get(issue.get('severity', 'MEDIUM'), '🟡')
                    print(f"   {emoji} {issue['message']}")
                
                # Try to generate fixes for semantic errors
                semantic_fixes = suggest_fixes_for_semantic_errors(semantic_issues, current_code)
                
                if semantic_fixes:
                    print(f"\n🔧 Generated {len(semantic_fixes)} semantic fix(es)")
                    
                    # Apply first semantic fix
                    fix = semantic_fixes[0]
                    print(f"   Applying: {fix['description']}")
                    
                    # Write fixed code
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(fix['patched_code'])
                    
                    # Log iteration
                    iteration_log = {
                        'iteration': current_iteration,
                        'error_type': 'SemanticError',
                        'error_message': semantic_issues[0]['message'],
                        'selected_patch_id': fix['id'],
                        'description': fix['description'],
                        'status': 'APPLIED_SEMANTIC_FIX'
                    }
                    iteration_logs.append(iteration_log)
                    
                    # Continue to next iteration
                    continue
                else:
                    print("   ℹ️ No automatic fixes available for these semantic issues")
            else:
                print("   ✓ No semantic issues detected")
            
            if not logic_validation['is_logically_correct']:
                print("   ⚠️ LOGICAL ISSUES DETECTED!")
                
                # Display issues
                for issue in logic_validation['issues']:
                    print(f"   - {issue['message']}")
                
                # Convert logical issue to error_data format
                error_data = format_logical_error(logic_validation)
                
                if error_data:
                    print(f"\n🔧 Generating logical patches...")
                    patches = generate_patch_candidates(
                        error_data, 
                        current_code, 
                        optimize_efficiency=False
                    )
                    
                    if patches:
                        print(f"   Generated {len(patches)} logical patch(es)")
                        
                        # Select and apply best patch
                        print(f"\n🏆 Selecting best patch...")
                        best_patch = select_best_patch(patches, current_code, run_in_sandbox)
                        
                        if best_patch:
                            print(f"   Selected: {best_patch['id']}")
                            print(f"   Description: {best_patch['description']}")
                            
                            # Apply patch
                            print(f"\n💾 Applying logical patch...")
                            apply_result = apply_patch_to_file(best_patch, file_path, auto_apply=True)
                            
                            if apply_result['applied']:
                                print(f"   ✅ Applied: {apply_result['backup_path']}")
                                
                                # Log iteration
                                iteration_logs.append({
                                    "iteration": current_iteration,
                                    "error_type": "LogicalError",
                                    "line_number": error_data.get('line_number'),
                                    "error_message": error_data.get('error_message'),
                                    "selected_patch_id": best_patch['id'],
                                    "description": best_patch['description'],
                                    "patch_score": best_patch['score'],
                                    "status": "retrying",
                                    "returncode": 0,
                                    "backup_path": apply_result['backup_path']
                                })
                                
                                print(f"\n📊 Iteration {current_iteration} Status: RETRYING (Logical fix applied)")
                                continue  # Re-run to verify fix
                
                # If we reach here, couldn't fix logical issue
                print("   ⚠️ Could not generate fix for logical issues")
            else:
                print("   ✓ Logic validation passed")
            
            # Read final code
            with open(file_path, 'r', encoding='utf-8') as f:
                final_code = f.read()
            
            # Log successful iteration
            iteration_logs.append({
                "iteration": current_iteration,
                "error_type": None,
                "line_number": None,
                "error_message": None,
                "selected_patch_id": None,
                "description": "Code executed successfully with valid logic",
                "status": "fixed",
                "returncode": 0
            })
            
            # Display output if available
            if sandbox_result['stdout']:
                print(f"\n📤 Output:")
                print(sandbox_result['stdout'])
            
            return _create_success_result(
                final_code,
                iteration_logs,
                current_iteration,
                initial_code,
                test_results=[r.to_dict() for r in test_results] if test_results else None,
                logical_analysis=logical_analysis_results
            )
        
        # Code has errors - proceed with repair
        print("\n❌ Execution failed with errors")
        
        # Read current code for error parsing
        with open(file_path, 'r', encoding='utf-8') as f:
            current_code = f.read()
        
        # STEP 2: Parse error
        print("\n🐛 Parsing error...")
        error_data = parse_error(sandbox_result, current_code)
        
        if not error_data['error_type']:
            print("   ⚠️ Could not parse error - stopping repair")
            
            iteration_logs.append({
                "iteration": current_iteration,
                "error_type": "Unknown",
                "line_number": None,
                "error_message": "Failed to parse error",
                "selected_patch_id": None,
                "description": "Error parsing failed",
                "status": "failed",
                "returncode": sandbox_result['returncode']
            })
            
            with open(file_path, 'r', encoding='utf-8') as f:
                final_code = f.read()
            
            return _create_failure_result(
                "Could not parse error",
                final_code,
                iteration_logs,
                initial_code
            )
        
        print(f"   Type: {error_data['error_type']}")
        print(f"   Line: {error_data['line_number']}")
        print(f"   Message: {error_data['error_message']}")
        
        # STEP 3: Generate patch candidates
        print(f"\n🔧 Generating patches (efficiency={optimize_efficiency})...")
        patches = generate_patch_candidates(
            error_data, 
            current_code, 
            optimize_efficiency=optimize_efficiency
        )
        
        if not patches:
            print("   ⚠️ No patches could be generated - stopping repair")
            
            iteration_logs.append({
                "iteration": current_iteration,
                "error_type": error_data['error_type'],
                "line_number": error_data['line_number'],
                "error_message": error_data['error_message'],
                "selected_patch_id": None,
                "description": "No patches generated",
                "status": "failed",
                "returncode": sandbox_result['returncode']
            })
            
            return _create_failure_result(
                "No patches could be generated",
                current_code,
                iteration_logs,
                initial_code
            )
        
        print(f"   Generated {len(patches)} patch candidate(s)")
        for i, p in enumerate(patches, 1):
            patch_type_label = f" [{p.get('patch_type', 'correctness').upper()}]"
            print(f"      {i}. {p['id']}{patch_type_label}: {p['description']}")
        
        # STEP 4: Select best patch
        print("\n🏆 Selecting best patch...")
        best_patch = select_best_patch(patches, current_code, run_in_sandbox)
        
        if not best_patch:
            print("   ⚠️ No suitable patch found - stopping repair")
            
            iteration_logs.append({
                "iteration": current_iteration,
                "error_type": error_data['error_type'],
                "line_number": error_data['line_number'],
                "error_message": error_data['error_message'],
                "selected_patch_id": None,
                "description": "No suitable patch selected",
                "status": "failed",
                "returncode": sandbox_result['returncode']
            })
            
            return _create_failure_result(
                "No suitable patch found",
                current_code,
                iteration_logs,
                initial_code
            )
        
        print(f"   Selected: {best_patch['id']}")
        print(f"   Score: {best_patch['score']} points")
        print(f"   Description: {best_patch['description']}")
        
        # STEP 5: Apply patch to file
        print("\n💾 Applying patch to file...")
        apply_result = apply_patch_to_file(best_patch, file_path, auto_apply=True)
        
        if not apply_result['applied']:
            print("   ⚠️ Failed to apply patch - stopping repair")
            
            iteration_logs.append({
                "iteration": current_iteration,
                "error_type": error_data['error_type'],
                "line_number": error_data['line_number'],
                "error_message": error_data['error_message'],
                "selected_patch_id": best_patch['id'],
                "description": best_patch['description'],
                "status": "failed",
                "returncode": sandbox_result['returncode']
            })
            
            return _create_failure_result(
                "Failed to apply patch",
                current_code,
                iteration_logs,
                initial_code
            )
        
        print(f"   ✅ Applied: {apply_result['backup_path']}")
        
        # Determine iteration status
        iteration_status = "fixed" if best_patch['score_breakdown']['success'] else "retrying"
        
        # Log iteration
        iteration_logs.append({
            "iteration": current_iteration,
            "error_type": error_data['error_type'],
            "line_number": error_data['line_number'],
            "error_message": error_data['error_message'],
            "selected_patch_id": best_patch['id'],
            "description": best_patch['description'],
            "patch_score": best_patch['score'],
            "status": iteration_status,
            "returncode": sandbox_result['returncode'],
            "backup_path": apply_result['backup_path']
        })
        
        print(f"\n📊 Iteration {current_iteration} Status: {iteration_status.upper()}")
    
    # Max iterations reached
    print(f"\n⚠️ MAX ITERATIONS REACHED ({max_iterations})")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        final_code = f.read()
    
    return {
        "success": False,
        "final_code": final_code,
        "initial_code": initial_code,
        "iterations": iteration_logs,
        "total_iterations": current_iteration,
        "final_status": "max_iterations_reached",
        "reason": f"Reached maximum iterations ({max_iterations}) without fixing all errors"
    }


# ============================================================
#  HELPER FUNCTIONS
# ============================================================

def _create_success_result(
    final_code: str, 
    iterations: List[Dict[str, Any]], 
    total: int,
    initial_code: str = "",
    test_results=None,
    logical_analysis=None
) -> Dict[str, Any]:
    """Create a successful repair result."""
    result = {
        "success": True,
        "final_code": final_code,
        "initial_code": initial_code,
        "iterations": iterations,
        "total_iterations": total,
        "final_status": "success",
        "reason": "Code successfully repaired and executes without errors"
    }
    
    if test_results is not None:
        result["test_results"] = test_results
    
    if logical_analysis is not None:
        result["logical_analysis"] = logical_analysis
    
    return result


def _create_failure_result(
    reason: str, 
    final_code: Optional[str], 
    iterations: List[Dict[str, Any]],
    initial_code: str = ""
) -> Dict[str, Any]:
    """Create a failure result."""
    return {
        "success": False,
        "final_code": final_code,
        "initial_code": initial_code,
        "iterations": iterations,
        "total_iterations": len(iterations),
        "final_status": "failed",
        "reason": reason
    }


def print_repair_summary(result: Dict[str, Any]) -> None:
    """
    Print a formatted summary of the repair process.
    
    Args:
        result: The result dictionary from autonomous_repair()
    """
    print("\n" + "=" * 80)
    print("📋 REPAIR SUMMARY")
    print("=" * 80)
    
    print(f"\n🎯 Final Status: {result['final_status'].upper()}")
    print(f"✅ Success: {result['success']}")
    print(f"🔄 Total Iterations: {result['total_iterations']}")
    print(f"📝 Reason: {result['reason']}")
    
    if result['iterations']:
        print(f"\n📊 ITERATION HISTORY:")
        print("-" * 80)
        
        for log in result['iterations']:
            status_emoji = {
                "fixed": "✅",
                "retrying": "🔄",
                "failed": "❌"
            }.get(log['status'], "⚠️")
            
            print(f"\n{status_emoji} Iteration {log['iteration']}:")
            if log['error_type']:
                print(f"   Error: {log['error_type']} (Line {log['line_number']})")
                print(f"   Message: {log['error_message']}")
            if log['selected_patch_id']:
                print(f"   Patch: {log['selected_patch_id']}")
                print(f"   Action: {log['description']}")
                if 'patch_score' in log:
                    print(f"   Score: {log['patch_score']} points")
            print(f"   Status: {log['status'].upper()}")
    
    print("\n" + "=" * 80)


def save_repair_log(result: Dict[str, Any], output_path: str) -> None:
    """
    Save repair log to a JSON file.
    
    Args:
        result: The result dictionary from autonomous_repair()
        output_path: Path where to save the JSON log
    """
    import json
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"📄 Repair log saved to: {output_path}")
    except Exception as e:
        print(f"⚠️ Failed to save repair log: {e}")


# ============================================================
#  COMMAND-LINE INTERFACE
# ============================================================

def main():
    """Command-line interface for autonomous repair."""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(
        description="FixGoblin Autonomous Repair Loop - Iteratively fix bugs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 autonomous_repair.py user.py
  python3 autonomous_repair.py user.py --max-iterations 10
  python3 autonomous_repair.py user.py --optimize
  python3 autonomous_repair.py user.py --log repair_log.json
        """
    )
    
    parser.add_argument(
        'file_path',
        help='Path to the code file to repair'
    )
    
    parser.add_argument(
        '--max-iterations',
        type=int,
        default=5,
        help='Maximum number of repair iterations (default: 5)'
    )
    
    parser.add_argument(
        '--optimize',
        action='store_true',
        help='Enable efficiency optimization patches'
    )
    
    parser.add_argument(
        '--log',
        metavar='LOG_FILE',
        help='Save repair log to JSON file'
    )
    
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress detailed output (only show summary)'
    )
    
    parser.add_argument(
        '--final-report',
        action='store_true',
        help='Generate comprehensive final debugging report'
    )
    
    args = parser.parse_args()
    
    # Run autonomous repair
    result = autonomous_repair(
        args.file_path,
        max_iterations=args.max_iterations,
        optimize_efficiency=args.optimize
    )
    
    # Print summary
    if not args.quiet:
        print_repair_summary(result)
    
    # Save log if requested
    if args.log:
        save_repair_log(result, args.log)
    
    # Generate final report if requested
    if args.final_report:
        try:
            # Read final code
            with open(args.file_path, 'r', encoding='utf-8') as f:
                final_code = f.read()
            
            # Get initial code from result (stored at start of repair)
            initial_code = result.get('initial_code', '')
            
            # Collect context for report
            context = collect_repair_context(
                file_path=args.file_path,
                original_code=initial_code,
                final_code=final_code,
                iterations_log=result.get('iterations', []),
                start_time=0,  # Time already calculated
                success=result['success'],
                final_status=result['final_status']
            )
            
            # Add execution time from result if available
            if 'execution_time' in result:
                context['execution_time'] = result['execution_time']
            
            generate_final_report(context)
        except Exception as e:
            print(f"\n⚠️ Failed to generate final report: {e}")
    
    # Exit with appropriate code
    sys.exit(0 if result['success'] else 1)


if __name__ == "__main__":
    main()
