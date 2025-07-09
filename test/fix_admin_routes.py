#!/usr/bin/env python3
"""
Script to remove duplicate content from admin_routes.py
The file appears to have content duplicated after line 2541
"""

def fix_admin_routes():
    """Remove duplicate content from admin_routes.py"""
    with open('app/admin_routes.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find the last occurrence of the get_sidebar_stats function end
    # We want to keep everything up to and including the first complete section
    
    # Look for the pattern that indicates the end of the first section
    cutoff_line = None
    for i, line in enumerate(lines):
        if 'pending_tickets\': 0' in line and i > 2500:  # Look after line 2500
            # Check if this is the end of the exception handler in get_sidebar_stats
            if i + 10 < len(lines) and any('@admin_bp.route' in lines[j] for j in range(i+1, min(i+10, len(lines)))):
                cutoff_line = i + 2  # Keep the closing brace and one empty line
                break
    
    if cutoff_line:
        # Keep only the first complete section
        cleaned_lines = lines[:cutoff_line]
        cleaned_lines.append('\n# End of admin routes - duplicates removed\n')
        
        # Write the cleaned file
        with open('app/admin_routes.py', 'w', encoding='utf-8') as f:
            f.writelines(cleaned_lines)
        
        print(f"Successfully cleaned admin_routes.py")
        print(f"Original lines: {len(lines)}")
        print(f"Cleaned lines: {len(cleaned_lines)}")
        print(f"Removed lines: {len(lines) - len(cleaned_lines)}")
        
        return True
    else:
        print("Could not find the cutoff point")
        return False

if __name__ == '__main__':
    fix_admin_routes()
