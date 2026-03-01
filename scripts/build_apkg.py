#!/usr/bin/env python3
"""
Build APKG from markdown cards. 7-field model with sub-decks.
Usage: python build_apkg.py <cards_md> <chapter_map_json> <output_apkg> <section_name_he>
"""

import genanki, re, json, hashlib, urllib.parse, warnings, os, sys, sqlite3, zipfile
warnings.filterwarnings("ignore")

MODEL_ID = 1607392322

QFMT = '''<div dir="rtl" style="text-align:right; font-family:'David','Arial Hebrew','Arial',sans-serif; font-size:20px; line-height:1.7; padding:20px;">
{{cloze:Text}}
</div>'''

AFMT = '''<div dir="rtl" style="text-align:right; font-family:'David','Arial Hebrew','Arial',sans-serif; font-size:20px; line-height:1.7; padding:20px;">
{{cloze:Text}}

{{#Extra}}
<div style="font-size:15px; color:#2d6a4f; background:#f0fdf4; border-right:3px solid #2d6a4f; padding:8px 12px; margin:12px 0; direction:rtl; text-align:right;">
💡 {{Extra}}
</div>
{{/Extra}}

<hr style="border:none; border-top:1px solid #ccc; margin:16px 0;">

<div style="font-size:14px; color:#555; direction:rtl; text-align:right; margin-bottom:6px;">
📌 {{Context}}
</div>

<div style="font-size:13px; color:#888; direction:ltr; text-align:left; margin-bottom:8px;">
📖 {{NelsonChapter}}
</div>

<div style="direction:ltr; text-align:left; font-size:13px;">
<span style="color:#999; font-family:Consolas,monospace;">{{SearchKeywords}}</span><br>
<a href="{{GoogleURL}}" style="color:#1a73e8; text-decoration:none;">🔍 Google</a>
{{#ChapterURL}}
&nbsp;|&nbsp;
<a href="{{ChapterURL}}" style="color:#34a853; text-decoration:none;">📗 Nelson Chapter</a>
{{/ChapterURL}}
</div>
</div>'''

CSS = '''.card {
    direction: rtl; text-align: right;
    font-family: 'David', 'Arial Hebrew', 'Noto Sans Hebrew', 'Arial', sans-serif;
    font-size: 20px; line-height: 1.7;
    max-width: 720px; margin: 0 auto; padding: 24px;
    color: #1a1a1a; background: #fafafa;
}
.card * { direction: rtl; text-align: right; }
.cloze { font-weight: bold; color: #0055bb; }
.nightMode .card { color: #e0e0e0; background: #1e1e1e; }
.nightMode .cloze { color: #5cb8ff; }'''

def build_model():
    return genanki.Model(
        MODEL_ID, 'Nelson Cloze v5',
        fields=[
            {'name': 'Text'}, {'name': 'Context'}, {'name': 'Extra'},
            {'name': 'NelsonChapter'}, {'name': 'SearchKeywords'},
            {'name': 'GoogleURL'}, {'name': 'ChapterURL'},
        ],
        templates=[{'name': 'Cloze', 'qfmt': QFMT, 'afmt': AFMT}],
        css=CSS,
        model_type=genanki.Model.CLOZE,
    )

def parse_cards(md_path):
    """Parse markdown cards into structured list."""
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Match: N. [עמ' XXX] body... optionally followed by > Extra: ...
    # Use \Z (end of string) not $ (end of line) so multi-line card bodies are captured fully
    card_pattern = re.compile(
        r'^(\d+)\.\s*\[עמ\'?\s*([\d\-]+)\]\s*(.*?)(?=\n\d+\.\s*\[עמ|\Z)',
        re.MULTILINE | re.DOTALL
    )
    cards = []
    for m in card_pattern.finditer(content):
        num, page, body = m.group(1), m.group(2), m.group(3).strip()

        # Extract Extra field (> Extra: ...)
        extra = ""
        extra_match = re.search(r'>\s*Extra:\s*(.+)', body)
        if extra_match:
            extra = extra_match.group(1).strip()
            body = body[:extra_match.start()].strip()

        # Extract keywords {curly braces} at end of body
        keywords = ""
        kw_match = re.search(r'\{([^}]+)\}\s*$', body)
        if kw_match:
            keywords = kw_match.group(1).strip()
            body = body[:kw_match.start()].strip()

        # Split title from body at first " - "
        parts = body.split(' - ', 1)
        title = parts[0].strip() if len(parts) > 1 else ""
        card_body = parts[1].strip() if len(parts) > 1 else body

        cards.append({
            'num': num, 'page': page.split('-')[0], 'title': title,
            'body': card_body, 'extra': extra, 'keywords': keywords
        })
    return cards

def build_chapter_lookup(chapter_map):
    """Build a reverse lookup from disease names/aliases to chapter info."""
    lookup = {}
    for key, info in chapter_map.items():
        if not isinstance(info, dict):
            continue
        # Add primary key and variants
        lookup[key] = info
        lookup[key.lower()] = info
        # Add with spaces instead of underscores (e.g. "cycling_neutropenia" -> "cycling neutropenia")
        spaced = key.replace('_', ' ')
        lookup[spaced] = info
        lookup[spaced.lower()] = info
        # Also title-case variant (e.g. "Cycling Neutropenia")
        lookup[spaced.title()] = info
        # Add name_he and name_en
        for name_field in ['name_he', 'name_en']:
            if info.get(name_field):
                lookup[info[name_field]] = info
                lookup[info[name_field].lower()] = info
        # Add topic_he directly
        if info.get('topic_he'):
            lookup[info['topic_he']] = info
            lookup[info['topic_he'].lower()] = info
        # Add aliases
        for alias in info.get('aliases', []):
            lookup[alias] = info
            lookup[alias.lower()] = info
        # Add sub_deck last part as lookup
        if info.get('sub_deck'):
            parts = info['sub_deck'].split('::')
            if len(parts) >= 3:
                lookup[parts[-1]] = info
                lookup[parts[-1].lower()] = info
    return lookup

def build_page_lookup(chapter_map):
    """Build a page number to chapter info lookup."""
    lookup = {}
    for key, info in chapter_map.items():
        if not isinstance(info, dict):
            continue
        for page in info.get('pages', []):
            if page not in lookup:
                lookup[page] = info
    return lookup

def find_chapter_info(disease, chapter_lookup, page=None, page_lookup=None):
    """Try multiple strategies to find chapter info for a disease name."""
    if not disease:
        if page and page_lookup and int(page) in page_lookup:
            return page_lookup[int(page)]
        return {}
    # Direct match
    if disease in chapter_lookup:
        return chapter_lookup[disease]
    if disease.lower() in chapter_lookup:
        return chapter_lookup[disease.lower()]
    # Try without spaces/underscores and vice versa
    normalized = disease.replace(' ', '_')
    if normalized in chapter_lookup:
        return chapter_lookup[normalized]
    if normalized.lower() in chapter_lookup:
        return chapter_lookup[normalized.lower()]
    # Try with underscores replaced by spaces
    spaced = disease.replace('_', ' ')
    if spaced in chapter_lookup:
        return chapter_lookup[spaced]
    if spaced.lower() in chapter_lookup:
        return chapter_lookup[spaced.lower()]
    # Try stripping parenthetical content: "Severe Congenital Neutropenia (Kostman)" -> "Severe Congenital Neutropenia"
    stripped = re.sub(r'\s*\([^)]*\)\s*', '', disease).strip()
    if stripped and stripped != disease:
        if stripped in chapter_lookup:
            return chapter_lookup[stripped]
        if stripped.lower() in chapter_lookup:
            return chapter_lookup[stripped.lower()]
        stripped_norm = stripped.replace(' ', '_').lower()
        if stripped_norm in chapter_lookup:
            return chapter_lookup[stripped_norm]
    # Try prefix match (disease name might be shorter than alias)
    for key, info in chapter_lookup.items():
        if isinstance(key, str) and key.startswith(disease):
            return info
        if isinstance(key, str) and disease.startswith(key) and len(key) > 3:
            return info
    # Try substring match in name_he
    for key, info in chapter_lookup.items():
        if isinstance(info, dict) and info.get('name_he'):
            if disease in info['name_he'] or info['name_he'] in disease:
                return info
    # Try matching partial words (e.g. "ASD Secundum" should match "ASD" alias)
    words = disease.replace('/', ' ').replace('-', ' ').split()
    for w in words:
        if len(w) >= 2 and w in chapter_lookup:
            return chapter_lookup[w]
    # Try matching first word if it's an abbreviation (>=2 chars, all caps)
    if words and len(words[0]) >= 2 and words[0].isupper() and words[0].isascii():
        if words[0] in chapter_lookup:
            return chapter_lookup[words[0]]
    # Fallback: match by page number
    if page and page_lookup:
        try:
            p = int(page)
            if p in page_lookup:
                return page_lookup[p]
        except ValueError:
            pass
    return {}

def build_apkg(cards, chapter_map, output_path, section_name_he, batch_id="batch"):
    model = build_model()

    # Build reverse lookup for chapter map
    chapter_lookup = build_chapter_lookup(chapter_map)
    page_lookup = build_page_lookup(chapter_map)

    # Create sub-decks per disease
    decks = {}  # disease_key → genanki.Deck
    default_deck_name = f"נלסון 21::{section_name_he}::כללי"

    total_clozes = 0
    max_clozes = 0
    violations = []
    ch_matched = 0
    ch_unmatched = []

    for card in cards:
        body = card['body'].replace('<', '&lt;').replace('>', '&gt;')

        # Convert **[...]** to cloze
        cloze_num = [0]
        def replace_cloze(m):
            cloze_num[0] += 1
            return '{{c' + str(cloze_num[0]) + '::' + m.group(1) + '}}'
        cloze_text = re.sub(r'\*\*\[([^\]]+)\]\*\*', replace_cloze, body)
        n_clozes = cloze_num[0]
        total_clozes += n_clozes
        max_clozes = max(max_clozes, n_clozes)

        if n_clozes > 5:
            violations.append(f"Card {card['num']}: {n_clozes} clozes (MAX 5!)")
            print(f"⚠️ Card {card['num']}: {n_clozes} clozes — SPLIT THIS CARD")

        if n_clozes == 0:
            print(f"⚠️ Card {card['num']}: 0 clozes — no blanks found, skipping")
            continue

        # Build Text field
        page = card['page']
        if card['title']:
            full_text = f"[עמ' {page}] {card['title']}<br><br>{cloze_text}"
        else:
            full_text = f"[עמ' {page}]<br><br>{cloze_text}"

        # Build Context
        disease = card['title'].split('—')[0].split('–')[0].strip() if card['title'] else ""
        subcategory = ""
        if '—' in card['title']:
            subcategory = card['title'].split('—')[1].strip()
        elif '–' in card['title']:
            subcategory = card['title'].split('–')[1].strip()
        context = ' | '.join([p for p in [disease, subcategory, f"עמ' {page}"] if p])

        # Build NelsonChapter + ChapterURL from chapter_map
        disease_key = disease.replace(' ', '_').split('(')[0].strip('_')
        page = card['page']
        ch_info = find_chapter_info(disease, chapter_lookup, page, page_lookup)
        if not ch_info:
            ch_info = find_chapter_info(disease_key, chapter_lookup, page, page_lookup)
        if not ch_info:
            # Try with full title (disease — subcategory)
            ch_info = find_chapter_info(card['title'], chapter_lookup, page, page_lookup)
        ch_parts = []
        chapter_url = ""
        if isinstance(ch_info, dict) and (ch_info.get('primary_chapter') or ch_info.get('related_chapters')):
            ch_matched += 1
            if ch_info.get('primary_chapter'):
                primary_title = ch_info.get('primary_chapter_title', '')
                ch_parts.append(f"Ch. {ch_info['primary_chapter']}" + (f" - {primary_title}" if primary_title else ""))
            for r in ch_info.get('related_chapter_titles', []):
                ch_parts.append(f"Ch. {r}")
            if not ch_parts and ch_info.get('related_chapters'):
                for r in ch_info['related_chapters']:
                    ch_parts.append(f"Ch. {r}")
            chapter_url = ch_info.get('chapter_url', '')
        else:
            ch_unmatched.append(f"Card {card['num']}: '{disease}'")
        nelson_chapter = ' | '.join([str(p) for p in ch_parts])

        # Build GoogleURL
        google_url = ""
        if card['keywords']:
            google_url = f"https://www.google.com/search?q={urllib.parse.quote(card['keywords'])}"

        # Determine sub-deck
        sub_deck_name = default_deck_name
        if isinstance(ch_info, dict) and ch_info.get('sub_deck'):
            sub_deck_name = ch_info['sub_deck']
        elif disease:
            sub_deck_name = f"נלסון 21::{section_name_he}::{disease}"

        # Get or create deck
        if sub_deck_name not in decks:
            import random
            deck_id = random.randrange(1 << 30, 1 << 31)
            decks[sub_deck_name] = genanki.Deck(deck_id, sub_deck_name)
        deck = decks[sub_deck_name]

        # Create note
        guid = hashlib.md5(f"nelson_v5_{batch_id}_{card['num']}_{page}".encode()).hexdigest()[:10]
        note = genanki.Note(
            model=model,
            fields=[full_text, context, card['extra'], nelson_chapter, card['keywords'], google_url, chapter_url],
            tags=[f"disease::{disease_key}", f"category::{subcategory.replace(' ', '_')}", f"page::{page}"],
            guid=guid,
        )
        deck.add_note(note)

    # Build package with all sub-decks
    all_decks = list(decks.values())
    if not all_decks:
        print("❌ No cards parsed! Check markdown format.")
        return False

    pkg = genanki.Package(all_decks)
    pkg.write_to_file(output_path)

    # Statistics
    notes_count = sum(len(d.notes) for d in all_decks)
    print(f"\n{'='*50}")
    print(f"Notes: {notes_count}")
    print(f"Total cloze deletions: {total_clozes}")
    print(f"Avg clozes/note: {total_clozes/notes_count:.1f}" if notes_count else "N/A")
    print(f"Max clozes on single note: {max_clozes}")
    print(f"Sub-decks: {len(all_decks)}")
    for d in all_decks:
        print(f"  {d.name}: {len(d.notes)} notes")
    print(f"File: {output_path} ({os.path.getsize(output_path)/1024:.1f} KB)")

    print(f"Chapter map matches: {ch_matched}/{notes_count}")
    if ch_unmatched:
        print(f"Unmatched diseases ({len(ch_unmatched)}):")
        for u in ch_unmatched[:20]:
            print(f"  {u}")
        if len(ch_unmatched) > 20:
            print(f"  ... and {len(ch_unmatched)-20} more")

    if violations:
        print(f"\n❌ VALIDATION FAILED: {len(violations)} notes exceed 5 clozes:")
        for v in violations:
            print(f"  {v}")
        return False
    else:
        print(f"\n✅ PASSED: All notes ≤5 clozes")
        return True

def verify_apkg(apkg_path):
    """Verify APKG structure and content."""
    import tempfile
    tmpdir = tempfile.mkdtemp()
    with zipfile.ZipFile(apkg_path, 'r') as z:
        z.extractall(tmpdir)

    db_path = os.path.join(tmpdir, 'collection.anki2')
    db = sqlite3.connect(db_path)
    cur = db.cursor()

    cur.execute("SELECT COUNT(*) FROM notes")
    n_notes = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM cards")
    n_cards = cur.fetchone()[0]

    # Verify 7-field model
    cur.execute("SELECT models FROM col")
    models = json.loads(cur.fetchone()[0])
    expected_fields = ['Text', 'Context', 'Extra', 'NelsonChapter', 'SearchKeywords', 'GoogleURL', 'ChapterURL']

    for mid, m in models.items():
        field_names = [f['name'] for f in m['flds']]
        print(f"\nModel: {m['name']}")
        print(f"Fields: {field_names}")
        assert field_names == expected_fields, f"Field mismatch! Expected {expected_fields}, got {field_names}"
        assert 'Context' not in m['tmpls'][0]['qfmt'], "Context should NOT be on front!"
        assert 'Extra' not in m['tmpls'][0]['qfmt'], "Extra should NOT be on front!"
        assert 'ChapterURL' in m['tmpls'][0]['afmt'], "ChapterURL missing from back!"
        assert 'GoogleURL' in m['tmpls'][0]['afmt'], "GoogleURL missing from back!"

    # Sample notes
    cur.execute("SELECT flds FROM notes LIMIT 3")
    for i, row in enumerate(cur.fetchall()):
        parts = row[0].split('\x1f')
        print(f"\n--- Sample Note {i+1} ---")
        for j, name in enumerate(expected_fields):
            val = parts[j] if j < len(parts) else "(MISSING)"
            print(f"  {name}: {val[:120]}{'...' if len(val)>120 else ''}")

    # Check max clozes across all notes
    cur.execute("SELECT flds FROM notes")
    max_seen = 0
    for row in cur.fetchall():
        text = row[0].split('\x1f')[0]
        n = len(re.findall(r'\{\{c\d+::', text))
        max_seen = max(max_seen, n)

    db.close()
    print(f"\n✅ VERIFIED: {n_notes} notes → {n_cards} cards")
    print(f"Max clozes in any note: {max_seen}")
    if max_seen > 5:
        print(f"❌ WARNING: {max_seen} clozes found — exceeds limit!")
        return False
    return True

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python build_apkg.py <cards.md> <chapter_map.json> <output.apkg> <section_name_he> [batch_id]")
        sys.exit(1)

    cards_md = sys.argv[1]
    chapter_map_path = sys.argv[2]
    output_apkg = sys.argv[3]
    section_he = sys.argv[4]
    batch_id = sys.argv[5] if len(sys.argv) > 5 else "batch"

    with open(chapter_map_path, 'r', encoding='utf-8') as f:
        cmap_data = json.load(f)
    chapter_map = cmap_data.get('diseases', cmap_data)

    cards = parse_cards(cards_md)
    print(f"Parsed {len(cards)} cards from {cards_md}")

    success = build_apkg(cards, chapter_map, output_apkg, section_he, batch_id)
    if success:
        print("\nRunning APKG verification...")
        verify_apkg(output_apkg)
    else:
        print("\n❌ Build failed validation. Fix issues and re-run.")
        sys.exit(1)
