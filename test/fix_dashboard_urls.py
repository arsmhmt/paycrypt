#!/usr/bin/env python3
"""Script to fix admin.dashboard URL references"""

import os
import re

def fix_admin_dashboard_urls(directory):
    """Fix all admin.dashboard references to admin.admin_dashboard"""
    files_fixed = 0
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Replace admin.dashboard with admin.admin_dashboard
                    original_content = content
                    content = content.replace("'admin.dashboard'", "'admin.admin_dashboard'")
                    content = content.replace('"admin.dashboard"', '"admin.admin_dashboard"')
                    content = content.replace("admin.dashboard", "admin.admin_dashboard")
                    
                    if content != original_content:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        print(f"Fixed: {file_path}")
                        files_fixed += 1
                        
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
    
    return files_fixed

if __name__ == "__main__":
    template_dir = "d:/CODES/main_apps/cpgateway/app/templates"
    fixed_count = fix_admin_dashboard_urls(template_dir)
    print(f"Fixed {fixed_count} template files")
