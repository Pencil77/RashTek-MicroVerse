import os

# CONFIGURATION
# ---------------------------------------------------------
# The folders to scan
folders = {
    "Micro_Apps": "🚀 Micro Apps",
    "Micro_Games": "🎮 Micro Games"
}

# HTML Template for the sub-pages
html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>{title} - Microverse</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; background: #222; color: #fff; text-align: center; padding: 20px; }}
        h1 {{ color: #f1c40f; margin-bottom: 10px; }}
        h3 {{ color: #888; font-weight: 300; margin-bottom: 40px; }}
        .container {{ max-width: 600px; margin: 0 auto; }}
        
        .link-item {{ 
            display: flex; justify-content: space-between; align-items: center;
            background: #333; margin: 15px 0; padding: 20px; 
            text-decoration: none; color: white; border-radius: 10px; 
            border-left: 5px solid #2ecc71; transition: 0.3s;
            font-size: 18px; font-weight: bold;
        }}
        .link-item:hover {{ background: #444; border-left-color: #f1c40f; transform: translateX(5px); }}
        .back-btn {{ display: inline-block; margin-bottom: 20px; color: #888; text-decoration: none; font-size: 14px; }}
        .back-btn:hover {{ color: #fff; }}
    </style>
</head>
<body>
    <a href="../index.html" class="back-btn">← Back to RashTek Microverse</a>
    <h1>{header}</h1>
    <h3>Directory Listing</h3>
    <div class="container">
        {links}
    </div>
</body>
</html>
"""

def generate_index():
    for folder, display_name in folders.items():
        # Check if folder exists
        if not os.path.exists(folder):
            print(f"Warning: Folder '{folder}' not found. Skipping.")
            continue

        # Get all HTML files in the folder (excluding index.html)
        files = [f for f in os.listdir(folder) if f.endswith('.html') and f != 'index.html']
        
        links_html = ""
        for file in files:
            # Create a clean name (e.g., "shooting_game.html" -> "Shooting Game")
            clean_name = file.replace(".html", "").replace("_", " ").title()
            
            links_html += f"""
            <a href="{file}" class="link-item">
                <span>{clean_name}</span> 
                <span style="color:#777">▶</span>
            </a>
            """
        
        if not links_html:
            links_html = "<p style='color:#777'>No files found yet.</p>"

        # Fill the template
        final_html = html_template.format(
            title=display_name,
            header=display_name,
            links=links_html
        )

        # Write the index.html file inside the folder
        output_path = os.path.join(folder, "index.html")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(final_html)
        
        print(f"✅ Updated {output_path} with {len(files)} items.")

if __name__ == "__main__":
    generate_index()

