"""Shared configuration for the Kronika Vranov OCR project."""

import os
from pathlib import Path

# --- Paths ---
PROJECT_DIR = Path(__file__).parent
DATA_DIR = PROJECT_DIR / "data"
IMAGES_DIR = DATA_DIR / "images"
OUTPUT_DIR = PROJECT_DIR / "output"

IMAGE_URLS_FILE = DATA_DIR / "image_urls.json"
TRANSCRIPTIONS_FILE = DATA_DIR / "transcriptions.json"
OUTPUT_HTML = OUTPUT_DIR / "kronika_vranov.html"

# Create directories
for d in [DATA_DIR, IMAGES_DIR, OUTPUT_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# --- Web ---
BASE_URL = "https://www.vranov.cz"
CHRONICLE_INDEX = f"{BASE_URL}/obec/historie/kronika-obce-vranov/"
IMAGE_BASE_URL = f"{BASE_URL}/evt_image.php?img="

# Section pages (slug -> display name)
SECTIONS = [
    {"name": "Úvod až rok 1919", "slug": "uvod-az-rok-1919-2cs.html"},
    {"name": "Rok 1920–1929", "slug": "rok-1920-1929-3cs.html"},
    {"name": "Rok 1930–1939", "slug": "rok-1930-1939-4cs.html"},
    {"name": "Rok 1940–1951", "slug": "rok-1940-1951-5cs.html"},
    {"name": "Rok 1951–1954", "slug": "rok-1951-1954-6cs.html"},
    {"name": "Rok 1955–1959", "slug": "rok-1955-1959-7cs.html"},
    {"name": "Rok 1960–1964", "slug": "rok-1960-1964-8cs.html"},
    {"name": "Rok 1965–1969", "slug": "rok-1965-1969-9cs.html"},
    {"name": "Rok 1970–1974", "slug": "rok-1970-1974-10cs.html"},
    {"name": "Rok 1975–1979", "slug": "rok-1975-1979-11cs.html"},
    {"name": "Rok 1980–1984", "slug": "rok-1980-1984-12cs.html"},
    {"name": "Rok 1985–1989", "slug": "rok-1985-1989-13cs.html"},
    {"name": "Rok 1990–1993", "slug": "rok-1990-1993-14cs.html"},
]

# --- Claude API ---
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = "claude-opus-4-20250514"
REQUEST_DELAY_SECONDS = 2  # Rate limiting between API calls

# System prompt for OCR transcription
OCR_SYSTEM_PROMPT = """Jsi expert na čtení ručně psaných českých textů z obecních kronik 20. století.
Přepisuješ naskenované stránky kroniky obce Vranov u Brna.

ZÁSADNÍ PRAVIDLA (porušení = chyba):

1. PŘESNÝ PŘEPIS: Přepisuj VÝHRADNĚ to, co vidíš na obrázku. Každé slovo musí
   odpovídat tomu, co je skutečně napsáno na stránce. Nic nepřidávej, nedoplňuj,
   nedomýšlej. Nepřidávej žádný úvod, komentář ani závěr.

2. NEČITELNÝ TEXT: Pokud slovo nedokážeš s jistotou přečíst, napiš [nečitelné].
   U slov, kde si jsi jistý z 80–95 %, napiš [?odhad?]. Pod 80 % jistoty piš
   vždy [nečitelné]. Raději označ jako nečitelné než hádat špatně.

3. ČESKÉ PRAVOPISNÉ VZORY: Text je psán česky. Dávej pozor na:
   - háčky a čárky (š, č, ř, ž, ň, ď, ť, á, é, í, ó, ú, ů, ý)
   - typická česká slova: obec, obyvatel, hospodářství, zemědělství, schůze,
     usnesení, rozpočet, kronikář, zastupitelstvo, volby, výbor, jednota
   - staré tvary slov a pravopis (předválečný, poválečný)
   - místní jména: Vranov, Brno, Moravany, Říčany, Ostrovačice, Lelekovice,
     Útěchov a další okolní obce
   - rozlišuj podobná písmena v rukopisu: l/t, n/u, m/nn, r/v, a/o, e/c, h/k

4. STRUKTURA: Zachovej odstavce a členění. Nadpisy (roky, témata) označ jako
   nadpisy. Tabulky reprodukuj. Obrázky/kresby popiš: [Obrázek: stručný popis].

5. FORMÁT ODPOVĚDI: Odpověz POUZE přepisem textu ze stránky. Žádný úvod typu
   "Zde je přepis..." ani závěr typu "Poznámka:..." nepřidávej."""
