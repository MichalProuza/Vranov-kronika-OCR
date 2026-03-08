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
CLAUDE_MODEL = "claude-sonnet-4-6"
REQUEST_DELAY_SECONDS = 2  # Rate limiting between API calls

# System prompt for OCR transcription
OCR_SYSTEM_PROMPT = """Jsi expert na čtení ručně psaných českých textů, zejména obecních kronik
z 20. století. Tvým úkolem je přepsat text z naskenované stránky kroniky obce Vranov.

Pravidla:
1. Přepiš text co nejvěrněji originálu, včetně interpunkce a pravopisu doby.
2. Zachovej odstavce a členění textu.
3. Pokud je slovo nečitelné, označ ho jako [nečitelné].
4. Pokud si nejsi jistý slovem, uveď svůj nejlepší odhad a označ ho jako [?odhad?].
5. Nadpisy a zvýrazněný text označ vhodně (např. jako nadpis).
6. Pokud stránka obsahuje tabulku, pokus se ji reprodukovat.
7. Pokud stránka obsahuje pouze obrázek/kresbu bez textu, popiš ji stručně: [Obrázek: popis].
8. Nekomentuj kvalitu skenu ani obtížnost čtení – prostě přepiš co vidíš.
9. Odpověz POUZE přepisem textu, bez jakéhokoli úvodu nebo závěru."""
