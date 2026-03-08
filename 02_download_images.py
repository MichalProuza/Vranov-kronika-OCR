#!/usr/bin/env python3
"""
Krok 2: Stáhne všechny obrázky kroniky.

Načte URL z data/image_urls.json a stáhne plné rozlišení obrázků
do data/images/. Podporuje resume – přeskočí už stažené soubory.
"""

import json
import time
from pathlib import Path

import requests
from tqdm import tqdm

from config import IMAGE_URLS_FILE, IMAGES_DIR


def download_image(url: str, filepath: Path) -> bool:
    """Download a single image. Returns True if downloaded, False if skipped."""
    if filepath.exists() and filepath.stat().st_size > 0:
        return False  # Already downloaded

    resp = requests.get(url, timeout=60, stream=True)
    resp.raise_for_status()

    with open(filepath, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)

    return True


def main():
    print("=" * 60)
    print("Kronika obce Vranov – Downloading images")
    print("=" * 60)

    # Load URLs
    with open(IMAGE_URLS_FILE, "r", encoding="utf-8") as f:
        sections = json.load(f)

    total_images = sum(len(s["images"]) for s in sections)
    downloaded = 0
    skipped = 0

    with tqdm(total=total_images, desc="Downloading") as pbar:
        for sec_idx, section in enumerate(sections, 1):
            sec_dir = IMAGES_DIR / f"section_{sec_idx:02d}"
            sec_dir.mkdir(exist_ok=True)

            for img_idx, img in enumerate(section["images"], 1):
                filename = f"page_{img_idx:03d}_id{img['id']}.jpg"
                filepath = sec_dir / filename

                try:
                    was_downloaded = download_image(img["url_full"], filepath)
                    if was_downloaded:
                        downloaded += 1
                        time.sleep(0.3)  # Be polite
                    else:
                        skipped += 1
                except Exception as e:
                    tqdm.write(f"  ❌ Error downloading img {img['id']}: {e}")

                pbar.update(1)

    print(f"\n{'=' * 60}")
    print(f"Staženo: {downloaded} nových, {skipped} přeskočeno (už existovaly)")
    print(f"Adresář: {IMAGES_DIR}")


if __name__ == "__main__":
    main()
