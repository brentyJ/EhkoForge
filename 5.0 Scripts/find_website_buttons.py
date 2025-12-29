"""
Find the website page buttons in the Website tab
"""

file_path = r"C:\EhkoVaults\EhkoForge\5.0 Scripts\ehko_control.py"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("Searching for website page buttons (Home, About, Projects, Contact)...\n")

for i, line in enumerate(lines):
    # Look for the Home button - this will show us the pattern
    if '"Home"' in line and 'Button' in line:
        print(f"Found Home button at line {i+1}")
        print("\nShowing surrounding context (20 lines):\n")
        
        start = max(0, i-5)
        end = min(len(lines), i+20)
        
        for j in range(start, end):
            print(f"{j+1}: {lines[j].rstrip()}")
        
        print("\n" + "="*70)
        print("Add the Feature Demos button after the Test Page button")
        print("="*70)
        break

input("\nPress Enter to close...")
