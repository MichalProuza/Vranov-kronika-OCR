#!/usr/bin/env python3
"""
Krok 1: Stáhne URL všech obrázků kroniky z webu vranov.cz.

Projde všech 13 sekcí kroniky a z HTML extrahuje URL obrázků.
Výsledek uloží do data/image_urls.json.
"""

import json
import re
import time

import requests
from bs4 import BeautifulSoup

from config import BASE_URL, CHRONICLE_INDEX, IMAGE_BASE_URL, IMAGE_URLS_FILE, SECTIONS


def scrape_section_images(section_slug: str) -> list[dict]:
    """Scrape image URLs from a single chronicle section page."""
    url = f"{CHRONICLE_INDEX}{section_slug}"
    print(f"  Fetching: {url}")

    resp = requests.get(url, timeout=30)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    images = []

    # Images are in links like: /evt_image.php?img=8
    # Thumbnails have width/height params, full images don't
    for link in soup.find_all("a", href=True):
        href = link["href"]
        match = re.match(r"/evt_image\.php\?img=(\d+)$", href)
        if match:
            img_id = int(match.group(1))
            images.append({
                "id": img_id,
                "url_full": f"{BASE_URL}/evt_image.php?img={img_id}",
                "url_thumb": f"{BASE_URL}/evt_image.php?img={img_id}&width=540&height=540&box=2",
            })

    return images


def main():
    print("=" * 60)
    print("Kronika obce Vranov – Scraping image URLs")
    print("=" * 60)

    all_data = []

    for section in SECTIONS:
        print(f"\n📖 {section['name']}")
        images = scrape_section_images(section["slug"])
        print(f"   Nalezeno {len(images)} obrázků")

        all_data.append({
            "section_name": section["name"],
            "section_slug": section["slug"],
            "images": images,
        })

        time.sleep(0.5)  # Be polite

    # Summary
    total = sum(len(s["images"]) for s in all_data)
    print(f"\n{'=' * 60}")
    print(f"Celkem: {total} obrázků v {len(all_data)} sekcích")

    # Save
    with open(IMAGE_URLS_FILE, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    print(f"Uloženo do: {IMAGE_URLS_FILE}")


if __name__ == "__main__":
    main()
