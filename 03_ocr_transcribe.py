#!/usr/bin/env python3
"""
Krok 3: OCR přepis stránek kroniky pomocí Claude API (vision).

Odešle každý obrázek do Claude API a uloží přepis.
Podporuje resume – přeskočí už přepsané stránky.
Podporuje filtrování po sekcích.
Posílá kontext předchozí stránky pro lepší kontinuitu přepisu.

Ve výchozím režimu posílá obrázky přímo z URL (plná kvalita, jako v chatu).
S --local čte obrázky z disku (vyžaduje předchozí stažení přes 02_download_images.py).

Použití:
    python 03_ocr_transcribe.py                             # Vše (z URL)
    python 03_ocr_transcribe.py --section "Rok 1920–1929"  # Jen jedna sekce
    python 03_ocr_transcribe.py --section-index 2          # Sekce č. 2 (1-indexed)
    python 03_ocr_transcribe.py --limit 5                  # Jen prvních 5 stránek
    python 03_ocr_transcribe.py --local                    # Čte z disku místo URL
    python 03_ocr_transcribe.py --dry-run                  # Jen ukáže co by dělal
"""

import argparse
import base64
import io
import json
import time
from pathlib import Path

import anthropic
from PIL import Image
from tqdm import tqdm

from config import (
    ANTHROPIC_API_KEY,
    CLAUDE_MODEL,
    IMAGE_BASE_URL,
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


def encode_image_from_file(image_path: Path) -> tuple[str, str]:
    """Read a local image file and encode to base64. Returns (base64_data, media_type)."""
    suffix = image_path.suffix.lower()
    media_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
    }
    media_type = media_types.get(suffix, "image/jpeg")

    with open(image_path, "rb") as f:
        image_data = base64.standard_b64encode(f.read()).decode("utf-8")
    return image_data, media_type


def build_image_content(img_id: int, local_path: Path | None = None) -> dict:
    """Build the image content block for the API request.

    If local_path is provided, sends base64-encoded local file.
    Otherwise sends the image URL directly (full original quality).
    """
    if local_path is not None:
        image_data, media_type = encode_image_from_file(local_path)
        return {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": media_type,
                "data": image_data,
            },
        }
    else:
        # Send URL directly – Claude fetches the original image at full quality,
        # identical to how images work when pasted in Claude.ai chat.
        return {
            "type": "image",
            "source": {
                "type": "url",
                "url": f"{IMAGE_BASE_URL}{img_id}",
            },
        }


def transcribe_image(
    client: anthropic.Anthropic,
    img_id: int,
    local_path: Path | None = None,
    previous_transcription: str | None = None,
) -> str:
    """Send a single image to Claude API and return the transcription.

    If local_path is provided, reads from disk. Otherwise fetches from URL.
    If previous_transcription is provided, it is included as context.
    """
    # Build user message content – image first, then instructions
    content = []

    # Image goes first so the model sees it before instructions
    content.append(build_image_content(img_id, local_path))

    # Add previous page context if available
    if previous_transcription:
        # Truncate very long transcriptions to last ~2000 chars to save tokens
        ctx = previous_transcription
        if len(ctx) > 2000:
            ctx = "…" + ctx[-2000:]
        content.append(
            {
                "type": "text",
                "text": (
                    "Přepiš text z této stránky kroniky obce Vranov. "
                    "Přepisuj POUZE to, co skutečně vidíš na obrázku výše – nic nepřidávej.\n\n"
                    "Pro kontext – přepis předchozí stránky (využij pro rozpoznání "
                    "jmen a míst, ale NEPŘEPISUJ text z předchozí stránky):\n"
                    "---\n"
                    f"{ctx}\n"
                    "---"
                ),
            }
        )
    else:
        content.append(
            {
                "type": "text",
                "text": (
                    "Přepiš text z této stránky kroniky obce Vranov. "
                    "Přepisuj POUZE to, co skutečně vidíš na obrázku výše – nic nepřidávej."
                ),
            }
        )

    # Call Claude API
    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=8192,
        temperature=0,
        system=OCR_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": content}],
    )

    return message.content[0].text


def get_previous_transcription(
    transcriptions: dict,
    current_section_name: str,
    current_img_idx: int,
    section_images: list,
    all_sections: list,
    section_index_map: dict,
) -> str | None:
    """Get the transcription text of the previous page, if available.

    Looks at the previous image in the current section first, then falls back
    to the last image of the previous section.
    """
    if current_img_idx > 1:
        # Previous page in the same section
        prev_img = section_images[current_img_idx - 2]  # img_idx is 1-based
        prev_key = f"img_{prev_img['id']}"
        sec_data = transcriptions.get(current_section_name, {})
        if prev_key in sec_data:
            return sec_data[prev_key]["text"]
    elif current_img_idx == 1:
        # First page of section – look at last page of previous section
        sec_names = [s["section_name"] for s in all_sections]
        try:
            cur_pos = sec_names.index(current_section_name)
        except ValueError:
            return None
        if cur_pos > 0:
            prev_sec_name = sec_names[cur_pos - 1]
            prev_sec_data = transcriptions.get(prev_sec_name, {})
            # Find the last image of that section
            prev_section = all_sections[cur_pos - 1]
            if prev_section["images"]:
                last_img = prev_section["images"][-1]
                last_key = f"img_{last_img['id']}"
                if last_key in prev_sec_data:
                    return prev_sec_data[last_key]["text"]
    return None


def main():
    parser = argparse.ArgumentParser(description="OCR přepis kroniky obce Vranov")
    parser.add_argument("--section", type=str, help="Název sekce k přepisu")
    parser.add_argument("--section-index", type=int, help="Číslo sekce (1-indexed)")
    parser.add_argument("--dry-run", action="store_true", help="Jen ukáže co by dělal")
    parser.add_argument("--force", action="store_true", help="Přepíše i už přepsané stránky")
    parser.add_argument("--limit", type=int, help="Maximální počet stránek k přepsání")
    parser.add_argument(
        "--local",
        action="store_true",
        help="Číst obrázky z disku místo z URL (vyžaduje 02_download_images.py)",
    )
    parser.add_argument(
        "--no-context",
        action="store_true",
        help="Neposílat kontext předchozí stránky",
    )
    args = parser.parse_args()

    if not ANTHROPIC_API_KEY and not args.dry_run:
        print("❌ Nastav ANTHROPIC_API_KEY jako environment variable!")
        print("   export ANTHROPIC_API_KEY='sk-ant-...'")
        return

    mode = "lokální soubory" if args.local else "URL (plná kvalita)"
    print("=" * 60)
    print("Kronika obce Vranov – OCR Transcription (Claude API)")
    print(f"Model: {CLAUDE_MODEL}")
    print(f"Zdroj obrázků: {mode}")
    print(f"Kontext předchozí stránky: {'ne' if args.no_context else 'ano'}")
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
            img_id = img["id"]
            page_key = f"img_{img_id}"

            # Stop if limit reached
            if limit is not None and processed >= limit:
                break

            # Check if already transcribed
            if page_key in transcriptions[sec_name] and not args.force:
                skipped += 1
                continue

            # Resolve local file path (needed for --local mode)
            filename = f"page_{img_idx:03d}_id{img_id}.jpg"
            local_path = None
            if args.local:
                local_path = IMAGES_DIR / f"section_{sec_num:02d}" / filename
                if not local_path.exists():
                    print(f"  ⚠️  Soubor nenalezen: {local_path}")
                    print(f"      Spusť nejdřív 02_download_images.py")
                    errors += 1
                    continue

            if args.dry_run:
                src = local_path if local_path else f"{IMAGE_BASE_URL}{img_id}"
                print(f"  [DRY RUN] Would transcribe: {src}")
                processed += 1
                continue

            # Get previous page context
            prev_text = None
            if not args.no_context:
                prev_text = get_previous_transcription(
                    transcriptions,
                    sec_name,
                    img_idx,
                    section["images"],
                    all_sections,
                    section_index_map,
                )

            # Transcribe
            try:
                ctx_info = " (s kontextem)" if prev_text else ""
                src_info = filename if args.local else f"URL id={img_id}"
                print(f"  🔍 Přepisuji: {src_info}{ctx_info}")
                text = transcribe_image(
                    client,
                    img_id,
                    local_path=local_path,
                    previous_transcription=prev_text,
                )

                transcriptions[sec_name][page_key] = {
                    "img_id": img_id,
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
                    text = transcribe_image(
                        client,
                        img_id,
                        local_path=local_path,
                        previous_transcription=prev_text,
                    )
                    transcriptions[sec_name][page_key] = {
                        "img_id": img_id,
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
