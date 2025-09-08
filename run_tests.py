#!/usr/bin/env python3
"""
Test runner script for CymbalBot.
This script provides easy access to all test scripts.
"""

import os
import sys
import subprocess
import argparse

def run_script(script_name, *args):
    """Run a test script from the scripts directory."""
    script_path = os.path.join("scripts", script_name)
    if not os.path.exists(script_path):
        print(f"❌ Script not found: {script_path}")
        return False
    
    cmd = [sys.executable, script_path] + list(args)
    print(f"🚀 Running: {' '.join(cmd)}")
    return subprocess.run(cmd).returncode == 0

def main():
    parser = argparse.ArgumentParser(description="CymbalBot Test Runner")
    parser.add_argument("test", choices=[
        "local", "deployed", "deployed-simple", "deployment"
    ], help="Test to run")
    parser.add_argument("args", nargs="*", help="Additional arguments for the test script")
    
    args = parser.parse_args()
    
    script_mapping = {
        "local": "test_local_agent.py",
        "deployed": "test_deployed_agent.py", 
        "deployed-simple": "test_deployed_agent_simple.py",
        "deployment": "test_deployment.py"
    }
    
    script_name = script_mapping[args.test]
    success = run_script(script_name, *args.args)
    
    if success:
        print(f"✅ {args.test} test completed successfully")
        sys.exit(0)
    else:
        print(f"❌ {args.test} test failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
