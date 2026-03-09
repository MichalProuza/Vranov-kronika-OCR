# Kronika obce Vranov – OCR Transcription Project

## Přehled projektu

Cílem je stáhnout naskenované stránky ručně psané kroniky obce Vranov z webu
https://www.vranov.cz/obec/historie/kronika-obce-vranov/ a pomocí Claude API
(vision) je přepsat do čitelného textu. Výstupem je HTML stránka s plným
přepisem kroniky.

## Struktura webu

Kronika je rozdělena do 13 sekcí. Každá sekce je na samostatné stránce a
obsahuje galerii naskenovaných obrázků (JPG) stránek kroniky. Obrázky jsou
ručně psaný český text (většinou kurzívní pero/inkoust).

### Seznam sekcí

| Sekce | URL slug | Rozsah obrázků (přibližně) |
|-------|----------|---------------------------|
| Úvod až rok 1919 | uvod-az-rok-1919-2cs.html | img 8–31 |
| Rok 1920–1929 | rok-1920-1929-3cs.html | img 32–69 |
| Rok 1930–1939 | rok-1930-1939-4cs.html | img 70–132 |
| Rok 1940–1951 | rok-1940-1951-5cs.html | img 133–245 |
| Rok 1951–1954 | rok-1951-1954-6cs.html | img 246–317 |
| Rok 1955–1959 | rok-1955-1959-7cs.html | img 318–447 |
| Rok 1960–1964 | rok-1960-1964-8cs.html | img 448–491 |
| Rok 1965–1969 | rok-1965-1969-9cs.html | img 492–508 |
| Rok 1970–1974 | rok-1970-1974-10cs.html | img 509–545 |
| Rok 1975–1979 | rok-1975-1979-11cs.html | img 546–611 |
| Rok 1980–1984 | rok-1980-1984-12cs.html | img 612–687 |
| Rok 1985–1989 | rok-1985-1989-13cs.html | img 688–727 |
| Rok 1990–1993 | rok-1990-1993-14cs.html | img 728+ |

## Pracovní postup

### Krok 1: Scrape URL obrázků (`01_scrape_urls.py`)
- Projde všech 13 sekcí
- Z HTML extrahuje plné URL všech obrázků kroniky
- Uloží do `data/image_urls.json`

### Krok 2: Stažení obrázků (`02_download_images.py`)
- Stáhne všechny obrázky do `data/images/`
- Pojmenuje je systematicky: `section_01_page_001.jpg` atd.
- Podporuje resume (přeskočí už stažené)

### Krok 3: OCR přepis pomocí Claude API (`03_ocr_transcribe.py`)
- Odešle každý obrázek do Claude API (claude-opus-4-20250514 s vision)
- Ve výchozím režimu posílá obrázky přímo z URL (plná kvalita bez komprese)
- S `--local` čte z disku (vyžaduje předchozí stažení přes krok 2)
- Posílá kontext přepisu předchozí stránky pro lepší rozpoznání jmen a míst
- Výsledky ukládá průběžně do `data/transcriptions.json`
- Podporuje resume (přeskočí už přepsané)
- Rate limiting: 1 request / 2 sekundy

### Krok 4: Sestavení HTML (`04_build_html.py`)
- Načte přepisy a sestaví výslednou HTML stránku
- Struktura: navigace po sekcích, jednotlivé stránky s přepisem
- Volitelně: vedle přepisu zobrazí i miniaturu originálu

## Důležité poznámky

- Ručně psaný text je obtížný na OCR – počítej s chybami, zvlášť u starších zápisů
- Některé stránky mohou obsahovat kresby, tabulky, mapy – ty nelze přepsat
- Doporučuji zpracovávat po sekcích a průběžně kontrolovat kvalitu
- API klíč se čte z env proměnné `ANTHROPIC_API_KEY`
- Plné URL obrázků: `https://www.vranov.cz/evt_image.php?img={ID}`
  (bez parametrů width/height vrátí originální rozlišení)

## Spuštění

```bash
# Nainstaluj závislosti
pip install -r requirements.txt

# 1. Stáhni URL obrázků
python 01_scrape_urls.py

# 2. Stáhni obrázky
python 02_download_images.py

# 3. Přepiš pomocí Claude API (trvá dlouho!)
# Ve výchozím režimu čte obrázky přímo z URL (plná kvalita):
python 03_ocr_transcribe.py

# Nebo přepiš jen jednu sekci:
python 03_ocr_transcribe.py --section "Úvod až rok 1919"

# Čtení z lokálních souborů místo URL (vyžaduje krok 2):
python 03_ocr_transcribe.py --local

# Bez kontextu předchozí stránky:
python 03_ocr_transcribe.py --no-context

# 4. Sestav HTML
python 04_build_html.py
```

## Výstup

Finální HTML stránka: `output/kronika_vranov.html`
