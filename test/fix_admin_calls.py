#!/usr/bin/env python3
"""Script to fix log_admin_action calls throughout the codebase"""

import re

def fix_log_admin_action_calls(file_path):
    """Fix log_admin_action parameter names in the given file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace parameter names
    content = re.sub(r'admin_id=([^,\)]+)', r'# admin_id parameter removed', content)
    content = re.sub(r'details=([^,\)]+)', r'description=\1', content)
    content = re.sub(r'old_value=([^,\)]+)', r'old_values=\1', content)
    content = re.sub(r'new_value=([^,\)]+)', r'new_values=\1', content)
    
    # Remove the admin_id comment lines
    content = re.sub(r'\s*# admin_id parameter removed,?\n', '', content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Fixed log_admin_action calls in {file_path}")

if __name__ == "__main__":
    fix_log_admin_action_calls("d:/CODES/main_apps/cpgateway/app/admin/routes.py")
