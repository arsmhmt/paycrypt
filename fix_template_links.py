import re

# Read the template file
with open('app/templates/pricing.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find all registration links
pattern = r'href="([^"]*?register[^"]*?package=)([^"]+)"'
matches = re.findall(pattern, content, re.IGNORECASE)

if matches:
    print("Found registration links:")
    for prefix, pkg in matches:
        print(f"- {prefix}{pkg}")
        
    # Update the links to use shorter package names
    updated_content = re.sub(
        r'(href="[^"]*?register[^"]*?package=)([^"]+)"',
        lambda m: f'{m.group(1)}{m.group(2).split("_")[0]}"',
        content
    )
    
    # Save the updated content
    with open('app/templates/pricing.html', 'w', encoding='utf-8') as f:
        f.write(updated_content)
    print("\nTemplate updated with shorter package names in registration links.")
else:
    print("No registration links found in the template.")
    print("Please check the template file manually and update the links to use the shorter package names.")
    print("Example: 'starter_flat_rate' should be just 'starter'")
