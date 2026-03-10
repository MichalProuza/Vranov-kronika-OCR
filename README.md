# 📜 Kronika obce Vranov – OCR přepis

Automatický přepis ručně psané obecní kroniky obce Vranov pomocí Claude AI (vision).

Zdrojové skeny kroniky: [vranov.cz/obec/historie/kronika-obce-vranov](https://www.vranov.cz/obec/historie/kronika-obce-vranov/)

## Jak to funguje

1. **Scraping** – ze stránek obce se stáhnou URL všech naskenovaných stránek kroniky (~700+ obrázků)
2. **Download** – obrázky se stáhnou v plném rozlišení
3. **OCR přepis** – každý obrázek se odešle do Claude API (vision model), který přečte ručně psaný český text
4. **Uhlazení textu** – surové OCR přepisy se pošlou jazykovému modelu, který opraví překlepy, gramatiku a chyby OCR
5. **HTML výstup** – z přepisů se sestaví přehledná webová stránka s navigací

## Požadavky

- Python 3.10+
- Anthropic API klíč (Claude Sonnet 4)
- Cca 700 API volání → odhadem **$5–15** dle velikosti obrázků

## Instalace

```bash
git clone <repo-url>
cd kronika-vranov-ocr
pip install -r requirements.txt
```

Nastav API klíč – podle prostředí:

**Linux / macOS (bash/zsh):**
```bash
export ANTHROPIC_API_KEY='sk-ant-api03-...'
```

**Windows PowerShell:**
```powershell
$env:ANTHROPIC_API_KEY = 'sk-ant-api03-...'
```

> Nastavení platí jen pro aktuální terminálovou session. Pro trvalé uložení přidej řádek do svého profilu (`$PROFILE`) nebo nastav proměnnou v Nastavení systému → Proměnné prostředí.

## Spuštění

```bash
# 1. Stáhni URL obrázků z webu
python 01_scrape_urls.py

# 2. Stáhni obrázky (700+ souborů, může trvat)
python 02_download_images.py

# 3. OCR přepis pomocí Claude API
#    Celé najednou:
python 03_ocr_transcribe.py

#    Nebo po sekcích:
python 03_ocr_transcribe.py --section "Úvod až rok 1919"
python 03_ocr_transcribe.py --section-index 2

#    Jen náhled bez volání API:
python 03_ocr_transcribe.py --dry-run

# 4. Uhlaď přepisy jazykovým modelem
#    Interaktivně se zeptá na model (opus/sonnet/haiku):
python 05_polish_text.py

#    Nebo rovnou s konkrétním modelem:
python 05_polish_text.py --model sonnet

#    Po sekcích:
python 05_polish_text.py --section "Úvod až rok 1919"

#    Přepsat existující uhlazení jiným modelem:
python 05_polish_text.py --force --model opus

# 5. Sestav HTML stránku (automaticky použije uhlazené přepisy)
python 04_build_html.py

# Ze surových OCR přepisů (bez uhlazení):
python 04_build_html.py --raw

# S miniaturami originálních skenů:
python 04_build_html.py --with-thumbnails
```

## Výstup

- `output/kronika_vranov.html` – kompletní přepis jako HTML stránka
- Responzivní design, navigace po sekcích, tisk-friendly
- Nejistá slova označena oranžově, nečitelná červeně
- Text zarovnaný do bloku (justify) – OCR řádkové zlomy se automaticky spojují do plynulého textu
- Rozdělovníky na konci řádku se automaticky spojí (např. `Schön-` + `brunn` → `Schönbrunn`)

## Resume podpora

Skripty 02, 03 a 05 podporují přerušení a pokračování – přeskočí už stažené/přepsané/uhlazené stránky. Můžeš klidně zpracovávat po sekcích a průběžně kontrolovat kvalitu.

Skript 05 při opakovaném spuštění detekuje existující uhlazené přepisy a nabídne přepsání jiným modelem, zpracování jen chybějících stránek, nebo zrušení.

## Struktura projektu

```
├── CLAUDE.md               # Instrukce pro Claude Code
├── README.md
├── requirements.txt
├── config.py               # Sdílená konfigurace
├── 01_scrape_urls.py       # Stáhne URL obrázků
├── 02_download_images.py   # Stáhne obrázky
├── 03_ocr_transcribe.py    # OCR přepis (Claude API)
├── 04_build_html.py        # Sestaví HTML výstup
├── 05_polish_text.py       # Uhlazení textu (Claude API)
├── data/
│   ├── image_urls.json     # URL obrázků (generováno)
│   ├── images/             # Stažené obrázky (generováno)
│   ├── transcriptions.json # Surové OCR přepisy (generováno)
│   └── transcriptions_polished.json # Uhlazené přepisy (generováno)
└── output/
    └── kronika_vranov.html # Finální HTML (generováno)
```

## Tipy

- **Kvalita přepisu** závisí na čitelnosti originálu. Starší zápisy (kurent, ornamentální písmo) budou méně přesné.
- **Po sekcích** – doporučuji zpracovat nejdřív 1–2 sekce a zkontrolovat kvalitu, než pustíš vše.
- **Cena OCR** – jeden obrázek stojí cca $0.01–0.02 (Sonnet). Celá kronika tak vyjde na $5–15.
- **Cena uhlazení** – závisí na modelu: Opus ~$38, Sonnet ~$8, Haiku ~$2 za celou kroniku.
- **Claude Code** – otevři projekt v Claude Code (`claude` v terminálu) a můžeš iterativně ladit přepisy.
