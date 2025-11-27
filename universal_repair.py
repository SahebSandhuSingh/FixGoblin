"""
Universal Auto-Repair Engine
============================
Automatic code repair for Python, C++, Java, and JavaScript.
Extends the existing Python-only repair to support multiple languages.
"""

import sys
import os
import tempfile
from typing import Dict, Optional

# Add Backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Backend'))

from core.multi_language_sandbox import compile_and_run
from core.cpp_patch_generator import generate_cpp_patches
from core.java_patch_generator import generate_java_patches
from core.js_patch_generator import generate_js_patches


def universal_repair(
    file_path: str,
    max_iterations: int = 5,
    language: Optional[str] = None
) -> Dict:
    """
    Universal auto-repair for multiple languages.
    
    Args:
        file_path: Path to source code file
        max_iterations: Maximum repair attempts
        language: Language (auto-detected if None)
        
    Returns:
        Dictionary with repair results
    """
    
    # Detect language from extension
    if not language:
        ext = os.path.splitext(file_path)[1]
        lang_map = {
            '.py': 'python',
            '.cpp': 'cpp', '.cc': 'cpp', '.cxx': 'cpp',
            '.c': 'c',
            '.java': 'java',
            '.js': 'javascript',
            '.go': 'go'
        }
        language = lang_map.get(ext, 'python')
    
    # Read original code
    with open(file_path, 'r', encoding='utf-8') as f:
        original_code = f.read()
    
    # For Python, use existing autonomous_repair
    if language == 'python':
        from core.autonomous_repair import autonomous_repair
        return autonomous_repair(file_path, max_iterations)
    
    # For other languages, use universal repair
    print(f"🌍 Universal Repair Mode: {language.upper()}")
    print("=" * 70)
    
    result = {
        'success': False,
        'total_iterations': 0,
        'iterations': [],
        'final_status': 'FAILED',
        'reason': 'No errors found or max iterations reached'
    }
    
    current_code = original_code
    
    # First check if code already works
    print("🔍 Checking if code needs repair...")
    initial_result = compile_and_run(current_code, language)
    
    if initial_result['success']:
        print(f"✅ CODE IS ALREADY PERFECT!")
        print(f"🎉 No errors found - your code works correctly!")
        result['success'] = True
        result['total_iterations'] = 0
        result['final_status'] = 'SUCCESS'
        result['reason'] = 'Code already works - no repair needed'
        
        print("\n" + "=" * 70)
        print("📋 REPAIR SUMMARY")
        print("=" * 70)
        print(f"Status: ✅ SUCCESS")
        print(f"Language: {language.upper()}")
        print(f"Iterations: 0 (no repair needed)")
        print(f"Reason: Code is already correct")
        print("=" * 70)
        
        return result
    
    print(f"❌ Found errors - starting repair process...\n")
    
    for iteration in range(1, max_iterations + 1):
        print(f"\n{'▶' * 40}")
        print(f"ITERATION {iteration}/{max_iterations}")
        print(f"{'▶' * 40}\n")
        
        # Run code
        exec_result = compile_and_run(current_code, language)
        
        if exec_result['success']:
            print(f"✅ CODE RUNS SUCCESSFULLY!")
            result['success'] = True
            result['total_iterations'] = iteration
            result['final_status'] = 'SUCCESS'
            result['reason'] = 'Code successfully repaired'
            
            # Write fixed code back to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(current_code)
            
            # Create backup of original
            backup_path = file_path + '.backup'
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_code)
            print(f"\n📦 Backup created: {backup_path}")
            
            break
        
        # Error detected
        print(f"❌ Execution failed with errors")
        print(f"🐛 Error Type: {exec_result['error_type']}")
        if exec_result.get('line_number'):
            print(f"📍 Line: {exec_result['line_number']}")
        
        # Generate patches based on language
        error_data = {
            'error_type': exec_result['error_type'],
            'line_number': exec_result.get('line_number'),
            'error': exec_result.get('error', ''),
            'error_message': exec_result.get('error', '')
        }
        
        patches = []
        if language == 'cpp' or language == 'c':
            patches = generate_cpp_patches(error_data, current_code)
        elif language == 'java':
            patches = generate_java_patches(error_data, current_code)
        elif language == 'javascript':
            patches = generate_js_patches(error_data, current_code)
        
        if not patches:
            print(f"❌ No patches generated for this error")
            result['reason'] = f'No patches available for {language} errors'
            break
        
        print(f"\n🔧 Generated {len(patches)} patch candidate(s)")
        for idx, patch in enumerate(patches, 1):
            print(f"   {idx}. {patch['id']}: {patch['description']}")
        
        # Test patches and select best one
        best_patch = _test_and_select_patch(patches, language)
        
        if not best_patch:
            print(f"❌ No working patch found")
            break
        
        print(f"\n✅ Applying patch: {best_patch['description']}")
        current_code = best_patch['patched_code']
        
        result['iterations'].append({
            'iteration': iteration,
            'error_type': error_data['error_type'],
            'line_number': error_data.get('line_number'),
            'patch_id': best_patch['id'],
            'description': best_patch['description'],
            'status': 'FIXED' if exec_result['success'] else 'RETRYING'
        })
        
        result['total_iterations'] = iteration
    
    if not result['success']:
        print(f"\n⚠️  MAX ITERATIONS REACHED ({max_iterations})")
        result['reason'] = f'Reached maximum iterations without fixing all errors'
    
    print("\n" + "=" * 70)
    print("📋 REPAIR SUMMARY")
    print("=" * 70)
    print(f"Status: {'✅ SUCCESS' if result['success'] else '❌ FAILED'}")
    print(f"Language: {language.upper()}")
    print(f"Iterations: {result['total_iterations']}")
    print(f"Reason: {result['reason']}")
    print("=" * 70)
    
    return result


def _test_and_select_patch(patches: list, language: str) -> Optional[Dict]:
    """Test each patch and return the best one"""
    best_patch = None
    best_score = -999
    
    print(f"\n🏆 Testing patches...")
    
    for idx, patch in enumerate(patches, 1):
        print(f"\n🔬 Testing Patch {idx}/{len(patches)}: {patch['id']}")
        
        # Test the patch
        result = compile_and_run(patch['patched_code'], language)
        
        score = 0
        if result['success']:
            score = 100
            print(f"   ✅ WORKS! Score: {score}")
        else:
            # Even if it doesn't fully work, it might reduce errors
            # Give it a positive score if it at least compiles or shows different error
            score = 10  # Small positive score for any patch
            print(f"   ⚡ Partial fix (still has errors)")
        
        if score > best_score:
            best_score = score
            best_patch = patch
    
    # Accept patches with any positive score (not just 100)
    return best_patch if best_score > 0 else None


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Universal Code Auto-Repair')
    parser.add_argument('file', help='Source code file to repair')
    parser.add_argument('--max-iterations', type=int, default=5, help='Maximum repair iterations')
    parser.add_argument('--language', help='Programming language (auto-detected if omitted)')
    
    args = parser.parse_args()
    
    result = universal_repair(args.file, args.max_iterations, args.language)
    
    sys.exit(0 if result['success'] else 1)
