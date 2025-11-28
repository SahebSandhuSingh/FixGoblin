"""
Benchmark: Logical Analyzer Performance
========================================
Measures speed, memory usage, and accuracy of the deterministic logical analyzer.
"""

import time
import sys
import os
import psutil
import json
from pathlib import Path

# Add Backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Backend'))
from core.logical_analyzer import analyze_logic


def measure_memory():
    """Get current memory usage in MB."""
    process = psutil.Process()
    return process.memory_info().rss / 1024 / 1024


def generate_test_code(lines: int) -> str:
    """Generate test code of specified size."""
    code_template = """
def function_{idx}(x):
    result = 0
    for i in range(x):
        result += i
    return result

"""
    
    code = ""
    for i in range(lines // 6):  # Each function is ~6 lines
        code += code_template.format(idx=i)
    
    # Add some bugs
    code += """
def buggy_infinite():
    i = 0
    while i < 10:
        print(i)
        # Bug: forgot to increment i
    return "done"

def buggy_recursion(n):
    # Bug: missing base case
    return n * buggy_recursion(n - 1)

def buggy_off_by_one(arr):
    total = 0
    # Bug: starts at 1 instead of 0
    for i in range(1, len(arr)):
        total += arr[i]
    return total
"""
    return code


def benchmark_speed():
    """Benchmark analysis speed for different code sizes."""
    print("=" * 70)
    print("📊 SPEED BENCHMARK")
    print("=" * 70)
    
    sizes = [50, 100, 200, 500, 1000, 2000]
    results = []
    
    for size in sizes:
        code = generate_test_code(size)
        actual_lines = len(code.split('\n'))
        
        # Warm-up run
        analyze_logic(code, "python")
        
        # Timed runs
        times = []
        for _ in range(5):
            start = time.time()
            result = analyze_logic(code, "python")
            elapsed = time.time() - start
            times.append(elapsed)
        
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        errors_found = len(result['logical_errors'])
        
        results.append({
            'target_lines': size,
            'actual_lines': actual_lines,
            'avg_time_ms': avg_time * 1000,
            'min_time_ms': min_time * 1000,
            'max_time_ms': max_time * 1000,
            'errors_found': errors_found,
            'lines_per_second': actual_lines / avg_time
        })
        
        print(f"\n📄 {actual_lines:4d} lines:")
        print(f"   ⏱️  Average: {avg_time*1000:6.2f}ms")
        print(f"   ⚡ Min:     {min_time*1000:6.2f}ms")
        print(f"   🐌 Max:     {max_time*1000:6.2f}ms")
        print(f"   🐛 Errors:  {errors_found}")
        print(f"   📈 Speed:   {actual_lines/avg_time:.0f} lines/sec")
    
    return results


def benchmark_memory():
    """Benchmark memory usage."""
    print("\n" + "=" * 70)
    print("💾 MEMORY BENCHMARK")
    print("=" * 70)
    
    sizes = [100, 500, 1000, 2000, 5000]
    results = []
    
    for size in sizes:
        code = generate_test_code(size)
        actual_lines = len(code.split('\n'))
        
        # Measure baseline
        mem_before = measure_memory()
        
        # Run analysis
        result = analyze_logic(code, "python")
        
        # Measure after
        mem_after = measure_memory()
        mem_used = mem_after - mem_before
        
        results.append({
            'lines': actual_lines,
            'memory_mb': mem_used,
            'memory_per_line_kb': (mem_used * 1024) / actual_lines
        })
        
        print(f"\n📄 {actual_lines:4d} lines:")
        print(f"   💾 Memory: {mem_used:.2f} MB")
        print(f"   📊 Per line: {(mem_used*1024)/actual_lines:.2f} KB/line")
    
    return results


def benchmark_accuracy():
    """Benchmark detection accuracy."""
    print("\n" + "=" * 70)
    print("🎯 ACCURACY BENCHMARK")
    print("=" * 70)
    
    test_cases = [
        {
            'name': 'Infinite Loop',
            'code': '''
def test():
    i = 0
    while i < 10:
        print(i)
    return "done"
''',
            'expected_error': 'infinite_loop',
            'expected_count': 1
        },
        {
            'name': 'Missing Base Case',
            'code': '''
def factorial(n):
    return n * factorial(n - 1)
''',
            'expected_error': 'incorrect_base_case',
            'expected_count': 1
        },
        {
            'name': 'Off-by-One',
            'code': '''
def sum_array(arr):
    total = 0
    for i in range(1, len(arr)):
        total += arr[i]
    return total
''',
            'expected_error': 'off_by_one',
            'expected_count': 1
        },
        {
            'name': 'Unreachable Code',
            'code': '''
def test():
    return 42
    print("never executes")
''',
            'expected_error': 'unreachable_code',
            'expected_count': 1
        },
        {
            'name': 'Wrong Comparison',
            'code': '''
def test(flag):
    if flag == True:
        return "yes"
    return "no"
''',
            'expected_error': 'wrong_comparison',
            'expected_count': 1
        },
        {
            'name': 'Always True',
            'code': '''
def test():
    if 5 == 5:
        return "always"
    return "never"
''',
            'expected_error': 'always_true_false',
            'expected_count': 1
        }
    ]
    
    detected = 0
    total = len(test_cases)
    false_positives = 0
    
    for test in test_cases:
        result = analyze_logic(test['code'], 'python')
        errors = result['logical_errors']
        
        # Check if expected error was found
        found = False
        for err in errors:
            if test['expected_error'] in err['type']:
                found = True
                break
        
        status = "✅" if found else "❌"
        print(f"\n{status} {test['name']}")
        print(f"   Expected: {test['expected_error']}")
        print(f"   Found: {len(errors)} error(s)")
        
        if found:
            detected += 1
            # Count false positives (extra errors beyond expected)
            extra = len(errors) - test['expected_count']
            if extra > 0:
                false_positives += extra
                print(f"   ⚠️  {extra} false positive(s)")
        else:
            print(f"   ❌ MISSED!")
            for err in errors:
                print(f"      - {err['type']}: {err['message'][:60]}")
    
    accuracy = (detected / total) * 100
    
    print(f"\n{'='*70}")
    print(f"🎯 Detection Rate: {detected}/{total} ({accuracy:.1f}%)")
    print(f"⚠️  False Positives: {false_positives} total")
    print(f"{'='*70}")
    
    return {
        'detected': detected,
        'total': total,
        'accuracy': accuracy,
        'false_positives': false_positives
    }


def benchmark_languages():
    """Benchmark multi-language support."""
    print("\n" + "=" * 70)
    print("🌍 MULTI-LANGUAGE BENCHMARK")
    print("=" * 70)
    
    test_codes = {
        'Python': '''
def buggy():
    i = 0
    while i < 10:
        print(i)
    return "done"
''',
        'Java': '''
public class Test {
    public void buggy() {
        int i = 0;
        while (i < 10) {
            System.out.println(i);
        }
    }
}
''',
        'C++': '''
void buggy() {
    int i = 0;
    while (i < 10) {
        cout << i;
    }
}
''',
        'JavaScript': '''
function buggy() {
    let i = 0;
    while (i < 10) {
        console.log(i);
    }
}
'''
    }
    
    results = []
    
    for lang, code in test_codes.items():
        start = time.time()
        result = analyze_logic(code, lang.lower())
        elapsed = time.time() - start
        
        errors = result['logical_errors']
        
        print(f"\n🔤 {lang}:")
        print(f"   ⏱️  Time: {elapsed*1000:.2f}ms")
        print(f"   🐛 Errors Found: {len(errors)}")
        print(f"   ✅ AST Valid: {result.get('ast_valid', 'N/A')}")
        
        results.append({
            'language': lang,
            'time_ms': elapsed * 1000,
            'errors_found': len(errors),
            'ast_valid': result.get('ast_valid', False)
        })
    
    return results


def generate_report(speed_results, memory_results, accuracy_results, lang_results):
    """Generate final benchmark report."""
    print("\n\n" + "=" * 70)
    print("📊 FINAL EFFICIENCY REPORT")
    print("=" * 70)
    
    # Speed summary
    avg_speeds = [r['lines_per_second'] for r in speed_results]
    avg_times = [r['avg_time_ms'] for r in speed_results]
    
    print("\n⚡ SPEED METRICS:")
    print(f"   Best: {max(avg_speeds):.0f} lines/sec")
    print(f"   Average: {sum(avg_speeds)/len(avg_speeds):.0f} lines/sec")
    print(f"   Typical Analysis Time (100 lines): {avg_times[1]:.2f}ms")
    
    # Memory summary
    mem_values = [r['memory_mb'] for r in memory_results]
    
    print("\n💾 MEMORY METRICS:")
    print(f"   Peak Usage: {max(mem_values):.2f} MB")
    print(f"   Average: {sum(mem_values)/len(mem_values):.2f} MB")
    print(f"   Efficiency: {memory_results[0]['memory_per_line_kb']:.2f} KB/line")
    
    # Accuracy summary
    print("\n🎯 ACCURACY METRICS:")
    print(f"   Detection Rate: {accuracy_results['accuracy']:.1f}%")
    print(f"   True Positives: {accuracy_results['detected']}/{accuracy_results['total']}")
    print(f"   False Positives: {accuracy_results['false_positives']}")
    
    # Language support
    print("\n🌍 LANGUAGE SUPPORT:")
    for result in lang_results:
        status = "✅" if result['ast_valid'] else "⚠️ "
        print(f"   {status} {result['language']}: {result['time_ms']:.1f}ms, {result['errors_found']} errors")
    
    # Overall rating
    print("\n" + "=" * 70)
    print("🏆 OVERALL EFFICIENCY RATING")
    print("=" * 70)
    
    speed_grade = "A+" if avg_speeds[1] > 1000 else "A" if avg_speeds[1] > 500 else "B"
    memory_grade = "A+" if mem_values[0] < 10 else "A" if mem_values[0] < 50 else "B"
    accuracy_grade = "A+" if accuracy_results['accuracy'] >= 95 else "A" if accuracy_results['accuracy'] >= 85 else "B"
    
    print(f"   ⚡ Speed:    {speed_grade} ({avg_speeds[1]:.0f} lines/sec)")
    print(f"   💾 Memory:   {memory_grade} ({mem_values[0]:.2f} MB for 100 lines)")
    print(f"   🎯 Accuracy: {accuracy_grade} ({accuracy_results['accuracy']:.1f}%)")
    
    overall_score = sum([
        100 if speed_grade == "A+" else 90 if speed_grade == "A" else 80,
        100 if memory_grade == "A+" else 90 if memory_grade == "A" else 80,
        accuracy_results['accuracy']
    ]) / 3
    
    print(f"\n   🎯 OVERALL SCORE: {overall_score:.1f}/100")
    
    if overall_score >= 90:
        print("   🏆 EXCELLENT - Production Ready!")
    elif overall_score >= 80:
        print("   ✅ GOOD - Ready for most use cases")
    else:
        print("   ⚠️  ACCEPTABLE - May need optimization")
    
    print("=" * 70)
    
    # Save detailed results
    report = {
        'speed': speed_results,
        'memory': memory_results,
        'accuracy': accuracy_results,
        'languages': lang_results,
        'overall_score': overall_score
    }
    
    with open('benchmark_results.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print("\n💾 Detailed results saved to: benchmark_results.json")


if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║     🦎 FixGoblin Logical Analyzer - Efficiency Benchmark         ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
""")
    
    # Run benchmarks
    speed_results = benchmark_speed()
    memory_results = benchmark_memory()
    accuracy_results = benchmark_accuracy()
    lang_results = benchmark_languages()
    
    # Generate report
    generate_report(speed_results, memory_results, accuracy_results, lang_results)
    
    print("\n✅ Benchmark complete!")
