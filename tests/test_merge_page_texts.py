"""Testy pro 06_merge_page_texts.py (slučování přepisů stránek)."""

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

_spec = importlib.util.spec_from_file_location("merge_page_texts", ROOT / "06_merge_page_texts.py")
merge = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(merge)

SECTIONS = [
    {"section_name": "Úvod až rok 1919", "images": [{"id": 8}, {"id": 9}]},
    {"section_name": "Rok 1920–1929", "images": [{"id": 32}]},
]


def _setup(tmp_path, monkeypatch, existing=None):
    urls = tmp_path / "image_urls.json"
    urls.write_text(json.dumps(SECTIONS), encoding="utf-8")
    out = tmp_path / "transcriptions.json"
    if existing is not None:
        out.write_text(json.dumps(existing), encoding="utf-8")
    pages = tmp_path / "ocr_pages"
    monkeypatch.setattr(merge, "IMAGE_URLS_FILE", urls)
    monkeypatch.setattr(merge, "TRANSCRIPTIONS_FILE", out)
    monkeypatch.setattr(merge, "PAGES_DIR", pages)
    return pages, out


def _write_page(pages, sec_idx, page_idx, img_id, text):
    sec_dir = pages / f"section_{sec_idx:02d}"
    sec_dir.mkdir(parents=True, exist_ok=True)
    (sec_dir / f"page_{page_idx:03d}_id{img_id}.txt").write_text(text, encoding="utf-8")


def test_merges_page_files_in_transcription_format(tmp_path, monkeypatch):
    pages, out = _setup(tmp_path, monkeypatch)
    _write_page(pages, 1, 1, 8, "  Kronika obce Vranova.\n")
    _write_page(pages, 2, 1, 32, "Rok 1920")

    merge.main()

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["Úvod až rok 1919"]["img_8"] == {
        "img_id": 8,
        "filename": "section_01/page_001_id8.jpg",
        "text": "Kronika obce Vranova.",
    }
    assert "img_9" not in data["Úvod až rok 1919"]
    assert data["Rok 1920–1929"]["img_32"]["text"] == "Rok 1920"


def test_keeps_existing_transcriptions(tmp_path, monkeypatch):
    existing = {"Úvod až rok 1919": {"img_9": {"img_id": 9, "filename": "x.jpg", "text": "starší přepis"}}}
    pages, out = _setup(tmp_path, monkeypatch, existing=existing)
    _write_page(pages, 1, 1, 8, "nový přepis")

    merge.main()

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["Úvod až rok 1919"]["img_9"]["text"] == "starší přepis"
    assert data["Úvod až rok 1919"]["img_8"]["text"] == "nový přepis"
