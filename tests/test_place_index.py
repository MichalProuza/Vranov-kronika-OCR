"""Testy pro place_index.py (rejstřík míst a rejstřík domů)."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import place_index  # noqa: E402

GAZETTEER = """
# komentář
[Vranov]
Babí lom: Bab* lom*, Babílom*
Svatá Kateřina: Sv. Kateřin*, do Kateřiny
Žižkov: Žižkov, Žižkově, ze Žižkova

[Obce]
Brno: Brno, Brna, Brně
Adamov: Adamov, Adamova, Adamově, Adamovsk*

[Nezařazovat]
Vranov u Brna: Vranov u Brna
"""


def _places(texts, tmp_path):
    gaz = tmp_path / "mista.txt"
    gaz.write_text(GAZETTEER, encoding="utf-8")
    pages = [{"id": i, "text": t} for i, t in enumerate(texts, start=1)]
    return place_index.build_place_index(pages, gazetteer_path=gaz)


def _houses(texts):
    pages = [{"id": i, "text": t} for i, t in enumerate(texts, start=1)]
    return {h.number: h for h in place_index.build_house_index(pages)}


def test_places_grouped_and_declined_forms_merged(tmp_path):
    groups = _places([
        "Šli jsme k Babímu lomu a pak do Adamova.",
        "Na Babím lomě sníh, v Adamovských závodech stávka. Pouť u Sv. Kateřiny.",
        "Procesí šlo do Kateřiny a zpět do Brna.",
    ], tmp_path)
    assert list(groups) == ["Vranov", "Obce"]
    vranov = {p.heading: p for p in groups["Vranov"]}
    assert sorted(vranov["Babí lom"].pages) == [1, 2]
    assert sorted(vranov["Svatá Kateřina"].pages) == [2, 3]
    obce = {p.heading: p for p in groups["Obce"]}
    assert sorted(obce["Adamov"].pages) == [1, 2]
    assert sorted(obce["Brno"].pages) == [3]


def test_place_word_boundaries_and_hidden_group(tmp_path):
    groups = _places([
        "Žižkova smrt, obraz. Kateřina Nováková se vdala.",  # jméno, ne místo
        "Kronika obce Vranov u Brna. Brněnský kraj.",  # Brno se nepočítá
        "Bydlel ve Žižkově, pak ze Žižkova odešel.",
    ], tmp_path)
    vranov = {p.heading: p for p in groups.get("Vranov", [])}
    assert sorted(vranov["Žižkov"].pages) == [3]
    assert "Svatá Kateřina" not in vranov
    obce = {p.heading: p for p in groups.get("Obce", [])}
    assert "Brno" not in obce or 2 not in obce["Brno"].pages
    assert "Vranov u Brna" not in vranov and "Nezařazovat" not in groups


def test_line_break_hyphenation_is_joined(tmp_path):
    groups = _places(["Cesta k Babímu lo-\nmu byla zavátá."], tmp_path)
    assert [p.heading for p in groups["Vranov"]] == ["Babí lom"]


def test_house_numbers_and_snippets():
    houses = _houses([
        "obzvláště za Hudcovými (Holešovský č. 35) k Babílomu.",
        "Zvolen Šrůtil Rudolf, zámečník, č. 34. Holešovský Karel č. p. 155 a Jan Kudla čp. 3.",
        "Byt. družstvo postavilo dva domy č. 125 a 126. Pak k č. 66 vedla cesta.",
    ])
    assert set(houses) == {3, 34, 35, 66, 125, 126, 155}
    before, hit, after = houses[35].mentions[0].snippet
    assert hit == "č. 35" and "Holešovský" in before
    assert houses[155].mentions[0].form == "č. p. 155"
    assert houses[126].mentions[0].form == "a 126"


def test_numbers_that_are_not_houses():
    houses = _houses([
        "1 kg masa 7.60 K. č. 1 kg sádla, rozpočet K. č. 48.250.-",
        "viz archiv kroniky č. 6/60, archiv č. 99. Strana č. 1 – Občanská demokratická strana.",
        "rezervace p. č. 365/30 a parc. č. 416/3. Městské autobusy č. 57 a č. 43 jezdí.",
        "Doplňovací volby do obvodu č. 36. Bydlel v chatě č. 705.",
        "Holešovský č. 35 a 2 synové.",
    ])
    assert set(houses) == {35}
