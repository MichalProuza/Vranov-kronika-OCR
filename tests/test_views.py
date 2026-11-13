"""Testy pro zobrazení po oddílech (listování, skok na stranu, hledání) v 04_build_html.py."""

import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

_spec = importlib.util.spec_from_file_location("build_html", ROOT / "04_build_html.py")
build = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(build)

FIRST, SECOND, THIRD = (s["name"] for s in build.SECTIONS[:3])
TRANSCRIPTIONS = {
    FIRST: {"img_1": {"img_id": 1, "text": "1.\n1919.\n\nPrvní strana."}},
    SECOND: {"img_2": {"img_id": 2, "text": "2.\n1920.\n\nDruhá strana."},
             "img_3": {"img_id": 3, "text": "3.\n1921.\n\nTřetí strana."}},
}


def _section(page: str, name: str) -> str:
    slug = build.slugify(name)
    return re.search(rf'<section id="{slug}".*?</section>', page, re.S).group(0)


def test_only_first_section_is_active():
    page = build.build_html(TRANSCRIPTIONS, related=[], extras=[])
    assert _section(page, FIRST).startswith(f'<section id="{build.slugify(FIRST)}" class="chronicle-section active">')
    assert page.count("chronicle-section active") == 1


def test_section_links_to_neighbours():
    page = build.build_html(TRANSCRIPTIONS, related=[], extras=[])
    first, second = _section(page, FIRST), _section(page, SECOND)
    assert "bar-prev" not in first and "pager-prev" not in first
    assert f'class="bar-next" href="#{build.slugify(SECOND)}"' in first
    assert f'class="bar-prev" href="#{build.slugify(FIRST)}"' in second
    assert f'class="pager-next" href="#{build.slugify(THIRD)}"' in second


def test_page_jump_lists_pages_of_section():
    second = _section(build.build_html(TRANSCRIPTIONS, related=[], extras=[]), SECOND)
    assert '<option value="page-2">Strana 2 · 1920</option><option value="page-3">Strana 3 · 1921</option>' in second
    assert "page-1" not in second


def test_search_view_and_script_present():
    page = build.build_html(TRANSCRIPTIONS, related=[], extras=[])
    assert 'id="hledani"' in page and 'href="#hledani"' in page
    assert "function route(" in page
    # skript se vkládá mimo f-string: nesmí v něm zůstat zdvojené složené závorky
    script = page[page.rindex("<script>"):]
    assert "{{" not in script and "}}" not in script
