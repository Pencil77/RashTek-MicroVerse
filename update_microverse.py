"""Generate the index.html listing page for each MicroVerse category folder.

Run from the repository root:
    python update_microverse.py

The GitHub Action ".github/workflows/update-index.yml" runs this automatically
on every push that adds or changes an app/game.

The index renders as an app-launcher style grid: icon tile with the short
name underneath. Icons come from `<folder>/icons/<stem>.png|.svg`; if a file
is missing, the EMOJIS fallback is shown instead.
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
    "chess_p2p": "Chess Online",
    "craft_game": "Craft World",
    "mario_game": "Mario Run",
    "Temple_Run": "Temple Run",
    "vice_city_game": "GTA Vice City",
    "hunter_assassin": "Hunter Assassin",
    "save_the_dog": "Save the Dog",
    "shooting_game": "Shooting Game",
    "snake_game": "Snake",
    "musical_chairs": "Musical Chairs",
    "kombat_arena": "Kombat Arena",
    "mili_militia": "Mili Militia",
    "hunger_box": "Hunger Box",
}

# Optional one-line descriptions shown as a tooltip on each card.
DESCRIPTIONS = {
    "2048_game": "Slide tiles and reach 2048",
    "chess_p2p": "Real-time chess with a friend, no server needed",
    "craft_game": "2D sandbox mining and building with retro pixel audio",
    "mario_game": "Classic platformer with authentic sprites & retro audio",
    "Temple_Run": "Endless runner over temple ruins",
    "vice_city_game": "Real 3D Miami open-world: driving, on-foot carjacking, police chases & synthwave",
    "hunter_assassin": "Tactical 2.5D stealth operative missions",
    "save_the_dog": "Draw shields to protect the dog",
    "shooting_game": "Neon space arcade shooter with retro blaster synth audio",
    "snake_game": "Neon grid snake with retro synth chimes",
    "musical_chairs": "Dodge the moving chairs",
    "kombat_arena": "Tekken-style 1v1 arcade fighter · 4 fighters, combos, specials & AI — best of 3",
    "mili_militia": "Explosive 2D jetpack deathmatch — fly, aim & blast 3 AI soldiers",
    "hunger_box": "Generate QR order cards for your store",
}

# Emoji shown when an icon image is missing entirely.
EMOJIS = {
    "2048_game": "🔢", "chess_p2p": "♞", "craft_game": "⛏️", "mario_game": "🍄",
    "Temple_Run": "🏃", "vice_city_game": "🌆", "hunter_assassin": "🗡️",
    "save_the_dog": "🐶", "shooting_game": "🔫", "snake_game": "🐍",
    "musical_chairs": "🎵", "kombat_arena": "🥊", "mili_militia": "🚁",
    "hunger_box": "🍔",
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
        body {{
            font-family: 'Segoe UI', Tahoma, sans-serif;
            background: radial-gradient(1200px 600px at 50% -10%, #2b2b40, #191922 60%, #101014);
            color: #fff; text-align: center; padding: 24px 16px; min-height: 100vh;
        }}
        h1 {{ color: #f1c40f; margin-bottom: 10px; }}
        h3 {{ color: #888; font-weight: 300; margin-bottom: 40px; }}

        .container {{
            max-width: 780px; margin: 0 auto;
            display: grid; gap: 22px 14px;
            grid-template-columns: repeat(auto-fill, minmax(96px, 1fr));
        }}

        .app-card {{
            text-decoration: none; color: #eee;
            display: flex; flex-direction: column; align-items: center; gap: 10px;
        }}
        .app-icon {{
            width: 92px; height: 92px; border-radius: 23%;
            overflow: hidden;
            background: linear-gradient(145deg, #33334a, #171722);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.45), inset 0 0 0 1px rgba(255, 255, 255, 0.09);
            display: flex; align-items: center; justify-content: center;
            transition: transform 0.25s ease, box-shadow 0.25s ease;
        }}
        .app-icon img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
        .app-icon .emoji {{ font-size: 44px; line-height: 1; }}
        .app-card:hover .app-icon, .app-card:focus-visible .app-icon {{
            transform: translateY(-5px) scale(1.05);
            box-shadow: 0 14px 28px rgba(0, 0, 0, 0.55), 0 0 24px rgba(46, 204, 113, 0.28);
        }}
        .app-card:focus-visible {{ outline: 3px solid #f1c40f; outline-offset: 4px; border-radius: 8px; }}
        .app-name {{
            font-size: 12.5px; font-weight: 600; color: #ddd;
            max-width: 102px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
        }}
        .app-card:hover .app-name {{ color: #fff; }}

        .back-btn {{ display: inline-block; margin-bottom: 20px; color: #888; text-decoration: none; font-size: 14px; }}
        .back-btn:hover {{ color: #fff; }}
        footer {{ margin-top: 50px; font-size: 12px; color: #666; }}

        @media (prefers-reduced-motion: reduce) {{
            .app-card:hover .app-icon, .app-icon {{ transition: none; transform: none; }}
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
    <script>
        document.querySelectorAll('.app-icon img').forEach(function (img) {{
            img.addEventListener('error', function () {{
                var s = document.createElement('span');
                s.className = 'emoji';
                s.textContent = img.dataset.emoji || '🎮';
                img.replaceWith(s);
            }}, {{ once: true }});
        }});
    </script>
</body>
</html>
"""


def display_name(filename):
    """Turn a raw filename into a friendly title."""
    stem = filename.rsplit(".", 1)[0]
    if stem in NAME_OVERRIDES:
        return NAME_OVERRIDES[stem]
    return stem.replace("_", " ").title()


def icon_for(folder, stem):
    """Return the index.html-relative icon path for a stem, or None."""
    for ext in (".png", ".svg", ".webp"):
        candidate = os.path.join(folder, "icons", stem + ext)
        if os.path.exists(candidate):
            return os.path.relpath(candidate, folder)
    return None


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
            desc = html.escape(DESCRIPTIONS.get(stem, NAME_OVERRIDES.get(stem, "")))
            emoji = html.escape(EMOJIS.get(stem, "🎮"))
            icon = icon_for(folder, stem)

            if icon:
                inner = (
                    f'<img src="{html.escape(icon)}" alt="{name}" '
                    f'loading="lazy" data-emoji="{emoji}">'
                )
            else:
                inner = f'<span class="emoji">{emoji}</span>'

            links_html += f"""            <a href="{html.escape(file)}" class="app-card" title="{desc}">
                <span class="app-icon">{inner}</span>
                <span class="app-name">{name}</span>
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
