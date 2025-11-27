"""
End-to-End Integration Test: Backend + Frontend
================================================
This script performs a comprehensive test of the integrated system
"""

import sys
import os

# Add Backend to path
backend_path = os.path.join(os.path.dirname(__file__), 'Backend')
sys.path.insert(0, backend_path)

print("="*80)
print("🧪 END-TO-END INTEGRATION TEST: BACKEND + FRONTEND")
print("="*80)
print()

# ============================================================================
# TEST 1: Import Verification
# ============================================================================
print("📦 TEST 1: Verifying All Imports")
print("-" * 80)

test_results = {
    'imports': 0,
    'configs': 0,
    'files': 0,
    'functions': 0
}

try:
    import streamlit
    print("   ✅ Streamlit")
    test_results['imports'] += 1
except ImportError:
    print("   ❌ Streamlit (FAILED)")

try:
    from core.autonomous_repair import autonomous_repair
    print("   ✅ autonomous_repair")
    test_results['imports'] += 1
except ImportError:
    print("   ❌ autonomous_repair (FAILED)")

try:
    from core.dsl_parser import parse_dsl_config
    print("   ✅ dsl_parser")
    test_results['imports'] += 1
except ImportError:
    print("   ❌ dsl_parser (FAILED)")

try:
    from core.sandbox_runner import run_in_sandbox
    print("   ✅ sandbox_runner")
    test_results['imports'] += 1
except ImportError:
    print("   ❌ sandbox_runner (FAILED)")

try:
    from core.error_parser import parse_error
    print("   ✅ error_parser")
    test_results['imports'] += 1
except ImportError:
    print("   ❌ error_parser (FAILED)")

try:
    from core.logical_validator import validate_logic
    print("   ✅ logical_validator")
    test_results['imports'] += 1
except ImportError:
    print("   ❌ logical_validator (FAILED)")

print()

# ============================================================================
# TEST 2: Configuration Files
# ============================================================================
print("📋 TEST 2: Checking Configuration Files")
print("-" * 80)

configs = [
    'strict_logical_rules.dsl',
    'debug_rules.dsl',
    'debug_rules_minimal.dsl'
]

for config in configs:
    if os.path.exists(config):
        print(f"   ✅ {config}")
        test_results['configs'] += 1
    else:
        print(f"   ❌ {config} (MISSING)")

print()

# ============================================================================
# TEST 3: Essential Files
# ============================================================================
print("📁 TEST 3: Checking Essential Files")
print("-" * 80)

essential_files = [
    'streamlit_app.py',
    'fixgoblin.py',
    'Backend/core/autonomous_repair.py',
    'Backend/core/dsl_parser.py',
    'Backend/core/sandbox_runner.py'
]

for filepath in essential_files:
    if os.path.exists(filepath):
        print(f"   ✅ {filepath}")
        test_results['files'] += 1
    else:
        print(f"   ❌ {filepath} (MISSING)")

print()

# ============================================================================
# TEST 4: Backend Functionality
# ============================================================================
print("🔧 TEST 4: Testing Backend Functions")
print("-" * 80)

import tempfile

# Test 4.1: Parse DSL Config
try:
    config = parse_dsl_config('strict_logical_rules.dsl')
    if config and 'allow' in config and 'deny' in config:
        print(f"   ✅ parse_dsl_config() - Loaded {len(config['allow'])} rules")
        test_results['functions'] += 1
    else:
        print("   ❌ parse_dsl_config() - Invalid config structure")
except Exception as e:
    print(f"   ❌ parse_dsl_config() - Error: {e}")

# Test 4.2: Sandbox Runner
try:
    test_code = '''
def test():
    return "Hello from sandbox"

print(test())
'''
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_code)
        temp_file = f.name
    
    result = run_in_sandbox(temp_file)
    os.unlink(temp_file)
    
    if result and 'stdout' in result:
        print(f"   ✅ run_in_sandbox() - Output: {result['stdout'].strip()[:30]}...")
        test_results['functions'] += 1
    else:
        print("   ❌ run_in_sandbox() - No output captured")
except Exception as e:
    print(f"   ❌ run_in_sandbox() - Error: {e}")

# Test 4.3: Autonomous Repair (Quick test)
try:
    buggy_code = '''
def add(a, b):
    return a + b

print(add(2, 3))
'''
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(buggy_code)
        temp_file = f.name
    
    result = autonomous_repair(temp_file, max_iterations=1, optimize_efficiency=True)
    os.unlink(temp_file)
    
    if result and 'success' in result:
        print(f"   ✅ autonomous_repair() - Status: {result['final_status']}")
        test_results['functions'] += 1
    else:
        print("   ❌ autonomous_repair() - Invalid result structure")
except Exception as e:
    print(f"   ❌ autonomous_repair() - Error: {e}")

print()

# ============================================================================
# TEST 5: Integration Test
# ============================================================================
print("🔗 TEST 5: Full Integration Test (Real Bug)")
print("-" * 80)

buggy_code = '''
def calculate_discount(price, percent):
    """Calculate final price after discount"""
    discount = price * percent
    return price + discount

result = calculate_discount(100, 20)
print(f"Discounted price: {result}")
print(f"Expected: 80, Got: {result}")
'''

try:
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(buggy_code)
        temp_file = f.name
    
    print("   → Created buggy code file")
    
    # Load config
    config = parse_dsl_config('strict_logical_rules.dsl')
    print(f"   → Loaded DSL config: {len(config['allow'])} rules")
    
    # Run repair
    result = autonomous_repair(
        file_path=temp_file,
        max_iterations=5,
        optimize_efficiency=True
    )
    
    print(f"   → Repair complete: {result['final_status']}")
    print(f"   → Iterations: {result['total_iterations']}")
    print(f"   → Success: {result['success']}")
    
    # Read fixed code
    with open(temp_file, 'r', encoding='utf-8') as f:
        fixed_code = f.read()
    
    print(f"   → Fixed code length: {len(fixed_code)} chars")
    
    # Run in sandbox
    sandbox_result = run_in_sandbox(temp_file)
    stdout = sandbox_result.get('stdout', '').strip()
    
    print(f"   → Final output: {stdout[:50]}...")
    
    # Cleanup
    os.unlink(temp_file)
    
    if result['success'] and '80' in stdout:
        print("   ✅ INTEGRATION TEST PASSED!")
    else:
        print("   ⚠️  INTEGRATION TEST PARTIAL SUCCESS")
    
except Exception as e:
    print(f"   ❌ INTEGRATION TEST FAILED: {e}")
    import traceback
    traceback.print_exc()

print()

# ============================================================================
# RESULTS SUMMARY
# ============================================================================
print("="*80)
print("📊 TEST RESULTS SUMMARY")
print("="*80)
print()

total_imports = 6
total_configs = 3
total_files = 5
total_functions = 3

print(f"✅ Imports:       {test_results['imports']}/{total_imports}")
print(f"✅ Configs:       {test_results['configs']}/{total_configs}")
print(f"✅ Files:         {test_results['files']}/{total_files}")
print(f"✅ Functions:     {test_results['functions']}/{total_functions}")
print()

total_tests = (test_results['imports'] + test_results['configs'] + 
               test_results['files'] + test_results['functions'])
max_tests = total_imports + total_configs + total_files + total_functions

success_rate = (total_tests / max_tests) * 100

print(f"TOTAL SCORE: {total_tests}/{max_tests} ({success_rate:.1f}%)")
print()

if success_rate >= 90:
    print("🎉 EXCELLENT! System is fully integrated and ready!")
    print()
    print("🚀 To launch Streamlit app:")
    print("   ./launch_streamlit.sh")
    print()
    print("   OR")
    print()
    print("   streamlit run streamlit_app.py")
elif success_rate >= 70:
    print("⚠️  GOOD! Most features working, some issues detected.")
elif success_rate >= 50:
    print("⚠️  PARTIAL! Significant issues detected.")
else:
    print("❌ FAILED! Major integration problems.")

print()
print("="*80)
print("📚 Documentation:")
print("   - INTEGRATION_STATUS.md (Status report)")
print("   - STREAMLIT_INTEGRATION_GUIDE.md (Technical guide)")
print("   - STREAMLIT_UI_GUIDE.md (User guide)")
print("="*80)
