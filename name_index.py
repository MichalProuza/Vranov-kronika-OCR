"""Rejstřík příjmení – vyhledání osob v přepisu kroniky.

Příjmení se z textu získávají heuristicky ve dvou průchodech:

1. **Rozpoznání příjmení** – slovo s velkým písmenem je příjmení, pokud stojí
   vedle křestního jména („Josef Skoupý“, „Skoupý Josef“, „Fr. Kudla“) nebo za
   titulem či oslovením („Ing. Nehyba“, „s. Puchar“, „p. Novák“).
2. **Vyhledání výskytů** – všechny stránky, kde se kterýkoli tvar už známého
   příjmení vyskytuje (i samostatně, např. „Holešovský řekl…“).

Skloňované tvary se slučují podle společného kmene, takže „Holešovský“,
„Holešovského“, „Holešovská“ i „Holešovskou“ tvoří jedno heslo; stejně tak
„Drexler“, „Drexlera“ a „Drexlerová“.

Výsledek je jen pomůcka: strojová extrakce z OCR přepisu nachytá i pár
nepříjmení a některá jména mine. Slova, která se do rejstříku dostala omylem,
lze vyřadit v souboru ``data/rejstrik_vyjimky.txt``.
"""

from __future__ import annotations

import re
import unicodedata
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

EXCEPTIONS_FILE = Path(__file__).parent / "data" / "rejstrik_vyjimky.txt"

UPPER = "A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽÄÖÜ"
LOWER = "a-záčďéěíňóřšťúůýžäöüß"
TOKEN_RE = re.compile(rf"[{UPPER}{LOWER}]+(?:-[{UPPER}][{LOWER}]+)?(?:\.(?![{LOWER}]))?|[.!?:;,()\[\]„“\"–—]")
CAP_WORD_RE = re.compile(rf"^[{UPPER}][{LOWER}]+(?:-[{UPPER}][{LOWER}]+)?$")
INITIAL_RE = re.compile(rf"^[{UPPER}]\.$")

# --- Křestní jména -----------------------------------------------------------
# Mužská jména: nominativ, případně s kmenem pro pády (Karel → Karl-a).
MALE_NAMES = """
Adam Adolf Albert Albín Alexandr Alexej Alfons Alfred Alois Ambrož Antonín Arnošt
Augustin Bartoloměj Bedřich Benedikt Blahoslav Bohdan Bohumil Bohumír Bohuslav
Boleslav Bořivoj Božetěch Bronislav Bruno Ctibor Ctirad Cyril Čestmír Dalibor Daniel
David Dominik Drahomír Dušan Eduard Emanuel Emil Erich Ernest Evžen Ferdinand Filip
František Gabriel Gustav Hanuš Havel Herbert Hubert Hugo Hynek Ignác Igor Ivan Ivo Jakub Jan
Jaromír Jaroslav Jindřich Jiří Josef Julius Kamil Karel Kazimír Klement Konrád
Kristián Kryštof Křesomysl Ladislav Leopold Leoš Libor Lubomír Luboš Luděk Ludvík
Lukáš Marcel Marek Marián Martin Matěj Matouš Maxmilián Metoděj Michal Michail Milan
Miloslav Miloš Miroslav Mojmír Norbert Oldřich Oskar Osvald Oswald Otakar Otmar
Patrik Pavel Petr Prokop Přemysl Radek Radim Radomír Radoslav Richard Robert Roman
Rostislav Rudolf Řehoř Samuel Slavomír Soběslav Stanislav Svatopluk Svatoslav Šimon
Štěpán Tadeáš Teodor Tibor Tomáš Valentin Václav Vavřinec Viktor Vilém Vít Vladimír
Vladislav Vlastimil Vlastislav Vojtěch Vratislav Zbyněk Zdeněk Zikmund Čeněk Jaromil
Ota Oto Otto Kuba Franta Jura Pepík Tonda Láďa Mirek Jirka Honza Vašek Karl Franz Johann
Josip Hans Georg Wilhelm Anton Ludwig Ernst Leonid Nikita Vladimir Fidel
Ronald Konstantin Valerián Erik Ervín Horymír Jarmil Jaroslaw Lumír Vítězslav Vlasta
"""
# Pády s odlišným kmenem (vložné e) nebo nepravidelné.
MALE_STEMS = {
    "Karel": "Karl", "Pavel": "Pavl", "Zdeněk": "Zdeňk", "Čeněk": "Čeňk", "Luděk": "Luďk",
    "Radek": "Radk", "Zbyněk": "Zbyňk", "Vavřinec": "Vavřinc", "Mirek": "Mirk",
    "Vašek": "Vašk", "Havel": "Havl", "František": "Františk", "Hynek": "Hyňk",
    "Marek": "Mark", "Jeník": "Jeník",
}
FEMALE_NAMES = """
Adéla Alena Alice Alžběta Amálie Anastázie Anděla Andrea Anežka Anna Antonie Aloisie
Barbora Běla Berta Blanka Blažena Bohdana Bohumila Bohuslava Božena Dagmar Dana
Daniela Darina Drahomíra Eliška Ema Emilie Emílie Eva Filoména Františka Gabriela
Hana Hedvika Helena Hermína Ilona Irena Iva Ivana Jana Jarmila Jaroslava Jindřiška
Jiřina Jitka Johana Josefa Julie Kamila Karla Karolína Kateřina Klára Kristina Kristýna
Květa Květoslava Lea Lenka Libuše Lucie Ludmila Lýdie Magdaléna Marcela Marie Markéta
Marta Martina Matylda Milada Milena Miloslava Miroslava Monika Naděžda Natálie Olga
Otýlie Pavla Pavlína Petra Renata Romana Rosálie Růžena Silvie Simona Soňa Stanislava
Štěpánka Taťána Terezie Tereza Teodora Ludvika Valerie Vanda Věra Veronika Viktorie Vilemína
Vladimíra Vlasta Zdena Zdenka Zdeňka Zita Zuzana Žofie Mařena Mařka Anča Bára Mína
Margit Margareta Hilda Frída Gertruda Greta Paula Ida Vilma Valentina Jindra Mirka
Jarka Dáša Jolana Bohunka Boženka Liběna Ladislava Vladislava Vlastimila Zora Zorka
"""
# Zkratky křestních jmen (s tečkou), jak je kronikáři píší.
NAME_ABBREVIATIONS = """
Fr Frant Fran Franc Jos Jar Jaros Ant Anton St Stan Stanisl Zd Zden Vlast Vl Vlad Jindř
Jin Osw Osv Os Ferd Boh Bohum Bož Lad Mir Mil Rud Ludv Al Alf Ed Em Leop Kar Jarm Bedř
Jiř Václ Vác Ol Oldř Ot Jul Gust Met Metod Mich Ludm Mar Hel Kv Květ Ann Lib
Mart Vojt Wil Vil Rich Rob Rom Rost Svat Tom Vikt Ign Kaz Kl Klem Laď Luď Šim
"""

# Tituly a oslovení, za kterými následuje příjmení (výraz bez tečky).
TITLES = {
    "pan", "pana", "panu", "panem", "pí", "paní", "slečna", "slečny", "slečně",
    "soudruh", "soudruha", "soudruhu", "soudruhem", "soudružka", "soudružky", "soudružce",
    "soudružkou", "farář", "faráře", "páter", "řídící", "učitel", "učitelka", "učitele",
    "učitelky", "starosta", "starostou", "starosty", "kronikář", "kronikáře", "kapelník",
}
# Tituly psané zkratkou s tečkou („Ing. Nehyba“); u plných slov tečka znamená konec věty.
ABBREV_TITLES = {"p", "pí", "sl", "s", "ss", "Ing", "Dr", "MUDr", "JUDr", "PhDr", "RNDr",
                 "MVDr", "PaedDr", "Mgr", "Prof", "prof", "doc", "Doc", "P", "dp", "Dp", "MUC",
                 "akad", "arch", "Bc", "inž", "Inž", "ing", "řed", "uč", "nadučitel", "říd"}
# Předložky – slovo za nimi bývá místo („do Adamova“), ne příjmení.
PREPOSITIONS = {"z", "ze", "do", "v", "ve", "na", "k", "ku", "pod", "nad", "od", "po", "přes",
                "při", "s", "se", "před", "za", "u", "o", "mezi", "proti", "kolem", "okolo"}
# Jednopísmenné „iniciály“, které bývají zkratkou něčeho jiného (°C, římské číslice).
NOT_INITIALS = {"C.", "I.", "V.", "X.", "L."}

# Slova s velkým písmenem, která nejsou příjmení, i když stojí vedle jména.
DEFAULT_STOPWORDS = """
Na Ve Do Za Po Od Ku Ke Ze Se So Pro Při Před Pod Nad Mezi Přes Ale Až Tak Též Také
Kč Kčs Sv Svatý Svatá Svaté Svatého Svatou Svatém Svatých Boží Božího Panny Panna
Nový Nová Nové Nového Starý Stará Staré Dolní Horní Pole
Poli Králově Královo Králova Lom Lomu Dvůr Dvoře Mlýn Mlýně
Vranov Vranova Vranově Vranovem Vranovu Brno Brna Brně Brnem Brnu Praha Prahy Praze
Prahou Prahu Vídeň Vídně Vídni Moravy Morava Moravě Čechy Čech Československo
Rok Roku Den Dne Dnes Okraj Poznámka Podpis Razítko Obrázek Strana Viz Pozn Úvod
Ježíš Kristus Krista Kristu Pán Pána Bůh Boha Maria Marie Mariánské Panenka Panno
Křtitel Křtitele Nepomucký Nepomuckého Evangelista Apoštol Veliký Velikého Dobrotivý
Mládeže Mládež Svazu Svaz Svazem Jednota Jednoty Sokol Sokola Orel
Orla Beseda Besedy Komise Výbor Rada Strana Fronta Fronty Národní Národního
Sjezd Sjezdu Družstvo Družstva Zbrojovka Zbrojovky Zbrojovce Zbrojovku Zbrojovkou Lidová Lidové Rudé Právo Práva
Pomocné Pomocná Pomocnice Bolestné Sedmibolestné Počasí Hostinec Hotel Hotelu Kino
Kostel Kaple Kaplička Škola Školy Obec Obce Kulturní Osvětová Místní Okresní Krajský
Prvý První Druhý Třetí Celý Celá Každý Všichni Nyní Letos Jinak Potom Dále Zde Jest
Byl Byla Bylo Byli Byly Bude Budou Je Jsou Má Mají Měl Měla Zemřel Zemřela Narodil
Narodila Zapsal Zapsala Oženil Provdala Umřel Umřela Pohřeb Svatba Úmrtí Narození
Leden Únor Březen Duben Květen Červen Červenec Srpen Září Říjen Listopad Prosinec
Vánoce Velikonoce Hody Pouť Silvestr Sylvestra Medarda Matěje Josefa
"""
# Tvary, které nejsou příjmení, ale sdílejí kmen s příjmením (Němci × Němec);
# vyřazuje se jen přesně tento tvar.
STOP_TOKENS = {"Němci", "Němců", "Němcům", "Němcích", "Rusové", "Rusů", "Rusům", "Rusy", "Češi",
               "Čechů", "Slováci", "Slováků", "Poláci", "Poláků", "Maďaři", "Maďarů", "Američané",
               "Angličané", "Francouzi", "Italové", "Rakušané", "Prušáci", "Turci", "Turků"}

# Místní jména a přídavná jména od nich (slučují se i jejich skloňované tvary).
PLACE_WORDS = """
Vranov Vranovský Adamov Adamovský Lelekovice Lelekovický Šebrov Šebrovský Útěchov
Útěchovský Ořešín Jehnice Jehnický Kuřim Kuřimský Soběšice Řečkovice Blansko Blanenský
Tišnov Tišnovský Žižkov Sokolnice Kozlovice Lištava Svitavy Svitava Brno Brněnský
Praha Pražský Vídeň Vídeňský Český Česko Čechy Moravský Slovensko Slovenský Německo
Německý Rakousko Rakouský Rusko Ruský Polsko Polský Maďarsko Francie Anglie Amerika
Jugoslávie Bulharsko Rumunsko Kanada Itálie Moskva Kateřina Kateřinský Babí Kanice
Ochoz Bílovice Bystrc Medlánky Rájec Křtiny Komín Husovice Obřany Maloměřice
Královo Krpole Žabovřesky Dětský Pionýrský Obecní Státní Osvětový Požární
Finanční Národní Okresní Krajský Místní Hasičský Sokolský Školní Kulturní Lidový
"""


def _fold(s: str) -> str:
    """Remove diacritics and lowercase – for sorting, search and merging spelling variants."""
    return "".join(c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn")


_CZ_ORDER = "aábcčdďeéěfghiíjklmnňoópqrřsštťuúůvwxyýzž"
_CZ_PRIMARY = {"á": "a", "ď": "d", "é": "e", "ě": "e", "í": "i", "ň": "n", "ó": "o", "ť": "t",
               "ú": "u", "ů": "u", "ý": "y", "ä": "a", "ö": "o", "ü": "u", "ß": "s"}


def czech_sort_key(text: str) -> tuple:
    """Řazení podle české abecedy: č, ř, š, ž a ch jsou samostatná písmena
    (ch za h), ostatní diakritika rozhoduje až při shodě."""
    def letters(s: str, primary: bool):
        s = s.lower()
        out, i = [], 0
        while i < len(s):
            if s.startswith("ch", i):
                out.append(_CZ_ORDER.index("h") + 0.5)
                i += 2
                continue
            c = _CZ_PRIMARY.get(s[i], s[i]) if primary else s[i]
            out.append(_CZ_ORDER.index(c) if c in _CZ_ORDER else 100 + ord(c))
            i += 1
        return out
    return letters(text, True), letters(text, False)


def _male_forms(name: str) -> set[str]:
    forms = {name}
    stem = MALE_STEMS.get(name, name)
    if name.endswith(("a", "o")):  # Franta, Jura, Ota
        base = name[:-1]
        forms |= {base + e for e in ("a", "y", "ovi", "ou", "o", "u")}
    elif name.endswith("í"):  # Jiří
        forms |= {name + e for e in ("ho", "mu", "m")}
    elif name.endswith("ec"):
        forms |= {stem + e for e in ("e", "i", "em")}
    else:
        forms |= {stem + e for e in ("a", "ovi", "em", "e", "u", "i", "ovy")}
        if stem[-1] in "šžčřcjďťň":
            forms |= {stem + "i", stem + "e"}
    return forms


_SOFTEN = {"k": "c", "g": "z", "h": "z", "r": "ř", "ch": "š"}


def _female_forms(name: str) -> set[str]:
    forms = {name}
    if name.endswith("ie"):  # Marie
        base = name[:-1]
        forms |= {base + "i", base + "í"}
    elif name.endswith("a"):
        base = name[:-1]
        forms |= {base + e for e in ("y", "u", "ou", "o", "e", "ě", "i")}
        for hard, soft in _SOFTEN.items():
            if base.endswith(hard):
                forms.add(base[: -len(hard)] + soft + "e")
    elif name.endswith("e"):  # Alice
        forms |= {name[:-1] + "i", name[:-1] + "í"}
    return forms


# Křestní jména, která jsou ve Vranově také příjmeními („Stanislav Marek“).
NAME_AND_SURNAME = {"Marek", "Marka", "Markovi", "Markem", "Havel", "Havla", "Vít", "Vítek",
                    "Kuba", "Kuby", "Martin", "Martina", "Matal", "Jura", "Beran", "Vlasta"}


def _build_name_sets(extra_stopwords: set[str]):
    first = set()
    for n in MALE_NAMES.split():
        first |= _male_forms(n)
    for n in FEMALE_NAMES.split():
        first |= _female_forms(n)
    abbrevs = {a + "." for a in NAME_ABBREVIATIONS.split()}
    stop_keys = {_fold(stem_key(w)) for w in set(DEFAULT_STOPWORDS.split()) | extra_stopwords
                 | set(PLACE_WORDS.split())}
    stop = set(DEFAULT_STOPWORDS.split()) | extra_stopwords | STOP_TOKENS
    # tvary křestních jmen (i zkomolené OCR, „Františeky“), pokud nejde i o příjmení
    fn_keys = {_fold(stem_key(w)) for w in first} - {_fold(stem_key(w)) for w in NAME_AND_SURNAME}
    return first, abbrevs, stop, stop_keys, fn_keys


def load_exceptions(path: Path = EXCEPTIONS_FILE) -> set[str]:
    """Read user-maintained list of words that are never surnames."""
    if not path.exists():
        return set()
    words = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        words.update(line.split())
    return words


# --- Slučování tvarů ----------------------------------------------------------

_ENDINGS = sorted([
    "ových", "ovými", "ovým", "ovou", "ové", "ová", "ovi", "ovy", "ovo", "ovu",
    "ského", "skému", "ským", "ských", "skými", "skou", "ská", "ské", "ský", "ští",
    "ckého", "ckému", "ckým", "ckých", "ckou", "cká", "cké", "cký", "čtí",
    "ého", "ému", "ým", "ých", "ými", "ího", "ímu", "ím", "ích",
    "ou", "em", "ům", "ů", "a", "e", "ě", "u", "y", "i", "o", "ý", "á", "é", "í",
], key=len, reverse=True)


def stem_key(word: str) -> str:
    """Kmen tvaru slova pro slučování skloňovaných tvarů jednoho příjmení."""
    w = word
    for end in _ENDINGS:
        if w.endswith(end) and len(w) - len(end) >= 3:
            core = w[: -len(end)]
            if end.startswith("sk") or end.startswith("ck") or end in ("ští", "čtí"):
                core += "sk" if end[0] in "sš" else "ck"
            w = core
            break
    # vložné e: Beránek/Beránka, Němec/Němce, Skácel/Skácela
    if len(w) >= 5 and w[-2] == "e" and w[-1] in "kcl":
        w = w[:-2] + w[-1]
    if len(w) >= 5 and w[-2] == "ě" and w[-1] in "kc":
        w = w[:-3] + {"d": "ď", "t": "ť", "n": "ň"}.get(w[-3], w[-3]) + w[-1]
    return w


_OBLIQUE = ("em", "ům", "ových", "ovým", "ých", "ým", "ovi", "ého", "ému", "ího", "ímu", "ích", "ech", "ách")


def _is_female(form: str) -> bool:
    return form.endswith(("ová", "ská", "cká")) or (form.endswith("á") and len(form) > 4)


def _male_nominative(forms: Counter) -> str | None:
    """Guess the masculine nominative (Novák, Kučera, Holešovský) from observed forms."""
    observed = [f for f in forms if not _is_female(f) and not f.endswith(_OBLIQUE)]
    hard = [f for f in observed if f[-1] not in "aeěiouyáéíóúů" or f.endswith(("ý", "í"))]
    if hard:
        return max(hard, key=lambda f: forms[f])
    in_a = [f for f in observed if f.endswith("a")]
    if in_a:
        best = max(in_a, key=lambda f: forms[f])
        stem = best[:-1]
        # „Dvořáka“ je 2. pád od „Dvořák“ (dlouhá samohláska před koncovkou,
        # doložený 7. pád „Dvořákem“); „Filka/Filkem“ ale zůstane „Filka“
        if (stem + "em") in forms and (stem + "ou") not in forms and stem[-2:-1] in "áéíóúů":
            return stem
        return best
    for f in forms:  # jen nepřímé pády: Skoupého → Skoupý, Filkem → Filka?
        for end, nom in (("ého", "ý"), ("ému", "ý"), ("ího", "í"), ("ímu", "í")):
            if f.endswith(end):
                return f[: -len(end)] + nom
    return None


def _female_nominative(forms: Counter) -> str | None:
    female = [f for f in forms if _is_female(f)]
    if female:
        return max(female, key=lambda f: forms[f])
    for f in forms:
        for end, nom in (("ovou", "ová"), ("ové", "ová"), ("skou", "ská"), ("ské", "ská"),
                         ("ckou", "cká"), ("cké", "cká")):
            if f.endswith(end):
                return f[: -len(end)] + nom
    return None


@dataclass
class Surname:
    key: str
    forms: Counter = field(default_factory=Counter)
    pages: dict = field(default_factory=dict)  # page_id -> počet výskytů

    @property
    def heading(self) -> str:
        parts = [p for p in (_male_nominative(self.forms), _female_nominative(self.forms)) if p]
        if not parts:
            parts = [self.forms.most_common(1)[0][0]]
        return ", ".join(dict.fromkeys(parts))

    @property
    def sort_key(self) -> tuple:
        return czech_sort_key(self.heading)


# --- Tokenizace ---------------------------------------------------------------

def _clean(text: str) -> str:
    text = re.sub(r"\[\?(.+?)\?\]", r"\1", text)
    text = re.sub(r"\[(?:Okraj|Poznámka|Obrázek|Razítko|Podpis)[^\]]*\]", " . ", text)
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)  # rozdělená slova na konci řádku
    text = re.sub(r"\n\s*\n", " . ", text)  # odstavec = konec věty
    return text.replace("\n", " ")


_CONTINUES_RE = re.compile(rf"\s*[{LOWER},]")
_KEEP_PERIOD = ({a for a in NAME_ABBREVIATIONS.split()} | ABBREV_TITLES
                | {"Sv", "Kr", "Král", "Osv", "Nár", "Míst", "Předs", "Čs", "Mor", "Br", "Vl"})


def _tokens(text: str) -> list[str]:
    """Words and punctuation. A trailing period stays on the word only for
    abbreviations (Fr., Ing., J., st.); otherwise it is a separate token, so a
    surname at the end of a sentence („…Josef Novák.“) is still recognised."""
    text = _clean(text)
    out = []
    for m in TOKEN_RE.finditer(text):
        tok = m.group(0)
        if len(tok) > 1 and tok.endswith("."):
            word = tok[:-1]
            # zkratka i u neznámého slova, když věta pokračuje („J. Holeš. se musel“, „Shrom., zvolena“)
            continues = _CONTINUES_RE.match(text, m.end())
            if not (word in _KEEP_PERIOD or len(word) == 1 or continues
                    or (word[0].islower() and len(word) <= 3)):
                out += [word, "."]
                continue
        out.append(tok)
    return out


def _is_sentence_start(tokens: list[str], i: int) -> bool:
    if i == 0:
        return True
    prev = tokens[i - 1]
    if prev in {".", "!", "?", ":", "„", "(", "[", "–", "—", ";", '"'}:
        return True
    return prev.endswith(".") and len(prev) > 3 and prev[0].islower()


class NameIndexBuilder:
    def __init__(self, extra_stopwords: set[str] | None = None):
        self.first, self.abbrevs, self.stop, self.stop_keys, self.fn_keys = _build_name_sets(extra_stopwords or set())
        self.lower_words: set[str] = set()
        self.lower_keys: set[str] = set()

    # -- klasifikace tokenů --
    def _first_kind(self, tokens: list[str], i: int) -> str | None:
        """'full' (Josef), 'abbr' (Fr., Jos.), 'initial' (J.), else None."""
        tok = tokens[i]
        if tok in self.first or (tok.endswith(".") and tok[:-1] in self.first):
            return "full"
        if tok in self.abbrevs:
            return "abbr"
        if INITIAL_RE.match(tok) and tok not in NOT_INITIALS:
            prev = tokens[i - 1] if i else ""
            nxt = tokens[i + 1] if i + 1 < len(tokens) else ""
            # řetězce zkratek „K. S. Č.“, „M. N. V.“ nejsou iniciály jmen
            if not (INITIAL_RE.match(prev) or INITIAL_RE.match(nxt)):
                return "initial"
        return None

    def _is_candidate(self, tok: str, weak: int = 0) -> bool:
        """weak: 0 = vedle vypsaného jména, 1 = vedle zkratky jména (Fr.),
        2 = vedle iniciály, za titulem nebo na začátku věty."""
        if not CAP_WORD_RE.match(tok) or len(tok) < 3 or tok in self.stop:
            return False
        if tok in self.first and tok not in NAME_AND_SURNAME:
            return False
        if self._blocked_key(tok):
            return False
        # u slabších vodítek (zkratka, titul, začátek věty) nesmí jít o běžné slovo
        # ani jeho jiný tvar („J. Účast“, „Mokrá Markéta“, „Šebela Fr. Údernou“)
        if weak >= 1 and tok.lower() in self.lower_words:
            return False
        return not (weak >= 2 and _fold(stem_key(tok)) in self.lower_keys)

    def _blocked_key(self, tok: str) -> bool:
        """Místo, běžné slovo ze seznamu nebo tvar křestního jména („Františeky“).
        Ženská příjmení na -ová („Adamová“, „Prokopová“) projdou vždy."""
        key = _fold(stem_key(tok))
        return key in self.stop_keys or (key in self.fn_keys and not tok.endswith("ová"))

    def _pattern_hits(self, tokens: list[str]):
        """Yield (surname, position) found next to a first name or after a title."""
        n = len(tokens)
        for i, tok in enumerate(tokens):
            kind = self._first_kind(tokens, i)
            nxt = tokens[i + 1] if i + 1 < n else ""
            if kind is None:
                is_title = tok in TITLES or (tok.endswith(".") and tok[:-1] in ABBREV_TITLES)
                if is_title and i and re.fullmatch(rf"[{LOWER}]\.", tokens[i - 1]):
                    is_title = False  # „n. p. Kovolit“, „n. s. Odstupující“
                if is_title and nxt not in NAME_AND_SURNAME and self._is_candidate(nxt, weak=2):
                    yield nxt, i + 1
                continue
            weak = {"full": 0, "abbr": 1, "initial": 2}[kind]
            # Jméno Příjmení („Josef Skoupý“, „Fr. Kudla“)
            if self._is_candidate(nxt, weak) and not (nxt in NAME_AND_SURNAME and tok in NAME_AND_SURNAME):
                yield nxt, i + 1
                continue
            if tok in NAME_AND_SURNAME and nxt in self.first and nxt not in NAME_AND_SURNAME:
                yield tok, i  # „Marek Stanislav“
                continue
            # Příjmení Jméno (seznamy: „Hemzal Karel, Holešovský Jindřich“)
            if i == 0 or (i >= 2 and self._first_kind(tokens, i - 2)):
                continue
            prev = tokens[i - 1]
            if i >= 2 and tokens[i - 2] in PREPOSITIONS:
                continue  # „do Adamova Josef…“
            starts = _is_sentence_start(tokens, i - 1)
            if self._is_candidate(prev, weak=2 if starts else weak):
                yield prev, i - 1

    def build(self, pages: list[dict]) -> list[Surname]:
        """pages: list of {"id": ..., "text": str}. Returns surnames sorted alphabetically."""
        tokenized = [(p["id"], _tokens(p["text"])) for p in pages]
        for _, toks in tokenized:
            self.lower_words.update(t.rstrip(".") for t in toks if t[:1].islower())
        self.lower_keys = {_fold(stem_key(w)) for w in self.lower_words if len(w) >= 4}

        # 1. průchod: kmeny doložené vzorem „jméno + příjmení“ nebo titulem
        hits = []
        known: set[str] = set()
        for _, toks in tokenized:
            page_hits = {pos for _, pos in self._pattern_hits(toks)}
            hits.append(page_hits)
            known |= {_fold(stem_key(toks[pos])) for pos in page_hits}
        known -= self.stop_keys

        # 2. průchod: všechny výskyty známých příjmení
        families: dict[str, Surname] = {}
        for (page_id, toks), page_hits in zip(tokenized, hits):
            for i, tok in enumerate(toks):
                if not CAP_WORD_RE.match(tok) or tok in self.stop:
                    continue
                key = _fold(stem_key(tok))
                if key not in known or self._blocked_key(tok):
                    continue
                if i not in page_hits:
                    if tok in self.first or tok in NAME_AND_SURNAME:
                        continue
                    if tok.lower() in self.lower_words and (_is_sentence_start(toks, i) or len(tok) <= 4):
                        continue
                fam = families.setdefault(key, Surname(key))
                fam.forms[tok] += 1
                fam.pages[page_id] = fam.pages.get(page_id, 0) + 1

        return sorted(families.values(), key=lambda s: s.sort_key)


def build_index(pages: list[dict], exceptions_path: Path = EXCEPTIONS_FILE) -> list[Surname]:
    return NameIndexBuilder(load_exceptions(exceptions_path)).build(pages)
