"""
Search for website buttons in ehko_control.py
This will show us the actual structure so we can add the button correctly
"""

file_path = r"C:\EhkoVaults\EhkoForge\5.0 Scripts\ehko_control.py"

print("Reading ehko_control.py...")
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"File has {len(lines)} lines\n")

# Find WebsiteTab class
print("=" * 70)
print("SEARCHING FOR WEBSITETAB CLASS")
print("=" * 70)

found_websitetab = False
for i, line in enumerate(lines):
    if 'class WebsiteTab' in line:
        found_websitetab = True
        print(f"\nFound WebsiteTab at line {i+1}")
        print("\nShowing next 100 lines with button-related code:\n")
        
        for j in range(i, min(i+150, len(lines))):
            # Show lines with button/URL keywords
            if any(keyword in lines[j].lower() for keyword in ['btn_', 'button', 'ttk.button', '_open_url', 'website_url']):
                print(f"{j+1}: {lines[j].rstrip()}")
        break

if not found_websitetab:
    print("WebsiteTab class not found!")

print("\n" + "=" * 70)
print("SEARCHING FOR ANY 'TEST' REFERENCES")
print("=" * 70 + "\n")

for i, line in enumerate(lines):
    if 'test' in line.lower() and any(kw in line.lower() for kw in ['button', 'btn', 'url', 'page']):
        print(f"{i+1}: {line.rstrip()}")

print("\n" + "=" * 70)
print("DONE - Review output above to find where to add the button")
print("=" * 70)

input("\nPress Enter to close...")
