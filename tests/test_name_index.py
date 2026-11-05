"""Testy pro name_index.py (rejstřík příjmení)."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import name_index  # noqa: E402


def _index(texts, tmp_path, exceptions=""):
    exc = tmp_path / "vyjimky.txt"
    exc.write_text(exceptions, encoding="utf-8")
    pages = [{"id": i, "text": t} for i, t in enumerate(texts, start=1)]
    return {s.heading: s for s in name_index.build_index(pages, exceptions_path=exc)}


def test_first_name_patterns_and_declension_are_merged(tmp_path):
    idx = _index([
        "Starostou zvolen Josef Holešovský, rolník.",
        "Za přítomnosti Holešovského Jindřicha a paní Marie Holešovské.",
        "Holešovský Karel, Skoupý Jan, Drexler Metoděj.",
        "Kronikář Drexler zapsal, že Holešovský opravil kapličku.",
    ], tmp_path)
    assert "Holešovský, Holešovská" in idx
    assert sorted(idx["Holešovský, Holešovská"].pages) == [1, 2, 3, 4]
    assert sorted(idx["Drexler"].pages) == [3, 4]
    assert "Skoupý" in idx


def test_female_and_a_surnames(tmp_path):
    idx = _index([
        "Učitelka Marta Kučerová vedla program. Jaroslav Kučera hrál.",
        "Eduard Filka a Fr. Kudla. S Filkem jsme orali.",
    ], tmp_path)
    assert sorted(idx["Kučera, Kučerová"].pages) == [1]
    assert sorted(idx["Filka"].pages) == [2]
    assert "Kudla" in idx


def test_places_titles_and_abbreviations_are_not_surnames(tmp_path):
    idx = _index([
        "Na Vranově Josef Novák. Šli jsme do Adamova Josef s námi.",
        "Schůzi K. S. Č. Účast slabá. Teplota 5 st. C. Další dny pršelo.",
        "Ing. Nehyba přednášel. n. p. Kovolit dodal stroje.",
    ], tmp_path)
    assert set(idx) == {"Novák", "Nehyba"}


def test_exceptions_file(tmp_path):
    idx = _index(["Josef Novák a Karel Celkem."], tmp_path, exceptions="Celkem  # omyl\n")
    assert set(idx) == {"Novák"}


def test_czech_alphabet_order(tmp_path):
    idx = _index(["Josef Chytil, Jan Cibulka, Karel Čermák, Petr Hora, Jan Šebek, Josef Sedlák."], tmp_path)
    assert list(idx) == ["Cibulka", "Čermák", "Hora", "Chytil", "Sedlák", "Šebek"]
