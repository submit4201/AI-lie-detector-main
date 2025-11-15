#!/usr/bin/env python3
"""
Script to start the backend server and run our validation tests.
"""

import subprocess
import time
import os
import sys
import signal

def start_backend():
    """Start the backend server."""
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    main_py = os.path.join(backend_dir, 'main.py')
    print("Starting AI Lie Detector Backend Server...")
    print(f"   Backend directory: {backend_dir}")
    print(f"   Main file: {main_py}")
    
    # Start the backend server
    try:
        process = subprocess.Popen([
            sys.executable, main_py
        ], cwd=backend_dir)
        
        print(f"   Server started with PID: {process.pid}")
        print("   Server should be available at http://localhost:8001")
        print("   Waiting for server to initialize...")
        
        # Wait for server to start
        time.sleep(5)
        
        return process
    except Exception as e:
        print(f"[ERROR] Failed to start backend: {e}")
        return None

def run_tests():
    """Run the backend validation tests."""
    print("\nRunning Backend Validation Tests...")
    
    try:
        # Run our test script
        result = subprocess.run([
            sys.executable, 'test_updated_backend_clean.py'
        ], cwd=os.path.dirname(__file__), capture_output=True, text=True)
        
        print("Test Output:")
        print("-" * 40)
        print(result.stdout)
        
        if result.stderr:
            print("Test Errors:")
            print("-" * 40)
            print(result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"[ERROR] Failed to run tests: {e}")
        return False

def main():
    """Main function to orchestrate backend testing."""
    print("AI Lie Detector Backend Validation")
    print("=" * 50)
    
    # Start backend server
    server_process = start_backend()
    if not server_process:
        print("[FAIL] Failed to start backend server")
        return
    
    try:
        # Run validation tests
        success = run_tests()
        
        if success:
            print("\n[SUCCESS] All tests passed! Backend validation successful.")
        else:
            print("\n[FAIL] Some tests failed. Check output above for details.")
            
    except KeyboardInterrupt:
        print("\n⏹️  Testing interrupted by user")
    finally:
        # Clean up - terminate the server
        print(f"\n🛑 Stopping backend server (PID: {server_process.pid})...")
        try:
            server_process.terminate()
            server_process.wait(timeout=5)
            print("   Server stopped gracefully")
        except subprocess.TimeoutExpired:
            print("   Server didn't stop gracefully, forcing termination...")
            server_process.kill()
        except Exception as e:
            print(f"   Error stopping server: {e}")

if __name__ == "__main__":
    main()
