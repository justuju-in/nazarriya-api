#!/usr/bin/env python3
"""
Wrapper script to run tests from the root directory
"""
import os
import sys
import subprocess

def main():
    """Run the test script directly"""
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    test_script = os.path.join(script_dir, "test_auth.py")
    
    if not os.path.exists(test_script):
        print("❌ Test script not found!")
        print(f"Expected location: {test_script}")
        return False
    
    print("🧪 Running test_auth.py...")
    print("=" * 60)
    
    # Run the test script
    try:
        result = subprocess.run([sys.executable, test_script], cwd=script_dir)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
