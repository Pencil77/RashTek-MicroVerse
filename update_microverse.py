"""Generate the index.html listing page for each MicroVerse category folder.

Run from the repository root:
    python update_microverse.py

The GitHub Action ".github/workflows/update-index.yml" runs this automatically
on every push that adds or changes an app/game.
"""

import html
import os

# CONFIGURATION
# ---------------------------------------------------------
# The folders to scan -> (emoji + display name)
folders = {
    "Micro_Apps": "🚀 Micro Apps",
    "Micro_Games": "🎮 Micro Games",
}

# Friendly display names for files whose raw name reads poorly.
NAME_OVERRIDES = {
    "2048_game": "2048",
    "chess_p2p": "P2P Online Chess",
    "craft_game": "Craft World",
    "mario_game": "Super Mario Run",
    "Temple_Run": "Temple Run",
    "vice_city_game": "GTA: Vice City",
    "hunter_assassin": "Hunter Assassin",
    "save_the_dog": "Save the Dog",
    "shooting_game": "Shooting Game",
    "snake_game": "Snake",
    "musical_chairs": "Musical Chairs",
    "hunger_box": "Hunger Box · QR Order Cards",
}

# Optional one-line descriptions shown under each title.
DESCRIPTIONS = {
    "2048_game": "Slide tiles and reach 2048",
    "chess_p2p": "Real-time chess with a friend, no server needed",
    "craft_game": "2D sandbox mining and building",
    "mario_game": "Classic platformer with authentic sprites & retro audio",
    "Temple_Run": "Endless runner over temple ruins",
    "vice_city_game": "80s open-world driving, car jacking & police pursuits",
    "hunter_assassin": "Tactical 2.5D stealth operative missions",
    "save_the_dog": "Draw shields to protect the dog",
    "shooting_game": "Aim fast, shoot faster",
    "snake_game": "The classic snake, in your browser",
    "musical_chairs": "Dodge the moving chairs",
    "hunger_box": "Generate QR order cards for your store",
}

# HTML Template for the sub-pages
html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="{header} — a collection of browser apps and games from RashTek Microverse.">
    <title>{title} · Microverse</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, sans-serif; background: #222; color: #fff; text-align: center; padding: 20px; }}
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
        .link-item:focus-visible {{ outline: 3px solid #f1c40f; outline-offset: 3px; }}
        .link-item .desc {{ display: block; font-size: 13px; font-weight: 300; color: #999; margin-top: 4px; }}
        .link-item .arrow {{ color: #777; }}
        .back-btn {{ display: inline-block; margin-bottom: 20px; color: #888; text-decoration: none; font-size: 14px; }}
        .back-btn:hover {{ color: #fff; }}
        footer {{ margin-top: 50px; font-size: 12px; color: #666; }}

        @media (prefers-reduced-motion: reduce) {{
            .link-item {{ transition: none; }}
            .link-item:hover {{ transform: none; }}
        }}
    </style>
</head>
<body>
    <a href="../index.html" class="back-btn">&larr; Back to RashTek Microverse</a>
    <h1>{header}</h1>
    <h3>{count} item(s) &middot; tap to play</h3>
    <div class="container">
        {links}
    </div>
    <footer>Hosted on GitHub Pages &middot; Auto-Generated</footer>
</body>
</html>
"""


def display_name(filename):
    """Turn a raw filename into a friendly title."""
    stem = filename.rsplit(".", 1)[0]
    if stem in NAME_OVERRIDES:
        return NAME_OVERRIDES[stem]
    return stem.replace("_", " ").title()


def generate_index():
    for folder, display_name_header in folders.items():
        # Check if folder exists
        if not os.path.exists(folder):
            print(f"Warning: Folder '{folder}' not found. Skipping.")
            continue

        # Get all HTML files in the folder (excluding index.html), sorted for stable output
        files = sorted(
            f for f in os.listdir(folder)
            if f.endswith(".html") and f != "index.html"
        )

        links_html = ""
        for file in files:
            stem = file.rsplit(".", 1)[0]
            name = html.escape(display_name(file))
            desc = DESCRIPTIONS.get(stem, "")
            desc_html = f'<span class="desc">{html.escape(desc)}</span>' if desc else ""

            links_html += f"""            <a href="{html.escape(file)}" class="link-item">
                <span>{name}{desc_html}</span>
                <span class="arrow">&#9654;</span>
            </a>
"""

        if not links_html:
            links_html = "            <p style='color:#777'>No files found yet.</p>\n"

        # Fill the template
        final_html = html_template.format(
            title=display_name_header,
            header=display_name_header,
            count=len(files),
            links=links_html,
        )

        # Write the index.html file inside the folder
        output_path = os.path.join(folder, "index.html")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(final_html)

        print(f"✅ Updated {output_path} with {len(files)} items.")


if __name__ == "__main__":
    generate_index()
