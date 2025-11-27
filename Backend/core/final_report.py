"""
Final Report Generator
======================
Generates comprehensive debugging reports for autonomous code repair pipeline.
Collects all repair history and formats it for terminal and JSON output.
"""

import json
import time
import difflib
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path


def generate_final_report(context: dict) -> None:
    """
    Generate a comprehensive final report for the repair pipeline.
    
    Args:
        context: Dictionary containing:
            - file_path: str - Path to the repaired file
            - original_code: str - Original file content
            - final_code: str - Final patched file content
            - patch_history: List[Dict] - List of applied patches with details
            - total_iterations: int - Number of repair attempts
            - execution_time: float - Total time taken (seconds)
            - success: bool - Whether repair was successful
            - stdout_logs: List[str] - Execution output logs (optional)
            - stderr_logs: List[str] - Error logs (optional)
            - final_status: str - "success", "failed", or "partial"
    """
    
    # Extract context
    file_path = context.get('file_path', 'unknown')
    original_code = context.get('original_code', '')
    final_code = context.get('final_code', '')
    patch_history = context.get('patch_history', [])
    total_iterations = context.get('total_iterations', 0)
    execution_time = context.get('execution_time', 0.0)
    success = context.get('success', False)
    stdout_logs = context.get('stdout_logs', [])
    stderr_logs = context.get('stderr_logs', [])
    final_status = context.get('final_status', 'unknown')
    
    # Generate report data
    report_data = _build_report_data(
        file_path=file_path,
        original_code=original_code,
        final_code=final_code,
        patch_history=patch_history,
        total_iterations=total_iterations,
        execution_time=execution_time,
        success=success,
        stdout_logs=stdout_logs,
        stderr_logs=stderr_logs,
        final_status=final_status
    )
    
    # Print terminal version
    _print_terminal_report(report_data)
    
    # Save JSON version
    json_path = _save_json_report(report_data, file_path)
    
    print(f"\n📄 Full report saved to: {json_path}")


def _build_report_data(
    file_path: str,
    original_code: str,
    final_code: str,
    patch_history: List[Dict],
    total_iterations: int,
    execution_time: float,
    success: bool,
    stdout_logs: List[str],
    stderr_logs: List[str],
    final_status: str
) -> Dict[str, Any]:
    """Build structured report data."""
    
    # Determine status emoji and text
    if final_status == 'success' or success:
        status_emoji = "✅"
        status_text = "Fixed"
    elif final_status == 'partial':
        status_emoji = "⚠️"
        status_text = "Partially Fixed"
    else:
        status_emoji = "❌"
        status_text = "Failed"
    
    # Extract error types from patch history
    error_types = set()
    for patch in patch_history:
        if patch.get('error_type'):
            error_types.add(patch['error_type'])
    
    # Generate code diff
    code_diff = _generate_code_diff(original_code, final_code)
    
    # Summarize applied patches
    patch_summaries = []
    for i, patch in enumerate(patch_history, 1):
        patch_summaries.append({
            'iteration': i,
            'patch_id': patch.get('patch_id', 'unknown'),
            'description': patch.get('description', 'No description'),
            'score': patch.get('score', 0),
            'error_type': patch.get('error_type', 'N/A'),
            'line_number': patch.get('line_number', 'N/A')
        })
    
    return {
        'metadata': {
            'file_path': file_path,
            'timestamp': datetime.now().isoformat(),
            'execution_time_seconds': round(execution_time, 2),
            'total_iterations': total_iterations
        },
        'status': {
            'emoji': status_emoji,
            'text': status_text,
            'success': success,
            'final_status': final_status
        },
        'errors': {
            'detected_types': sorted(list(error_types)),
            'count': len(error_types)
        },
        'patches': {
            'applied_count': len(patch_summaries),
            'summaries': patch_summaries
        },
        'code_changes': {
            'diff': code_diff,
            'lines_changed': _count_changed_lines(code_diff),
            'original_lines': len(original_code.split('\n')),
            'final_lines': len(final_code.split('\n'))
        },
        'logs': {
            'stdout': stdout_logs[-10:] if stdout_logs else [],  # Last 10 entries
            'stderr': stderr_logs[-10:] if stderr_logs else []   # Last 10 entries
        },
        'original_code': original_code,
        'final_code': final_code
    }


def _generate_code_diff(original: str, final: str) -> List[str]:
    """Generate unified diff between original and final code."""
    original_lines = original.splitlines(keepends=True)
    final_lines = final.splitlines(keepends=True)
    
    diff = list(difflib.unified_diff(
        original_lines,
        final_lines,
        fromfile='original',
        tofile='patched',
        lineterm=''
    ))
    
    return [line.rstrip() for line in diff]


def _count_changed_lines(diff: List[str]) -> int:
    """Count number of changed lines in diff."""
    count = 0
    for line in diff:
        if line.startswith('+') and not line.startswith('+++'):
            count += 1
        elif line.startswith('-') and not line.startswith('---'):
            count += 1
    return count


def _print_terminal_report(report_data: Dict[str, Any]) -> None:
    """Print formatted report to terminal."""
    
    metadata = report_data['metadata']
    status = report_data['status']
    errors = report_data['errors']
    patches = report_data['patches']
    code_changes = report_data['code_changes']
    
    print("\n" + "=" * 80)
    print("🔍 FINAL DEBUGGING REPORT")
    print("=" * 80)
    
    # Metadata section
    print(f"\n📁 File: {metadata['file_path']}")
    print(f"⏱️  Execution Time: {metadata['execution_time_seconds']}s")
    print(f"🔄 Total Iterations: {metadata['total_iterations']}")
    print(f"📅 Generated: {metadata['timestamp']}")
    
    # Status section
    print(f"\n{status['emoji']} Status: {status['text']}")
    print(f"   Success: {status['success']}")
    print(f"   Final Status: {status['final_status']}")
    
    # Errors section
    print(f"\n🐛 Detected Error Types ({errors['count']}):")
    if errors['detected_types']:
        for error_type in errors['detected_types']:
            print(f"   • {error_type}")
    else:
        print("   No errors detected")
    
    # Patches section
    print(f"\n🔧 Applied Patches ({patches['applied_count']}):")
    if patches['summaries']:
        for patch in patches['summaries']:
            print(f"\n   Iteration {patch['iteration']}:")
            print(f"      ID: {patch['patch_id']}")
            print(f"      Description: {patch['description']}")
            print(f"      Score: {patch['score']} points")
            print(f"      Error Type: {patch['error_type']}")
            print(f"      Line: {patch['line_number']}")
    else:
        print("   No patches applied")
    
    # Code changes section
    print(f"\n📄 Code Changes:")
    print(f"   Original Lines: {code_changes['original_lines']}")
    print(f"   Final Lines: {code_changes['final_lines']}")
    print(f"   Lines Changed: {code_changes['lines_changed']}")
    
    # Diff preview (first 20 lines)
    print(f"\n📊 Code Diff (Preview):")
    if code_changes['diff']:
        preview_lines = code_changes['diff'][:20]
        for line in preview_lines:
            if line.startswith('+++') or line.startswith('---'):
                print(f"   {line}")
            elif line.startswith('+'):
                print(f"   \033[92m{line}\033[0m")  # Green
            elif line.startswith('-'):
                print(f"   \033[91m{line}\033[0m")  # Red
            elif line.startswith('@@'):
                print(f"   \033[94m{line}\033[0m")  # Blue
            else:
                print(f"   {line}")
        
        if len(code_changes['diff']) > 20:
            print(f"   ... ({len(code_changes['diff']) - 20} more lines)")
    else:
        print("   No changes detected")
    
    print("\n" + "=" * 80)


def _save_json_report(report_data: Dict[str, Any], file_path: str) -> str:
    """Save report as JSON file."""
    
    # Determine output path
    if file_path and file_path != 'unknown':
        base_path = Path(file_path).parent
        file_stem = Path(file_path).stem
    else:
        base_path = Path.cwd() / 'backend' / 'logs'
        file_stem = 'unknown'
    
    # Ensure logs directory exists
    logs_dir = Path.cwd() / 'backend' / 'logs'
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = logs_dir / f"{file_stem}_final_report.json"
    
    # Save JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
    
    return str(output_path)


def collect_repair_context(
    file_path: str,
    original_code: str,
    final_code: str,
    iterations_log: List[Dict[str, Any]],
    start_time: float,
    success: bool,
    final_status: str = 'success'
) -> Dict[str, Any]:
    """
    Helper function to collect context from autonomous_repair.py
    
    Args:
        file_path: Path to the file being repaired
        original_code: Original source code
        final_code: Final patched source code
        iterations_log: List of iteration dictionaries from repair loop
        start_time: Timestamp when repair started
        success: Whether repair succeeded
        final_status: Final status string
    
    Returns:
        Context dictionary ready for generate_final_report()
    """
    
    # Extract patch history from iterations
    patch_history = []
    stdout_logs = []
    stderr_logs = []
    
    for iteration in iterations_log:
        if iteration.get('selected_patch_id'):
            patch_history.append({
                'patch_id': iteration.get('selected_patch_id'),
                'description': iteration.get('description', ''),
                'score': iteration.get('patch_score', 0),
                'error_type': iteration.get('error_type'),
                'line_number': iteration.get('line_number'),
                'iteration': iteration.get('iteration')
            })
        
        # Collect logs if available
        if 'stdout' in iteration:
            stdout_logs.append(iteration['stdout'])
        if 'stderr' in iteration:
            stderr_logs.append(iteration['stderr'])
    
    execution_time = time.time() - start_time
    
    return {
        'file_path': file_path,
        'original_code': original_code,
        'final_code': final_code,
        'patch_history': patch_history,
        'total_iterations': len(iterations_log),
        'execution_time': execution_time,
        'success': success,
        'stdout_logs': stdout_logs,
        'stderr_logs': stderr_logs,
        'final_status': final_status
    }


# Example usage integration point
if __name__ == "__main__":
    # Example context (normally provided by autonomous_repair.py)
    example_context = {
        'file_path': 'backend/tests/user.py',
        'original_code': 'def buggy():\n    x = [1,2,3]\n    return x[5]',
        'final_code': 'def buggy():\n    x = [1,2,3]\n    return x[2]',
        'patch_history': [
            {
                'patch_id': 'patch_1',
                'description': 'Fix IndexError: change x[5] to x[2]',
                'score': 110,
                'error_type': 'IndexError',
                'line_number': 3
            }
        ],
        'total_iterations': 1,
        'execution_time': 1.5,
        'success': True,
        'stdout_logs': ['[1, 2, 3]'],
        'stderr_logs': [],
        'final_status': 'success'
    }
    
    generate_final_report(example_context)
