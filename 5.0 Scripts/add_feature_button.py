"""
Add Feature Demos button to ehko_control.py
Run this script to automatically add the button
"""
import re

file_path = r"C:\EhkoVaults\EhkoForge\5.0 Scripts\ehko_control.py"

print("Reading ehko_control.py...")
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern to find: Test Page button and its pack() line
pattern = r'(btn_test = ttk\.Button\(pages_frame, text="Test Page"[^\n]+\n\s+btn_test\.pack[^\n]+\n)'

match = re.search(pattern, content, re.DOTALL)

if match:
    print("✓ Found Test Page button")
    
    # Add Feature Demos button right after
    new_button = '''
        btn_feature_demos = ttk.Button(pages_frame, text="Feature Demos", command=lambda: self._open_url(f"{WEBSITE_URL}/feature-demos"), width=15)
        btn_feature_demos.pack(side=LEFT, padx=5)
'''
    
    # Insert after the Test Page button
    insertion_point = match.end()
    new_content = content[:insertion_point] + new_button + content[insertion_point:]
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✓ Successfully added Feature Demos button!")
    print(f"✓ Button added after line {content[:insertion_point].count(chr(10)) + 1}")
    
else:
    print("✗ Could not find Test Page button")
    print("\nSearching for any button pattern...")
    
    if '"Test Page"' in content:
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if 'Test Page' in line:
                print(f"Found 'Test Page' at line {i}: {line.strip()}")

print("\nDone!")
input("Press Enter to close...")
