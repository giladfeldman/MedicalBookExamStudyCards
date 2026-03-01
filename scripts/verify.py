#!/usr/bin/env python3
"""
Comprehensive APKG verification. Checks ALL 7 fields, cloze limits,
template structure, and field completeness.

Exit code 0 = PASS, 1 = FAIL (hard errors), 2 = WARN (soft issues)
"""

import sqlite3, zipfile, json, re, sys, os, tempfile, io

# Force UTF-8 output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def verify(apkg_path, strict=True):
    tmpdir = tempfile.mkdtemp()
    with zipfile.ZipFile(apkg_path, 'r') as z:
        z.extractall(tmpdir)

    db = sqlite3.connect(os.path.join(tmpdir, 'collection.anki2'))
    cur = db.cursor()

    errors = []    # hard failures — always block
    warnings = []  # soft issues — block in strict mode

    # ── Count notes and cards ──
    cur.execute("SELECT COUNT(*) FROM notes")
    n_notes = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM cards")
    n_cards = cur.fetchone()[0]
    print(f"Notes: {n_notes}, Cards (cloze instances): {n_cards}")

    if n_notes == 0:
        errors.append("APKG contains 0 notes!")
        db.close()
        print(f"\n{'❌'} 1 ERROR: APKG contains 0 notes!")
        return False

    # ── Check model structure ──
    expected_fields = ['Text', 'Context', 'Extra', 'NelsonChapter',
                       'SearchKeywords', 'GoogleURL', 'ChapterURL']
    EXPECTED_MODEL_ID = 1607392322
    EXPECTED_MODEL_NAME = "Nelson Cloze v5"

    cur.execute("SELECT models FROM col")
    models = json.loads(cur.fetchone()[0])
    for mid, m in models.items():
        fields = [f['name'] for f in m['flds']]
        if fields != expected_fields:
            errors.append(f"Field mismatch: got {fields}, expected {expected_fields}")
        if m['name'] != EXPECTED_MODEL_NAME:
            errors.append(f"Model name mismatch: got '{m['name']}', expected '{EXPECTED_MODEL_NAME}'")
        if int(mid) != EXPECTED_MODEL_ID:
            errors.append(f"Model ID mismatch: got {mid}, expected {EXPECTED_MODEL_ID}")
        if m.get('type') != 1:  # 1 = cloze
            errors.append(f"Model type is not cloze (type={m.get('type')})")
        # Template checks
        qfmt = m['tmpls'][0]['qfmt']
        afmt = m['tmpls'][0]['afmt']
        if 'Context' in qfmt:
            errors.append("Context found on front template (should be back only)")
        if 'Extra' in qfmt:
            errors.append("Extra found on front template (should be back only)")
        if 'ChapterURL' not in afmt:
            errors.append("ChapterURL missing from back template")
        if 'GoogleURL' not in afmt:
            errors.append("GoogleURL missing from back template")

    # ── Check every note — ALL 7 fields ──
    cur.execute("SELECT id, flds, tags FROM notes")
    max_clozes = 0
    cloze_counts = []
    text_lengths = []
    empty_fields = {name: [] for name in expected_fields}
    page_coverage = {}

    for note_id, flds, tags in cur.fetchall():
        parts = flds.split('\x1f')
        if len(parts) < 7:
            errors.append(f"Note {note_id}: only {len(parts)} fields (need 7)")
            continue

        # Check each field for emptiness
        for i, name in enumerate(expected_fields):
            if not parts[i].strip():
                empty_fields[name].append(note_id)

        # Cloze count
        text = parts[0]
        n_clozes = len(re.findall(r'\{\{c\d+::', text))
        max_clozes = max(max_clozes, n_clozes)
        cloze_counts.append(n_clozes)
        if n_clozes > 5:
            errors.append(f"Note {note_id}: {n_clozes} clozes (hard limit: 5)")
        if n_clozes == 0:
            errors.append(f"Note {note_id}: 0 clozes (no blanks)")

        # Text length (strip HTML tags for length check)
        clean_text = re.sub(r'<[^>]+>', '', text)
        clean_text = re.sub(r'\{\{c\d+::', '', clean_text).replace('}}', '')
        text_lengths.append(len(clean_text))

        # Page coverage
        page_match = re.search(r"עמ'\s*(\d+)", text)
        if page_match:
            pg = page_match.group(1)
            page_coverage[pg] = page_coverage.get(pg, 0) + 1

    db.close()

    # ── Report: Field completeness ──
    print(f"\n{'='*60}")
    print("FIELD COMPLETENESS CHECK")
    print(f"{'='*60}")

    # Fields that MUST be 100% populated (hard errors)
    required_fields = ['Text', 'Context', 'Extra', 'SearchKeywords', 'GoogleURL']
    # Fields that SHOULD be populated (warnings in lenient mode, errors in strict)
    important_fields = ['NelsonChapter', 'ChapterURL']

    for name in expected_fields:
        count = len(empty_fields[name])
        pct = count / n_notes * 100
        if count == 0:
            print(f"  {name}: {n_notes}/{n_notes} (100%) ✓")
        else:
            marker = "FAIL" if name in required_fields else ("FAIL" if strict else "WARN")
            print(f"  {name}: {n_notes - count}/{n_notes} ({100 - pct:.1f}%) — {count} empty {marker}")
            if name in required_fields:
                errors.append(f"{count} notes missing required field '{name}'")
            elif name in important_fields:
                if strict:
                    errors.append(f"{count} notes missing '{name}' (strict mode)")
                else:
                    warnings.append(f"{count} notes missing '{name}'")

    # ── Report: Cloze distribution ──
    print(f"\n{'='*60}")
    print("CLOZE DISTRIBUTION CHECK")
    print(f"{'='*60}")

    avg_clozes = sum(cloze_counts) / n_notes if n_notes else 0
    cards_le3 = sum(1 for c in cloze_counts if c <= 3)
    cards_eq5 = sum(1 for c in cloze_counts if c == 5)
    cards_gt5 = sum(1 for c in cloze_counts if c > 5)
    pct_le3 = cards_le3 / n_notes * 100
    pct_eq5 = cards_eq5 / n_notes * 100

    print(f"  Max clozes on any note: {max_clozes}")
    print(f"  Avg clozes/note: {avg_clozes:.2f} (target 2.5-3.2)")
    print(f"  Notes with ≤3 clozes: {cards_le3} ({pct_le3:.0f}%) — need ≥50%: {'PASS' if pct_le3 >= 50 else 'FAIL'}")
    print(f"  Notes with 5 clozes: {cards_eq5} ({pct_eq5:.0f}%) — need ≤20%: {'PASS' if pct_eq5 <= 20 else 'FAIL'}")
    print(f"  Notes with >5 clozes: {cards_gt5} — need 0: {'PASS' if cards_gt5 == 0 else 'FAIL'}")

    if pct_le3 < 50:
        errors.append(f"Only {pct_le3:.0f}% of notes have ≤3 clozes (need ≥50%)")
    if pct_eq5 > 20:
        errors.append(f"{pct_eq5:.0f}% of notes have 5 clozes (need ≤20%)")

    # Histogram
    print("\n  Cloze histogram:")
    for i in range(1, 7):
        count = sum(1 for c in cloze_counts if c == i)
        bar = "#" * min(count, 80)
        print(f"    {i} clozes: {count:>3} notes  {bar}")

    # ── Report: Text length ──
    print(f"\n{'='*60}")
    print("CARD TEXT LENGTH CHECK")
    print(f"{'='*60}")

    avg_len = sum(text_lengths) / n_notes if n_notes else 0
    over_380 = sum(1 for t in text_lengths if t > 380)
    pct_over = over_380 / n_notes * 100
    print(f"  Avg text length: {avg_len:.0f} chars (target 250-320)")
    print(f"  Notes >380 chars: {over_380} ({pct_over:.0f}%)")
    if pct_over > 10:
        warnings.append(f"{pct_over:.0f}% of notes exceed 380 chars")

    # ── Report: Page coverage ──
    print(f"\n{'='*60}")
    print("PAGE COVERAGE")
    print(f"{'='*60}")
    for pg in sorted(page_coverage.keys(), key=int):
        print(f"  Page {pg}: {page_coverage[pg]} notes")

    # ── Final verdict ──
    print(f"\n{'='*60}")
    if warnings:
        print(f"WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"  ⚠ {w}")

    if errors:
        print(f"ERRORS ({len(errors)}):")
        for e in errors:
            print(f"  ✗ {e}")
        print(f"\n✗ VERIFICATION FAILED ({len(errors)} errors)")
        print(f"{'='*60}")
        return False
    else:
        print(f"✓ ALL CHECKS PASSED — {n_notes} notes, {n_cards} cards")
        print(f"{'='*60}")
        return True


def audit_all(output_dir, strict=True):
    """Run verification on all APKGs in a directory. Summary report."""
    import glob
    apkg_files = sorted(glob.glob(os.path.join(output_dir, '*.apkg')))
    if not apkg_files:
        print(f"No APKG files found in {output_dir}")
        return

    results = []
    for apkg_path in apkg_files:
        fname = os.path.basename(apkg_path)
        print(f"\n{'#'*70}")
        print(f"# {fname}")
        print(f"{'#'*70}")
        ok = verify(apkg_path, strict=strict)
        results.append((fname, ok))

    print(f"\n\n{'='*70}")
    print("AUDIT SUMMARY")
    print(f"{'='*70}")
    passed = sum(1 for _, ok in results if ok)
    failed = sum(1 for _, ok in results if not ok)
    for fname, ok in results:
        status = "PASS" if ok else "FAIL"
        print(f"  {'✓' if ok else '✗'} {fname}: {status}")
    print(f"\n{passed} passed, {failed} failed out of {len(results)} APKGs")
    return failed == 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python verify.py <file.apkg>              # Verify single APKG (strict)")
        print("  python verify.py <file.apkg> --lenient     # Verify (NelsonChapter warn-only)")
        print("  python verify.py --audit <output_dir>      # Audit all APKGs in directory")
        sys.exit(1)

    if sys.argv[1] == '--audit':
        output_dir = sys.argv[2] if len(sys.argv) > 2 else 'output'
        strict = '--lenient' not in sys.argv
        ok = audit_all(output_dir, strict=strict)
        sys.exit(0 if ok else 1)
    else:
        strict = '--lenient' not in sys.argv
        ok = verify(sys.argv[1], strict=strict)
        sys.exit(0 if ok else 1)
