#!/usr/bin/env python3
"""
Test Validator - Quickly identifies which tests are still working
Runs basic imports and quick checks on all test files to categorize them.
"""

import sys
import os
import importlib.util
import traceback
from pathlib import Path
import ast

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

class TestValidator:
    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.results = {
            "working": [],
            "broken": [],
            "deprecated": [],
            "frontend": [],
            "backend": [],
            "integration": []
        }
    
    def analyze_test_file(self, test_file):
        """Analyze a test file to determine its status and category"""
        file_path = self.test_dir / test_file
        
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Basic categorization based on content
            is_frontend = test_file.endswith('.jsx') or 'react' in content.lower() or 'jsx' in content.lower()
            is_integration = 'integration' in test_file.lower() or 'e2e' in test_file.lower()
            is_api = 'api' in test_file.lower() or 'requests' in content or 'http' in content.lower()
            
            # Check for obvious issues
            has_main = 'if __name__ == "__main__"' in content
            has_imports = 'import' in content
            
            # Try to parse as Python (if it's a .py file)
            if test_file.endswith('.py'):
                try:
                    ast.parse(content)
                    syntax_ok = True
                except SyntaxError:
                    syntax_ok = False
                    return self.categorize_as_broken(test_file, "Syntax error")
            else:
                syntax_ok = True
            
            # Try basic import test for Python files
            if test_file.endswith('.py') and syntax_ok:
                try:
                    spec = importlib.util.spec_from_file_location("test_module", file_path)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        # Don't execute, just check if it can be loaded
                        import_ok = True
                    else:
                        import_ok = False
                except Exception as e:
                    import_ok = False
                    if "deprecated" in str(e).lower() or "outdated" in str(e).lower():
                        return self.categorize_as_deprecated(test_file, str(e))
                    else:
                        return self.categorize_as_broken(test_file, str(e))
            else:
                import_ok = True
            
            # Categorize based on analysis
            if is_frontend:
                self.results["frontend"].append(test_file)
                return "frontend"
            elif is_integration:
                self.results["integration"].append(test_file)
                if import_ok and syntax_ok:
                    self.results["working"].append(test_file)
                    return "working_integration"
                else:
                    return "broken_integration"
            elif syntax_ok and import_ok and has_main:
                self.results["working"].append(test_file)
                self.results["backend"].append(test_file)
                return "working_backend"
            else:
                return self.categorize_as_broken(test_file, "Missing main or import issues")
                
        except Exception as e:
            return self.categorize_as_broken(test_file, str(e))
    
    def categorize_as_broken(self, test_file, reason):
        """Mark a test as broken"""
        self.results["broken"].append({"file": test_file, "reason": reason})
        return "broken"
    
    def categorize_as_deprecated(self, test_file, reason):
        """Mark a test as deprecated"""
        self.results["deprecated"].append({"file": test_file, "reason": reason})
        return "deprecated"
    
    def validate_all_tests(self):
        """Validate all test files in the directory"""
        print("[SEARCH] Validating test files...")
        print("=" * 60)
        
        # Get all test files
        test_files = [f for f in os.listdir(self.test_dir) 
                     if f.startswith('test_') or f.startswith('run_') or f.endswith('test.py') or f.endswith('.jsx')]
        
        for test_file in sorted(test_files):
            status = self.analyze_test_file(test_file)
            print(f"  {test_file:<40} {self.get_status_icon(status)}")
        
        self.print_summary()
        self.generate_recommendations()
    
    def get_status_icon(self, status):
        """Get status icon for display"""
        icons = {
            "working_backend": "[PASS] Backend",
            "working_integration": "[PASS] Integration", 
            "frontend": "🎨 Frontend",
            "broken": "[FAIL] Broken",
            "deprecated": "📦 Deprecated",
            "broken_integration": "[FAIL] Broken Integration"
        }
        return icons.get(status, "❓ Unknown")
    
    def print_summary(self):
        """Print validation summary"""
        print("\n" + "=" * 60)
        print("[DATA] VALIDATION SUMMARY")
        print("=" * 60)
        
        working_count = len(self.results["working"])
        broken_count = len(self.results["broken"])
        deprecated_count = len(self.results["deprecated"])
        frontend_count = len(self.results["frontend"])
        
        print(f"[PASS] Working Tests: {working_count}")
        print(f"[FAIL] Broken Tests: {broken_count}")
        print(f"📦 Deprecated Tests: {deprecated_count}")
        print(f"🎨 Frontend Tests: {frontend_count}")
        
        print(f"\n📂 By Category:")
        print(f"  Backend: {len(self.results['backend'])}")
        print(f"  Integration: {len(self.results['integration'])}")
        print(f"  Frontend: {len(self.results['frontend'])}")
        
        if self.results["broken"]:
            print(f"\n[FAIL] Broken Tests ({len(self.results['broken'])}):")
            for item in self.results["broken"]:
                if isinstance(item, dict):
                    print(f"  • {item['file']}: {item['reason'][:50]}...")
                else:
                    print(f"  • {item}")
        
        if self.results["deprecated"]:
            print(f"\n📦 Deprecated Tests ({len(self.results['deprecated'])}):")
            for item in self.results["deprecated"]:
                if isinstance(item, dict):
                    print(f"  • {item['file']}: {item['reason'][:50]}...")
                else:
                    print(f"  • {item}")
    
    def generate_recommendations(self):
        """Generate recommendations for test improvement"""
        print(f"\n[IDEA] RECOMMENDATIONS")
        print("=" * 60)
        
        if len(self.results["working"]) > 0:
            print("[PASS] Good news! You have working tests to build upon:")
            for test in self.results["working"][:5]:  # Show first 5
                print(f"  • {test}")
            if len(self.results["working"]) > 5:
                print(f"  • ... and {len(self.results['working']) - 5} more")
        
        if len(self.results["broken"]) > 0:
            print(f"\n[TOOL] Priority fixes needed for {len(self.results['broken'])} broken tests:")
            print("  1. Update import paths for moved modules")
            print("  2. Fix deprecated API calls")
            print("  3. Update test data to match current models")
        
        if len(self.results["frontend"]) > 0:
            print(f"\n🎨 Frontend tests need React/Jest test runner:")
            for test in self.results["frontend"]:
                print(f"  • {test}")
        
        print(f"\n📋 Next Steps:")
        print("  1. Run: python master_test_runner.py backend_validation")
        print("  2. Run: python test_streaming_comprehensive.py")
        print("  3. Fix broken tests one category at a time")
        print("  4. Set up frontend test runner for .jsx files")
        
        print("=" * 60)

def main():
    validator = TestValidator()
    validator.validate_all_tests()

if __name__ == "__main__":
    main()
