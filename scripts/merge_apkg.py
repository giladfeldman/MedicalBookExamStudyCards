#!/usr/bin/env python3
"""
Merge all Nelson APKG files into a single combined deck.

Zero dependencies — uses only Python standard library (zipfile, sqlite3, json).
APKG files are ZIP archives containing a SQLite database (collection.anki2)
and a media mapping file.

Usage:
    python scripts/merge_apkg.py
    python scripts/merge_apkg.py --output output/nelson_complete.apkg
    python scripts/merge_apkg.py --input-dir output --output my_deck.apkg
"""

import zipfile
import sqlite3
import json
import os
import sys
import tempfile
import shutil
import argparse


def extract_apkg(apkg_path, dest_dir):
    """Extract an APKG (ZIP) file to a directory. Returns path to the SQLite db."""
    with zipfile.ZipFile(apkg_path, 'r') as z:
        z.extractall(dest_dir)
    db_path = os.path.join(dest_dir, 'collection.anki2')
    if not os.path.exists(db_path):
        # Some APKG versions use 'collection.anki21'
        alt = os.path.join(dest_dir, 'collection.anki21')
        if os.path.exists(alt):
            db_path = alt
    return db_path


def merge_apkgs(input_dir, output_path):
    """Merge all .apkg files in input_dir into a single output .apkg."""
    # Collect all APKG files, excluding the output file itself
    output_basename = os.path.basename(output_path)
    apkg_files = sorted([
        os.path.join(input_dir, f)
        for f in os.listdir(input_dir)
        if f.endswith('.apkg') and f != output_basename
    ])

    if not apkg_files:
        print("ERROR: No .apkg files found in", input_dir)
        sys.exit(1)

    print(f"Found {len(apkg_files)} APKG files to merge\n")

    # Create temp working directory
    tmpdir = tempfile.mkdtemp(prefix='anki_merge_')

    try:
        # --- Step 1: Extract the first APKG as our base ---
        base_dir = os.path.join(tmpdir, 'base')
        os.makedirs(base_dir)
        base_db_path = extract_apkg(apkg_files[0], base_dir)

        conn = sqlite3.connect(base_db_path)
        conn.execute("PRAGMA journal_mode=WAL")

        # Get existing GUIDs to deduplicate
        existing_guids = set(
            row[0] for row in conn.execute("SELECT guid FROM notes")
        )
        # Get existing note IDs (needed to link cards)
        existing_note_ids = set(
            row[0] for row in conn.execute("SELECT id FROM notes")
        )
        existing_card_ids = set(
            row[0] for row in conn.execute("SELECT id FROM cards")
        )

        # Load base deck definitions
        base_decks = json.loads(
            conn.execute("SELECT decks FROM col").fetchone()[0]
        )
        base_models = json.loads(
            conn.execute("SELECT models FROM col").fetchone()[0]
        )

        n_base_notes = len(existing_guids)
        n_base_cards = len(existing_card_ids)
        print(f"  Base: {os.path.basename(apkg_files[0])} "
              f"({n_base_notes} notes, {n_base_cards} cards)")

        total_notes = n_base_notes
        total_cards = n_base_cards
        skipped_dupes = 0

        # --- Step 2: Merge each subsequent APKG ---
        for apkg_path in apkg_files[1:]:
            merge_dir = os.path.join(tmpdir, 'merge_tmp')
            os.makedirs(merge_dir, exist_ok=True)

            try:
                merge_db_path = extract_apkg(apkg_path, merge_dir)
                merge_conn = sqlite3.connect(merge_db_path)

                # Merge deck definitions
                merge_decks = json.loads(
                    merge_conn.execute("SELECT decks FROM col").fetchone()[0]
                )
                for deck_id, deck_info in merge_decks.items():
                    if deck_id not in base_decks:
                        base_decks[deck_id] = deck_info

                # Merge model definitions
                merge_models = json.loads(
                    merge_conn.execute("SELECT models FROM col").fetchone()[0]
                )
                for model_id, model_info in merge_models.items():
                    if model_id not in base_models:
                        base_models[model_id] = model_info

                # Merge notes (deduplicate by GUID)
                new_notes = 0
                batch_dupes = 0
                notes = merge_conn.execute("SELECT * FROM notes").fetchall()
                note_col_count = len(notes[0]) if notes else 0

                for note in notes:
                    guid = note[1]  # guid is column index 1
                    if guid in existing_guids:
                        batch_dupes += 1
                        continue
                    placeholders = ','.join(['?'] * len(note))
                    conn.execute(f"INSERT INTO notes VALUES ({placeholders})", note)
                    existing_guids.add(guid)
                    existing_note_ids.add(note[0])
                    new_notes += 1

                # Merge cards (only if their note exists in merged db)
                new_cards = 0
                cards = merge_conn.execute("SELECT * FROM cards").fetchall()

                for card in cards:
                    card_id = card[0]
                    nid = card[1]  # note id is column index 1
                    if card_id in existing_card_ids:
                        continue
                    if nid not in existing_note_ids:
                        continue
                    placeholders = ','.join(['?'] * len(card))
                    conn.execute(f"INSERT INTO cards VALUES ({placeholders})", card)
                    existing_card_ids.add(card_id)
                    new_cards += 1

                merge_conn.close()

                total_notes += new_notes
                total_cards += new_cards
                skipped_dupes += batch_dupes

                status = f"{new_notes} notes, {new_cards} cards"
                if batch_dupes:
                    status += f" ({batch_dupes} dupes skipped)"
                print(f"  + {os.path.basename(apkg_path)}: {status}")

            finally:
                shutil.rmtree(merge_dir, ignore_errors=True)

        # --- Step 3: Update the col table with merged decks/models ---
        conn.execute("UPDATE col SET decks = ?", [json.dumps(base_decks)])
        conn.execute("UPDATE col SET models = ?", [json.dumps(base_models)])
        conn.commit()
        conn.close()

        # --- Step 4: Package into output APKG ---
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as z:
            z.write(base_db_path, 'collection.anki2')
            # Write media file (empty — our cards have no media)
            media_src = os.path.join(base_dir, 'media')
            if os.path.exists(media_src):
                z.write(media_src, 'media')
            else:
                media_tmp = os.path.join(tmpdir, 'media')
                with open(media_tmp, 'w') as f:
                    json.dump({}, f)
                z.write(media_tmp, 'media')

        # --- Done ---
        print(f"\n{'='*50}")
        print(f"Merged APKG: {output_path}")
        print(f"Total: {total_notes} notes, {total_cards} cards")
        if skipped_dupes:
            print(f"Duplicates skipped: {skipped_dupes}")
        size_mb = os.path.getsize(output_path) / (1024 * 1024)
        print(f"File size: {size_mb:.1f} MB")
        print(f"{'='*50}")

    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Merge all Nelson APKG files into a single deck'
    )
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    default_input = os.path.join(project_dir, 'output')
    default_output = os.path.join(project_dir, 'output', 'nelson_complete.apkg')

    parser.add_argument('--input-dir', default=default_input,
                        help='Directory containing .apkg files')
    parser.add_argument('--output', default=default_output,
                        help='Output path for merged .apkg')
    args = parser.parse_args()

    merge_apkgs(args.input_dir, args.output)
