# 📜 Kronika obce Vranov – OCR přepis

Automatický přepis ručně psané obecní kroniky obce Vranov pomocí Claude AI (vision).

Zdrojové skeny kroniky: [vranov.cz/obec/historie/kronika-obce-vranov](https://www.vranov.cz/obec/historie/kronika-obce-vranov/)

**Přepis online:** [michalprouza.github.io/Vranov-kronika-OCR](https://michalprouza.github.io/Vranov-kronika-OCR/)
(stránku sestavuje a publikuje workflow `.github/workflows/pages.yml` při každé změně
`data/transcriptions.json` ve větvi `main`).

**Kronika je přepsaná celá: všech 828 skenů ve 13 sekcích.** Přepis vznikl přímým
čtením skenů (a jejich zvětšených výřezů) jazykovým modelem s vizí; zachovává
dobový jazyk, řádky rukopisu, okrajové poznámky, popisy kreseb a razítek.
Nejistá čtení jsou označena `[?slovo?]`, nerozpoznaný text `[nečitelné]`. Nejde
o kritickou edici – zejména u vlastních jmen a v kurzívě starších kronikářů jsou
další chyby čtení možné.

| Sekce | Skenů | Strany kroniky | Souvislý přepis | Místa k ověření | Strany |
| --- | --- | --- | --- | --- | --- |
| Úvod až rok 1919 | 24 | I–26 | — | — | `data/ocr_pages/section_01/` |
| 1920–1929 | 38 | 27–63 | [1920-1929.md](docs/transcriptions/1920-1929.md) | [seznam](docs/transcriptions/1920-1929-k-overeni.md) | `data/ocr_pages/section_02/` |
| 1930–1939 | 63 | 63–125 | [1930-1939.md](docs/transcriptions/1930-1939.md) | [seznam](docs/transcriptions/1930-1939-k-overeni.md) | `data/ocr_pages/section_03/` |
| 1940–1951 | 112 | 125–236 (konec I. dílu) | [1940-1951.md](docs/transcriptions/1940-1951.md) | [seznam](docs/transcriptions/1940-1951-k-overeni.md) | `data/ocr_pages/section_04/` |
| 1951–1954 | 73 | II. díl 1–78 | [1951-1954.md](docs/transcriptions/1951-1954.md) | [seznam](docs/transcriptions/1951-1954-k-overeni.md) | `data/ocr_pages/section_05/` |
| 1955–1959 | 130 | II. díl 79–208 | [1955-1959.md](docs/transcriptions/1955-1959.md) | [seznam](docs/transcriptions/1955-1959-k-overeni.md) | `data/ocr_pages/section_06/` |
| 1960–1964 | 44 | 209–242 | [1960-1964.md](docs/transcriptions/1960-1964.md) | [seznam](docs/transcriptions/1960-1964-k-overeni.md) | `data/ocr_pages/section_07/` |
| 1965–1969 | 17 | 243–259 | [1965-1969.md](docs/transcriptions/1965-1969.md) | [seznam](docs/transcriptions/1965-1969-k-overeni.md) | `data/ocr_pages/section_08/` |
| 1970–1974 | 37 | 260–296 | [1970-1974.md](docs/transcriptions/1970-1974.md) | [seznam](docs/transcriptions/1970-1974-k-overeni.md) | `data/ocr_pages/section_09/` |
| 1975–1979 | 66 | 297–362 | [1975-1979.md](docs/transcriptions/1975-1979.md) | [seznam](docs/transcriptions/1975-1979-k-overeni.md) | `data/ocr_pages/section_10/` |
| 1980–1984 | 76 | 363–438 | [1980-1984.md](docs/transcriptions/1980-1984.md) | [seznam](docs/transcriptions/1980-1984-k-overeni.md) | `data/ocr_pages/section_11/` |
| 1985–1989 | 80 | 439–517 | [1985-1989.md](docs/transcriptions/1985-1989.md) | [seznam](docs/transcriptions/1985-1989-k-overeni.md) | `data/ocr_pages/section_12/` |
| 1990–1993 | 68 | 518–584 + nečíslovaná | [1990-1993.md](docs/transcriptions/1990-1993.md) | — | `data/ocr_pages/section_13/` |

Všechny strany jsou také v `data/transcriptions.json`; HTML stránku s celým
přepisem sestavíte příkazem `python 04_build_html.py --raw`
(výstup `output/kronika_vranov.html`). Podrobnosti k jednotlivým sekcím (kronikáři,
číslování stran, duplicitní skeny mezi galeriemi, známé nejistoty) jsou v souborech
`README.md` v adresářích `data/ocr_pages/section_XX/`.

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
