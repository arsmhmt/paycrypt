import sys
import subprocess

def run_test(script_name):
    """Run a test script and return True if it succeeds"""
    print(f"\n{'='*50}")
    print(f"Running {script_name}...")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            check=True,
            text=True,
            capture_output=True
        )
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {script_name} failed with exit code {e.returncode}")
        print("\n=== STDOUT ===")
        print(e.stdout)
        print("\n=== STDERR ===")
        print(e.stderr)
        return False

def main():
    # List of test scripts to run in order
    test_scripts = [
        'test_login.py',
        'test_dashboard.py',
        'test_refresh.py',
        'test_logout.py'
    ]
    
    # Run each test
    results = {}
    for script in test_scripts:
        success = run_test(script)
        results[script] = success
        if not success:
            print(f"\n❌ Test failed: {script}")
            break
    
    # Print summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    all_passed = all(results.values())
    
    for script, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{script}: {status}")
    
    if all_passed:
        print("\n🎉 All tests passed successfully!")
    else:
        print("\n❌ Some tests failed. See above for details.")
    
    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()
