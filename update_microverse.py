"""Generate the index.html pages for RashTek MicroVerse.

Run from the repository root:
    python update_microverse.py

The GitHub Action ".github/workflows/update-index.yml" runs this automatically
on every push that adds or changes an app/game.

- The HOME page (index.html) is an app-launcher with a top tab bar:
  Games (default) and Apps, switched without navigation (hash-based).
- Each category folder keeps its own index.html list page.

Cards show an icon tile from `<folder>/icons/<stem>.png|.svg` with the short
name underneath; EMOJIS provide the fallback when a file is missing.
"""

import html
import os

# CONFIGURATION
# ---------------------------------------------------------
# Folder -> (emoji + display name, tagline shown under the heading)
folders = {
    "Micro_Apps": ("🚀 Micro Apps", "Utilities, Calculators & Tools"),
    "Micro_Games": ("🎮 Micro Games", "Arcade, Logic & Fun"),
}

PAGES = {  # heading used on a category folder's own index.html
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
    "hunter_assassin": "Tactical 2.5D stealth operative missions with 4 threat levels (Cadet → Nightmare)",
    "save_the_dog": "Draw shields to protect the dog",
    "shooting_game": "Neon space arcade shooter with retro blaster synth audio",
    "snake_game": "Neon grid snake with retro synth chimes",
    "musical_chairs": "Dodge the moving chairs",
    "kombat_arena": "Tekken-style 1v1 arcade fighter · 4 fighters, combos, specials & AI — best of 3",
    "mili_militia": "Explosive 2D jetpack deathmatch — fly, aim & blast 3 AI soldiers",
    "hunger_box": "Generate QR order cards for your store",
}

# IDs used for the tab bar on the home page.
TAB_IDS = {"Micro_Apps": "apps", "Micro_Games": "games"}
DEFAULT_TAB = "games"  # the site opens straight into the games screen

# Emoji shown when an icon image is missing entirely.
EMOJIS = {
    "2048_game": "🔢", "chess_p2p": "♞", "craft_game": "⛏️", "mario_game": "🍄",
    "Temple_Run": "🏃", "vice_city_game": "🌆", "hunter_assassin": "🗡️",
    "save_the_dog": "🐶", "shooting_game": "🔫", "snake_game": "🐍",
    "musical_chairs": "🎵", "kombat_arena": "🥊", "mili_militia": "🚁",
    "hunger_box": "🍔",
}

# ---------------------------------------------------------
# Shared styles for the card grid (home page + folder pages)
STYLE = """
        body {
            font-family: 'Segoe UI', Tahoma, sans-serif;
            background: radial-gradient(1200px 600px at 50% -10%, #2b2b40, #191922 60%, #101014);
            color: #fff; text-align: center; padding: 24px 16px; min-height: 100vh; margin: 0;
        }
        h1 { color: #f1c40f; margin-bottom: 10px; }

        .grid {
            max-width: 720px; margin: 0 auto;
            display: grid; gap: 20px 12px;
            grid-template-columns: repeat(auto-fill, minmax(84px, 1fr));
        }

        .app-card {
            text-decoration: none; color: #eee;
            display: flex; flex-direction: column; align-items: center; gap: 9px;
        }
        .app-icon {
            width: 72px; height: 72px; border-radius: 23%;
            overflow: hidden;
            background: linear-gradient(145deg, #33334a, #171722);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.45), inset 0 0 0 1px rgba(255, 255, 255, 0.09);
            display: flex; align-items: center; justify-content: center;
            transition: transform 0.25s ease, box-shadow 0.25s ease;
        }
        .app-icon img { width: 100%; height: 100%; object-fit: cover; display: block; }
        .app-icon .emoji { font-size: 34px; line-height: 1; }
        .app-card:hover .app-icon, .app-card:focus-visible .app-icon {
            transform: translateY(-5px) scale(1.05);
            box-shadow: 0 14px 28px rgba(0, 0, 0, 0.55), 0 0 24px rgba(46, 204, 113, 0.28);
        }
        .app-card:focus-visible { outline: 3px solid #f1c40f; outline-offset: 4px; border-radius: 8px; }
        .app-name {
            font-size: 12px; font-weight: 600; color: #ddd;
            max-width: 92px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
        }
        .app-card:hover .app-name { color: #fff; }

        @media (prefers-reduced-motion: reduce) {
            .app-card:hover .app-icon, .app-icon { transition: none; transform: none; }
        }
"""

# ---------------------------------------------------------
# Card rendering helpers


def display_name(filename):
    """Turn a raw filename into a friendly title."""
    stem = filename.rsplit(".", 1)[0]
    if stem in NAME_OVERRIDES:
        return NAME_OVERRIDES[stem]
    return stem.replace("_", " ").title()


def icon_for(folder, stem):
    """Return the folder-relative icon path for a stem, or None."""
    for ext in (".png", ".svg", ".webp"):
        candidate = os.path.join(folder, "icons", stem + ext)
        if os.path.exists(candidate):
            return os.path.relpath(candidate, folder)
    return None


def cards_for(folder, href_prefix="", icon_prefix=""):
    """Build the .app-card markup block for one folder."""
    if not os.path.exists(folder):
        return []
    files = sorted(
        f for f in os.listdir(folder)
        if f.endswith(".html") and f != "index.html"
    )
    cards = []
    for file in files:
        stem = file.rsplit(".", 1)[0]
        name = html.escape(display_name(file))
        desc = html.escape(DESCRIPTIONS.get(stem, NAME_OVERRIDES.get(stem, "")))
        emoji = html.escape(EMOJIS.get(stem, "🎮"))
        icon = icon_for(folder, stem)
        if icon:
            inner = (
                f'<img src="{html.escape(icon_prefix + icon)}" alt="{name}" '
                f'loading="lazy" data-emoji="{emoji}">'
            )
        else:
            inner = f'<span class="emoji">{emoji}</span>'
        cards.append(
            f'            <a href="{html.escape(href_prefix + file)}" class="app-card" title="{desc}">\n'
            f'                <span class="app-icon">{inner}</span>\n'
            f'                <span class="app-name">{name}</span>\n'
            f"            </a>\n"
        )
    return cards


# ---------------------------------------------------------
# Category folder pages (kept for back-navigation / deep links)
folder_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="{header} — a collection of browser apps and games from RashTek Microverse.">
    <title>{title} · Microverse</title>
    <style>
{style}
        h3 {{ color: #888; font-weight: 300; margin-bottom: 40px; }}
        .back-btn {{ display: inline-block; margin-bottom: 20px; color: #888; text-decoration: none; font-size: 14px; }}
        .back-btn:hover {{ color: #fff; }}
        footer {{ margin-top: 50px; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <a href="../index.html" class="back-btn">&larr; Back to RashTek Microverse</a>
    <h1>{header}</h1>
    <h3>{count} item(s) &middot; tap to play</h3>
{links}
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

# ---------------------------------------------------------
# Home page with a top tab bar (Games default, Apps secondary)
home_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Microverse by RashTek</title>
    <meta name="description" content="RashTek Microverse with micro apps and games.">
    <style>
{style}
        .brand {{ margin: 6px 0 18px; }}
        .brand h1 {{ font-size: 2.6rem; margin: 0; letter-spacing: 3px; }}
        .brand h3 {{
            font-size: 0.95rem; margin-top: 4px; color: #888; font-weight: 300;
            text-transform: uppercase; letter-spacing: 5px;
        }}

        .tabs {{
            position: sticky; top: 12px; z-index: 10;
            display: inline-flex; gap: 6px; margin-bottom: 30px;
            background: rgba(18, 18, 28, 0.85); backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 999px; padding: 6px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.45);
        }}
        .tab {{
            display: inline-flex; align-items: center; gap: 8px;
            padding: 10px 26px; border: none; border-radius: 999px;
            background: transparent; color: #9aa; cursor: pointer;
            font-family: inherit; font-size: 15px; font-weight: 600;
            transition: all 0.25s ease;
        }}
        .tab:hover {{ color: #fff; }}
        .tab.active {{
            background: linear-gradient(45deg, #f1c40f, #f7ca4a);
            color: #222; box-shadow: 0 4px 14px rgba(241, 196, 15, 0.35);
        }}
        .tab .count {{ font-size: 11px; opacity: 0.65; font-weight: 400; }}

        section {{ display: none; }}
        section.active {{ display: block; }}
        .tagline {{ color: #888; font-weight: 300; margin: 0 0 26px; }}
        footer {{ margin-top: 50px; font-size: 12px; color: #666; }}

        @media (prefers-reduced-motion: reduce) {{ .tab {{ transition: none; }} }}
    </style>
</head>
<body>
    <div class="brand">
        <h1>MICROVERSE</h1>
        <h3>by RashTek</h3>
    </div>

    <div class="tabs" role="tablist">
{tabs}
    </div>

{sections}
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

        // Tab switching, hash-routed — the site opens on the Games screen.
        var tabs = document.querySelectorAll('.tab');
        var sections = document.querySelectorAll('section');
        function show(name) {{
            tabs.forEach(function (t) {{ t.classList.toggle('active', t.dataset.tab === name); }});
            sections.forEach(function (s) {{ s.classList.toggle('active', s.dataset.tab === name); }});
        }}
        function current() {{
            return (location.hash || '').replace('#', '') || '{default}';
        }}
        function apply() {{
            var name = current();
            if (!document.querySelector('section[data-tab="' + name + '"]')) name = '{default}';
            show(name);
        }}
        tabs.forEach(function (t) {{
            t.addEventListener('click', function () {{ location.hash = t.dataset.tab; }});
        }});
        addEventListener('hashchange', apply);
        apply();
    </script>
</body>
</html>
"""


def build_home():
    tab_buttons = ""
    for folder, (emoji_name, _) in folders.items():
        hid = TAB_IDS[folder]
        emoji, label = emoji_name.split(" ", 1)
        files = [f for f in os.listdir(folder) if f.endswith(".html") and f != "index.html"] if os.path.exists(folder) else []
        tab_buttons += (
            f'        <button class="tab" data-tab="{hid}" role="tab">'
            f'{emoji} {label} <span class="count">{len(files)}</span></button>\n'
        )

    sections = ""
    for folder, (_, tagline) in folders.items():
        hid = TAB_IDS[folder]
        cards = cards_for(folder, href_prefix=folder + "/", icon_prefix=folder + "/")
        grids = "".join(cards) or "            <p style='color:#777'>No files found yet.</p>\n"
        is_default = " active" if TAB_IDS[folder] == DEFAULT_TAB else ""
        sections += (
            f'<section data-tab="{hid}" class="{is_default.strip()}" id="{hid}">\n'
            f'        <p class="tagline">{len(cards)} item(s) · {html.escape(tagline)}</p>\n'
            f'        <div class="grid">\n{grids}        </div>\n'
            f"    </section>\n\n"
        )
    sections = sections.rstrip() + "\n"

    return home_template.format(
        style=STYLE,
        tabs=tab_buttons.rstrip(),
        sections=sections,
        default=DEFAULT_TAB,
    )


def generate_index():
    # Category folder pages
    for folder, header in PAGES.items():
        if not os.path.exists(folder):
            print(f"Warning: Folder '{folder}' not found. Skipping.")
            continue
        cards = cards_for(folder)
        links = "".join(cards) or "            <p style='color:#777'>No files found yet.</p>\n"
        final_html = folder_template.format(
            title=header,
            header=header,
            count=len(cards),
            links="    <div class=\"grid\">\n        " + links.rstrip() + "\n    </div>",
            style=STYLE,
        )
        output_path = os.path.join(folder, "index.html")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(final_html)
        print(f"✅ Updated {output_path} with {len(cards)} items.")

    # Home page with tab bar
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(build_home())
    print("✅ Updated tabbed home page (index.html).")


if __name__ == "__main__":
    generate_index()
