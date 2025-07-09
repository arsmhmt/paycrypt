#!/usr/bin/env python3
"""
Script to properly truncate admin_routes.py to remove duplicates
"""

def truncate_admin_routes():
    """Truncate admin_routes.py to remove duplicates"""
    
    # Read the file
    with open('app/admin_routes.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Keep only the first 2541 lines (the original complete section)
    # Line 2541 is the end of the first get_sidebar_stats function
    truncated_lines = lines[:2541]
    
    # Add a final comment
    truncated_lines.append('\n# End of admin routes - duplicates removed\n')
    
    # Write the truncated file
    with open('app/admin_routes.py', 'w', encoding='utf-8') as f:
        f.writelines(truncated_lines)
    
    print(f"Successfully truncated admin_routes.py")
    print(f"Original lines: {len(lines)}")
    print(f"Truncated lines: {len(truncated_lines)}")
    print(f"Removed lines: {len(lines) - len(truncated_lines)}")
    
    return True

if __name__ == '__main__':
    truncate_admin_routes()
