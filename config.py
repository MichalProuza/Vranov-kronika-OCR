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
POLISHED_FILE = DATA_DIR / "transcriptions_polished.json"
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
OCR_SYSTEM_PROMPT = """Jsi expert na přepis ručně psaných českých kronik. Přepisuješ kroniku obce Vranov u Brna (20. století).

Pravidla:
- Přepisuj POUZE text, který vidíš na obrázku. Nic nevymýšlej, nedoplňuj.
- Nečitelná slova označ [nečitelné], nejistá slova [?odhad?].
- Zachovej odstavce, nadpisy a členění textu.
- Stránky bez textu (kresby, mapy) popiš: [Obrázek: stručný popis].
- Odpověz pouze přepisem – žádný úvod ani komentář."""

# System prompt for text polishing (post-OCR cleanup)
POLISH_SYSTEM_PROMPT = """Jsi editor a korektor českých textů. Dostaneš surový přepis ručně psané kroniky obce Vranov u Brna, získaný pomocí OCR. Tvým úkolem je text uhladit a opravit zjevné chyby OCR, ale zachovat původní obsah a styl.

Pravidla:
- Oprav zjevné překlepy a chyby způsobené špatným rozpoznáním ručního písma.
- Oprav gramatiku, interpunkci a diakritiku tam, kde je zřejmé, že OCR udělalo chybu.
- Zachovej původní styl a slovník kronikáře – NEMODERNIZUJ jazyk, neměň formulace.
- Zachovej odstavce, nadpisy a členění textu.
- Značky [nečitelné] a [?odhad?] ponech beze změny (pokud ale odhadneš správné slovo, nahraď [?odhad?] správným slovem).
- Značky [Obrázek: popis] ponech beze změny.
- Pokud je slovo jasně špatně přečtené a znáš správný tvar, oprav ho.
- NEPŘIDÁVEJ žádný nový obsah – pouze opravuj existující text.
- Odpověz pouze opraveným textem – žádný úvod, komentář ani vysvětlení."""
