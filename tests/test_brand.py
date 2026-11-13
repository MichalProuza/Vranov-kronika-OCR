import importlib.util
import re
import sys
import xml.dom.minidom
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import brand  # noqa: E402

spec = importlib.util.spec_from_file_location("build_html", ROOT / "04_build_html.py")
build_html = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build_html)


def test_mark_variants_are_valid_svg():
    for variant in brand.MARK_VARIANTS:
        svg = brand.mark_svg(variant, standalone=True)
        assert xml.dom.minidom.parseString(svg).documentElement.tagName == "svg"


def test_text_colors_are_readable_on_paper():
    for key in ("ink", "carmine", "petrol"):
        assert brand.contrast(brand.HEX[key], brand.HEX["paper"]) >= 4.5
        assert brand.contrast(brand.HEX[key], brand.HEX["parchment"]) >= 4.5


def test_logomanual_lists_every_color():
    manual = brand.build_logomanual_html()
    for name, hex_color, _ in brand.COLORS.values():
        assert name in manual and hex_color in manual


def test_page_contains_logomanual_view_and_brand():
    page = build_html.build_html({"Úvod až rok 1919": {"1": {"text": "Text strany."}}}, related=[])
    assert '<section id="logomanual" class="chronicle-section logomanual">' in page
    assert 'href="#logomanual" class="nav-item"' in page
    assert 'rel="icon"' in page and "Grenze+Gotisch" in page
    # nevyplněné zástupné znaky šablony by zůstaly jako {jméno}
    assert not re.search(r"\{[a-z_]+\}", page.split("<script>")[0])
