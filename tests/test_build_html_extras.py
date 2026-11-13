"""Testy pro zařazení tisků mimo kroniku (EXTRA_SECTIONS) do HTML."""

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

_spec = importlib.util.spec_from_file_location("build_html", ROOT / "04_build_html.py")
build_html = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(build_html)

SECTION = {"name": "Zkušební tisk (1990)", "short": "Tisk", "dir": "tisk", "id_base": 5000,
           "source_url": "https://example.org/tisk.pdf", "intro": "Úvod k tisku."}


def _extras(tmp_path):
    d = tmp_path / "tisk"
    d.mkdir()
    (d / "page_001.txt").write_text("[Obálka]\n\nTITUL", encoding="utf-8")
    (d / "page_002.txt").write_text("- 1 -\n\n1864 – Stavba silnice.\n\nřádek a | 1\nřádek b | 2", encoding="utf-8")
    return build_html.load_extra_sections([SECTION], tmp_path)


def test_load_extra_sections_reads_printed_number(tmp_path):
    (section,) = _extras(tmp_path)
    cover, first = section["pages"]
    assert (cover["id"], cover["number"], cover["scan"]) == (5001, "", 1)
    assert cover["text"].startswith("[Obálka]")
    assert (first["id"], first["number"], first["scan"]) == (5002, "1", 2)
    assert first["text"].startswith("1864 – Stavba silnice.")


def test_missing_directory_is_skipped(tmp_path):
    assert build_html.load_extra_sections([SECTION], tmp_path) == []


def test_format_text_keep_breaks():
    assert build_html.format_text("a | 1\nb | 2", keep_breaks=True) == "<p>a | 1<br>\nb | 2</p>"
    assert build_html.format_text("a\nb") == "<p>a b</p>"


def test_extra_section_rendered_after_chronicle(tmp_path):
    page = build_html.build_html({}, extras=_extras(tmp_path))
    assert 'id="zkusebni-tisk-1990"' in page
    assert 'id="page-5002"' in page
    assert "Strana 1 · sken 2/2" in page
    assert "https://example.org/tisk.pdf" in page
    assert "řádek a | 1<br>" in page
    assert page.index('id="rok-1990-1993"') < page.index('id="zkusebni-tisk-1990"') < page.index('id="rejstrik"')
    assert "Přepsáno 2 stránek" in page


def test_no_extras_keeps_chronicle_only():
    page = build_html.build_html({}, extras=[])
    assert "Tisky k 750. výročí" not in page.split("<body>")[1].split('<main class="content">')[0]
