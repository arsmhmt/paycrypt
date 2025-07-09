#!/usr/bin/env python3
"""
Production Cleanup Script - Identifies and reports duplications and issues
for Google Cloud deployment readiness
"""

import os
import sys
import glob
import ast
from collections import defaultdict
from typing import Dict, List, Set

class CodeAnalyzer:
    def __init__(self, root_path: str):
        self.root_path = root_path
        self.duplicates = defaultdict(list)
        self.test_files = []
        self.debug_files = []
        self.temp_files = []
        self.duplicate_functions = defaultdict(list)
        
    def scan_files(self):
        """Scan all Python files for issues"""
        print("🔍 Scanning files for duplications and issues...")
        
        # Get all Python files in root (exclude venv, __pycache__, etc.)
        pattern = os.path.join(self.root_path, "*.py")
        py_files = glob.glob(pattern)
        
        for file_path in py_files:
            filename = os.path.basename(file_path)
            
            # Categorize files
            if filename.startswith(('test_', 'debug_', 'demo_')):
                self.test_files.append(filename)
            elif filename.startswith(('quick_', 'create_test_', 'fix_', 'remove_', 'truncate_')):
                self.temp_files.append(filename)
            elif filename.startswith('verify_') or filename.startswith('check_'):
                self.debug_files.append(filename)
                
            # Check for duplicate functions
            try:
                self.analyze_functions(file_path)
            except Exception as e:
                print(f"⚠️  Could not analyze {filename}: {e}")
                
    def analyze_functions(self, file_path: str):
        """Analyze functions in a file for duplicates"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            tree = ast.parse(content)
            filename = os.path.basename(file_path)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_name = node.name
                    self.duplicate_functions[func_name].append(filename)
                    
        except (SyntaxError, UnicodeDecodeError):
            # Skip files with syntax errors or encoding issues
            pass
            
    def find_duplicate_imports(self):
        """Find files with similar import patterns (potential duplicates)"""
        print("\n📦 Checking for duplicate import patterns...")
        
        import_patterns = defaultdict(list)
        pattern = os.path.join(self.root_path, "*.py")
        
        for file_path in glob.glob(pattern):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[:20]  # Check first 20 lines
                    
                imports = []
                for line in lines:
                    line = line.strip()
                    if line.startswith(('from app import', 'import app')):
                        imports.append(line)
                        
                if imports:
                    key = tuple(sorted(imports))
                    import_patterns[key].append(os.path.basename(file_path))
                    
            except Exception:
                continue
                
        # Report patterns with multiple files
        for pattern, files in import_patterns.items():
            if len(files) > 1:
                print(f"📋 Similar import pattern in: {', '.join(files)}")
                
    def generate_report(self):
        """Generate cleanup report"""
        print("\n" + "="*60)
        print("🧹 PRODUCTION CLEANUP REPORT")
        print("="*60)
        
        # Test files
        if self.test_files:
            print(f"\n🧪 TEST FILES TO REMOVE ({len(self.test_files)}):")
            for file in sorted(self.test_files):
                print(f"   - {file}")
                
        # Debug files  
        if self.debug_files:
            print(f"\n🐛 DEBUG FILES TO REMOVE ({len(self.debug_files)}):")
            for file in sorted(self.debug_files):
                print(f"   - {file}")
                
        # Temporary files
        if self.temp_files:
            print(f"\n📝 TEMPORARY FILES TO REMOVE ({len(self.temp_files)}):")
            for file in sorted(self.temp_files):
                print(f"   - {file}")
                
        # Duplicate functions
        duplicates = {k: v for k, v in self.duplicate_functions.items() if len(v) > 1}
        if duplicates:
            print(f"\n🔄 DUPLICATE FUNCTIONS ({len(duplicates)}):")
            for func, files in duplicates.items():
                if not func.startswith('_'):  # Skip private methods
                    print(f"   - {func}() in: {', '.join(files)}")
                    
        # Check for specific issues
        self.check_specific_issues()
        
        # Recommendations
        print("\n💡 RECOMMENDATIONS:")
        print("   1. Remove all test_*, debug_*, demo_* files before deployment")
        print("   2. Remove quick_*, create_test_*, fix_*, verify_* files")  
        print("   3. Review duplicate functions for consolidation")
        print("   4. Ensure .gcloudignore excludes all test files")
        print("   5. Check that only production code remains")
        
    def check_specific_issues(self):
        """Check for specific known issues"""
        print(f"\n🔧 SPECIFIC ISSUES:")
        
        # Check for multiple client creation scripts
        client_scripts = [f for f in os.listdir(self.root_path) 
                         if f.startswith('create_') and 'client' in f and f.endswith('.py')]
        if len(client_scripts) > 1:
            print(f"   ⚠️  Multiple client creation scripts: {', '.join(client_scripts)}")
            
        # Check for multiple init scripts
        init_scripts = [f for f in os.listdir(self.root_path) 
                       if f.startswith('init_') and f.endswith('.py')]
        if len(init_scripts) > 1:
            print(f"   ⚠️  Multiple init scripts: {', '.join(init_scripts)}")
            
        # Check for database files in root
        db_files = [f for f in os.listdir(self.root_path) 
                   if f.endswith(('.db', '.sqlite', '.sqlite3'))]
        if db_files:
            print(f"   ⚠️  Database files in root (should be in instance/): {', '.join(db_files)}")
            
        # Check for test HTML files
        test_html = [f for f in os.listdir(self.root_path) 
                    if f.endswith('.html') and ('test' in f or 'debug' in f)]
        if test_html:
            print(f"   ⚠️  Test HTML files: {', '.join(test_html)}")

def main():
    """Main cleanup analysis"""
    root_path = os.path.dirname(os.path.abspath(__file__))
    analyzer = CodeAnalyzer(root_path)
    
    print("🚀 PRODUCTION DEPLOYMENT CLEANUP ANALYSIS")
    print("=" * 50)
    
    analyzer.scan_files()
    analyzer.find_duplicate_imports()
    analyzer.generate_report()
    
    print(f"\n✅ Analysis complete. Check the report above.")
    print(f"📁 Analyzed directory: {root_path}")

if __name__ == "__main__":
    main()
