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

from config import OUTPUT_HTML, POLISHED_FILE, RELATED_FILE, SECTIONS, TRANSCRIPTIONS_FILE
from name_index import build_index
from place_index import build_house_index, build_place_index


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


PAGE_NUM_RE = re.compile(r"^(?:Strana\s+)?(\[\??|\[)?(\d+|[IVXLC]+)\.?(\?\])?\]?(?:\s+(.*))?$")
YEAR_RE = re.compile(r"^(?:v\s+)?(?:r\.?|R\.?|Rok|rok)?\s*\d{4}\b.*$")


def split_page_header(text: str) -> tuple[str, str, str]:
    """Split a page transcription into (page number, year, body).

    Page files start with the chronicle page number on the first line and the
    year (or an empty line) on the second. Pages without a number (drawings,
    blank pages) are returned unchanged with an empty page number.
    """
    lines = text.split("\n")
    m = PAGE_NUM_RE.match(lines[0].strip()) if lines else None
    if not m:
        return "", "", text
    number = m.group(2)
    if m.group(1):  # number derived by the transcriber, e.g. "[305]"
        number = f"[{number}]"
    year = (m.group(4) or "").strip()
    body_start = 1
    if len(lines) > 1:
        second = lines[1].strip()
        if not second:
            body_start = 2
        elif len(second) <= 30 and YEAR_RE.match(second):
            year = f"{year} {second}".strip() if year else second
            body_start = 2
    return number, year.rstrip("."), "\n".join(lines[body_start:]).strip("\n")


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
            # Join single line breaks into flowing text (OCR often breaks
            # at the original handwritten line endings which prevents
            # proper text-align: justify). Keep explicit line breaks only
            # when the line ends with a period/colon or looks intentional.
            lines = p.split("\n")
            merged = []
            for i, line in enumerate(lines):
                stripped = line.rstrip()
                merged.append(stripped)
                # Add space when joining, unless next line continues a hyphenated word
                if i < len(lines) - 1:
                    next_line = lines[i + 1].lstrip()
                    if stripped.endswith("-") and next_line and next_line[0].islower():
                        # Remove trailing hyphen – word continues on next line
                        merged[-1] = stripped[:-1]
                    else:
                        merged[-1] = stripped + " "
            p = "".join(merged).strip()
            result.append(f"<p>{p}</p>")
    return "\n".join(result)


SECTION_SHORT = re.compile(r"^Rok\s+")
INDEX_ALPHABET = ["A", "B", "C", "Č", "D", "E", "F", "G", "H", "Ch", "I", "J", "K", "L", "M", "N",
                  "O", "P", "Q", "R", "Ř", "S", "Š", "T", "U", "V", "W", "X", "Y", "Z", "Ž"]
_LETTER_BASE = {"Á": "A", "Ď": "D", "É": "E", "Ě": "E", "Í": "I", "Ň": "N", "Ó": "O", "Ť": "T",
                "Ú": "U", "Ů": "U", "Ý": "Y", "Ä": "A", "Ö": "O", "Ü": "U"}


def _index_letter(heading: str) -> str:
    if heading.startswith("Ch"):
        return "Ch"
    first = heading[:1].upper()
    return _LETTER_BASE.get(first, first)


def _collect_pages(transcriptions: dict) -> tuple[list[dict], dict]:
    """All pages in chronicle order and their metadata for index links.
    meta: img_id -> (section order, section label, page label, year)."""
    pages = []
    meta = {}
    for order, section in enumerate(SECTIONS):
        name = section["name"]
        short = SECTION_SHORT.sub("", name)
        for page_data in sorted(transcriptions.get(name, {}).values(), key=lambda p: p.get("img_id", 0)):
            img_id = page_data.get("img_id")
            text = page_data.get("text", "")
            number, year, _ = split_page_header(text)
            meta[img_id] = (order, short, number or f"sken {img_id}", year)
            pages.append({"id": img_id, "text": text})
    return pages, meta


def _page_title(meta: dict, pid) -> str:
    _, short, number, year = meta[pid]
    return f"{short}, strana {number}" + (f" ({year})" if year else "")


def _page_links(page_ids, meta: dict) -> str:
    """Page links grouped by chronicle section: „1920–1929: 12 14 15“."""
    parts, current = [], None
    for pid in sorted(page_ids, key=lambda i: (meta[i][0], i)):
        _, short, number, _ = meta[pid]
        if short != current:
            if current is not None:
                parts.append("</span>")
            parts.append(f'<span class="ni-sec"><span class="ni-sec-name">{html.escape(short)}:</span> ')
            current = short
        parts.append(f'<a href="#page-{pid}" title="{html.escape(_page_title(meta, pid))}">{html.escape(number)}</a> ')
    parts.append("</span>")
    return "".join(parts)


def _plural(n: int, one: str, few: str, many: str) -> str:
    return f"{n} {one if n == 1 else few if 2 <= n <= 4 else many}"


def _pages_count(n: int) -> str:
    return _plural(n, "strana", "strany", "stran")


def _index_entry(heading: str, count: str, search_terms, forms, body: str) -> str:
    search = " ".join(dict.fromkeys(t for t in search_terms if t))
    return (f'<li class="ni-entry" data-search="{html.escape(search)}" data-forms="{html.escape("|".join(forms))}">'
            f'<details><summary><span class="ni-name">{html.escape(heading)}</span> '
            f'<span class="ni-count">{html.escape(count)}</span></summary>'
            f'<div class="ni-pages">{body}</div></details></li>')


def _index_section(section_id: str, prefix: str, title: str, intro: str, placeholder: str,
                   total_label: str, groups: list[tuple[str, str, list[str]]]) -> str:
    """groups: (short label for the jump bar, group heading, entry html list)."""
    jump_bar = " ".join(f'<a href="#{prefix}-{i}">{html.escape(label)}</a>' for i, (label, _, _) in enumerate(groups))
    blocks = "\n".join(
        f'<div class="ni-group" id="{prefix}-{i}"><h3>{html.escape(heading)}</h3><ul>{"".join(entries)}</ul></div>'
        for i, (_, heading, entries) in enumerate(groups)
    )
    return f'''
        <section id="{section_id}" class="chronicle-section name-index" data-total="{html.escape(total_label)}">
            <h2>{html.escape(title)}</h2>
            <p class="ni-intro">{intro}</p>
            <div class="ni-tools">
                <input type="search" class="ni-search" placeholder="{html.escape(placeholder)}" autocomplete="off" aria-label="{html.escape(placeholder)}">
                <span class="ni-status">{html.escape(total_label)}</span>
            </div>
            <nav class="ni-letters" aria-label="Skupiny rejstříku">{jump_bar}</nav>
            <div class="ni-list">{blocks}</div>
            <p class="ni-empty empty" hidden>Nic neodpovídá hledání. Zkuste jiný tvar nebo hledejte v celém textu (Ctrl+F).</p>
        </section>'''


def build_name_index_html(pages: list[dict], meta: dict) -> tuple[str, int]:
    """Build the surname index section. Returns (html, number of surnames)."""
    surnames = build_index(pages)

    groups: dict[str, list[str]] = {}
    for s in surnames:
        forms = sorted(s.forms, key=len, reverse=True)
        search = [_fold_js(f) for f in [*s.heading.split(", "), *forms]]
        groups.setdefault(_index_letter(s.heading), []).append(
            _index_entry(s.heading, _pages_count(len(s.pages)), search, forms, _page_links(s.pages, meta)))

    letters = [c for c in INDEX_ALPHABET if c in groups] + [c for c in groups if c not in INDEX_ALPHABET]
    intro = ('Abecední seznam příjmení, která se v přepisu kroniky vyskytují, s odkazy na strany. '
             'Skloňované tvary a ženská příjmení jsou sloučeny pod jedno heslo (Holešovský, Holešovského, Holešovská…). '
             'Rejstřík je sestaven strojově z přepisu – některá jména mohou chybět nebo být zkomolená stejně jako v přepisu; '
             'pro jistotu hledejte i v celém textu (Ctrl+F). Po kliknutí na číslo strany se jméno na stránce zvýrazní.')
    section_html = _index_section(
        "rejstrik", "ni", "Rejstřík příjmení", intro, "Hledat příjmení, např. Skoupý",
        _plural(len(surnames), "příjmení", "příjmení", "příjmení"),
        [(c, c, groups[c]) for c in letters])
    return section_html, len(surnames)


def build_place_index_html(pages: list[dict], meta: dict) -> tuple[str, int]:
    """Build the place index section. Returns (html, number of places)."""
    place_groups = build_place_index(pages)
    groups = []
    total = 0
    for group, places in place_groups.items():
        entries = []
        for p in places:
            forms = sorted(p.forms, key=len, reverse=True)
            search = [_fold_js(w) for w in re.split(r"[\s(),]+", p.heading)] + [_fold_js(f) for f in forms]
            entries.append(_index_entry(p.heading, _pages_count(len(p.pages)), search, forms,
                                        _page_links(p.pages, meta)))
        total += len(entries)
        groups.append((group.split(" – ")[0], group, entries))
    intro = ('Obce, části Vranova, pomístní názvy, budovy, země a řeky zmíněné v kronice, s odkazy na strany. '
             'Rejstřík vychází z ručně sestaveného seznamu míst a jejich tvarů (soubor <code>data/rejstrik_mist.txt</code> '
             'v repozitáři projektu), který lze doplňovat. Místo zapsané v přepisu zkomoleně se nenajde – '
             'hledejte i v celém textu (Ctrl+F). Po kliknutí na číslo strany se místo na stránce zvýrazní.')
    section_html = _index_section(
        "rejstrik-mist", "nm", "Rejstřík míst", intro, "Hledat místo, např. Babí lom",
        _plural(total, "místo", "místa", "míst"), groups)
    return section_html, total


HOUSE_GROUP_SIZE = 50


def build_house_index_html(pages: list[dict], meta: dict) -> tuple[str, int]:
    """Build the house-number index section. Returns (html, number of houses)."""
    houses = build_house_index(pages)
    groups: dict[int, list[str]] = {}
    for h in houses:
        items = []
        for m in sorted(h.mentions, key=lambda m: (meta[m.page_id][0], m.page_id)):
            before, hit, after = (html.escape(x) for x in m.snippet)
            _, short, number, year = meta[m.page_id]
            label = f"{short}, s.\u00a0{number}" + (f" ({year})" if year else "")
            items.append(f'<li><a href="#page-{m.page_id}" title="{html.escape(_page_title(meta, m.page_id))}">'
                         f'{html.escape(label)}</a> {before}<b>{hit}</b>{after}</li>')
        words = {_fold_js(w) for m in h.mentions for w in re.findall(r"\w{3,}", m.snippet[0] + " " + m.snippet[2])
                 if not w.isdigit()}
        forms = sorted({m.form for m in h.mentions}, key=len, reverse=True)
        n = len(h.mentions)
        count = _plural(n, "zmínka", "zmínky", "zmínek")
        groups.setdefault((h.number - 1) // HOUSE_GROUP_SIZE, []).append(
            _index_entry(f"č. {h.number}", count, [str(h.number), *sorted(words)], forms,
                         f'<ul class="nd-mentions">{"".join(items)}</ul>'))
    group_list = []
    for g in sorted(groups):
        lo, hi = g * HOUSE_GROUP_SIZE + 1, (g + 1) * HOUSE_GROUP_SIZE
        group_list.append((f"{lo}–{hi}", f"Čísla {lo}–{hi}", groups[g]))
    intro = ('Čísla domů (popisná čísla) zmíněná v kronice – „č. 35“, „č. p. 35“ – s úryvkem textu, '
             'takže je vidět, kdo v domě bydlel nebo co se v něm stalo. Hledat lze číslo domu i jméno z úryvku '
             '(např. Holešovský). Rejstřík je sestaven strojově: číslo stojí u domů ve Vranově i v okolních obcích '
             '(z úryvku je obvykle poznat, o kterou jde) a výjimečně může jít o jiné číslo než popisné.')
    section_html = _index_section(
        "rejstrik-domu", "nd", "Rejstřík domů", intro, "Hledat číslo domu nebo jméno, např. 35",
        _plural(len(houses), "dům", "domy", "domů"), group_list)
    return section_html, len(houses)


def load_related(path=RELATED_FILE) -> list[dict]:
    """Articles from other sources that complement the chronicle (data/souvislosti.json)."""
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f).get("clanky", [])


def _related_source(article: dict) -> str:
    source = article["zdroj"]
    if article.get("strany_pdf"):
        source += f', s. {article["strany_pdf"]}'
    return source


def _related_link(article: dict) -> str:
    author = f' <span class="rel-author">({html.escape(article["autor"])})</span>' if article.get("autor") else ""
    return (f'<a href="{html.escape(article["url"])}" target="_blank" rel="noopener">{html.escape(article["titul"])}</a>'
            f'{author} <span class="rel-source">– {html.escape(_related_source(article))}, PDF ↗</span>')


def build_page_related_html(articles: list[dict]) -> str:
    """Box under a chronicle page listing the articles linked to it."""
    if not articles:
        return ""
    items = "".join(f"<li>{_related_link(a)}</li>" for a in articles)
    return (f'<aside class="related"><span class="rel-label">Souvislosti</span>'
            f'<ul>{items}</ul><a class="rel-more" href="#souvislosti">všechny souvislosti</a></aside>')


def build_related_section_html(related: list[dict], meta: dict) -> str:
    """Overview of all related articles grouped by topic, with links back to chronicle pages."""
    if not related:
        return ""
    groups: dict[str, list[dict]] = {}
    for article in related:
        groups.setdefault(article.get("tema") or "Ostatní", []).append(article)
    blocks = []
    for topic, articles in groups.items():
        items = []
        for a in articles:
            pages = [pid for pid in a.get("strany", []) if pid in meta]
            page_links = f'<div class="rel-pages">V kronice: {_page_links(pages, meta)}</div>' if pages else ""
            items.append(f'<li class="rel-item">{_related_link(a)}'
                         f'<p class="rel-desc">{html.escape(a.get("popis", ""))}</p>{page_links}</li>')
        blocks.append(f'<div class="rel-group"><h3>{html.escape(topic)}</h3><ul>{"".join(items)}</ul></div>')
    return f'''
        <section id="souvislosti" class="chronicle-section related-section">
            <h2>Souvislosti</h2>
            <p class="ni-intro">Články z Vranovského zpravodaje (2002–2024), které zápisy kroniky doplňují: vzpomínky pamětníků,
            výpisy z jiných kronik a komentáře obecních kronikářů. Odkazy vedou na PDF na
            <a href="https://www.vranov.cz/obec/zpravodaj-/">webu obce Vranov</a>; u stran kroniky, kterých se článek týká,
            je na něj odkaz přímo pod přepisem. Seznam je ruční výběr (soubor <code>data/souvislosti.json</code>) a není úplný.</p>
            {"".join(blocks)}
        </section>'''


def _fold_js(s: str) -> str:
    """Lowercase without diacritics – must match foldText() in the page script."""
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn")


def build_html(transcriptions: dict, with_thumbnails: bool = False, related: list[dict] | None = None) -> str:
    """Build the complete HTML page."""
    related = load_related() if related is None else related
    related_by_page: dict[int, list[dict]] = {}
    for article in related:
        for pid in article.get("strany", []):
            related_by_page.setdefault(pid, []).append(article)
    # Navigation
    nav_items = []
    for section in SECTIONS:
        name = section["name"]
        slug = slugify(name)
        page_count = len(transcriptions.get(name, {}))
        status = f" ({page_count} stránek)" if page_count > 0 else " (nepřepsáno)"
        nav_items.append(f'<a href="#{slug}" class="nav-item">{html.escape(name)}<span class="count">{status}</span></a>')

    nav_html = "\n".join(nav_items)
    index_pages, index_meta = _collect_pages(transcriptions)
    index_html, surname_count = build_name_index_html(index_pages, index_meta)
    place_html, place_count = build_place_index_html(index_pages, index_meta)
    house_html, house_count = build_house_index_html(index_pages, index_meta)
    related_html = build_related_section_html(related, index_meta)
    related_nav = (f'<a href="#souvislosti" class="nav-item nav-index">Souvislosti<span class="count">'
                   f'({_plural(len(related), "článek", "články", "článků")})</span></a>') if related else ""

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
                number, year, body = split_page_header(text)
                formatted = format_text(body)
                label = f"Strana {html.escape(number)}" if number else "Nečíslovaná strana"
                if year:
                    label += f" · {html.escape(year)}"
                scan_url = f"https://www.vranov.cz/evt_image.php?img={img_id}"

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
                        <span class="page-number">{label}</span>
                        <a class="scan-link" href="{scan_url}" target="_blank" rel="noopener">originální sken ↗</a>
                    </div>
                    <div class="page-content">
                        {thumb_html}
                        <div class="transcription">
                            {formatted}
                        </div>
                    </div>
                    {build_page_related_html(related_by_page.get(img_id, []))}
                </div>''')

        content_sections.append(f'''
        <section id="{slug}" class="chronicle-section">
            <h2>{html.escape(name)}</h2>
            {"".join(pages_html)}
        </section>''')

    content_sections += [related_html, index_html, place_html, house_html]
    content_html = "\n".join(content_sections)

    # Stats
    total_pages = sum(len(v) for v in transcriptions.values())
    total_chars = sum(
        len(p.get("text", ""))
        for section in transcriptions.values()
        for p in section.values()
    )

    total_chars_fmt = f"{total_chars:,}".replace(",", "\u00a0")

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
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            gap: 1rem;
        }}
        .scan-link {{
            font-family: var(--font-ui);
            font-size: 0.75rem;
            color: var(--color-accent);
            text-decoration: none;
            white-space: nowrap;
        }}
        .scan-link:hover {{ text-decoration: underline; }}
        .notice {{
            max-width: 760px;
            width: calc(100% - 2rem);
            margin: 1.5rem auto 0;
            padding: 1rem 1.25rem;
            background: var(--color-paper);
            border: 1px solid var(--color-border);
            border-left: 4px solid var(--color-accent-light);
            border-radius: 4px;
            font-family: var(--font-ui);
            font-size: 0.9rem;
            line-height: 1.55;
            color: var(--color-text-light);
        }}
        .notice strong {{ color: var(--color-text); }}
        .notice a {{ color: var(--color-accent); }}
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

        /* --- Souvislosti (články z jiných pramenů) --- */
        .related {{
            font-family: var(--font-ui);
            font-size: 0.85rem;
            line-height: 1.5;
            border-top: 1px dashed var(--color-border);
            padding: 0.7rem 1.5rem 0.8rem;
            color: var(--color-text-light);
        }}
        .rel-label {{
            font-weight: 600;
            font-size: 0.75rem;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            color: var(--color-accent);
        }}
        .related ul {{ list-style: none; margin: 0.3rem 0; padding: 0; }}
        .related li {{ margin: 0.2rem 0; }}
        .related a, .rel-item a {{ color: var(--color-accent); text-decoration: none; }}
        .related a:hover, .rel-item a:hover {{ text-decoration: underline; }}
        .rel-more {{ font-size: 0.8rem; }}
        .related-section {{ font-family: var(--font-ui); }}
        .rel-group h3 {{ font-size: 1rem; margin: 1.4rem 0 0.4rem; color: var(--color-text); }}
        .rel-group ul {{ list-style: none; margin: 0; padding: 0; }}
        .rel-item {{ padding: 0.6rem 0; border-bottom: 1px solid var(--color-border); font-size: 0.95rem; line-height: 1.5; }}
        .rel-source, .rel-author {{ color: var(--color-text-light); font-size: 0.85rem; }}
        .rel-desc {{ margin: 0.2rem 0 0; font-size: 0.88rem; color: var(--color-text-light); }}
        .rel-pages {{ padding: 0.2rem 0 0; font-size: 0.85rem; color: var(--color-text-light); }}
        .rel-pages .ni-sec {{ display: inline; margin-right: 0.6em; }}
        .related-section .ni-intro a {{ color: var(--color-accent); }}

        /* --- Rejstříky (příjmení, místa, domy) --- */
        .nav-indexes {{
            border-bottom: 1px solid var(--color-border);
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
        }}
        .nav-index {{
            font-weight: 600;
            color: var(--color-accent);
        }}
        .ni-intro {{
            font-family: var(--font-ui);
            font-size: 0.9rem;
            line-height: 1.55;
            color: var(--color-text-light);
            margin-bottom: 1.2rem;
        }}
        .ni-tools {{
            display: flex;
            gap: 1rem;
            align-items: center;
            flex-wrap: wrap;
            position: sticky;
            top: 0;
            background: var(--color-bg);
            padding: 0.6rem 0;
            z-index: 2;
        }}
        .ni-search {{
            flex: 1;
            min-width: 0;
            font: inherit;
            font-family: var(--font-ui);
            font-size: 1rem;
            padding: 0.55rem 0.8rem;
            border: 1px solid var(--color-accent-light);
            border-radius: 4px;
            background: var(--color-paper);
            color: var(--color-text);
        }}
        .ni-search:focus {{ outline: 2px solid var(--color-accent); outline-offset: 1px; }}
        .ni-status {{
            font-family: var(--font-ui);
            font-size: 0.85rem;
            color: var(--color-text-light);
        }}
        .ni-letters {{
            font-family: var(--font-ui);
            font-size: 0.9rem;
            margin: 0.5rem 0 1.5rem;
            display: flex;
            flex-wrap: wrap;
            gap: 0.25rem 0.6rem;
        }}
        .ni-letters a {{ color: var(--color-accent); text-decoration: none; font-weight: 600; }}
        .ni-letters a:hover {{ text-decoration: underline; }}
        .ni-group h3 {{
            font-size: 1.2rem;
            color: var(--color-accent);
            margin: 1.2rem 0 0.4rem;
        }}
        .ni-group ul {{ list-style: none; }}
        .ni-entry {{ border-bottom: 1px solid var(--color-border); }}
        .ni-entry summary {{
            cursor: pointer;
            padding: 0.35rem 0;
            display: flex;
            justify-content: space-between;
            gap: 1rem;
            list-style: none;
        }}
        .ni-entry summary::-webkit-details-marker {{ display: none; }}
        .ni-entry summary::before {{
            content: "▸";
            color: var(--color-accent-light);
            width: 1em;
            flex-shrink: 0;
        }}
        .ni-entry details[open] summary::before {{ content: "▾"; }}
        .ni-name {{ flex: 1; }}
        .ni-count {{
            font-family: var(--font-ui);
            font-size: 0.8rem;
            color: var(--color-text-light);
            white-space: nowrap;
        }}
        .ni-pages {{
            font-family: var(--font-ui);
            font-size: 0.85rem;
            line-height: 1.7;
            padding: 0 0 0.7rem 1em;
        }}
        .ni-sec {{ display: block; }}
        .ni-sec-name {{ color: var(--color-text-light); }}
        .ni-pages a {{ color: var(--color-accent); text-decoration: none; padding: 0 0.1em; }}
        .ni-pages a:hover {{ text-decoration: underline; }}
        mark.ni-hit {{
            background: #f7dc8f;
            color: inherit;
            border-radius: 2px;
            padding: 0 0.1em;
        }}
        .nd-mentions {{
            list-style: none;
            padding-left: 0;
        }}
        .nd-mentions li {{
            padding: 0.25rem 0;
            line-height: 1.5;
            color: var(--color-text-light);
        }}
        .nd-mentions li + li {{ border-top: 1px dotted var(--color-border); }}
        .nd-mentions a {{ font-weight: 600; padding: 0 0.3em 0 0; }}
        .nd-mentions b {{ color: var(--color-text); }}
        .ni-intro code {{ font-size: 0.85em; }}
        .page.ni-target {{ box-shadow: 0 0 0 2px var(--color-accent-light); }}
        #ni-back {{
            position: fixed;
            right: 1.2rem;
            bottom: 1.2rem;
            font-family: var(--font-ui);
            font-size: 0.9rem;
            background: var(--color-accent);
            color: #faf3eb;
            border: none;
            border-radius: 4px;
            padding: 0.6rem 0.9rem;
            cursor: pointer;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
            z-index: 5;
        }}
        #ni-back[hidden] {{ display: none; }}

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
            .sidebar, .ni-tools, .ni-letters, #ni-back {{ display: none; }}
            .header {{ padding: 1rem; }}
            .page {{ break-inside: avoid; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Kronika obce Vranov</h1>
        <p class="subtitle">Přepis ručně psané obecní kroniky</p>
        <p class="stats">Přepsáno {total_pages} stránek · {total_chars_fmt} znaků · rejstřík <a href="#rejstrik" style="color: inherit;">příjmení</a>, <a href="#rejstrik-mist" style="color: inherit;">míst</a> a <a href="#rejstrik-domu" style="color: inherit;">domů</a> · Zdroj: <a href="https://www.vranov.cz/obec/historie/kronika-obce-vranov/" style="color: inherit;">vranov.cz</a></p>
    </div>

    <div class="notice">
        <strong>O přepisu.</strong> Text vznikl čtením naskenovaných stran pomocí umělé inteligence (Claude, Anthropic)
        a není kritickou edicí. Pravopis a údaje kronikářů nejsou opravovány. Přepis může obsahovat chyby čtení,
        zejména u vlastních jmen. <span class="uncertain">Čárkovaně podtržená</span> místa jsou nejistá,
        <span class="unreadable">[nečitelné]</span> označuje nerozpoznaný text. Rozhodující je vždy originál: u každé strany
        je odkaz na její sken na <a href="https://www.vranov.cz/obec/historie/kronika-obce-vranov/">webu obce Vranov</a>.
    </div>

    <div class="container">
        <nav class="sidebar">
            <div class="nav-indexes">
                <a href="#rejstrik" class="nav-item nav-index">Rejstřík příjmení<span class="count">({surname_count} příjmení)</span></a>
                <a href="#rejstrik-mist" class="nav-item nav-index">Rejstřík míst<span class="count">({place_count} míst)</span></a>
                <a href="#rejstrik-domu" class="nav-item nav-index">Rejstřík domů<span class="count">({house_count} čísel domů)</span></a>
                {related_nav}
            </div>
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

    <button type="button" id="ni-back" hidden>↩ Zpět do rejstříku</button>

    <script>
        // Smooth scrolling for navigation
        document.querySelectorAll('.nav-item').forEach(link => {{
            link.addEventListener('click', e => {{
                e.preventDefault();
                const target = document.querySelector(link.getAttribute('href'));
                if (target) target.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
            }});
        }});

        // --- Rejstříky: příjmení, místa, domy ---
        (function () {{
            const foldText = s => s.toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g, '');
            document.querySelectorAll('section.name-index').forEach(section => {{
                const input = section.querySelector('.ni-search');
                const status = section.querySelector('.ni-status');
                const empty = section.querySelector('.ni-empty');
                const entries = Array.from(section.querySelectorAll('.ni-entry'));
                const groups = Array.from(section.querySelectorAll('.ni-group'));
                const keys = entries.map(li => li.dataset.search.split(' '));
                const total = entries.length;

                function filter() {{
                    const q = foldText(input.value.trim()).replace(/^c\\.\\s*(p\\.\\s*)?/, '');
                    const numeric = /^\\d+$/.test(q);
                    let shown = 0;
                    entries.forEach((li, i) => {{
                        const k = keys[i];
                        // číslo domu hledej přesně (35 nenajde 135), slova i uprostřed
                        const hit = !q || (numeric ? k[0] === q
                            : k.some(w => w.startsWith(q)) || (q.length >= 3 && k.some(w => w.includes(q))));
                        li.hidden = !hit;
                        if (hit) shown++;
                    }});
                    groups.forEach(g => {{ g.hidden = !g.querySelector('.ni-entry:not([hidden])'); }});
                    const open = q && shown <= 5;
                    entries.forEach(li => {{ if (!li.hidden) li.querySelector('details').open = open; }});
                    status.textContent = q ? `nalezeno ${{shown}} z ${{total}}` : section.dataset.total;
                    empty.hidden = shown > 0;
                }}
                input.addEventListener('input', filter);
            }});

            // Zvýraznění jména na cílové stránce
            const back = document.getElementById('ni-back');
            let returnTo = null;
            function clearMarks() {{
                document.querySelectorAll('mark.ni-hit').forEach(m => m.replaceWith(document.createTextNode(m.textContent)));
                document.querySelectorAll('.page.ni-target').forEach(p => p.classList.remove('ni-target'));
            }}
            function highlight(page, forms) {{
                const escaped = forms.map(f => f.replace(/[.*+?^${{}}()|[\\]\\\\]/g, '\\\\$&').replace(/\\s+/g, '\\\\s*'));
                const re = new RegExp(`(^|[^\\p{{L}}\\d])(${{escaped.join('|')}})(?![\\p{{L}}\\d])`, 'gu');
                const walker = document.createTreeWalker(page.querySelector('.transcription'), NodeFilter.SHOW_TEXT);
                const nodes = [];
                while (walker.nextNode()) nodes.push(walker.currentNode);
                nodes.forEach(node => {{
                    const text = node.nodeValue;
                    re.lastIndex = 0;
                    if (!re.test(text)) return;
                    re.lastIndex = 0;
                    const frag = document.createDocumentFragment();
                    let last = 0, m;
                    while ((m = re.exec(text))) {{
                        const start = m.index + m[1].length;
                        frag.append(text.slice(last, start));
                        const mark = document.createElement('mark');
                        mark.className = 'ni-hit';
                        mark.textContent = m[2];
                        frag.append(mark);
                        last = start + m[2].length;
                    }}
                    frag.append(text.slice(last));
                    node.replaceWith(frag);
                }});
            }}
            document.querySelectorAll('.ni-pages a').forEach(a => {{
                a.addEventListener('click', e => {{
                    const page = document.querySelector(a.getAttribute('href'));
                    if (!page) return;
                    e.preventDefault();
                    clearMarks();
                    const li = a.closest('.ni-entry');
                    highlight(page, li.dataset.forms.split('|'));
                    page.classList.add('ni-target');
                    returnTo = li;
                    back.hidden = false;
                    history.pushState(null, '', a.getAttribute('href'));
                    const first = page.querySelector('mark.ni-hit');
                    (first || page).scrollIntoView({{ block: first ? 'center' : 'start' }});
                }});
            }});
            back.addEventListener('click', () => {{
                if (returnTo) returnTo.scrollIntoView({{ block: 'center' }});
                back.hidden = true;
            }});
        }})();
    </script>
</body>
</html>'''


def main():
    parser = argparse.ArgumentParser(description="Sestavení HTML z přepisů kroniky")
    parser.add_argument("--with-thumbnails", action="store_true",
                        help="Přidá miniatury originálních skenů (vyžaduje internet)")
    parser.add_argument("--raw", action="store_true",
                        help="Použije surové OCR přepisy místo uhlazených")
    args = parser.parse_args()

    print("=" * 60)
    print("Kronika obce Vranov – Building HTML")
    print("=" * 60)

    # Load transcriptions – prefer polished version unless --raw
    if not args.raw and POLISHED_FILE.exists():
        print("Používám uhlazené přepisy (transcriptions_polished.json)")
        with open(POLISHED_FILE, "r", encoding="utf-8") as f:
            polished = json.load(f)
        # Merge: use polished where available, fall back to raw
        if TRANSCRIPTIONS_FILE.exists():
            with open(TRANSCRIPTIONS_FILE, "r", encoding="utf-8") as f:
                raw = json.load(f)
            for sec_name, pages in raw.items():
                if sec_name not in polished:
                    polished[sec_name] = pages
                else:
                    for page_key, page_data in pages.items():
                        if page_key not in polished[sec_name]:
                            polished[sec_name][page_key] = page_data
        transcriptions = polished
    elif TRANSCRIPTIONS_FILE.exists():
        print("Používám surové OCR přepisy (transcriptions.json)")
        with open(TRANSCRIPTIONS_FILE, "r", encoding="utf-8") as f:
            transcriptions = json.load(f)
    else:
        print("Nejdřív spusť 03_ocr_transcribe.py!")
        return

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
