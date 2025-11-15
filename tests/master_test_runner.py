#!/usr/bin/env python3
"""
Master Test Runner for AI Lie Detector System
Consolidates and runs all working tests for the current system state.
"""

import os
import sys
import subprocess
import importlib.util
import traceback
from pathlib import Path
from datetime import datetime
import json

# Add the backend directory to Python path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

class TestRunner:
    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "test_results": {},
            "errors": []
        }
        
        # Define categories of tests
        self.test_categories = {
            "backend_validation": [
                "run_backend_validation_clean.py",
                "test_complete_validation.py",
                "test_model_validation.py"
            ],
            "api_tests": [
                "simple_api_test.py",
                "test_api_data_flow_fixed.py",
                "test_complete_integration.py"
            ],
            "service_tests": [
                "test_linguistic_service.py",
                "test_enhanced_formality.py",
                "test_formality_final.py"
            ],
            "analysis_tests": [
                "test_enhanced_analysis.py",
                "test_enhanced_patterns.py",
                "test_direct_patterns.py"
            ],
            "session_tests": [
                "test_e2e_session_insights.py",
                "test_real_transcript_insights.py"
            ],
            "streaming_tests": [
                "test_real_audio_file.py"  # This likely tests the audio processing pipeline
            ]
        }
    
    def print_header(self):
        """Print test runner header"""
        print("=" * 80)
        print("[TEST] AI LIE DETECTOR SYSTEM - MASTER TEST RUNNER")
        print("=" * 80)
        print(f"Starting comprehensive test suite at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
    
    def run_python_test(self, test_file):
        """Run a Python test file and capture results"""
        test_path = self.test_dir / test_file
        if not test_path.exists():
            return False, f"Test file not found: {test_file}"
        
        try:
            print(f"  Running {test_file}...")
            
            # Run the test as a subprocess to capture output
            result = subprocess.run(
                [sys.executable, str(test_path)],
                capture_output=True,
                text=True,
                timeout=60,  # 60 second timeout per test
                cwd=str(self.test_dir)
            )
            
            if result.returncode == 0:
                print(f"    [PASS] PASSED")
                return True, result.stdout
            else:
                print(f"    [FAIL] FAILED")
                error_msg = f"Exit code: {result.returncode}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
                return False, error_msg
                
        except subprocess.TimeoutExpired:
            print(f"    [TIMEOUT] TIMEOUT")
            return False, "Test timed out after 60 seconds"
        except Exception as e:
            print(f"    💥 ERROR: {str(e)}")
            return False, f"Exception running test: {str(e)}"
    
    def run_category(self, category_name, test_files):
        """Run all tests in a category"""
        print(f"\n[FILE] Running {category_name.upper()} tests:")
        print("-" * 60)
        
        category_results = {
            "passed": 0,
            "failed": 0,
            "tests": {}
        }
        
        for test_file in test_files:
            self.results["tests_run"] += 1
            success, output = self.run_python_test(test_file)
            
            if success:
                self.results["tests_passed"] += 1
                category_results["passed"] += 1
            else:
                self.results["tests_failed"] += 1
                category_results["failed"] += 1
                self.results["errors"].append({
                    "test": test_file,
                    "category": category_name,
                    "error": output
                })
            
            category_results["tests"][test_file] = {
                "passed": success,
                "output": output[:500] + "..." if len(output) > 500 else output
            }
        
        self.results["test_results"][category_name] = category_results
        
        # Print category summary
        total = category_results["passed"] + category_results["failed"]
        print(f"\n{category_name} Summary: {category_results['passed']}/{total} tests passed")
    
    def run_all_tests(self):
        """Run all test categories"""
        self.print_header()
        
        for category_name, test_files in self.test_categories.items():
            self.run_category(category_name, test_files)
        
        self.print_summary()
        self.save_results()
    
    def print_summary(self):
        """Print overall test summary"""
        print("\n" + "=" * 80)
        print("[TARGET] OVERALL TEST SUMMARY")
        print("=" * 80)
        
        total_tests = self.results["tests_run"]
        passed = self.results["tests_passed"]
        failed = self.results["tests_failed"]
        
        print(f"Total Tests Run: {total_tests}")
        print(f"[PASS] Passed: {passed}")
        print(f"[FAIL] Failed: {failed}")
        
        if total_tests > 0:
            success_rate = (passed / total_tests) * 100
            print(f"[DATA] Success Rate: {success_rate:.1f}%")
        
        # Show category breakdown
        print("\n[DATA] Category Breakdown:")
        for category_name, category_results in self.results["test_results"].items():
            total = category_results["passed"] + category_results["failed"]
            if total > 0:
                rate = (category_results["passed"] / total) * 100
                print(f"  {category_name}: {category_results['passed']}/{total} ({rate:.1f}%)")
        
        # Show failed tests
        if self.results["errors"]:
            print(f"\n[FAIL] Failed Tests ({len(self.results['errors'])}):")
            for error in self.results["errors"]:
                print(f"  • {error['test']} ({error['category']})")
        
        print(f"\nTest completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
    
    def save_results(self):
        """Save test results to JSON file"""
        results_file = self.test_dir / "test_results.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n📄 Detailed results saved to: {results_file}")
    
    def run_specific_category(self, category_name):
        """Run tests for a specific category only"""
        if category_name not in self.test_categories:
            print(f"[FAIL] Unknown category: {category_name}")
            print(f"Available categories: {', '.join(self.test_categories.keys())}")
            return
        
        self.print_header()
        print(f"Running only {category_name} tests...\n")
        
        self.run_category(category_name, self.test_categories[category_name])
        self.print_summary()
        self.save_results()

def main():
    """Main entry point"""
    runner = TestRunner()
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        category = sys.argv[1]
        if category == "--list":
            print("Available test categories:")
            for cat in runner.test_categories.keys():
                print(f"  • {cat}")
            return
        elif category == "--help":
            print("Usage:")
            print("  python master_test_runner.py [category]")
            print("  python master_test_runner.py --list    # List categories")
            print("  python master_test_runner.py --help    # Show this help")
            print("\nRun without arguments to run all tests.")
            return
        else:
            runner.run_specific_category(category)
    else:
        runner.run_all_tests()

if __name__ == "__main__":
    main()
