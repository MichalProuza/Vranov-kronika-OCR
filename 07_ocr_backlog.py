#!/usr/bin/env python3
"""Inventory unfinished scans and stage OCR candidates without replacing reviewed text.

Run without --run to inspect the backlog. With --run, each available local scan is
sent to Claude and its result is saved under the ignored output/ocr_candidates/.
Candidates require comparison with the scan before replacing a working transcript.
"""

import argparse
import base64
import json
import re
import time
from dataclasses import dataclass
from pathlib import Path

from config import (
    ANTHROPIC_API_KEY,
    CLAUDE_MODEL,
    IMAGE_URLS_FILE,
    IMAGES_DIR,
    OCR_SYSTEM_PROMPT,
    OUTPUT_DIR,
    TRANSCRIPTIONS_FILE,
)


INCOMPLETE_NOTE = re.compile(
    r"\[[^\]]*(?:zatím|nepřeps|chybí|většina|zbytek|ostatní)[^\]]*\]",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class BacklogPage:
    section_index: int
    section_name: str
    page_index: int
    image_id: int
    reason: str

    @property
    def stem(self) -> str:
        return f"page_{self.page_index:03d}_id{self.image_id}"

    @property
    def section_dir(self) -> str:
        return f"section_{self.section_index:02d}"

    def image_path(self, images_dir: Path = IMAGES_DIR) -> Path:
        return images_dir / self.section_dir / f"{self.stem}.jpg"

    def candidate_path(self, candidates_dir: Path) -> Path:
        return candidates_dir / self.section_dir / f"{self.stem}.txt"


def needs_new_ocr(text: str, section_index: int, page_index: int) -> bool:
    # Pages 243–247 have substantial fragments without a standard editorial note.
    return bool(
        INCOMPLETE_NOTE.search(text)
        or "[…]" in text
        or (section_index == 8 and page_index <= 5)
    )


def build_backlog(sections: list, transcriptions: dict) -> list[BacklogPage]:
    pending = []
    for section_index, section in enumerate(sections, 1):
        name = section["section_name"]
        existing = transcriptions.get(name, {})
        for page_index, image in enumerate(section["images"], 1):
            image_id = image["id"]
            entry = existing.get(f"img_{image_id}")
            if entry is None:
                reason = "missing"
            elif needs_new_ocr(entry["text"], section_index, page_index):
                reason = "incomplete"
            else:
                continue
            pending.append(BacklogPage(section_index, name, page_index, image_id, reason))
    return pending


def transcribe(client, page: BacklogPage, model: str, images_dir: Path) -> str:
    image_bytes = page.image_path(images_dir).read_bytes()
    encoded = base64.b64encode(image_bytes).decode("ascii")
    response = client.messages.create(
        model=model,
        max_tokens=8192,
        temperature=0,
        system=OCR_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": encoded}},
                    {"type": "text", "text": "Přepiš celou tuto stránku kroniky. Zachovej pořadí textu. Přepisuj pouze to, co je vidět na snímku; nejasné pasáže označ podle pravidel."},
                ],
            }
        ],
    )
    if response.stop_reason == "max_tokens":
        raise ValueError(f"OCR skenu {page.image_id} bylo uříznuto limitem odpovědi")
    result = "\n".join(block.text for block in response.content if block.type == "text").strip()
    if not result:
        raise ValueError(f"Model nevrátil text pro sken {page.image_id}")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true", help="Vytvořit OCR kandidáty pomocí API")
    parser.add_argument("--section-index", type=int, help="Zpracovat jen jednu sekci (1–13)")
    parser.add_argument("--limit", type=int, help="Nejvýše tento počet nových kandidátů")
    parser.add_argument("--model", default=CLAUDE_MODEL, help="Model Anthropic API")
    parser.add_argument("--delay", type=float, default=2, help="Prodleva mezi voláními API v sekundách")
    args = parser.parse_args()

    sections = json.loads(IMAGE_URLS_FILE.read_text(encoding="utf-8"))
    transcriptions = json.loads(TRANSCRIPTIONS_FILE.read_text(encoding="utf-8"))
    if args.section_index is not None and not 1 <= args.section_index <= len(sections):
        parser.error("--section-index musí odpovídat existující sekci")
    if args.limit is not None and args.limit <= 0:
        parser.error("--limit musí být kladné číslo")
    if args.delay < 0:
        parser.error("--delay nesmí být záporná")

    candidates_dir = OUTPUT_DIR / "ocr_candidates"
    backlog = build_backlog(sections, transcriptions)
    if args.section_index is not None:
        backlog = [p for p in backlog if p.section_index == args.section_index]

    print("Sekce | Chybí | Rozpracováno | Bez lokálního skenu | Kandidát připraven")
    for index, section in enumerate(sections, 1):
        pages = [p for p in backlog if p.section_index == index]
        if pages:
            print(
                f"{index:02d} {section['section_name']}: "
                f"{sum(p.reason == 'missing' for p in pages)} | "
                f"{sum(p.reason == 'incomplete' for p in pages)} | "
                f"{sum(not p.image_path().exists() for p in pages)} | "
                f"{sum(p.candidate_path(candidates_dir).exists() for p in pages)}"
            )
    print(f"Celkem k doplnění: {len(backlog)}")

    if not args.run:
        return
    if not ANTHROPIC_API_KEY:
        parser.error("ANTHROPIC_API_KEY není nastavený; doplňte jej bezpečně v nastavení prostředí")

    import anthropic

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    created = 0
    for page in backlog:
        if args.limit is not None and created >= args.limit:
            break
        candidate = page.candidate_path(candidates_dir)
        if candidate.exists():
            continue
        if not page.image_path().exists():
            print(f"Přeskakuji {page.stem}: chybí lokální sken")
            continue
        try:
            result = transcribe(client, page, args.model, IMAGES_DIR)
        except Exception as exc:
            print(f"Chyba u {page.stem}: {type(exc).__name__}: {exc}")
            continue
        candidate.parent.mkdir(parents=True, exist_ok=True)
        candidate.write_text(result + "\n", encoding="utf-8")
        created += 1
        print(f"Uložen kandidát: {candidate}")
        if args.delay:
            time.sleep(args.delay)
    print(f"Noví kandidáti: {created}")


if __name__ == "__main__":
    main()
