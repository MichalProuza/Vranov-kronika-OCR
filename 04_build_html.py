#!/usr/bin/env python3
"""
Krok 4: Sestaví výslednou HTML stránku z přepisů kroniky.

Načte přepisy z data/transcriptions.json a vygeneruje
přehlednou HTML stránku s navigací a přepisy.

Použití:
    python 04_build_html.py
    python 04_build_html.py --with-thumbnails   # Přidá miniatury originálů
"""

import argparse
import html
import json
import re

from config import OUTPUT_HTML, SECTIONS, TRANSCRIPTIONS_FILE


def slugify(text: str) -> str:
    """Create a URL-safe slug from Czech text."""
    slug = text.lower()
    replacements = {"á": "a", "č": "c", "ď": "d", "é": "e", "ě": "e", "í": "i",
                    "ň": "n", "ó": "o", "ř": "r", "š": "s", "ť": "t", "ú": "u",
                    "ů": "u", "ý": "y", "ž": "z", "–": "-", " ": "-"}
    for k, v in replacements.items():
        slug = slug.replace(k, v)
    slug = re.sub(r"[^a-z0-9-]", "", slug)
    return re.sub(r"-+", "-", slug).strip("-")


def format_text(text: str) -> str:
    """Convert plain transcription text to HTML paragraphs."""
    escaped = html.escape(text)
    # Mark uncertain words
    escaped = re.sub(r"\[\?(.+?)\?\]", r'<span class="uncertain" title="Nejistý přepis">\1</span>', escaped)
    # Mark unreadable words
    escaped = re.sub(r"\[nečitelné\]", r'<span class="unreadable">[nečitelné]</span>', escaped)
    # Mark image descriptions
    escaped = re.sub(r"\[Obrázek: (.+?)\]", r'<div class="image-note">🖼️ \1</div>', escaped)
    # Convert line breaks to paragraphs
    paragraphs = escaped.split("\n\n")
    result = []
    for p in paragraphs:
        p = p.strip()
        if p:
            # Keep single line breaks within paragraphs
            p = p.replace("\n", "<br>")
            result.append(f"<p>{p}</p>")
    return "\n".join(result)


def build_html(transcriptions: dict, with_thumbnails: bool = False) -> str:
    """Build the complete HTML page."""
    # Navigation
    nav_items = []
    for section in SECTIONS:
        name = section["name"]
        slug = slugify(name)
        page_count = len(transcriptions.get(name, {}))
        status = f" ({page_count} stránek)" if page_count > 0 else " (nepřepsáno)"
        nav_items.append(f'<a href="#{slug}" class="nav-item">{html.escape(name)}<span class="count">{status}</span></a>')

    nav_html = "\n".join(nav_items)

    # Content sections
    content_sections = []
    for section in SECTIONS:
        name = section["name"]
        slug = slugify(name)
        section_transcriptions = transcriptions.get(name, {})

        pages_html = []
        if not section_transcriptions:
            pages_html.append('<p class="empty">Tato sekce zatím nebyla přepsána.</p>')
        else:
            # Sort by image ID
            sorted_pages = sorted(
                section_transcriptions.items(),
                key=lambda x: x[1].get("img_id", 0)
            )
            for page_key, page_data in sorted_pages:
                img_id = page_data.get("img_id", "?")
                text = page_data.get("text", "")
                formatted = format_text(text)

                thumb_html = ""
                if with_thumbnails:
                    thumb_url = f"https://www.vranov.cz/evt_image.php?img={img_id}&width=200&height=200&box=2"
                    full_url = f"https://www.vranov.cz/evt_image.php?img={img_id}"
                    thumb_html = f'''
                    <div class="thumbnail">
                        <a href="{full_url}" target="_blank" title="Zobrazit originál">
                            <img src="{thumb_url}" alt="Strana {img_id}" loading="lazy">
                        </a>
                    </div>'''

                pages_html.append(f'''
                <div class="page" id="page-{img_id}">
                    <div class="page-header">
                        <span class="page-number">Strana {img_id}</span>
                    </div>
                    <div class="page-content">
                        {thumb_html}
                        <div class="transcription">
                            {formatted}
                        </div>
                    </div>
                </div>''')

        content_sections.append(f'''
        <section id="{slug}" class="chronicle-section">
            <h2>{html.escape(name)}</h2>
            {"".join(pages_html)}
        </section>''')

    content_html = "\n".join(content_sections)

    # Stats
    total_pages = sum(len(v) for v in transcriptions.values())
    total_chars = sum(
        len(p.get("text", ""))
        for section in transcriptions.values()
        for p in section.values()
    )

    return f'''<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kronika obce Vranov – Přepis</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Literata:ital,opsz,wght@0,7..72,400;0,7..72,700;1,7..72,400&family=Source+Sans+3:wght@400;600&display=swap" rel="stylesheet">
    <style>
        :root {{
            --color-bg: #faf8f4;
            --color-paper: #ffffff;
            --color-text: #2c2416;
            --color-text-light: #6b5e4e;
            --color-accent: #8b4513;
            --color-accent-light: #d4a574;
            --color-border: #e8dfd3;
            --color-uncertain: #c77b2a;
            --color-unreadable: #b44;
            --font-body: 'Literata', 'Georgia', serif;
            --font-ui: 'Source Sans 3', sans-serif;
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            font-family: var(--font-body);
            background: var(--color-bg);
            color: var(--color-text);
            line-height: 1.75;
            font-size: 17px;
        }}

        /* --- Header --- */
        .header {{
            background: var(--color-accent);
            color: #faf3eb;
            padding: 3rem 2rem;
            text-align: center;
        }}
        .header h1 {{
            font-size: 2.4rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            letter-spacing: 0.02em;
        }}
        .header .subtitle {{
            font-family: var(--font-ui);
            font-size: 1rem;
            opacity: 0.85;
        }}
        .stats {{
            font-family: var(--font-ui);
            font-size: 0.85rem;
            opacity: 0.7;
            margin-top: 1rem;
        }}

        /* --- Layout --- */
        .container {{
            display: flex;
            max-width: 1200px;
            margin: 0 auto;
            min-height: calc(100vh - 200px);
        }}

        /* --- Navigation --- */
        .sidebar {{
            width: 280px;
            flex-shrink: 0;
            background: var(--color-paper);
            border-right: 1px solid var(--color-border);
            padding: 1.5rem 0;
            position: sticky;
            top: 0;
            height: 100vh;
            overflow-y: auto;
        }}
        .sidebar h3 {{
            font-family: var(--font-ui);
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: var(--color-text-light);
            padding: 0 1.5rem;
            margin-bottom: 0.75rem;
        }}
        .nav-item {{
            display: block;
            padding: 0.6rem 1.5rem;
            color: var(--color-text);
            text-decoration: none;
            font-family: var(--font-ui);
            font-size: 0.9rem;
            border-left: 3px solid transparent;
            transition: all 0.15s;
        }}
        .nav-item:hover {{
            background: var(--color-bg);
            border-left-color: var(--color-accent-light);
        }}
        .nav-item .count {{
            display: block;
            font-size: 0.75rem;
            color: var(--color-text-light);
        }}

        /* --- Content --- */
        .content {{
            flex: 1;
            padding: 2rem 3rem;
            max-width: 800px;
        }}

        .chronicle-section {{
            margin-bottom: 4rem;
        }}
        .chronicle-section h2 {{
            font-size: 1.6rem;
            color: var(--color-accent);
            border-bottom: 2px solid var(--color-accent-light);
            padding-bottom: 0.5rem;
            margin-bottom: 2rem;
        }}

        /* --- Page --- */
        .page {{
            margin-bottom: 2.5rem;
            background: var(--color-paper);
            border: 1px solid var(--color-border);
            border-radius: 4px;
            overflow: hidden;
        }}
        .page-header {{
            background: var(--color-bg);
            padding: 0.4rem 1.2rem;
            border-bottom: 1px solid var(--color-border);
        }}
        .page-number {{
            font-family: var(--font-ui);
            font-size: 0.8rem;
            color: var(--color-text-light);
        }}
        .page-content {{
            padding: 1.5rem;
            display: flex;
            gap: 1.5rem;
        }}
        .thumbnail {{
            flex-shrink: 0;
        }}
        .thumbnail img {{
            width: 150px;
            border: 1px solid var(--color-border);
            border-radius: 2px;
            opacity: 0.9;
            transition: opacity 0.2s;
        }}
        .thumbnail img:hover {{
            opacity: 1;
        }}
        .transcription {{
            flex: 1;
        }}
        .transcription p {{
            margin-bottom: 0.8em;
            text-align: justify;
            hyphens: auto;
        }}

        /* --- Special marks --- */
        .uncertain {{
            color: var(--color-uncertain);
            border-bottom: 1px dashed var(--color-uncertain);
            cursor: help;
        }}
        .unreadable {{
            color: var(--color-unreadable);
            font-style: italic;
            font-size: 0.9em;
        }}
        .image-note {{
            background: var(--color-bg);
            padding: 0.5rem 1rem;
            border-radius: 4px;
            font-style: italic;
            color: var(--color-text-light);
            margin: 0.5em 0;
        }}
        .empty {{
            color: var(--color-text-light);
            font-style: italic;
            padding: 2rem;
            text-align: center;
        }}

        /* --- Footer --- */
        .footer {{
            text-align: center;
            padding: 2rem;
            font-family: var(--font-ui);
            font-size: 0.8rem;
            color: var(--color-text-light);
            border-top: 1px solid var(--color-border);
        }}

        /* --- Responsive --- */
        @media (max-width: 768px) {{
            .container {{ flex-direction: column; }}
            .sidebar {{
                width: 100%;
                position: relative;
                height: auto;
                border-right: none;
                border-bottom: 1px solid var(--color-border);
            }}
            .content {{ padding: 1.5rem; }}
            .page-content {{ flex-direction: column; }}
            .thumbnail img {{ width: 100%; max-width: 300px; }}
        }}

        /* --- Print --- */
        @media print {{
            .sidebar {{ display: none; }}
            .header {{ padding: 1rem; }}
            .page {{ break-inside: avoid; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Kronika obce Vranov</h1>
        <p class="subtitle">Přepis ručně psané obecní kroniky</p>
        <p class="stats">Přepsáno {total_pages} stránek · {total_chars:,} znaků · Zdroj: <a href="https://www.vranov.cz/obec/historie/kronika-obce-vranov/" style="color: inherit;">vranov.cz</a></p>
    </div>

    <div class="container">
        <nav class="sidebar">
            <h3>Obsah kroniky</h3>
            {nav_html}
        </nav>

        <main class="content">
            {content_html}
        </main>
    </div>

    <div class="footer">
        <p>Přepis vytvořen pomocí Claude AI (Anthropic) z naskenovaných stránek obecní kroniky.</p>
        <p>Originální skeny: <a href="https://www.vranov.cz/obec/historie/kronika-obce-vranov/">Oficiální stránky obce Vranov</a></p>
    </div>

    <script>
        // Smooth scrolling for navigation
        document.querySelectorAll('.nav-item').forEach(link => {{
            link.addEventListener('click', e => {{
                e.preventDefault();
                const target = document.querySelector(link.getAttribute('href'));
                if (target) target.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
            }});
        }});
    </script>
</body>
</html>'''


def main():
    parser = argparse.ArgumentParser(description="Sestavení HTML z přepisů kroniky")
    parser.add_argument("--with-thumbnails", action="store_true",
                        help="Přidá miniatury originálních skenů (vyžaduje internet)")
    args = parser.parse_args()

    print("=" * 60)
    print("Kronika obce Vranov – Building HTML")
    print("=" * 60)

    # Load transcriptions
    if not TRANSCRIPTIONS_FILE.exists():
        print("❌ Nejdřív spusť 03_ocr_transcribe.py!")
        return

    with open(TRANSCRIPTIONS_FILE, "r", encoding="utf-8") as f:
        transcriptions = json.load(f)

    # Build HTML
    html_content = build_html(transcriptions, with_thumbnails=args.with_thumbnails)

    # Write output
    OUTPUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)

    total_pages = sum(len(v) for v in transcriptions.values())
    print(f"\n✅ HTML vygenerováno: {OUTPUT_HTML}")
    print(f"   {total_pages} stránek přepisů v {len(transcriptions)} sekcích")


if __name__ == "__main__":
    main()
