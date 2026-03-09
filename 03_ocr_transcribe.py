#!/usr/bin/env python3
"""
Krok 3: OCR přepis stránek kroniky pomocí Claude API (vision).

Odešle každý obrázek do Claude API a uloží přepis.
Podporuje resume – přeskočí už přepsané stránky.
Podporuje filtrování po sekcích.

Použití:
    python 03_ocr_transcribe.py                             # Vše
    python 03_ocr_transcribe.py --section "Rok 1920–1929"  # Jen jedna sekce
    python 03_ocr_transcribe.py --section-index 2          # Sekce č. 2 (1-indexed)
    python 03_ocr_transcribe.py --limit 5                  # Jen prvních 5 stránek
    python 03_ocr_transcribe.py --section "Rok 1920–1929" --limit 5  # Kombinace
    python 03_ocr_transcribe.py --dry-run                  # Jen ukáže co by dělal
"""

import argparse
import base64
import json
import time
from pathlib import Path

import anthropic
from tqdm import tqdm

from config import (
    ANTHROPIC_API_KEY,
    CLAUDE_MODEL,
    IMAGE_URLS_FILE,
    IMAGES_DIR,
    OCR_SYSTEM_PROMPT,
    REQUEST_DELAY_SECONDS,
    TRANSCRIPTIONS_FILE,
)


def load_transcriptions() -> dict:
    """Load existing transcriptions (for resume support)."""
    if TRANSCRIPTIONS_FILE.exists():
        with open(TRANSCRIPTIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_transcriptions(data: dict):
    """Save transcriptions to disk."""
    with open(TRANSCRIPTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def transcribe_image(client: anthropic.Anthropic, image_path: Path) -> str:
    """Send a single image to Claude API and return the transcription."""
    # Read and encode image
    with open(image_path, "rb") as f:
        image_data = base64.standard_b64encode(f.read()).decode("utf-8")

    # Detect media type
    suffix = image_path.suffix.lower()
    media_types = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".gif": "image/gif"}
    media_type = media_types.get(suffix, "image/jpeg")

    # Call Claude API
    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=4096,
        system=OCR_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": "Přepiš text z této stránky kroniky obce Vranov.",
                    },
                ],
            }
        ],
    )

    # Extract text from response
    return message.content[0].text


def main():
    parser = argparse.ArgumentParser(description="OCR přepis kroniky obce Vranov")
    parser.add_argument("--section", type=str, help="Název sekce k přepisu")
    parser.add_argument("--section-index", type=int, help="Číslo sekce (1-indexed)")
    parser.add_argument("--dry-run", action="store_true", help="Jen ukáže co by dělal")
    parser.add_argument("--force", action="store_true", help="Přepíše i už přepsané stránky")
    parser.add_argument("--limit", type=int, help="Maximální počet stránek k přepsání")
    args = parser.parse_args()

    if not ANTHROPIC_API_KEY and not args.dry_run:
        print("❌ Nastav ANTHROPIC_API_KEY jako environment variable!")
        print("   export ANTHROPIC_API_KEY='sk-ant-...'")
        return

    print("=" * 60)
    print("Kronika obce Vranov – OCR Transcription (Claude API)")
    print("=" * 60)

    # Load image URLs
    if not IMAGE_URLS_FILE.exists():
        print("❌ Nejdřív spusť 01_scrape_urls.py!")
        return

    with open(IMAGE_URLS_FILE, "r", encoding="utf-8") as f:
        all_sections = json.load(f)

    sections = all_sections

    # Filter sections
    if args.section:
        sections = [s for s in sections if args.section.lower() in s["section_name"].lower()]
        if not sections:
            print(f"❌ Sekce '{args.section}' nenalezena!")
            return
    elif args.section_index:
        idx = args.section_index - 1
        if 0 <= idx < len(sections):
            sections = [sections[idx]]
        else:
            print(f"❌ Neplatný index sekce: {args.section_index}")
            return

    # Build lookup: section_name -> 1-based index in full list
    section_index_map = {s["section_name"]: i + 1 for i, s in enumerate(all_sections)}

    # Load existing transcriptions
    transcriptions = load_transcriptions()

    # Init API client
    client = None
    if not args.dry_run:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    # Process
    total_pages = sum(len(s["images"]) for s in sections)
    processed = 0
    skipped = 0
    errors = 0
    limit = args.limit

    for section in sections:
        sec_num = section_index_map[section["section_name"]]

        sec_name = section["section_name"]
        print(f"\n📖 {sec_name} ({len(section['images'])} stránek)")

        if sec_name not in transcriptions:
            transcriptions[sec_name] = {}

        if limit is not None and processed >= limit:
            break

        for img_idx, img in enumerate(section["images"], 1):
            img_id = str(img["id"])
            page_key = f"img_{img_id}"

            # Stop if limit reached
            if limit is not None and processed >= limit:
                break

            # Check if already transcribed
            if page_key in transcriptions[sec_name] and not args.force:
                skipped += 1
                continue

            # Find the local file
            filename = f"page_{img_idx:03d}_id{img['id']}.jpg"
            filepath = IMAGES_DIR / f"section_{sec_num:02d}" / filename

            if not filepath.exists():
                print(f"  ⚠️  Soubor nenalezen: {filepath}")
                print(f"      Spusť nejdřív 02_download_images.py")
                errors += 1
                continue

            if args.dry_run:
                print(f"  [DRY RUN] Would transcribe: {filepath}")
                processed += 1
                continue

            # Transcribe
            try:
                print(f"  🔍 Přepisuji: {filename} (img_id={img_id})")
                text = transcribe_image(client, filepath)

                transcriptions[sec_name][page_key] = {
                    "img_id": img["id"],
                    "filename": filename,
                    "text": text,
                }

                processed += 1

                # Save after each page (resume support)
                save_transcriptions(transcriptions)

                # Rate limit
                time.sleep(REQUEST_DELAY_SECONDS)

            except anthropic.RateLimitError:
                print("  ⏳ Rate limit – čekám 60s...")
                time.sleep(60)
                # Retry
                try:
                    text = transcribe_image(client, filepath)
                    transcriptions[sec_name][page_key] = {
                        "img_id": img["id"],
                        "filename": filename,
                        "text": text,
                    }
                    processed += 1
                    save_transcriptions(transcriptions)
                    time.sleep(REQUEST_DELAY_SECONDS)
                except Exception as e:
                    print(f"  ❌ Retry failed: {e}")
                    errors += 1

            except Exception as e:
                print(f"  ❌ Error: {e}")
                errors += 1

    print(f"\n{'=' * 60}")
    print(f"Přepsáno: {processed}, přeskočeno: {skipped}, chyby: {errors}")
    if not args.dry_run:
        print(f"Přepisy uloženy: {TRANSCRIPTIONS_FILE}")


if __name__ == "__main__":
    main()
