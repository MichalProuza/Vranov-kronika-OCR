"""Rejstřík míst a rejstřík domů – vyhledání v přepisu kroniky.

**Rejstřík míst** vychází z ručně sestaveného seznamu v ``data/rejstrik_mist.txt``
(heslo a jeho tvary v textu). Strojově rozpoznávat místní jména spolehlivě
nejde – „Kateřina“ je jednou poutní místo a podruhé křestní jméno, „Březina“
část obce i příjmení –, proto se hledají jen tvary ze seznamu. Seznam lze
libovolně doplňovat. Kandidáty na doplnění vypíše::

    python place_index.py --kandidati

**Rejstřík domů** hledá čísla domů zapsaná jako „č. 35“, „čp. 35“, „č. p. 35“
nebo „čís. 35“. Vynechává čísla, která domy nejsou („K. č.“ = korun
českých, „archiv kroniky č. 6/60“, „Strana č. 1“, parcelní čísla s lomítkem).
U každého výskytu si pamatuje kousek okolního textu, takže je v rejstříku
vidět, kdo v domě bydlel nebo co se tam stalo.
"""

from __future__ import annotations

import re
import unicodedata
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from name_index import czech_sort_key

GAZETTEER_FILE = Path(__file__).parent / "data" / "rejstrik_mist.txt"
HIDDEN_GROUP = "Nezařazovat"


def clean_text(text: str) -> str:
    """Text without uncertainty markers, with words split at line ends joined
    and all whitespace collapsed to single spaces."""
    text = re.sub(r"\[\?(.+?)\?\]", r"\1", text)
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)
    return re.sub(r"\s+", " ", text)


def _fold(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn")


# --- Rejstřík míst ------------------------------------------------------------

@dataclass
class PlaceEntry:
    heading: str
    group: str
    variants: list[str]
    pattern: re.Pattern = field(repr=False, default=None)

    def __post_init__(self):
        if self.pattern is None:
            alts = sorted((variant_regex(v) for v in self.variants), key=len, reverse=True)
            self.pattern = re.compile("|".join(alts))


@dataclass
class Place:
    heading: str
    group: str
    forms: Counter = field(default_factory=Counter)
    pages: dict = field(default_factory=dict)  # page_id -> počet výskytů

    @property
    def sort_key(self) -> tuple:
        return czech_sort_key(self.heading)


def variant_regex(variant: str) -> str:
    """„Bab* lom*“ → regulární výraz; * = libovolná koncovka slova."""
    parts = []
    for word in variant.split():
        star = word.endswith("*")
        word = word.rstrip("*")
        p = re.escape(word) + (r"\w*" if star else "")
        if parts:
            parts.append(r"\s*" if parts[-1].endswith(r"\.") else r"\s+")
        parts.append(p)
    regex = r"(?<!\w)" + "".join(parts)
    return regex if variant.endswith(".") else regex + r"(?!\w)"


def load_gazetteer(path: Path = GAZETTEER_FILE) -> list[PlaceEntry]:
    entries = []
    group = ""
    if not path.exists():
        return entries
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        if line.startswith("[") and line.endswith("]"):
            group = line[1:-1].strip()
            continue
        if ":" not in line:
            raise ValueError(f"{path.name}: chybí dvojtečka v řádku „{raw}“")
        heading, variants = line.split(":", 1)
        variants = [v.strip() for v in variants.split(",") if v.strip()]
        if variants:
            entries.append(PlaceEntry(heading.strip(), group, variants))
    return entries


def find_places(text: str, entries: list[PlaceEntry]) -> list[tuple[int, int, PlaceEntry]]:
    """Non-overlapping matches (start, end, entry); the longest match wins,
    so „Vranov u Brna“ is not also counted as Brno."""
    hits = []
    for entry in entries:
        hits += [(m.start(), m.end(), entry) for m in entry.pattern.finditer(text)]
    hits.sort(key=lambda h: (h[0], -(h[1] - h[0])))
    out, last_end = [], -1
    for start, end, entry in hits:
        if start >= last_end:
            out.append((start, end, entry))
            last_end = end
    return out


def build_place_index(pages: list[dict], gazetteer_path: Path = GAZETTEER_FILE) -> dict[str, list[Place]]:
    """pages: list of {"id": ..., "text": str}.
    Returns {group: [Place sorted alphabetically]} in the order of the gazetteer."""
    entries = load_gazetteer(gazetteer_path)
    places: dict[str, Place] = {}
    for page in pages:
        text = clean_text(page["text"])
        for start, end, entry in find_places(text, entries):
            if entry.group == HIDDEN_GROUP:
                continue
            place = places.setdefault(entry.heading, Place(entry.heading, entry.group))
            place.forms[text[start:end]] += 1
            place.pages[page["id"]] = place.pages.get(page["id"], 0) + 1
    groups: dict[str, list[Place]] = {}
    for entry in entries:
        if entry.heading in places and entry.heading not in {p.heading for p in groups.get(entry.group, [])}:
            groups.setdefault(entry.group, []).append(places[entry.heading])
    return {g: sorted(ps, key=lambda p: p.sort_key) for g, ps in groups.items()}


# --- Rejstřík domů ------------------------------------------------------------

HOUSE_RE = re.compile(r"(?<!\w)(č\.\s*p\.|čp\.|čís\.|č\.)\s*(\d{1,3})(?![\d\w])(?!\s*/\s*\d)(?![.,]\d)")
MAX_HOUSE = 400
# Slova, za nimiž „č.“ neoznačuje dům.
NOT_HOUSE_BEFORE = {
    "korun", "archiv", "archivu", "archiv.", "kroniky", "kron", "kroniku", "kronika",
    "dokl", "doklad", "strana", "strany", "hnuti", "parc", "p", "autobus", "autobusy", "autobusu",
    "linka", "linky", "pluk", "pluku", "zakon", "zakona", "zakonem", "vyhlaska", "vyhlasky",
    "usneseni", "smlouva", "smlouvy", "sesit", "list", "listu", "priloha", "prilohy", "bod", "odst",
    "odstavec", "kapitola", "svetnici", "scitani", "vlak", "vlaku", "tramvaj", "rota", "prapor",
    "cislo", "kniha", "knihy", "fotografie", "foto", "obr", "obrazek", "snimek", "vyrobni",
    "obvod", "obvodu", "okrsek", "okrsku",
}
CURRENCY = {"K", "Kč", "Kčs"}  # „5 K. č.“ = korun českých (malé „k č. 66“ je předložka)
_WORD_BEFORE_RE = re.compile(r"([^\W\d_]+)\.?\W*$")
_SNIPPET_BEFORE = 70
_SNIPPET_AFTER = 40


@dataclass
class HouseMention:
    page_id: object
    form: str  # „č. 35“ přesně jak stojí v textu
    snippet: tuple[str, str, str]  # (před, zmínka, za)


@dataclass
class House:
    number: int
    mentions: list[HouseMention] = field(default_factory=list)

    @property
    def pages(self) -> dict:
        out: dict = {}
        for m in self.mentions:
            out[m.page_id] = out.get(m.page_id, 0) + 1
        return out


def _snippet(text: str, start: int, end: int) -> tuple[str, str, str]:
    a = max(0, start - _SNIPPET_BEFORE)
    b = min(len(text), end + _SNIPPET_AFTER)
    before, after = text[a:start], text[end:b]
    if a > 0:
        before = "…" + before.split(" ", 1)[-1] if " " in before else "…" + before
    if b < len(text):
        after = after.rsplit(" ", 1)[0] + "…" if " " in after else after + "…"
    return before, text[start:end], after


def find_houses(text: str) -> list[tuple[int, int, int]]:
    """(start, end, number) of house numbers in cleaned text."""
    out = []
    excluded_end = None
    for m in HOUSE_RE.finditer(text):
        number = int(m.group(2))
        prev = _WORD_BEFORE_RE.search(text[max(0, m.start() - 30):m.start()])
        prev_raw = prev.group(1) if prev else ""
        prev_word = _fold(prev_raw)
        # „autobusy č. 57 a č. 43“ – druhé číslo patří ke stejnému výčtu
        chained = excluded_end is not None and re.fullmatch(r"\s*(?:a|,)\s*", text[excluded_end:m.start()])
        if prev_word in NOT_HOUSE_BEFORE or prev_raw in CURRENCY or chained or not 1 <= number <= MAX_HOUSE:
            excluded_end = m.end()
            continue
        excluded_end = None
        out.append((m.start(), m.end(), number))
        # „domy č. 125 a 126.“ (ne „č. 35 a 2 synové“)
        tail = re.match(r"\s+(a\s+(\d{1,3}))(?=\s*[.,;)](?!\d)|\s*$)", text[m.end():])
        if tail and 1 <= int(tail.group(2)) <= MAX_HOUSE:
            out.append((m.end() + tail.start(1), m.end() + tail.end(1), int(tail.group(2))))
    return out


def build_house_index(pages: list[dict]) -> list[House]:
    """pages: list of {"id": ..., "text": str}. Returns houses sorted by number."""
    houses: dict[int, House] = {}
    for page in pages:
        text = clean_text(page["text"])
        for start, end, number in find_houses(text):
            houses.setdefault(number, House(number)).mentions.append(
                HouseMention(page["id"], text[start:end], _snippet(text, start, end)))
    return [houses[n] for n in sorted(houses)]


# --- Kandidáti na doplnění seznamu míst --------------------------------------

def suggest_places(pages: list[dict], gazetteer_path: Path = GAZETTEER_FILE, min_count: int = 2):
    """Capitalised words after place prepositions that the gazetteer does not cover."""
    from name_index import stem_key
    entries = load_gazetteer(gazetteer_path)
    counts: Counter = Counter()
    forms: dict[str, Counter] = {}
    word = r"[A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ][a-záčďéěíňóřšťúůýž]{2,}"
    for page in pages:
        text = clean_text(page["text"])
        covered = [(s, e) for s, e, _ in find_places(text, entries)]
        for m in re.finditer(rf"(?<!\w)(?:do|ze|z|ve|v|na|u|ku|k|pod|nad|od|přes|kolem)\s+({word})", text):
            if any(s <= m.start(1) < e for s, e in covered):
                continue
            key = _fold(stem_key(m.group(1)))
            counts[key] += 1
            forms.setdefault(key, Counter())[m.group(1)] += 1
    return [(n, [f for f, _ in forms[k].most_common(4)]) for k, n in counts.most_common() if n >= min_count]


if __name__ == "__main__":
    import argparse
    import json

    from config import TRANSCRIPTIONS_FILE

    parser = argparse.ArgumentParser(description="Rejstřík míst a domů")
    parser.add_argument("--kandidati", action="store_true",
                        help="Vypíše slova za předložkami (do, ve, na…), která v seznamu míst chybí")
    args = parser.parse_args()
    data = json.loads(TRANSCRIPTIONS_FILE.read_text(encoding="utf-8"))
    all_pages = [{"id": p.get("img_id"), "text": p.get("text", "")} for sec in data.values() for p in sec.values()]
    if args.kandidati:
        for n, fs in suggest_places(all_pages):
            print(f"{n:5}  {', '.join(fs)}")
    else:
        for group, places in build_place_index(all_pages).items():
            print(f"[{group}]")
            for p in places:
                print(f"  {p.heading}: {len(p.pages)} stran – {', '.join(f for f, _ in p.forms.most_common(5))}")
        houses = build_house_index(all_pages)
        print(f"\nDomy: {len(houses)} čísel, {sum(len(h.mentions) for h in houses)} zmínek")
