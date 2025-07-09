#!/usr/bin/env python3
"""
Fix duplicate function definitions in admin_routes.py
"""

def fix_duplicates():
    input_file = 'app/admin_routes.py'
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Track which functions we've seen
    seen_functions = set()
    lines = content.split('\n')
    result_lines = []
    skip_until_next_function = False
    current_function = None
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Check if this is a function definition we need to track
        if '@admin_bp.route(' in line and 'endpoint=' in line:
            # Extract endpoint name
            if "endpoint='export_clients'" in line:
                current_function = 'export_clients'
            elif "endpoint='withdrawal_stats_api'" in line:
                current_function = 'withdrawal_stats_api'
            else:
                current_function = None
            
            # If we've seen this function before, skip it
            if current_function and current_function in seen_functions:
                print(f"Skipping duplicate function: {current_function} at line {i+1}")
                skip_until_next_function = True
                i += 1
                continue
            elif current_function:
                seen_functions.add(current_function)
                print(f"Keeping first occurrence of: {current_function} at line {i+1}")
        
        # If we're skipping, look for the next function or significant break
        if skip_until_next_function:
            # Stop skipping when we find another @admin_bp.route or end of function
            if ('@admin_bp.route(' in line or 
                (line.strip() and not line.startswith(' ') and not line.startswith('\t') and 
                 line.strip() != '' and not line.startswith('#'))):
                skip_until_next_function = False
                current_function = None
                # Don't skip this line, process it normally
            else:
                # Skip this line
                i += 1
                continue
        
        # Add the line to result
        result_lines.append(line)
        i += 1
    
    # Write the fixed content
    with open(input_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(result_lines))
    
    print(f"Fixed duplicates in {input_file}")

if __name__ == '__main__':
    fix_duplicates()
