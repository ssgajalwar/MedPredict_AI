"""
Master Test Runner for MedPredict AI API
Runs all API tests in the backend/test directory.
"""

import sys
import subprocess
from pathlib import Path

def run_test_file(test_file):
    """Run a single test file"""
    print(f"\n{'='*80}")
    print(f"Running: {test_file.name}")
    print(f"{'='*80}\n")
    
    try:
        result = subprocess.run(
            [sys.executable, str(test_file)],
            cwd=Path(__file__).parent.parent.parent,  # Run from project root
            capture_output=False,
            text=True
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Error running {test_file.name}: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*80)
    print(" " * 25 + "MEDPREDICT AI - API TEST SUITE")
    print("="*80)
    
    # Get test directory
    test_dir = Path(__file__).parent
    
    # Find all test files
    test_files = [
        test_dir / "test_unified_api.py",
        test_dir / "quick_api_test.py"
    ]
    
    # Filter existing files
    test_files = [f for f in test_files if f.exists()]
    
    if not test_files:
        print("\n⚠️  No test files found in backend/test/")
        return
    
    print(f"\nFound {len(test_files)} test file(s):")
    for f in test_files:
        print(f"  - {f.name}")
    
    # Run tests
    results = {}
    for test_file in test_files:
        results[test_file.name] = run_test_file(test_file)
    
    # Summary
    print("\n" + "="*80)
    print(" " * 30 + "TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"\nTotal Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    
    print("\nDetailed Results:")
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {test_name:30s} {status}")
    
    print("\n" + "="*80)
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("⚠️  SOME TESTS FAILED")
    
    print("="*80 + "\n")
    
    # Exit with appropriate code
    sys.exit(0 if passed == total else 1)

if __name__ == "__main__":
    main()
