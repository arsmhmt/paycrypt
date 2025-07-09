#!/usr/bin/env python3
"""
Advanced script to remove duplicate functions in admin_routes.py
"""
import re

def remove_duplicate_functions():
    """Remove duplicate functions from admin_routes.py"""
    file_path = 'app/admin_routes.py'
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find where the first complete section ends
    # Look for the end of the get_sidebar_stats function
    pattern = r'(def get_sidebar_stats\(\):.*?return \{[^}]*\'pending_tickets\': 0[^}]*\})'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        # Find the position after the get_sidebar_stats function
        end_pos = match.end()
        
        # Look for the next function definition to find the exact end
        remaining = content[end_pos:]
        next_function_match = re.search(r'\n\n@admin_bp\.route', remaining)
        
        if next_function_match:
            # Keep everything up to the start of the duplicate section
            cutoff_point = end_pos + next_function_match.start()
            clean_content = content[:cutoff_point]
            
            # Add a comment to mark the end
            clean_content += '\n\n# End of admin routes - duplicates removed\n'
            
            # Write the cleaned content back
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(clean_content)
            
            print(f"Successfully removed duplicates from {file_path}")
            print(f"Original file: {len(content)} characters")
            print(f"Cleaned file: {len(clean_content)} characters")
            print(f"Removed: {len(content) - len(clean_content)} characters")
            
            # Count lines
            original_lines = len(content.splitlines())
            cleaned_lines = len(clean_content.splitlines())
            print(f"Original lines: {original_lines}")
            print(f"Cleaned lines: {cleaned_lines}")
            print(f"Removed lines: {original_lines - cleaned_lines}")
            
        else:
            print("Could not find next function to determine cutoff point")
    else:
        print("Could not find the get_sidebar_stats function end pattern")

if __name__ == '__main__':
    remove_duplicate_functions()
