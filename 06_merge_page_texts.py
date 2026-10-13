"""
Sloučí ručně/agentem vytvořené přepisy jednotlivých stránek do transcriptions.json.

Přepisy stránek leží v data/ocr_pages/section_XX/page_NNN_idID.txt
(stejné pojmenování jako obrázky z 02_download_images.py).
Výsledek má stejný formát jako výstup 03_ocr_transcribe.py, takže
na něj lze rovnou pustit 05_polish_text.py nebo 04_build_html.py.

Použití:
    python 06_merge_page_texts.py
"""

import json

from config import DATA_DIR, IMAGE_URLS_FILE, TRANSCRIPTIONS_FILE

PAGES_DIR = DATA_DIR / "ocr_pages"


def main():
    with open(IMAGE_URLS_FILE, "r", encoding="utf-8") as f:
        sections = json.load(f)

    transcriptions = {}
    if TRANSCRIPTIONS_FILE.exists():
        with open(TRANSCRIPTIONS_FILE, "r", encoding="utf-8") as f:
            transcriptions = json.load(f)

    added = 0
    for sec_idx, section in enumerate(sections, 1):
        sec_name = section["section_name"]
        sec_dir = PAGES_DIR / f"section_{sec_idx:02d}"
        for img_idx, img in enumerate(section["images"], 1):
            stem = f"page_{img_idx:03d}_id{img['id']}"
            txt_path = sec_dir / f"{stem}.txt"
            if not txt_path.exists():
                continue
            text = txt_path.read_text(encoding="utf-8").strip()
            transcriptions.setdefault(sec_name, {})[f"img_{img['id']}"] = {
                "img_id": img["id"],
                "filename": f"section_{sec_idx:02d}/{stem}.jpg",
                "text": text,
            }
            added += 1

    with open(TRANSCRIPTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(transcriptions, f, ensure_ascii=False, indent=2)

    total = sum(len(s["images"]) for s in sections)
    print(f"Sloučeno {added} / {total} stránek do {TRANSCRIPTIONS_FILE}")


if __name__ == "__main__":
    main()
