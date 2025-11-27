"""
Complete Debugging Pipeline Test
=================================
Tests the full pipeline: Sandbox → Error Parser → Patch Generator
"""

from sandbox_runner import run_in_sandbox
from error_parser import parse_error
from patch_generator import generate_patch_candidates
import sys


def test_full_pipeline(file_path: str):
    """Run complete debugging pipeline and generate patch candidates."""
    
    print("=" * 70)
    print("COMPLETE AUTONOMOUS DEBUGGING PIPELINE")
    print("=" * 70)
    print(f"\n📁 File: {file_path}\n")
    
    # STEP 1: Execute in sandbox
    print("STEP 1: Executing code in sandbox...")
    print("-" * 70)
    sandbox_result = run_in_sandbox(file_path)
    
    print(f"Language: {sandbox_result['language']}")
    print(f"Return Code: {sandbox_result['returncode']}")
    
    if sandbox_result['returncode'] == 0:
        print("\n✅ Code executed successfully! No fixes needed.")
        return
    
    print(f"\n❌ Execution failed with errors.")
    
    # STEP 2: Parse errors
    print("\nSTEP 2: Parsing error signals...")
    print("-" * 70)
    
    # Read user code
    with open(file_path, 'r') as f:
        user_code = f.read()
    
    error_analysis = parse_error(sandbox_result, user_code)
    
    if not error_analysis['error_type']:
        print("Could not parse error information.")
        return
    
    print(f"\n🐛 Error Detected:")
    print(f"   Type: {error_analysis['error_type']}")
    print(f"   Line: {error_analysis['line_number']}")
    print(f"   Message: {error_analysis['error_message']}")
    print(f"   Code: {error_analysis['faulty_snippet']}")
    
    # STEP 3: Generate patch candidates
    print("\nSTEP 3: Generating patch candidates...")
    print("-" * 70)
    
    patches = generate_patch_candidates(error_analysis, user_code)
    
    if not patches:
        print("❌ No patches could be generated for this error type.")
        return
    
    print(f"\n✨ Generated {len(patches)} patch candidate(s):\n")
    
    for i, patch in enumerate(patches, 1):
        print(f"\n{'=' * 70}")
        print(f"PATCH {i}: {patch['description']}")
        print(f"ID: {patch['id']}")
        print(f"{'=' * 70}")
        print("\nDiff:")
        print(patch['diff'])
        print("\n" + "-" * 70)
        print("Patched Code Preview:")
        print("-" * 70)
        # Show first 15 lines of patched code
        preview_lines = patch['patched_code'].splitlines()[:15]
        for line_num, line in enumerate(preview_lines, 1):
            print(f"{line_num:3d} | {line}")
        if len(patch['patched_code'].splitlines()) > 15:
            print("    | ...")
    
    print("\n" + "=" * 70)
    print(f"✅ Pipeline complete! Generated {len(patches)} fix candidates.")
    print("=" * 70)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 test_pipeline.py <file_path>")
        print("Example: python3 test_pipeline.py user.py")
        sys.exit(1)
    
    file_path = sys.argv[1]
    test_full_pipeline(file_path)
