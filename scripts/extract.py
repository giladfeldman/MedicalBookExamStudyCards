#!/usr/bin/env python3
"""Extract PDF pages for a batch. Saves text + image pages."""

import fitz
import json
import sys
import os

def extract_batch(pdf_path, start_page, end_page, output_dir="work"):
    os.makedirs(output_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    data = {"pages": {}, "summary": {"total_pages": 0, "text_pages": 0, "image_pages": 0, "total_chars": 0}}

    for p in range(start_page, end_page + 1):
        idx = p - 1
        if idx < 0 or idx >= len(doc):
            print(f"⚠️ Page {p} out of range (PDF has {len(doc)} pages)")
            continue
        page = doc[idx]
        text = page.get_text()
        char_count = len(text.strip())
        data["summary"]["total_pages"] += 1
        data["summary"]["total_chars"] += char_count

        if char_count < 200:
            pix = page.get_pixmap(dpi=150)
            img_path = os.path.join(output_dir, f"page_{p}.png")
            pix.save(img_path)
            data["pages"][str(p)] = {"type": "image", "chars": char_count, "text": text.strip(), "image": img_path}
            data["summary"]["image_pages"] += 1
            print(f"Page {p}: {char_count:>5} chars → IMAGE ({img_path})")
        else:
            data["pages"][str(p)] = {"type": "text", "chars": char_count, "text": text.strip()}
            data["summary"]["text_pages"] += 1
            print(f"Page {p}: {char_count:>5} chars → TEXT")

    doc.close()
    output_file = os.path.join(output_dir, "current_extraction.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*50}")
    print(f"Total: {data['summary']['total_pages']} pages, {data['summary']['text_pages']} text, {data['summary']['image_pages']} image, {data['summary']['total_chars']:,} chars")
    return data

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python extract.py <pdf_path> <start_page> <end_page>")
        sys.exit(1)
    extract_batch(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))
