#!/usr/bin/env python3
"""
Wrapper script to run tests from the root directory
"""
import os
import sys
import subprocess
import glob

def main():
    """Run all test scripts automatically"""
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Find all test files that start with 'test_'
    test_pattern = os.path.join(script_dir, "test_*.py")
    test_scripts = glob.glob(test_pattern)
    
    if not test_scripts:
        print("❌ No test files found!")
        print(f"Expected pattern: {test_pattern}")
        return False
    
    # Sort test files for consistent execution order
    test_scripts.sort()
    
    print(f"🧪 Found {len(test_scripts)} test files:")
    for script in test_scripts:
        print(f"   - {os.path.basename(script)}")
    print("=" * 60)
    
    # Track overall success
    all_passed = True
    passed_count = 0
    total_count = len(test_scripts)
    
    # Run each test script
    for test_script in test_scripts:
        script_name = os.path.basename(test_script)
        print(f"\n🧪 Running {script_name}...")
        print("-" * 40)
        
        try:
            result = subprocess.run([sys.executable, test_script], cwd=script_dir, capture_output=True, text=True)
            
            # Print output
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(f"⚠️ Stderr: {result.stderr}")
            
            if result.returncode == 0:
                print(f"✅ {script_name} passed!")
                passed_count += 1
            else:
                print(f"❌ {script_name} failed with exit code {result.returncode}")
                all_passed = False
                
        except Exception as e:
            print(f"❌ Error running {script_name}: {e}")
            all_passed = False
    
    # Summary
    print("\n" + "=" * 60)
    print(f"📊 Test Summary: {passed_count}/{total_count} tests passed")
    if all_passed:
        print("🎉 All tests passed!")
    else:
        print("⚠️ Some tests failed!")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
