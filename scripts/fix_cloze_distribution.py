#!/usr/bin/env python3
"""
Fix cloze distribution in APKGs by surgically removing excess cloze
wrappers from notes that have too many. Removes the highest-numbered
cloze deletion from selected notes, keeping the answer text visible.
Also deletes the corresponding card from the cards table.

Usage: python fix_cloze_distribution.py
"""

import sqlite3, zipfile, json, re, os, sys, shutil, tempfile, io

# Force UTF-8 output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

OUTPUT_DIR = "output"
BACKUP_DIR = os.path.join(OUTPUT_DIR, "backup_cloze_fix")

# Define what needs fixing for each APKG
FIXES = {
    "batch2a_neurology_p1.apkg": {
        # First reduce 5-cloze notes to 4 (to get ≤20% at 5-cloze)
        # Then reduce 4-cloze notes to 3 (to get ≥50% at ≤3)
        "reduce_from_5": 17,  # 5→4 clozes
        "reduce_from_4": 15,  # 4→3 clozes
    },
    "batch2b_neurology_p2_redo.apkg": {
        "reduce_from_5": 0,
        "reduce_from_4": 45,  # 4→3 clozes
    },
    "batch3b_cardiology_p2_redo.apkg": {
        "reduce_from_5": 0,
        "reduce_from_4": 8,  # 4→3 clozes
    },
    "batch5b_immunology_p2_redo.apkg": {
        "reduce_from_5": 0,
        "reduce_from_4": 10,  # 4→3 clozes
    },
}


def remove_highest_cloze(text, target_cloze_num):
    """
    Remove the {{cN::answer}} wrapper for the highest cloze number,
    keeping the answer text visible. Also handles hints: {{cN::answer::hint}}.

    target_cloze_num: the cloze number to remove (e.g., 5 for {{c5::...}})
    """
    # Pattern matches {{cN::answer}} or {{cN::answer::hint}}
    pattern = r'\{\{c' + str(target_cloze_num) + r'::(.*?)(?:::.*?)?\}\}'

    def replace_fn(m):
        # Return just the answer text (group 1), without the cloze wrapper
        return m.group(1)

    new_text = re.sub(pattern, replace_fn, text)
    return new_text


def fix_apkg(apkg_path, reduce_from_5, reduce_from_4):
    """Fix cloze distribution in a single APKG."""
    fname = os.path.basename(apkg_path)
    print(f"\n{'='*60}")
    print(f"Fixing: {fname}")
    print(f"  Reduce from 5 clozes: {reduce_from_5} notes")
    print(f"  Reduce from 4 clozes: {reduce_from_4} notes")
    print(f"{'='*60}")

    # Backup
    os.makedirs(BACKUP_DIR, exist_ok=True)
    backup_path = os.path.join(BACKUP_DIR, fname)
    if not os.path.exists(backup_path):
        shutil.copy2(apkg_path, backup_path)
        print(f"  Backed up to {backup_path}")

    # Extract APKG
    tmpdir = tempfile.mkdtemp()
    with zipfile.ZipFile(apkg_path, 'r') as z:
        z.extractall(tmpdir)

    db_path = os.path.join(tmpdir, 'collection.anki2')
    db = sqlite3.connect(db_path)
    cur = db.cursor()

    # Get all notes with their cloze counts
    cur.execute("SELECT id, flds FROM notes")
    notes = []
    for nid, flds in cur.fetchall():
        text = flds.split('\x1f')[0]
        n_clozes = len(re.findall(r'\{\{c\d+::', text))
        notes.append((nid, flds, text, n_clozes))

    total_fixed = 0
    cards_deleted = 0

    # Step 1: Reduce 5-cloze notes → 4-cloze
    if reduce_from_5 > 0:
        five_cloze_notes = [(nid, flds, text, n) for nid, flds, text, n in notes if n == 5]
        to_fix = five_cloze_notes[:reduce_from_5]
        print(f"\n  Step 1: Reducing {len(to_fix)} notes from 5→4 clozes")

        for nid, flds, text, _ in to_fix:
            new_text = remove_highest_cloze(text, 5)
            new_flds = new_text + flds[len(text):]  # Keep other fields intact
            cur.execute("UPDATE notes SET flds = ? WHERE id = ?", (new_flds, nid))

            # Delete the card for ord=4 (cloze 5, 0-indexed)
            cur.execute("DELETE FROM cards WHERE nid = ? AND ord = 4", (nid,))
            deleted = cur.rowcount
            cards_deleted += deleted
            total_fixed += 1

        print(f"    Fixed {len(to_fix)} notes, deleted {cards_deleted} cards")

    # Step 2: Reduce 4-cloze notes → 3-cloze
    if reduce_from_4 > 0:
        # Re-query to account for any 5→4 changes
        cur.execute("SELECT id, flds FROM notes")
        notes2 = []
        for nid, flds in cur.fetchall():
            text = flds.split('\x1f')[0]
            n_clozes = len(re.findall(r'\{\{c\d+::', text))
            notes2.append((nid, flds, text, n_clozes))

        four_cloze_notes = [(nid, flds, text, n) for nid, flds, text, n in notes2 if n == 4]
        to_fix = four_cloze_notes[:reduce_from_4]
        print(f"\n  Step 2: Reducing {len(to_fix)} notes from 4→3 clozes")

        step2_cards = 0
        for nid, flds, text, _ in to_fix:
            new_text = remove_highest_cloze(text, 4)
            new_flds = new_text + flds[len(text):]
            cur.execute("UPDATE notes SET flds = ? WHERE id = ?", (new_flds, nid))

            # Delete the card for ord=3 (cloze 4, 0-indexed)
            cur.execute("DELETE FROM cards WHERE nid = ? AND ord = 3", (nid,))
            deleted = cur.rowcount
            step2_cards += deleted
            cards_deleted += deleted
            total_fixed += 1

        print(f"    Fixed {len(to_fix)} notes, deleted {step2_cards} cards")

    db.commit()

    # Verify the new distribution
    cur.execute("SELECT id, flds FROM notes")
    new_dist = {}
    for nid, flds in cur.fetchall():
        text = flds.split('\x1f')[0]
        n = len(re.findall(r'\{\{c\d+::', text))
        new_dist[n] = new_dist.get(n, 0) + 1

    total = sum(new_dist.values())
    le3 = sum(v for k, v in new_dist.items() if k <= 3)
    eq5 = new_dist.get(5, 0)

    cur.execute("SELECT COUNT(*) FROM cards")
    n_cards = cur.fetchone()[0]

    print(f"\n  New distribution (total {total} notes, {n_cards} cards):")
    for k in sorted(new_dist.keys()):
        print(f"    {k} clozes: {new_dist[k]} notes ({new_dist[k]/total*100:.0f}%)")
    print(f"  <=3 clozes: {le3}/{total} ({le3/total*100:.1f}%) {'PASS' if le3/total >= 0.5 else 'FAIL'}")
    print(f"  =5 clozes: {eq5}/{total} ({eq5/total*100:.1f}%) {'PASS' if eq5/total <= 0.2 else 'FAIL'}")

    db.close()

    # Repackage APKG
    with zipfile.ZipFile(apkg_path, 'w', zipfile.ZIP_DEFLATED) as zout:
        for root, dirs, files in os.walk(tmpdir):
            for f in files:
                full = os.path.join(root, f)
                arcname = os.path.relpath(full, tmpdir)
                zout.write(full, arcname)

    print(f"\n  Total: {total_fixed} notes fixed, {cards_deleted} cards removed")
    print(f"  Saved: {apkg_path}")

    # Cleanup
    shutil.rmtree(tmpdir, ignore_errors=True)

    return le3/total >= 0.5 and eq5/total <= 0.2


def main():
    all_pass = True
    for fname, fix_spec in FIXES.items():
        apkg_path = os.path.join(OUTPUT_DIR, fname)
        if not os.path.exists(apkg_path):
            print(f"WARNING: {apkg_path} not found, skipping")
            continue

        ok = fix_apkg(
            apkg_path,
            reduce_from_5=fix_spec["reduce_from_5"],
            reduce_from_4=fix_spec["reduce_from_4"],
        )
        if not ok:
            print(f"  WARNING: {fname} still doesn't pass after fix!")
            all_pass = False

    print(f"\n{'='*60}")
    if all_pass:
        print("ALL FIXES APPLIED SUCCESSFULLY")
    else:
        print("SOME FIXES DID NOT ACHIEVE TARGET — manual review needed")
    print(f"{'='*60}")

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
