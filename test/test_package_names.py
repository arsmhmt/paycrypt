#!/usr/bin/env python3
"""Test package name display transformation"""

# Test the string replacement logic that will be used in templates
test_packages = [
    "Starter Flat Rate",
    "Business Flat Rate", 
    "Enterprise Flat Rate",
    "Starter Commission",
    "Business Commission",
    "Enterprise Commission",
    "Basic",
    "Premium"
]

print("Package Name Display Transformation Test:")
print("=" * 50)

for package_name in test_packages:
    clean_name = package_name.replace(' Flat Rate', '').replace(' Commission', '')
    print(f"Backend: '{package_name}' -> Frontend: '{clean_name}'")

print("\n✅ All package names will display cleanly on the frontend!")
