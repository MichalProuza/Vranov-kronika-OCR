"""Testy pro „Souvislosti“ (data/souvislosti.json a jejich vykreslení v 04_build_html.py)."""

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

_spec = importlib.util.spec_from_file_location("build_html", ROOT / "04_build_html.py")
build = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(build)

ARTICLE = {
    "zdroj": "Vranovský zpravodaj 2/2005", "strany_pdf": "3–7", "url": "https://www.vranov.cz/x.pdf#page=3",
    "titul": "Vzpomínka <na> konec války", "autor": "Jiří Skoupý", "tema": "Osvobození 1945",
    "popis": "Popis.", "strany": [2],
}
TRANSCRIPTIONS = {
    build.SECTIONS[0]["name"]: {
        "img_1": {"img_id": 1, "text": "1.\n1945.\n\nPrvní strana."},
        "img_2": {"img_id": 2, "text": "2.\n1945.\n\nDruhá strana."},
    }
}


def test_data_file_is_consistent():
    articles = build.load_related()
    assert articles
    with open(ROOT / "data" / "transcriptions.json", encoding="utf-8") as f:
        known = {p["img_id"] for section in json.load(f).values() for p in section.values()}
    for a in articles:
        for key in ("zdroj", "url", "titul", "tema", "popis", "strany"):
            assert key in a, (key, a.get("titul"))
        assert a["url"].startswith("https://www.vranov.cz/"), a["url"]
        assert set(a["strany"]) <= known, a["titul"]


def test_box_only_on_linked_pages():
    out = build.build_html(TRANSCRIPTIONS, related=[ARTICLE])
    page1, page2 = out.split('id="page-1"')[1].split('id="page-2"')
    assert 'class="related"' not in page1
    assert 'class="related"' in page2.split("</section>")[0]
    assert "Vzpomínka &lt;na&gt; konec války" in out
    assert 'id="souvislosti"' in out
    assert 'href="#page-2"' in out.split('id="souvislosti"')[1]


def test_no_related_no_section():
    out = build.build_html(TRANSCRIPTIONS, related=[])
    assert 'id="souvislosti"' not in out
    assert 'class="related"' not in out
