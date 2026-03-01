#!/usr/bin/env python3
"""
Validate card density and cloze distribution against enforced minimums.
Usage: python validate_density.py <cards.md> <extraction.json> <start_page> <end_page>

Exit code 0 = PASS, 1 = FAIL
"""

import re, json, sys, os

def parse_cards_from_md(md_path):
    """Parse cards and return list of dicts with page, cloze_count, text_length."""
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    card_pattern = re.compile(
        r'^(\d+)\.\s*\[עמ\'?\s*([\d\-]+)\]\s*(.*?)(?=\n\d+\.\s*\[עמ|\Z)',
        re.MULTILINE | re.DOTALL
    )
    cards = []
    for m in card_pattern.finditer(content):
        num, page, body = m.group(1), m.group(2).split('-')[0], m.group(3).strip()

        # Remove Extra line from body for length calculation
        extra_match = re.search(r'>\s*Extra:\s*(.+)', body)
        card_body = body[:extra_match.start()].strip() if extra_match else body

        # Count clozes
        n_clozes = len(re.findall(r'\*\*\[([^\]]+)\]\*\*', card_body))

        cards.append({
            'num': int(num),
            'page': int(page),
            'cloze_count': n_clozes,
            'text_length': len(card_body),
        })
    return cards


def load_extraction(extraction_path, start_page, end_page):
    """Load extraction JSON and return per-page char counts."""
    with open(extraction_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    page_chars = {}
    for p in range(start_page, end_page + 1):
        pdata = data['pages'].get(str(p), {})
        page_chars[p] = pdata.get('chars', 0)
    return page_chars


def min_notes_for_chars(chars):
    """Return minimum required notes based on source character count."""
    if chars >= 6000:
        return 15
    elif chars >= 4000:
        return 10
    elif chars >= 2000:
        return 5
    elif chars >= 200:  # text page but sparse
        return 3
    else:  # image-only
        return 0


def validate(cards, page_chars, md_path=None):
    """Run all validation checks. Returns (passed: bool, report: str)."""
    lines = []
    failures = []
    warnings = []

    # --- Per-page density ---
    lines.append("=" * 60)
    lines.append("PER-PAGE DENSITY CHECK")
    lines.append("=" * 60)

    cards_per_page = {}
    for c in cards:
        cards_per_page.setdefault(c['page'], []).append(c)

    for page in sorted(page_chars.keys()):
        chars = page_chars[page]
        n_cards = len(cards_per_page.get(page, []))
        required = min_notes_for_chars(chars)
        status = "PASS" if n_cards >= required else "FAIL"
        ratio = f"{n_cards / (chars / 1000):.1f}" if chars > 0 else "N/A"

        line = f"  Page {page}: {chars:>6} chars | {n_cards:>3} cards (min {required:>2}) | {ratio} notes/1k chars | {status}"
        lines.append(line)
        if status == "FAIL":
            failures.append(f"Page {page}: {n_cards} cards but minimum is {required} (source has {chars} chars)")

    # --- Cloze distribution ---
    lines.append("")
    lines.append("=" * 60)
    lines.append("CLOZE DISTRIBUTION CHECK")
    lines.append("=" * 60)

    total_cards = len(cards)
    if total_cards == 0:
        failures.append("No cards found!")
        return False, "\n".join(lines + ["NO CARDS FOUND"])

    cloze_counts = [c['cloze_count'] for c in cards]
    avg_clozes = sum(cloze_counts) / total_cards
    cards_le3 = sum(1 for c in cloze_counts if c <= 3)
    cards_eq5 = sum(1 for c in cloze_counts if c == 5)
    cards_gt5 = sum(1 for c in cloze_counts if c > 5)
    pct_le3 = cards_le3 / total_cards * 100
    pct_eq5 = cards_eq5 / total_cards * 100

    lines.append(f"  Total cards: {total_cards}")
    lines.append(f"  Avg clozes/card: {avg_clozes:.2f} (target 2.5-3.2)")
    lines.append(f"  Cards with <=3 clozes: {cards_le3} ({pct_le3:.0f}%) — need >=50%: {'PASS' if pct_le3 >= 50 else 'FAIL'}")
    lines.append(f"  Cards with 5 clozes: {cards_eq5} ({pct_eq5:.0f}%) — need <=20%: {'PASS' if pct_eq5 <= 20 else 'FAIL'}")
    lines.append(f"  Cards with >5 clozes: {cards_gt5} — need 0: {'PASS' if cards_gt5 == 0 else 'FAIL'}")

    if pct_le3 < 50:
        failures.append(f"Only {pct_le3:.0f}% of cards have <=3 clozes (need >=50%)")
    if pct_eq5 > 20:
        failures.append(f"{pct_eq5:.0f}% of cards have 5 clozes (need <=20%)")
    if cards_gt5 > 0:
        failures.append(f"{cards_gt5} cards exceed 5 clozes (hard limit)")
    if avg_clozes > 3.5:
        warnings.append(f"Avg clozes ({avg_clozes:.2f}) above 3.5 — consider splitting bloated cards")

    # --- Cloze histogram ---
    lines.append("")
    lines.append("  Cloze histogram:")
    for i in range(1, 7):
        count = sum(1 for c in cloze_counts if c == i)
        bar = "#" * count
        lines.append(f"    {i} clozes: {count:>3} cards  {bar}")

    # --- Extra field and keywords presence ---
    lines.append("")
    lines.append("=" * 60)
    lines.append("EXTRA FIELD & KEYWORDS CHECK")
    lines.append("=" * 60)

    if md_path is None:
        lines.append("  (skipped — no md_path provided)")
    else:
        with open(md_path, 'r', encoding='utf-8') as f:
            raw = f.read()
        card_pat = re.compile(
            r'^(\d+)\.\s*\[עמ\'?\s*([\d\-]+)\]\s*(.*?)(?=\n\d+\.\s*\[עמ|\Z)',
            re.MULTILINE | re.DOTALL
        )
        missing_extra = []
        missing_kw = []
        for m2 in card_pat.finditer(raw):
            cnum, cbody = m2.group(1), m2.group(3)
            if not re.search(r'>\s*Extra:', cbody):
                missing_extra.append(int(cnum))
            extra_m = re.search(r'>\s*Extra:', cbody)
            body_before_extra = cbody[:extra_m.start()].strip() if extra_m else cbody.strip()
            if not re.search(r'\{[^}]+\}\s*$', body_before_extra):
                missing_kw.append(int(cnum))

        if missing_extra:
            pct_missing = len(missing_extra) / total_cards * 100
            lines.append(f"  Cards missing Extra: {len(missing_extra)} ({pct_missing:.0f}%) — FAIL")
            failures.append(f"{len(missing_extra)} cards missing Extra field: {missing_extra[:10]}{'...' if len(missing_extra)>10 else ''}")
        else:
            lines.append(f"  All {total_cards} cards have Extra field: PASS")

        if missing_kw:
            pct_kw = len(missing_kw) / total_cards * 100
            lines.append(f"  Cards missing {{keywords}}: {len(missing_kw)} ({pct_kw:.0f}%) — FAIL")
            failures.append(f"{len(missing_kw)} cards missing {{keywords}}: {missing_kw[:10]}{'...' if len(missing_kw)>10 else ''}")
        else:
            lines.append(f"  All {total_cards} cards have {{keywords}}: PASS")

    # --- Card text length ---
    lines.append("")
    lines.append("=" * 60)
    lines.append("CARD TEXT LENGTH CHECK")
    lines.append("=" * 60)

    text_lengths = [c['text_length'] for c in cards]
    avg_len = sum(text_lengths) / total_cards
    over_380 = sum(1 for t in text_lengths if t > 380)
    pct_over = over_380 / total_cards * 100

    lines.append(f"  Avg card text length: {avg_len:.0f} chars (target 250-320)")
    lines.append(f"  Cards >380 chars: {over_380} ({pct_over:.0f}%)")

    if avg_len > 380:
        warnings.append(f"Avg card text length ({avg_len:.0f}) exceeds 380 chars — cards may be too bloated")
    if pct_over > 30:
        warnings.append(f"{pct_over:.0f}% of cards exceed 380 chars — consider splitting")

    # --- Summary ---
    lines.append("")
    lines.append("=" * 60)
    passed = len(failures) == 0

    if warnings:
        lines.append("WARNINGS:")
        for w in warnings:
            lines.append(f"  - {w}")

    if failures:
        lines.append(f"FAILED ({len(failures)} issues):")
        for f in failures:
            lines.append(f"  - {f}")
    else:
        lines.append("ALL CHECKS PASSED")

    lines.append("=" * 60)
    return passed, "\n".join(lines)


def main():
    if len(sys.argv) < 5:
        print("Usage: python validate_density.py <cards.md> <extraction.json> <start_page> <end_page>")
        sys.exit(1)

    cards_md = sys.argv[1]
    extraction_json = sys.argv[2]
    start_page = int(sys.argv[3])
    end_page = int(sys.argv[4])

    cards = parse_cards_from_md(cards_md)
    page_chars = load_extraction(extraction_json, start_page, end_page)

    passed, report = validate(cards, page_chars, md_path=cards_md)
    print(report)
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
