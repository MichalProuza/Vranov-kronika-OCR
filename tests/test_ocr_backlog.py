"""Selection of pages for staged OCR must preserve completed transcripts."""

import importlib.util
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
spec = importlib.util.spec_from_file_location("ocr_backlog", ROOT / "07_ocr_backlog.py")
backlog = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = backlog
spec.loader.exec_module(backlog)


def test_backlog_selects_missing_and_working_pages_only(tmp_path):
    sections = [
        {"section_name": f"section {i}", "images": [{"id": i * 10}]} for i in range(1, 10)
    ]
    transcriptions = {
        "section 1": {"img_10": {"text": "Hotový souvislý přepis."}},
        "section 3": {"img_30": {"text": "Hotový souvislý přepis."}},
        "section 4": {"img_40": {"text": "Hotový souvislý přepis."}},
        "section 5": {"img_50": {"text": "Hotový souvislý přepis."}},
        "section 6": {"img_60": {"text": "Ukázka […] [Zbytek zatím nepřepsán.]"}},
        "section 7": {"img_70": {"text": "Hotový souvislý přepis."}},
        "section 8": {"img_80": {"text": "Úvodní fragment."}},
        "section 9": {"img_90": {"text": "Hotový text s [?nejistým?] slovem."}},
    }

    pages = backlog.build_backlog(sections, transcriptions)

    assert [(p.image_id, p.reason) for p in pages] == [
        (20, "missing"),
        (60, "incomplete"),
        (80, "incomplete"),
    ]
    assert pages[1].image_path(tmp_path) == tmp_path / "section_06/page_001_id60.jpg"
    assert pages[1].candidate_path(tmp_path) == tmp_path / "section_06/page_001_id60.txt"


def test_transcription_uses_local_scan_and_rejects_truncated_output(tmp_path):
    page = backlog.BacklogPage(6, "Rok 1955–1959", 1, 318, "missing")
    image = page.image_path(tmp_path)
    image.parent.mkdir(parents=True)
    image.write_bytes(b"jpeg image bytes")

    class Messages:
        stop_reason = "end_turn"

        def create(self, **kwargs):
            self.request = kwargs
            return SimpleNamespace(
                stop_reason=self.stop_reason,
                content=[SimpleNamespace(type="text", text="Přepsaný text")],
            )

    messages = Messages()
    client = SimpleNamespace(messages=messages)
    assert backlog.transcribe(client, page, "test-model", tmp_path) == "Přepsaný text"
    source = messages.request["messages"][0]["content"][0]["source"]
    assert source["media_type"] == "image/jpeg"
    assert source["data"] == "anBlZyBpbWFnZSBieXRlcw=="

    messages.stop_reason = "max_tokens"
    try:
        backlog.transcribe(client, page, "test-model", tmp_path)
    except ValueError as error:
        assert "uříznuto" in str(error)
    else:
        raise AssertionError("Truncated OCR was accepted")
