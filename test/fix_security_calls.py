#!/usr/bin/env python3
"""Script to fix log_security_event calls throughout the codebase"""

import re

def fix_log_security_event_calls(file_path):
    """Fix log_security_event parameter structure in the given file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match log_security_event calls with the old format
    pattern = r'log_security_event\(\s*event_type=([^,\)]+),\s*user_id=([^,\)]+),\s*description=([^,\)]+),\s*ip_address=([^,\)]+),\s*user_agent=([^,\)]+)\s*\)'
    
    def replacement(match):
        event_type = match.group(1).strip()
        user_id = match.group(2).strip() 
        description = match.group(3).strip()
        ip_address = match.group(4).strip()
        user_agent = match.group(5).strip()
        
        return f"""log_security_event(
            event_type={event_type},
            details={{
                'description': {description},
                'user_agent': {user_agent}
            }},
            user_id={user_id},
            ip_address={ip_address}
        )"""
    
    content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Fixed log_security_event calls in {file_path}")

if __name__ == "__main__":
    fix_log_security_event_calls("d:/CODES/main_apps/cpgateway/app/admin/routes.py")
