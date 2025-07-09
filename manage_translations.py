#!/usr/bin/env python3
"""
Translation management script for PayCrypt
Usage:
    python manage_translations.py extract
    python manage_translations.py update
    python manage_translations.py compile
    python manage_translations.py init <language>
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(cmd, shell=True, check=True, cwd=cwd, 
                              capture_output=True, text=True)
        print(f"✓ {cmd}")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {cmd}")
        print(f"Error: {e.stderr}")
        return False

def extract_translations():
    """Extract translatable strings to messages.pot"""
    print("Extracting translatable strings...")
    return run_command("pybabel extract -F babel.cfg -k _ -o messages.pot .")

def update_translations():
    """Update existing translation files"""
    print("Updating translation files...")
    return run_command("pybabel update -i messages.pot -d translations")

def compile_translations():
    """Compile translation files"""
    print("Compiling translation files...")
    return run_command("pybabel compile -d translations")

def init_language(language):
    """Initialize a new language"""
    print(f"Initializing translation for language: {language}")
    return run_command(f"pybabel init -i messages.pot -d translations -l {language}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python manage_translations.py <command> [args]")
        print("Commands: extract, update, compile, init <language>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "extract":
        extract_translations()
    elif command == "update":
        if not extract_translations():
            sys.exit(1)
        update_translations()
    elif command == "compile":
        compile_translations()
    elif command == "init":
        if len(sys.argv) < 3:
            print("Usage: python manage_translations.py init <language>")
            sys.exit(1)
        language = sys.argv[2]
        if not extract_translations():
            sys.exit(1)
        init_language(language)
    elif command == "all":
        print("Running full translation workflow...")
        if extract_translations() and update_translations() and compile_translations():
            print("✓ All translation tasks completed successfully!")
        else:
            print("✗ Some translation tasks failed!")
            sys.exit(1)
    else:
        print(f"Unknown command: {command}")
        print("Commands: extract, update, compile, init <language>, all")
        sys.exit(1)

if __name__ == "__main__":
    main()
