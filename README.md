# 📜 Kronika obce Vranov – OCR přepis

Přepis ručně psané obecní kroniky obce Vranov (u Brna) pomocí Claude AI (vision) a statický web s přepisem, rejstříky a hledáním.

Zdrojové skeny kroniky: [vranov.cz/obec/historie/kronika-obce-vranov](https://www.vranov.cz/obec/historie/kronika-obce-vranov/)

**Přepis online:** [michalprouza.github.io/Vranov-kronika-OCR](https://michalprouza.github.io/Vranov-kronika-OCR/)
(stránku sestavuje a publikuje workflow `.github/workflows/pages.yml` při změně přepisů,
dat nebo skriptů webu ve větvi `main`, viz [Publikace](#publikace)).

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

Součástí stránky jsou tři **rejstříky** s vyhledáváním a odkazy na strany (po
kliknutí se hledané slovo na stránce zvýrazní):

- **rejstřík příjmení** – osoby, které kronika zmiňuje, viz
  [Rejstřík příjmení](#rejstřík-příjmení),
- **rejstřík míst** – části Vranova, pomístní názvy (Babí lom, Žižkov, Vranovský
  žleb…), budovy, okolní obce, země a řeky, viz [Rejstřík míst](#rejstřík-míst),
- **rejstřík domů** – čísla domů („č. 35“) s úryvkem textu, takže je vidět, kdo
  v domě v různých letech bydlel, viz [Rejstřík domů](#rejstřík-domů).

Pod některými stranami je rámeček **Souvislosti** s odkazy na články
[Vranovského zpravodaje](https://www.vranov.cz/obec/zpravodaj-/), které zápis doplňují
– například vzpomínky pamětníků a výpisy ze sokolské kroniky k osvobození v květnu 1945
(zpravodaj 2/2005). Další odkazy vedou na badatelské stránky
(např. o pádu německého cvičného letounu u Vranova na davar.cz), Encyklopedii dějin
města Brna, Paměť národa a na dobové noviny a knihy z let 1864–1950 v
[Národní digitální knihovně](https://ndk.cz/) (volně dostupné skeny: svěcení školy 1885,
vyloupení lichtenštejnské hrobky 1871, Topografie diecése brněnské 1908, poutě 1947…).
Přehled všech 120 vybraných článků je na stránce před rejstříky;
seznam se udržuje ručně v `data/souvislosti.json` (pole `strany` = ID skenů stran
kroniky, k nimž článek patří).

Všechny strany jsou také v `data/transcriptions.json`; HTML stránku s celým
přepisem sestavíte příkazem `python 04_build_html.py --raw`
(výstup `output/kronika_vranov.html`). Podrobnosti k jednotlivým sekcím (kronikáři,
číslování stran, duplicitní skeny mezi galeriemi, známé nejistoty) jsou v souborech
`README.md` v adresářích `data/ocr_pages/section_XX/` (sekce 01 a 11 je nemají).

## Tisky mimo kroniku

Mimo kroniku jsou přepsané i dva strojopisné tisky z roku 1990, jejichž skeny jsou
v releasu [Vranov_1990](https://github.com/MichalProuza/Vranov-kronika-OCR/releases/tag/Vranov_1990),
a tištěná brožurka z roku 1937, jejíž sken je volně v Národní digitální knihovně:

| Tisk | Stran | Souvislý přepis | Strany |
| --- | --- | --- | --- |
| Vranov u Brna 750 (1240–1990) – historie v datech, pomístní jména | 33 | [vranov-u-brna-750-1240-1990.md](docs/transcriptions/vranov-u-brna-750-1240-1990.md) | `data/ocr_pages/vranov_1240-1990/` |
| Vranovák, srpen–září 1990 | 16 | [vranovak-1990.md](docs/transcriptions/vranovak-1990.md) | `data/ocr_pages/vranovak_1990_1/` |
| František Fürst: Vranov, poutní místo u Brna (3. vyd., 1937) – [sken v NDK](https://ndk.cz/uuid/uuid:2bff7e60-8f98-11ef-9e23-5ef3fc9bb22f) | 12 | [vranov-poutni-misto-1937.md](docs/transcriptions/vranov-poutni-misto-1937.md) | `data/ocr_pages/vranov_poutni_misto_1937/` |

Na webu jsou tisky zařazeny jako samostatné sekce za kronikou a rejstříky zahrnují i je. Nejsou
v `data/transcriptions.json`; `04_build_html.py` je čte přímo ze souborů stran podle seznamu
`EXTRA_SECTIONS` v `config.py` (`source_label` mění text odkazu na sken, výchozí je „sken (PDF)“).

### Národní knihovna

Plné texty Národní digitální knihovny (Kramerius NK) obsahují spojení „Vranov u Brna“ na zhruba
2 900 stranách. Asi 190 z nich je volně dostupných; z nich je vybráno 39 zpráv do Souvislostí a
brožurka z roku 1937 je přepsaná výše. Ostatní díla (např. Vladimír Beránek: *Vranov u Brna – historie
a památky*, 1940; sborník *Poutní místo Vranov*, 1997; Rovnost, Vlastivědný věstník moravský) jsou
chráněná autorským právem a otevřou se jen přihlášenému čtenáři NK. Jejich pracovní seznam s odkazy
přímo na strany se zmínkou je v [docs/narodni-knihovna-po-prihlaseni.md](docs/narodni-knihovna-po-prihlaseni.md).

## Jak přepis vznikl

Repozitář obsahuje dvě cesty k přepisu. Zveřejněný přepis vznikl tou druhou.

**A. Původní pipeline přes Claude API (skripty 01–05)**

1. **Scraping** (`01_scrape_urls.py`) – z 13 galerií na webu obce vytáhne ID a URL skenů do
   `data/image_urls.json` (828 skenů, soubor je v repozitáři).
2. **Download** (`02_download_images.py`) – stáhne skeny v plném rozlišení do
   `data/images/section_XX/page_NNN_idID.jpg` (adresář není v gitu).
3. **OCR přepis** (`03_ocr_transcribe.py`) – pošle každý sken do Claude API (vision) spolu s koncem
   přepisu předchozí strany jako kontextem; výsledek ukládá do `data/transcriptions.json`.
4. **Uhlazení textu** (`05_polish_text.py`) – surové přepisy pošle jazykovému modelu k opravě
   překlepů a chyb OCR; výsledek ukládá do `data/transcriptions_polished.json`.
5. **HTML výstup** (`04_build_html.py`) – z přepisů sestaví webovou stránku.

**B. Přepis po stranách do souborů (takto vznikl současný stav)**

Strany jsou přepsané přímým čtením skenů a uložené jako textové soubory
`data/ocr_pages/section_XX/page_NNN_idID.txt` (první řádek je číslo strany kroniky, druhý rok
nebo prázdný řádek). Skript `06_merge_page_texts.py` je podle `data/image_urls.json` sloučí do
`data/transcriptions.json` ve stejném formátu, jaký vyrábí krok 3. Soubor
`data/transcriptions.json` v repozitáři odpovídá souborům stran přesně (828 stran). Uhlazení
(krok 4) se na zveřejněný přepis nepoužilo: `data/transcriptions_polished.json` v repozitáři
není a web se sestavuje s `--raw`.

Souvislé přepisy a seznamy míst k ověření v `docs/transcriptions/` jsou uložené hotové; skript,
který by je generoval, v repozitáři není.

## Požadavky

- Python 3.10+ (testy běží v CI na 3.10, web se sestavuje na 3.12).
- Sestavení HTML (`04_build_html.py`), sloučení stran (`06_merge_page_texts.py`) a rejstříky
  nepotřebují nic mimo standardní knihovnu – ani API klíč, ani internet.
- Skripty 01 a 02 potřebují `requests`, `beautifulsoup4` a `tqdm`; skripty 03 a 05 balíček
  `anthropic` a API klíč v proměnné `ANTHROPIC_API_KEY`. Vše je v `requirements.txt`.

> **Pozor – modely ve skriptech 03 a 05 je před použitím potřeba aktualizovat.**
> `config.py` má `CLAUDE_MODEL = "claude-opus-4-20250514"` (používá ho `03_ocr_transcribe.py`)
> a `05_polish_text.py` nabízí `claude-opus-4-20250514`, `claude-sonnet-4-20250514`
> a `claude-haiku-4-5-20251001`. Modely Claude Opus 4 a Sonnet 4 už Anthropic neprovozuje
> (vyřazeny 15. 6. 2026), takže krok 3 a volby `opus`/`sonnet` v kroku 5 bez úpravy ID modelu
> skončí chybou API. Cenu nového běhu je proto nutné spočítat podle aktuálního ceníku; částky,
> které vypisuje `05_polish_text.py` (~$38 / ~$8 / ~$2 za celou kroniku), platily pro původní modely.

## Instalace

```bash
git clone https://github.com/MichalProuza/Vranov-kronika-OCR.git
cd Vranov-kronika-OCR
pip install -r requirements.txt
```

API klíč (jen pro skripty 03 a 05) – podle prostředí:

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

### Sestavení webu z přepisů v repozitáři

```bash
# Po úpravě souborů stran v data/ocr_pages/section_XX/ je slouč do transcriptions.json
python 06_merge_page_texts.py

# Sestav HTML (stejně jako workflow pro GitHub Pages); trvá zhruba půl minuty
python 04_build_html.py --raw

# S miniaturami skenů vedle přepisu (načítají se z vranov.cz až při prohlížení)
python 04_build_html.py --raw --with-thumbnails
```

Bez `--raw` použije `04_build_html.py` uhlazené přepisy z `data/transcriptions_polished.json`,
pokud soubor existuje (strany, které v něm chybí, doplní ze surových); jinak sestaví ze surových.

### Původní pipeline (stahuje z webu obce a volá placené API)

```bash
# 1. Stáhni URL obrázků z webu (přepíše data/image_urls.json)
python 01_scrape_urls.py

# 2. Stáhni obrázky (828 souborů, může trvat)
python 02_download_images.py

# 3. OCR přepis pomocí Claude API (obrázky posílá jako URL, plná kvalita)
python 03_ocr_transcribe.py
python 03_ocr_transcribe.py --section "Úvod až rok 1919"   # jen sekce (stačí část názvu)
python 03_ocr_transcribe.py --section-index 2              # sekce podle pořadí (od 1)
python 03_ocr_transcribe.py --limit 5                      # nejvýš 5 stran
python 03_ocr_transcribe.py --local                        # obrázky z disku (po kroku 2)
python 03_ocr_transcribe.py --no-context                   # bez přepisu předchozí strany
python 03_ocr_transcribe.py --force                        # přepíše i hotové strany
python 03_ocr_transcribe.py --dry-run                      # jen vypíše, co by dělal

# 4. Uhlaď přepisy jazykovým modelem
python 05_polish_text.py                 # na model (opus/sonnet/haiku) se zeptá
python 05_polish_text.py --model haiku   # nebo rovnou s modelem
python 05_polish_text.py --section "Úvod až rok 1919"
python 05_polish_text.py --force --model haiku   # přepíše existující uhlazení
# dále --section-index, --limit, --no-context, --dry-run jako u kroku 3

# 5. Sestav HTML (automaticky použije uhlazené přepisy, pokud existují)
python 04_build_html.py
```

`03_ocr_transcribe.py` zapisuje do stejného `data/transcriptions.json`, ve kterém je hotový
přepis; hotové strany přeskakuje, s `--force` by je ale přepsal výstupem API.

### Testy

```bash
pip install pytest
pytest
```

V `tests/` je 30 testů (rejstřík příjmení, míst a domů, Souvislosti, tisky mimo kroniku,
přepínání oddílů, vzhled, slučování stran). Skripty 01–03 a 05 testy nemají. Workflow
`.github/workflows/python-app.yml` pouští flake8 a pytest při pushi do `main` a u pull requestů.

## Výstup

- `output/kronika_vranov.html` – celý přepis v jednom souboru (asi 4,4 MB, adresář `output/`
  není v gitu). CSS i skript jsou vložené; z internetu se načítají jen písma (Google Fonts),
  odkazované skeny a případné miniatury
- Responzivní design, tisk-friendly
- Zobrazuje se vždy jen jeden oddíl (desetiletí, tisk, rejstřík…): listování předchozí/další, skok na stranu,
  odkazy na oddíl i stranu v adrese (`#rok-1920-1929`, `#page-123`). Bez JavaScriptu a při tisku je
  vidět vše pod sebou
- Hledání v celém textu kroniky najednou (bez ohledu na diakritiku) se skokem na nalezené místo
- Rejstřík příjmení, míst a domů s vyhledáváním (bez ohledu na diakritiku) a zvýrazněním na stránce
- Souvislosti pod stranami a v souhrnném přehledu, tisky mimo kroniku (1937, 1990) jako sekce za kronikou
- U každé strany odkaz na originální sken na webu obce (u tisků z roku 1990 na PDF v releasu, u brožurky z roku 1937 na Národní knihovnu)
- Nejistá slova označena oranžově, nečitelná červeně
- Text zarovnaný do bloku (justify) – OCR řádkové zlomy se automaticky spojují do plynulého textu;
  u strojopisných tisků se řádky ponechávají
- Rozdělovníky na konci řádku se automaticky spojí (např. `Schön-` + `brunn` → `Schönbrunn`)
- Na konci stránky je **logomanuál** (`#logomanual`): značka webu, barvy a písma. Vzhled je
  v `brand.py` a vychází ze znaku obce (`data/znak_obce.png`); značka je zjednodušená kresba,
  ne úřední znak

Strany se v sekci řadí podle ID skenu, ne podle pořadí v galerii. V sekci 1951–1954 proto web
ukazuje strany v pořadí 3, 1, 2 (skeny 245, 246, 247).

## Rejstřík příjmení

Rejstřík sestavuje `name_index.py` při každém spuštění `04_build_html.py`
(není potřeba API ani žádný další krok). Příjmení se hledají heuristicky:

1. slovo s velkým písmenem vedle křestního jména („Josef Skoupý“, „Skoupý Josef“,
   „Fr. Kudla“, „J. Novák“) nebo za titulem („Ing. Nehyba“, „s. Puchar“, „pí Nečasová“),
2. pak se dohledají všechny stránky, kde se kterýkoli tvar už známého příjmení
   vyskytuje i samostatně („Holešovský řekl…“).

Skloňované tvary a ženská příjmení se slučují pod jedno heslo
(„Holešovský, Holešovská“ zahrnuje i „Holešovského“, „Holešovskou“…), stejně jako
pravopisné varianty lišící se jen diakritikou (Svitil/Svítil). Hesla jsou řazena
podle české abecedy (ch za h).

Jde o strojovou pomůcku – některá jména mohou chybět a výjimečně se do rejstříku
dostane i slovo, které příjmením není. Taková slova se vyřadí zapsáním do
`data/rejstrik_vyjimky.txt` (vyřadí se i jejich ostatní tvary) a novým sestavením
HTML.

## Rejstřík míst

Místní jména se strojově spolehlivě rozpoznat nedají („Kateřina“ je poutní místo
i křestní jméno, „Březina“ část obce i příjmení), proto rejstřík míst
(`place_index.py`) vychází z ručně sestaveného seznamu `data/rejstrik_mist.txt`.
Každý řádek je heslo a jeho tvary v textu, hvězdička zastoupí koncovku:

```
[Vranov – části obce a pomístní názvy]
Babí lom: Bab* lom*, Bab* Lom*, Babílom*
Svatá Kateřina: Sv. Kateřin*, do Kateřiny, u Kateřiny, Kateřinsk*
```

Řádek v hranatých závorkách zahajuje skupinu rejstříku. Skupina `[Nezařazovat]` se
nezobrazí – jen zabrání tomu, aby se např. „Vranov u Brna“ počítalo jako zmínka
o Brně. Místa, která v seznamu ještě chybí (slova s velkým písmenem za předložkami
do, ve, na…), vypíše:

```bash
python place_index.py --kandidati
```

## Rejstřík domů

Rejstřík domů (také `place_index.py`) hledá čísla domů zapsaná jako „č. 35“,
„č. p. 35“, „čp. 35“ nebo „čís. 35“ a u každého výskytu ukáže kousek okolního textu
(„…Holešovský Frant. **č. 35**, předseda…“). Vyhledávat lze číslem domu i jménem
z úryvku. Vynechává čísla, která domy nejsou: „K. č.“ (korun českých), „archiv
kroniky č. 6/60“, „Strana č. 1“, „autobusy č. 57“, parcelní čísla s lomítkem.
Čísla domů v okolních obcích se od vranovských automaticky nerozliší – pozná se to
z úryvku.

## Resume podpora

Skripty 02, 03 a 05 podporují přerušení a pokračování – přeskočí už stažené/přepsané/uhlazené stránky. Skripty 03 a 05 ukládají po každé straně a mezi voláními API čekají 2 sekundy.

- Skript 02 považuje za stažený každý neprázdný soubor. Po přerušeném stahování proto nedokončený
  obrázek smaž ručně, jinak se už nestáhne znovu.
- Skripty 03 a 05 při překročení limitu API (rate limit) počkají 60 s a stranu zkusí ještě jednou.
  Jinou chybu jen vypíšou a pokračují další stranou; chybějící strany doplní další spuštění.
- Odpověď oříznutou limitem 8192 výstupních tokenů skripty nepoznají a uloží ji jako hotovou.

Skript 05 při opakovaném spuštění detekuje existující uhlazené přepisy a nabídne přepsání jiným modelem, zpracování jen chybějících stránek, nebo zrušení.

## Publikace

Web na GitHub Pages sestavuje a publikuje `.github/workflows/pages.yml`: spustí
`python 04_build_html.py --raw` a výsledek nasadí jako `index.html`. Spouští se při pushi do
`main`, který změní `data/transcriptions.json`, `data/souvislosti.json`, seznamy rejstříků
(`data/rejstrik_mist.txt`, `data/rejstrik_vyjimky.txt`), strany tisků v `data/ocr_pages/vranov_1240-1990/`
a `data/ocr_pages/vranovak_1990_1/`, `data/znak_obce.png`, `04_build_html.py`, `brand.py`,
`name_index.py`, `place_index.py`, `config.py` nebo samotný workflow; lze ho pustit i ručně.
Změna souborů stran kroniky v `data/ocr_pages/section_XX/` se na webu projeví až po sloučení
skriptem `06_merge_page_texts.py`.

## Struktura projektu

```
├── CLAUDE.md               # Instrukce pro Claude Code
├── README.md
├── requirements.txt
├── config.py               # Sdílená konfigurace (cesty, sekce, EXTRA_SECTIONS, model, prompty)
├── 01_scrape_urls.py       # Stáhne URL obrázků
├── 02_download_images.py   # Stáhne obrázky
├── 03_ocr_transcribe.py    # OCR přepis (Claude API)
├── 04_build_html.py        # Sestaví HTML výstup
├── 05_polish_text.py       # Uhlazení textu (Claude API)
├── 06_merge_page_texts.py  # Sloučí data/ocr_pages/section_XX/*.txt do transcriptions.json
├── name_index.py           # Rejstřík příjmení (používá 04_build_html.py)
├── place_index.py          # Rejstřík míst a domů (používá 04_build_html.py)
├── brand.py                # Vzhled webu: barvy, písma, značka, logomanuál
├── tests/                  # Testy (pytest)
├── .github/workflows/
│   ├── pages.yml           # Sestavení a publikace na GitHub Pages
│   └── python-app.yml      # flake8 + pytest
├── data/
│   ├── image_urls.json     # URL obrázků (výstup kroku 1)
│   ├── images/             # Stažené obrázky (generováno, není v gitu)
│   ├── ocr_pages/          # Přepisy po stranách: section_01–13 (kronika), tisky z let 1937 a 1990
│   ├── transcriptions.json # Přepisy všech stran kroniky (z 06 nebo 03)
│   ├── transcriptions_polished.json # Uhlazené přepisy (generováno krokem 4, v repozitáři není)
│   ├── souvislosti.json    # Ruční seznam souvisejících článků
│   ├── rejstrik_mist.txt   # Seznam míst a jejich tvarů pro rejstřík míst
│   ├── rejstrik_vyjimky.txt # Slova vyřazená z rejstříku příjmení
│   └── znak_obce.png       # Znak obce (předloha vzhledu, zobrazen v logomanuálu)
├── docs/transcriptions/    # Souvislé přepisy sekcí (Markdown) a seznamy míst k ověření
├── docs/narodni-knihovna-po-prihlaseni.md # Díla o Vranově v NDK dostupná jen po přihlášení
├── vranov-kronika-ocr-web/ # Starší samostatná ukázka prvních 5 stran; web ji nepoužívá
└── output/
    └── kronika_vranov.html # Finální HTML (generováno, není v gitu)
```

## Tipy

- **Kvalita přepisu** závisí na čitelnosti originálu. Starší zápisy (kurent, ornamentální písmo) budou méně přesné.
- **Po sekcích** – při novém běhu přes API doporučuji zpracovat nejdřív 1–2 sekce (nebo `--limit 5`) a zkontrolovat kvalitu, než pustíš vše.
- **Místa k ověření** – seznamy nejistých čtení po sekcích jsou v `docs/transcriptions/*-k-overeni.md`.
- **Claude Code** – otevři projekt v Claude Code (`claude` v terminálu) a můžeš iterativně ladit přepisy.
