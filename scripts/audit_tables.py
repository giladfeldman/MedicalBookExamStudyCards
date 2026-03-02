#!/usr/bin/env python3
"""
Table Coverage Audit — detects tables in the source PDF and cross-references
their cell contents against the Anki cards to find uncovered table data.

Usage:
  python scripts/audit_tables.py                    # Full audit
  python scripts/audit_tables.py --cache            # Reuse cached table scan
  python scripts/audit_tables.py --page 7           # Audit single page
  python scripts/audit_tables.py --export-flagged   # Export PNGs for flagged pages

Exit codes: 0 = all GREEN, 1 = any RED pages, 2 = YELLOW but no RED
"""

import argparse
import json
import os
import re
import sys
import io
import unicodedata
from collections import defaultdict
from pathlib import Path

# Force UTF-8 output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    import fitz  # PyMuPDF
except ImportError:
    print("ERROR: PyMuPDF not installed. Run: pip install pymupdf")
    sys.exit(1)

# ── Paths ──────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
PDF_PATH = PROJECT_ROOT / "input" / "source.pdf"
OUTPUT_DIR = PROJECT_ROOT / "output"
WORK_DIR = PROJECT_ROOT / "work"
CACHE_PATH = WORK_DIR / "table_cache.json"
REPORT_PATH = WORK_DIR / "table_audit_report.json"

# ── Table filter thresholds ────────────────────────────────────────────────
MIN_ROWS = 3
MIN_COLS = 2
MIN_NON_EMPTY_CELLS = 6

# ── Coverage flag thresholds ───────────────────────────────────────────────
RED_THRESHOLD = 0.40    # <40% covered = RED
YELLOW_THRESHOLD = 0.70 # 40-70% = YELLOW, >70% = GREEN


# ═══════════════════════════════════════════════════════════════════════════
# Phase 1: Table Detection
# ═══════════════════════════════════════════════════════════════════════════

def smart_reverse_cell(text):
    """Reverse Hebrew text from PyMuPDF tables back to correct reading order.

    PyMuPDF find_tables() returns Hebrew characters in reversed order (both
    character order within words and word order are flipped). A full string
    reversal restores the correct reading. Mixed Hebrew/Latin content needs
    segment-aware handling.
    """
    if not text or not text.strip():
        return text

    # Check if text contains Hebrew characters
    has_hebrew = any('\u0590' <= ch <= '\u05FF' for ch in text)
    if not has_hebrew:
        return text

    # Check if text also contains substantial Latin/digit runs
    latin_runs = re.findall(r'[A-Za-z0-9]{2,}', text)

    if not latin_runs:
        # Pure Hebrew (possibly with punctuation) — full reversal works
        return text[::-1]

    # Mixed content: reverse the full string, then re-reverse Latin/digit runs
    # so they read left-to-right again
    reversed_text = text[::-1]
    for run in re.finditer(r'[A-Za-z0-9]+', reversed_text):
        original = run.group()
        fixed = original[::-1]
        reversed_text = reversed_text[:run.start()] + fixed + reversed_text[run.end():]

    return reversed_text


def detect_tables(doc, page_filter=None):
    """Scan PDF pages for tables. Returns dict: page_num -> list of table dicts."""
    tables_by_page = {}

    pages_to_scan = range(doc.page_count)
    if page_filter is not None:
        pages_to_scan = [page_filter - 1]  # 0-indexed

    for pn in pages_to_scan:
        if pn < 0 or pn >= doc.page_count:
            continue
        page = doc[pn]
        page_num = pn + 1  # 1-indexed

        finder = page.find_tables()
        if not finder.tables:
            continue

        page_tables = []
        for table in finder.tables:
            data = table.extract()
            if not data:
                continue

            rows = len(data)
            cols = len(data[0]) if data else 0
            # Collect non-empty cells
            cells = []
            for r_idx, row in enumerate(data):
                for c_idx, cell in enumerate(row):
                    if cell and cell.strip():
                        cleaned = smart_reverse_cell(cell.strip())
                        cells.append({
                            "row": r_idx,
                            "col": c_idx,
                            "text": cleaned,
                            "raw": cell.strip(),
                        })

            non_empty = len(cells)

            # Filter: must meet minimum thresholds to be a "real" table
            if rows < MIN_ROWS or cols < MIN_COLS or non_empty < MIN_NON_EMPTY_CELLS:
                continue

            bbox = list(table.bbox) if hasattr(table, 'bbox') else None
            page_tables.append({
                "rows": rows,
                "cols": cols,
                "non_empty_cells": non_empty,
                "bbox": bbox,
                "cells": cells,
            })

        if page_tables:
            tables_by_page[page_num] = page_tables

    return tables_by_page


def save_cache(tables_by_page):
    """Save table scan results to JSON cache."""
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    # Convert int keys to strings for JSON
    cache = {str(k): v for k, v in tables_by_page.items()}
    with open(CACHE_PATH, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)
    print(f"  Cache saved: {CACHE_PATH}")


def load_cache():
    """Load cached table scan results."""
    if not CACHE_PATH.exists():
        return None
    with open(CACHE_PATH, 'r', encoding='utf-8') as f:
        cache = json.load(f)
    # Convert string keys back to ints
    return {int(k): v for k, v in cache.items()}


# ═══════════════════════════════════════════════════════════════════════════
# Phase 2: Card Parsing
# ═══════════════════════════════════════════════════════════════════════════

def parse_all_cards():
    """Parse all output/*_cards.md files. Returns dict: page_num -> combined text."""
    card_pattern = re.compile(
        r'^\d+\.\s*\[עמ\'?\s*([\d\-]+)\]\s*(.*?)(?=\n\d+\.\s*\[עמ|\Z)',
        re.MULTILINE | re.DOTALL
    )

    page_texts = defaultdict(str)
    page_card_counts = defaultdict(int)

    md_files = sorted(OUTPUT_DIR.glob("*_cards.md"))
    if not md_files:
        print("WARNING: No *_cards.md files found in output/")
        return page_texts, page_card_counts

    for md_file in md_files:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        for m in card_pattern.finditer(content):
            page_ref = m.group(1).split('-')[0]
            try:
                page_num = int(page_ref)
            except ValueError:
                continue
            body = m.group(2).strip()
            # Strip cloze markers: **[text]** -> text
            clean_body = re.sub(r'\*\*\[([^\]]+)\]\*\*', r'\1', body)
            page_texts[page_num] += " " + clean_body
            page_card_counts[page_num] += 1

    return page_texts, page_card_counts


def tokenize(text):
    """Extract meaningful tokens (>=3 chars) from text."""
    # Remove punctuation, split on whitespace
    cleaned = re.sub(r'[^\w\s]', ' ', text)
    tokens = set()
    for word in cleaned.split():
        if len(word) >= 3:
            tokens.add(word.lower())
    return tokens


# ═══════════════════════════════════════════════════════════════════════════
# Phase 3: Cross-Reference Matching
# ═══════════════════════════════════════════════════════════════════════════

def clean_cell_text(text):
    """Normalize cell text for matching: strip whitespace, newlines, punctuation."""
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'^[\-:•·]+', '', text).strip()
    return text


def cell_is_trivial(text):
    """Return True if cell contains only trivial content (numbers, single chars, etc.)."""
    cleaned = re.sub(r'[^\w]', '', text)
    if len(cleaned) <= 2:
        return True
    # Pure numbers or very short
    if re.match(r'^[\d\.\,\%\-\+\/]+$', cleaned):
        return True
    return False


def cell_is_header(cell, table):
    """Heuristic: cells in row 0 that are short category labels, not factual content.

    Table headers (column/section titles) are organizational — the actual data
    beneath them is what matters for card coverage. Mark them so they don't
    inflate the "uncovered" count when the real content IS covered.
    """
    # Only row 0 is a candidate for a header
    if cell["row"] != 0:
        return False
    text = clean_cell_text(cell["text"])
    # Short text (< 40 chars) in row 0 is likely a column/section header
    if len(text) < 40:
        return True
    return False


def check_cell_coverage(cell_text, page_combined_text, page_tokens):
    """Check if a table cell's content appears in the cards for that page.

    Uses 4 strategies:
    1. Substring match: cleaned cell text appears verbatim
    2. Token overlap >= 50%: at least half of meaningful tokens match
    3. Distinctive token: any single token >= 5 chars matches exactly
    4. Fuzzy token containment: a cell token appears AS A SUBSTRING of a page
       token (handles hyphenated compounds like "מינרלו-קורטיקואידים" in table
       vs "מינרלוקורטיקואידים" in cards)

    Returns: (covered: bool, strategy: str or None)
    """
    cleaned_cell = clean_cell_text(cell_text)

    if cell_is_trivial(cleaned_cell):
        return True, "trivial"

    if not page_combined_text:
        return False, None

    page_lower = page_combined_text.lower()

    # Strategy 1: Substring match
    if len(cleaned_cell) >= 4 and cleaned_cell.lower() in page_lower:
        return True, "substring"

    # Strategy 2: Token overlap >= 50% (exact + fuzzy)
    cell_tokens = tokenize(cleaned_cell)
    if cell_tokens:
        # Count exact matches
        exact_overlap = cell_tokens & page_tokens
        # Count fuzzy matches: cell token is a substring of any page token
        fuzzy_matches = set()
        for ct in cell_tokens - exact_overlap:
            if len(ct) >= 4:  # only fuzzy-match substantial tokens
                for pt in page_tokens:
                    if len(pt) >= len(ct) and ct in pt:
                        fuzzy_matches.add(ct)
                        break
        total_matched = len(exact_overlap) + len(fuzzy_matches)
        overlap_ratio = total_matched / len(cell_tokens)
        if overlap_ratio >= 0.50:
            strategy = "token_overlap" if not fuzzy_matches else "token_overlap_fuzzy"
            return True, strategy

    # Strategy 3: Distinctive token (any token >= 5 chars matches exactly)
    for token in cell_tokens:
        if len(token) >= 5 and token in page_tokens:
            return True, "distinctive_token"

    # Strategy 4: Fuzzy distinctive token (cell token is substring of page token)
    for token in cell_tokens:
        if len(token) >= 5:
            for pt in page_tokens:
                if len(pt) > len(token) and token in pt:
                    return True, "fuzzy_distinctive"

    return False, None


def audit_page(page_num, page_tables, page_text, page_tokens):
    """Audit table coverage for a single page. Returns page result dict."""
    total_cells = 0
    covered_cells = 0
    trivial_cells = 0
    header_cells = 0
    uncovered = []

    for t_idx, table in enumerate(page_tables):
        for cell in table["cells"]:
            cell_text = cell["text"]
            total_cells += 1

            # Check if cell is a table header (organizational, not factual)
            if cell_is_header(cell, table):
                header_cells += 1
                covered_cells += 1  # headers don't penalize coverage
                continue

            covered, strategy = check_cell_coverage(cell_text, page_text, page_tokens)
            if covered:
                covered_cells += 1
                if strategy == "trivial":
                    trivial_cells += 1
            else:
                uncovered.append({
                    "table": t_idx,
                    "row": cell["row"],
                    "col": cell["col"],
                    "text": cell_text[:120],
                })

    meaningful_total = total_cells - trivial_cells - header_cells
    meaningful_covered = covered_cells - trivial_cells - header_cells

    if meaningful_total == 0:
        coverage = 1.0
    else:
        coverage = meaningful_covered / meaningful_total

    if coverage >= YELLOW_THRESHOLD:
        flag = "GREEN"
    elif coverage >= RED_THRESHOLD:
        flag = "YELLOW"
    else:
        flag = "RED"

    return {
        "page": page_num,
        "n_tables": len(page_tables),
        "total_cells": total_cells,
        "trivial_cells": trivial_cells,
        "meaningful_cells": meaningful_total,
        "covered_cells": meaningful_covered,
        "coverage": round(coverage, 3),
        "flag": flag,
        "uncovered_samples": uncovered[:10],  # Cap at 10 samples
    }


# ═══════════════════════════════════════════════════════════════════════════
# Phase 4: Report Generation
# ═══════════════════════════════════════════════════════════════════════════

def print_report(results, tables_by_page):
    """Print terminal report with summary and per-page details."""
    print()
    print("=" * 70)
    print("TABLE COVERAGE AUDIT REPORT")
    print("=" * 70)

    total_pages_with_tables = len(results)
    red_pages = [r for r in results if r["flag"] == "RED"]
    yellow_pages = [r for r in results if r["flag"] == "YELLOW"]
    green_pages = [r for r in results if r["flag"] == "GREEN"]

    total_meaningful = sum(r["meaningful_cells"] for r in results)
    total_covered = sum(r["covered_cells"] for r in results)
    overall_coverage = total_covered / total_meaningful if total_meaningful else 1.0

    print(f"\n  Pages with qualifying tables: {total_pages_with_tables}")
    print(f"  Total meaningful cells:       {total_meaningful}")
    print(f"  Covered cells:                {total_covered}")
    print(f"  Overall coverage:             {overall_coverage:.1%}")
    print(f"\n  GREEN (>70%): {len(green_pages)} pages")
    print(f"  YELLOW (40-70%): {len(yellow_pages)} pages")
    print(f"  RED (<40%): {len(red_pages)} pages")

    # RED-flagged pages detail
    if red_pages:
        print(f"\n{'=' * 70}")
        print("RED-FLAGGED PAGES (< 40% table coverage)")
        print("=" * 70)
        for r in sorted(red_pages, key=lambda x: x["coverage"]):
            print(f"\n  Page {r['page']}: {r['coverage']:.0%} coverage "
                  f"({r['covered_cells']}/{r['meaningful_cells']} cells, "
                  f"{r['n_tables']} table(s))")
            if r["uncovered_samples"]:
                print(f"    Uncovered cell samples:")
                for u in r["uncovered_samples"][:5]:
                    text_preview = u["text"][:80]
                    print(f"      - [{u['row']},{u['col']}] {text_preview}")

    # YELLOW pages summary
    if yellow_pages:
        print(f"\n{'=' * 70}")
        print("YELLOW-FLAGGED PAGES (40-70% table coverage)")
        print("=" * 70)
        for r in sorted(yellow_pages, key=lambda x: x["coverage"]):
            print(f"  Page {r['page']}: {r['coverage']:.0%} coverage "
                  f"({r['covered_cells']}/{r['meaningful_cells']} cells)")

    # Full page-by-page table
    print(f"\n{'=' * 70}")
    print("PAGE-BY-PAGE TABLE COVERAGE")
    print(f"{'=' * 70}")
    print(f"  {'Page':>6}  {'Tables':>6}  {'Cells':>7}  {'Covered':>8}  {'Coverage':>9}  Flag")
    print(f"  {'─' * 6}  {'─' * 6}  {'─' * 7}  {'─' * 8}  {'─' * 9}  ────")
    for r in sorted(results, key=lambda x: x["page"]):
        flag_marker = {"RED": "!!!", "YELLOW": " ! ", "GREEN": "   "}[r["flag"]]
        print(f"  {r['page']:>6}  {r['n_tables']:>6}  {r['meaningful_cells']:>7}  "
              f"{r['covered_cells']:>8}  {r['coverage']:>8.0%}  {r['flag']}{flag_marker}")

    print(f"\n{'=' * 70}")
    return len(red_pages), len(yellow_pages)


def save_json_report(results, tables_by_page):
    """Save machine-readable JSON report."""
    WORK_DIR.mkdir(parents=True, exist_ok=True)

    total_meaningful = sum(r["meaningful_cells"] for r in results)
    total_covered = sum(r["covered_cells"] for r in results)

    report = {
        "summary": {
            "pages_with_tables": len(results),
            "total_meaningful_cells": total_meaningful,
            "total_covered_cells": total_covered,
            "overall_coverage": round(total_covered / total_meaningful, 3) if total_meaningful else 1.0,
            "red_pages": len([r for r in results if r["flag"] == "RED"]),
            "yellow_pages": len([r for r in results if r["flag"] == "YELLOW"]),
            "green_pages": len([r for r in results if r["flag"] == "GREEN"]),
        },
        "pages": sorted(results, key=lambda x: x["page"]),
    }

    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"  JSON report saved: {REPORT_PATH}")


def export_flagged_pngs(doc, results):
    """Export page images for RED-flagged pages."""
    red_pages = [r for r in results if r["flag"] == "RED"]
    if not red_pages:
        print("  No RED-flagged pages to export.")
        return

    export_dir = WORK_DIR / "flagged_pages"
    export_dir.mkdir(parents=True, exist_ok=True)

    for r in red_pages:
        pn = r["page"] - 1  # 0-indexed
        page = doc[pn]
        pix = page.get_pixmap(dpi=150)
        out_path = export_dir / f"page_{r['page']:03d}_RED.png"
        pix.save(str(out_path))
        print(f"  Exported: {out_path}")

    print(f"  {len(red_pages)} PNG(s) exported to {export_dir}")


# ═══════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Audit table coverage in Anki cards")
    parser.add_argument("--cache", action="store_true",
                        help="Reuse cached table scan from work/table_cache.json")
    parser.add_argument("--page", type=int, default=None,
                        help="Audit a single page number")
    parser.add_argument("--export-flagged", action="store_true",
                        help="Export PNGs for RED-flagged pages")
    args = parser.parse_args()

    if not PDF_PATH.exists():
        print(f"ERROR: Source PDF not found: {PDF_PATH}")
        sys.exit(1)

    doc = fitz.open(str(PDF_PATH))

    # ── Phase 1: Table Detection ──
    print("Phase 1: Table Detection")
    if args.cache and args.page is None:
        tables_by_page = load_cache()
        if tables_by_page:
            print(f"  Loaded {len(tables_by_page)} pages from cache")
        else:
            print("  No cache found, scanning PDF...")
            tables_by_page = detect_tables(doc)
            save_cache(tables_by_page)
    elif args.page is not None:
        print(f"  Scanning page {args.page}...")
        tables_by_page = detect_tables(doc, page_filter=args.page)
    else:
        print(f"  Scanning all {doc.page_count} pages...")
        tables_by_page = detect_tables(doc)
        save_cache(tables_by_page)

    total_tables = sum(len(v) for v in tables_by_page.values())
    print(f"  Found {total_tables} qualifying tables on {len(tables_by_page)} pages")

    if not tables_by_page:
        print("  No qualifying tables found. Nothing to audit.")
        doc.close()
        sys.exit(0)

    # ── Phase 2: Card Parsing ──
    print("\nPhase 2: Card Parsing")
    page_texts, page_card_counts = parse_all_cards()
    total_cards = sum(page_card_counts.values())
    print(f"  Parsed {total_cards} cards across {len(page_texts)} pages")

    # Pre-compute token sets per page
    page_token_sets = {}
    for pg, text in page_texts.items():
        page_token_sets[pg] = tokenize(text)

    # ── Batch boundary gap check ──
    pages_with_zero_cards = [pg for pg in sorted(tables_by_page.keys())
                             if page_card_counts.get(pg, 0) == 0]
    if pages_with_zero_cards:
        print(f"\n  WARNING: {len(pages_with_zero_cards)} table page(s) have ZERO cards:")
        print(f"    {pages_with_zero_cards}")
        print(f"    (likely batch boundary gaps — check progress.json)")

    # ── RC-1 check: Bottom-of-page truncation ──
    print("\nPhase 2b: Bottom-of-Page Truncation Scan")
    truncated_pages = []
    for pn in range(doc.page_count):
        pg = pn + 1
        if args.page is not None and pg != args.page:
            continue
        text = doc[pn].get_text().strip()
        if len(text) < 3000:
            continue
        cutoff = int(len(text) * 0.7)
        bottom_text = text[cutoff:]
        bottom_words = set(re.findall(r'[\u0590-\u05FF]{5,}', bottom_text))
        if not bottom_words:
            continue
        card_text = page_texts.get(pg, '')
        if not card_text:
            continue
        found = sum(1 for w in bottom_words if w in card_text)
        ratio = found / len(bottom_words) if bottom_words else 1
        if ratio < 0.15:
            truncated_pages.append((pg, len(text), len(bottom_words), found, ratio))

    if truncated_pages:
        print(f"  WARNING: {len(truncated_pages)} page(s) may have bottom-of-page truncation:")
        for pg, chars, total_w, found_w, ratio in truncated_pages:
            print(f"    Page {pg}: {chars} chars, bottom-30% words in cards: {found_w}/{total_w} ({ratio:.0%})")
    else:
        print(f"  No truncation detected")

    # ── RC-2 check: Image-table pages with sparse text but few cards ──
    print("\nPhase 2c: Image-Table Density Mismatch Scan")
    image_table_gaps = []
    for pg, tables in tables_by_page.items():
        if args.page is not None and pg != args.page:
            continue
        pn = pg - 1
        text = doc[pn].get_text().strip()
        chars = len(text)
        cards = page_card_counts.get(pg, 0)
        total_cells = sum(len(t["cells"]) for t in tables)
        if chars < 1500 and total_cells >= 10 and cards < total_cells * 0.3:
            image_table_gaps.append((pg, chars, total_cells, cards))

    if image_table_gaps:
        print(f"  WARNING: {len(image_table_gaps)} page(s) have table cells but sparse text and few cards:")
        for pg, chars, cells, cards in image_table_gaps:
            print(f"    Page {pg}: {chars} text chars, {cells} table cells, only {cards} cards")
    else:
        print(f"  No image-table mismatches detected")

    # ── RC-3 check: Dense table pages with low cards-per-cell ratio ──
    print("\nPhase 2d: Dense Table Under-Coverage Scan")
    dense_table_gaps = []
    for pg, tables in tables_by_page.items():
        if args.page is not None and pg != args.page:
            continue
        total_cells = sum(1 for t in tables for c in t["cells"]
                         if len(c["text"].strip()) > 5)
        cards = page_card_counts.get(pg, 0)
        if total_cells >= 30 and cards > 0 and cards / total_cells < 0.25:
            dense_table_gaps.append((pg, total_cells, cards, cards / total_cells))

    if dense_table_gaps:
        print(f"  WARNING: {len(dense_table_gaps)} page(s) have dense tables with very few cards:")
        for pg, cells, cards, ratio in sorted(dense_table_gaps, key=lambda x: x[3]):
            print(f"    Page {pg}: {cells} meaningful cells, {cards} cards (ratio {ratio:.2f})")
    else:
        print(f"  No dense-table under-coverage detected")

    # ── Phase 3: Cross-Reference ──
    print("\nPhase 3: Cross-Reference Matching")
    results = []
    for page_num in sorted(tables_by_page.keys()):
        page_tables = tables_by_page[page_num]
        page_text = page_texts.get(page_num, "")
        page_tokens = page_token_sets.get(page_num, set())
        result = audit_page(page_num, page_tables, page_text, page_tokens)
        results.append(result)

    # ── Phase 4: Report ──
    n_red, n_yellow = print_report(results, tables_by_page)

    save_json_report(results, tables_by_page)

    if args.export_flagged:
        print(f"\nExporting PNGs for RED-flagged pages...")
        export_flagged_pngs(doc, results)

    doc.close()

    # Exit code
    if n_red > 0:
        sys.exit(1)
    elif n_yellow > 0:
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
