#!/usr/bin/env python3
"""
Krok 5: Uhlazení OCR přepisů jazykovým modelem.

Projde surové přepisy z data/transcriptions.json a pošle je
jazykovému modelu, který opraví chyby OCR, gramatiku a interpunkci,
ale zachová původní obsah a styl kronikáře.

Výsledky ukládá do data/transcriptions_polished.json (stejný formát).
Podporuje resume – přeskočí už uhlazené stránky.

Použití:
    python 05_polish_text.py                             # Vše
    python 05_polish_text.py --section "Rok 1920–1929"  # Jen jedna sekce
    python 05_polish_text.py --section-index 2          # Sekce č. 2 (1-indexed)
    python 05_polish_text.py --limit 5                  # Jen prvních 5 stránek
    python 05_polish_text.py --dry-run                  # Jen ukáže co by dělal
    python 05_polish_text.py --force                    # Přepíše i už uhlazené
"""

import argparse
import json
import time

import anthropic
from tqdm import tqdm

from config import (
    ANTHROPIC_API_KEY,
    CLAUDE_MODEL,
    POLISH_SYSTEM_PROMPT,
    POLISHED_FILE,
    REQUEST_DELAY_SECONDS,
    SECTIONS,
    TRANSCRIPTIONS_FILE,
)


def load_polished() -> dict:
    """Load existing polished transcriptions (for resume support)."""
    if POLISHED_FILE.exists():
        with open(POLISHED_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_polished(data: dict):
    """Save polished transcriptions to disk."""
    with open(POLISHED_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def polish_text(
    client: anthropic.Anthropic,
    raw_text: str,
    previous_polished: str | None = None,
) -> str:
    """Send raw OCR text to Claude for polishing. Returns cleaned text."""
    content = "Oprav a uhlaď následující surový OCR přepis stránky kroniky:\n\n"
    content += "---\n"
    content += raw_text
    content += "\n---"

    if previous_polished:
        ctx = previous_polished
        if len(ctx) > 2000:
            ctx = "…" + ctx[-2000:]
        content += (
            "\n\nPro kontext – uhlazený text předchozí stránky "
            "(využij pro konzistenci jmen a míst):\n"
            "---\n"
            f"{ctx}\n"
            "---"
        )

    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=8192,
        temperature=0,
        system=POLISH_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": content}],
    )

    return message.content[0].text


def main():
    parser = argparse.ArgumentParser(description="Uhlazení OCR přepisů kroniky")
    parser.add_argument("--section", type=str, help="Název sekce k uhlazení")
    parser.add_argument("--section-index", type=int, help="Číslo sekce (1-indexed)")
    parser.add_argument("--dry-run", action="store_true", help="Jen ukáže co by dělal")
    parser.add_argument("--force", action="store_true", help="Přepíše i už uhlazené stránky")
    parser.add_argument("--limit", type=int, help="Maximální počet stránek ke zpracování")
    parser.add_argument(
        "--no-context",
        action="store_true",
        help="Neposílat kontext předchozí stránky",
    )
    args = parser.parse_args()

    if not ANTHROPIC_API_KEY and not args.dry_run:
        print("Nastav ANTHROPIC_API_KEY jako environment variable!")
        print("   export ANTHROPIC_API_KEY='sk-ant-...'")
        return

    print("=" * 60)
    print("Kronika obce Vranov – Uhlazení textu (Claude API)")
    print(f"Model: {CLAUDE_MODEL}")
    print(f"Kontext předchozí stránky: {'ne' if args.no_context else 'ano'}")
    print("=" * 60)

    # Load raw transcriptions
    if not TRANSCRIPTIONS_FILE.exists():
        print("Nejdřív spusť 03_ocr_transcribe.py!")
        return

    with open(TRANSCRIPTIONS_FILE, "r", encoding="utf-8") as f:
        raw_transcriptions = json.load(f)

    # Determine which sections to process
    section_names = [s["name"] for s in SECTIONS]

    if args.section:
        section_names = [n for n in section_names if args.section.lower() in n.lower()]
        if not section_names:
            print(f"Sekce '{args.section}' nenalezena!")
            return
    elif args.section_index:
        idx = args.section_index - 1
        if 0 <= idx < len(section_names):
            section_names = [section_names[idx]]
        else:
            print(f"Neplatný index sekce: {args.section_index}")
            return

    # Load existing polished transcriptions
    polished = load_polished()

    # Init API client
    client = None
    if not args.dry_run:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    # Process
    processed = 0
    skipped = 0
    errors = 0
    limit = args.limit

    for sec_name in section_names:
        raw_section = raw_transcriptions.get(sec_name, {})
        if not raw_section:
            print(f"\n  {sec_name} – žádné přepisy k uhlazení")
            continue

        # Sort pages by img_id
        sorted_pages = sorted(raw_section.items(), key=lambda x: x[1].get("img_id", 0))

        print(f"\n  {sec_name} ({len(sorted_pages)} stránek)")

        if sec_name not in polished:
            polished[sec_name] = {}

        if limit is not None and processed >= limit:
            break

        prev_polished_text = None

        for page_key, page_data in sorted_pages:
            if limit is not None and processed >= limit:
                break

            # Check if already polished
            if page_key in polished[sec_name] and not args.force:
                # Still track the polished text for context
                prev_polished_text = polished[sec_name][page_key].get("text")
                skipped += 1
                continue

            raw_text = page_data.get("text", "")
            if not raw_text.strip():
                skipped += 1
                continue

            if args.dry_run:
                print(f"  [DRY RUN] Would polish: img_{page_data.get('img_id', '?')}")
                processed += 1
                continue

            try:
                img_id = page_data.get("img_id", "?")
                ctx_info = " (s kontextem)" if prev_polished_text and not args.no_context else ""
                print(f"  Uhlazuji: strana {img_id}{ctx_info}")

                context = prev_polished_text if not args.no_context else None
                polished_text = polish_text(client, raw_text, previous_polished=context)

                polished[sec_name][page_key] = {
                    "img_id": page_data["img_id"],
                    "filename": page_data.get("filename", ""),
                    "text": polished_text,
                }

                prev_polished_text = polished_text
                processed += 1

                # Save after each page (resume support)
                save_polished(polished)

                # Rate limit
                time.sleep(REQUEST_DELAY_SECONDS)

            except anthropic.RateLimitError:
                print("  Rate limit – čekám 60s...")
                time.sleep(60)
                try:
                    context = prev_polished_text if not args.no_context else None
                    polished_text = polish_text(client, raw_text, previous_polished=context)
                    polished[sec_name][page_key] = {
                        "img_id": page_data["img_id"],
                        "filename": page_data.get("filename", ""),
                        "text": polished_text,
                    }
                    prev_polished_text = polished_text
                    processed += 1
                    save_polished(polished)
                    time.sleep(REQUEST_DELAY_SECONDS)
                except Exception as e:
                    print(f"  Retry failed: {e}")
                    errors += 1

            except Exception as e:
                print(f"  Error: {e}")
                errors += 1

    print(f"\n{'=' * 60}")
    print(f"Uhlazeno: {processed}, přeskočeno: {skipped}, chyby: {errors}")
    if not args.dry_run and processed > 0:
        print(f"Uhlazené přepisy uloženy: {POLISHED_FILE}")


if __name__ == "__main__":
    main()
