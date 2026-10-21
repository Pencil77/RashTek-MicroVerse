import os
import re

# --- CONFIGURATION ---
# Output goes to the folder that contains 'python_based_games', resolved
# relative to this script so it works no matter where you run it from.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(SCRIPT_DIR)

# 1. SETUP THE INDEX HTML HEADER
index_content = """
<!DOCTYPE html>
<html>
<head>
    <title>My Termux Games</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #222; color: #fff; text-align: center; padding: 20px; }
        h1 { color: #f1c40f; margin-bottom: 30px; }
        .game-container { max-width: 600px; margin: 0 auto; }
        .game-link { 
            display: block; background: #333; margin: 15px 0; padding: 20px; 
            text-decoration: none; color: white; border-radius: 10px; 
            border-left: 5px solid #2ecc71; transition: 0.3s;
            text-align: left; font-size: 18px; font-weight: bold;
            display: flex; justify-content: space-between; align-items: center;
        }
        .game-link:hover { background: #444; border-left-color: #f1c40f; transform: translateX(5px); }
        .arrow { color: #777; }
        .note { font-size: 12px; color: #777; margin-top: 50px; }
    </style>
</head>
<body>
    <h1>🎮 My Game Collection</h1>
    <div class="game-container">
"""

print(f"--- 🔄 Converting Games to Parent Directory ({PARENT_DIR}) ---")

# 2. SCAN THIS SCRIPT'S FOLDER FOR ALL PYTHON FILES
files = [f for f in os.listdir(SCRIPT_DIR) if f.endswith('.py')]
files.sort()

count = 0

for py_file in files:
    if py_file == os.path.basename(__file__):
        continue

    with open(os.path.join(SCRIPT_DIR, py_file), 'r', encoding='utf-8') as f:
        content = f.read()

    # 3. LOOK FOR THE HTML TEMPLATE
    match = re.search(r'(?:GAME|HTML)?_?TEMPLATE\s*=\s*"""(.*?)"""', content, re.DOTALL)
    
    if match:
        html_content = match.group(1)
        
        # Determine new filename (e.g., snake.html)
        html_filename = py_file.replace('.py', '.html')
        
        # Path to save in PARENT directory
        target_path = os.path.join(PARENT_DIR, html_filename)
        
        # Display Name generation
        display_name = py_file.replace('.py', '').replace('_', ' ').title()
        display_name = display_name.replace("Game", "").strip()
        if display_name == "Game 2048": display_name = "2048 Puzzle"

        # Write the HTML file to the PARENT directory
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        print(f"✅ Generated: {target_path} ({display_name})")
        
        # Add to index (Link refers to file in same directory as index, so no ../ needed in href)
        index_content += f'<a href="{html_filename}" class="game-link"><span>{display_name}</span> <span class="arrow">▶</span></a>\n'
        count += 1
    else:
        print(f"⚠️  Skipped {py_file} (No HTML template found)")

# 4. FINISH INDEX HTML AND SAVE TO PARENT
index_content += """
    </div>
    <p class="note">Hosted on GitHub Pages • Auto-Generated</p>
</body></html>
"""

if count > 0:
    index_path = os.path.join(PARENT_DIR, 'index.html')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index_content)
    print(f"\n🎉 Success! 'index.html' and {count} games saved to parent folder.")
else:
    print("\n❌ No compatible game files found.")

