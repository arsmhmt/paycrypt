#!/usr/bin/env python3
"""
Script to fix log_security_event parameter issues
"""

import re
import os

def fix_log_security_event_calls(file_path):
    """Fix log_security_event calls to use correct parameter structure"""
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Pattern to match log_security_event calls
    pattern = r'log_security_event\(\s*([^)]+)\)'
    
    def fix_call(match):
        params = match.group(1)
        
        # Skip if already has details= parameter
        if 'details=' in params:
            return match.group(0)
        
        # Parse parameters
        lines = params.split('\n')
        new_params = []
        details = []
        
        for line in lines:
            line = line.strip()
            if not line or line == ',':
                continue
                
            # Extract parameter name and value
            if '=' in line:
                param_name, param_value = line.split('=', 1)
                param_name = param_name.strip()
                param_value = param_value.strip().rstrip(',')
                
                if param_name in ['event_type', 'user_id', 'severity', 'ip_address']:
                    new_params.append(f"{param_name}={param_value}")
                else:
                    # Move to details dict
                    details.append(f"'{param_name}': {param_value}")
            else:
                # Positional parameter
                new_params.append(line.rstrip(','))
        
        # Build new call
        result = "log_security_event(\n"
        
        # Add main parameters
        for param in new_params:
            result += f"        {param},\n"
        
        # Add details if any
        if details:
            result += "        details={\n"
            for detail in details:
                result += f"            {detail},\n"
            result += "        }\n"
        
        result += "    )"
        
        return result
    
    # Apply fixes
    content = re.sub(pattern, fix_call, content, flags=re.DOTALL)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed log_security_event calls in {file_path}")
        return True
    else:
        print(f"No changes needed in {file_path}")
        return False

def fix_all_files():
    """Fix log_security_event calls in all relevant files"""
    files_to_fix = [
        'app/admin/routes.py',
        'app/auth_routes.py',
        'app/client_routes.py',
        'app/utils/security.py'
    ]
    
    base_dir = 'd:/CODES/main_apps/cpgateway'
    
    for file_path in files_to_fix:
        full_path = os.path.join(base_dir, file_path)
        fix_log_security_event_calls(full_path)

if __name__ == "__main__":
    fix_all_files()
