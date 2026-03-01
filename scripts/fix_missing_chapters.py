#!/usr/bin/env python3
"""
Fix APKG files that have notes missing NelsonChapter and ChapterURL fields.

Strategy:
1. Parse disease names and page numbers from each note's Text field
2. Map each disease to a Nelson chapter using a comprehensive lookup table
3. Build ChapterURL from pdf_filenames.txt
4. Update the SQLite DB inside each APKG
5. Repackage as APKG
"""

import sqlite3, zipfile, tempfile, os, sys, re, shutil, json, io, urllib.parse

# Force UTF-8 output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_DIR = os.path.join(BASE_DIR, 'input')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')

# ═══════════════════════════════════════════════════════════════════
# STEP 1: Build chapter number → PDF filename mapping
# ═══════════════════════════════════════════════════════════════════

def build_pdf_filename_map():
    """Parse pdf_filenames.txt to get chapter_number -> filename."""
    pdf_map = {}
    with open(os.path.join(INPUT_DIR, 'pdf_filenames.txt'), 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # Pattern: "Chapter NNN - Title.pdf" or "Chapter NNN – Title.pdf" or "Part XX - Title.pdf"
            m = re.match(r'Chapter\s+(\d+)\s*[-–—]\s*(.+?)\.pdf', line, re.IGNORECASE)
            if m:
                ch_num = int(m.group(1))
                pdf_map[ch_num] = line
            # Also handle "Part XX" entries
            m2 = re.match(r'(Part\s+\d+\S*)\s*[-–—]\s*(.+?)\.pdf', line, re.IGNORECASE)
            if m2:
                pdf_map[m2.group(1)] = line
    return pdf_map


def make_chapter_url(pdf_filename):
    """Build a Google Drive search URL for a PDF filename."""
    if not pdf_filename:
        return ""
    encoded = urllib.parse.quote(pdf_filename)
    return f"https://drive.google.com/drive/search?q={encoded}"


# Fallback: for chapters that don't have their own PDF, use closest related chapter PDF
CHAPTER_PDF_FALLBACK = {
    # Ch. 165 (Primary Defects of Cellular Immunity) → use Ch. 164 (Orientation to Inborn Errors of Immunity)
    165: 164,
    # Ch. 170 (The Complement System) → use Ch. 168 (Neutrophils - same Part XIV section)
    170: 168,
    # Ch. 174 (Immune Dysregulation) → use Ch. 164 (Orientation)
    174: 164,
    # Ch. 185 (Childhood Asthma) → use Ch. 184 (Allergic Rhinitis - same section)
    185: 184,
    # Ch. 186 (Adverse Reactions to Foods) → use Ch. 187 (Insect Allergy - same section)
    186: 187,
    # Ch. 188 (Ocular Allergies) → use Ch. 187 (Insect Allergy)
    188: 187,
    # Ch. 189 (Urticaria and Angioedema) → use Ch. 190 (Anaphylaxis)
    189: 190,
}


# ═══════════════════════════════════════════════════════════════════
# STEP 2: Build comprehensive disease → chapter mapping
# ═══════════════════════════════════════════════════════════════════

def build_disease_chapter_map(pdf_map):
    """
    Build a comprehensive mapping of disease/topic keywords to Nelson chapters.
    This uses the PDF page ranges from the source PDF to determine which
    Nelson chapter each disease belongs to.

    Page ranges in the source PDF:
    - Pages 73-83: Cardiovascular (Nelson Part XVIII, Chapters 469-494)
    - Pages 84-95: Pulmonary (Nelson Part XVII, Chapters 421-468)
    - Pages 96-103: Allergy & Immunology (Nelson Part XV, Chapters 182-193)
    - Pages 104-111: Immunodeficiency (Nelson Chapters 164-181)
    - Pages 112-123: Hematology (Nelson Part XIX, Chapters 495-536)
    - Pages 124-137: Oncology (Nelson Part XX, Chapters 540-556)
    """

    # Manual mapping: disease name (from Text field) → (chapter_num, chapter_title)
    # We'll build this based on the specific diseases found in the affected notes

    disease_map = {}

    # ─── BATCH 5a: Allergy (pages 96-103) ───
    # Allergy chapters: 182-193
    allergy_topics = {
        # Sleep topics on page 96 (these are Nelson Ch. 31 - Sleep Medicine)
        'פראסומניות': (31, 'Sleep Medicine'),
        'OSAS': (31, 'Sleep Medicine'),
        'CCHS': (31, 'Sleep Medicine'),

        # Asthma - Ch. 185
        'אסטמה': (185, 'Childhood Asthma'),
        'asthma': (185, 'Childhood Asthma'),

        # Allergy diagnosis - Ch. 183
        'אבחון אלרגיה': (183, 'Diagnosis of Allergic Disease'),

        # Allergic rhinitis - Ch. 184
        'נזלת אלרגית': (184, 'Allergic Rhinitis'),
        'רינוקונגונקטיביטיס': (184, 'Allergic Rhinitis'),

        # Food allergy - Ch. 186 (Adverse Reactions to Foods)
        'אלרגיה למזון': (186, 'Adverse Reactions to Foods'),
        'אלרגיה למזון IgE': (186, 'Adverse Reactions to Foods'),
        'אלרגיה למזון Non-IgE': (186, 'Adverse Reactions to Foods'),
        'אלרגיה למזונות': (186, 'Adverse Reactions to Foods'),
        'Food Allergy IgE-mediated': (186, 'Adverse Reactions to Foods'),
        'Food Intolerance': (186, 'Adverse Reactions to Foods'),
        'FPIES': (186, 'Adverse Reactions to Foods'),
        'Food Protein Induced Proctocolitis': (186, 'Adverse Reactions to Foods'),
        'EoE': (370, 'Eosinophilic Esophagitis, Pill Esophagitis, and Infective Esophagitis'),
        'Eosinophilic Gastroenteritis': (383, 'Eosinophilic Gastroenteritis'),

        # Insect allergy - Ch. 187
        'אלרגיה לחרקים': (187, 'Insect Allergy'),

        # Ocular allergies - Ch. 188
        'אלרגיות עיניים': (188, 'Ocular Allergies'),
        'Allergic Conjunctivitis': (188, 'Ocular Allergies'),
        'Vernal Keratoconjunctivitis': (188, 'Ocular Allergies'),

        # Urticaria/Angioedema - Ch. 189
        'אורטיקריה': (189, 'Urticaria (Hives) and Angioedema'),
        'אורטיקריה אקוטית': (189, 'Urticaria (Hives) and Angioedema'),
        'אורטיקריה כרונית': (189, 'Urticaria (Hives) and Angioedema'),
        'HAE': (189, 'Urticaria (Hives) and Angioedema'),

        # Anaphylaxis - Ch. 190
        'אנפילקסיס': (190, 'Anaphylaxis'),

        # Serum sickness - Ch. 191
        'Serum Sickness': (191, 'Serum Sickness'),
        'Serum Sickness-like Reaction': (191, 'Serum Sickness'),

        # Drug allergy - Ch. 193
        'אלרגיה לתרופות': (193, 'Adverse and Allergic Reactions to Drugs'),
        'DRESS': (193, 'Adverse and Allergic Reactions to Drugs'),
        'Red Man Syndrome': (193, 'Adverse and Allergic Reactions to Drugs'),
        'אלרגיה לבטא-לקטמים': (193, 'Adverse and Allergic Reactions to Drugs'),
        'אלרגיה לביצים וחיסונים': (193, 'Adverse and Allergic Reactions to Drugs'),

        # Allergic basis - Ch. 182
        'רינוסינוסיטיס אלרגית': (184, 'Allergic Rhinitis'),
    }
    disease_map.update(allergy_topics)

    # ─── BATCH 5b: Immunodeficiency (pages 104-111) ───
    # Primary immunodeficiency chapters: 164-181
    immunodeficiency_topics = {
        # Orientation - Ch. 164
        'בירור חסר חיסוני': (164, 'Orientation to the Consideration of Inborn Errors of Immunity'),
        'הערכת מערכת חיסונית הומורלית': (164, 'Orientation to the Consideration of Inborn Errors of Immunity'),

        # T-cell defects - Ch. 165 (Primary Defects of Cellular Immunity)
        'SCID': (165, 'Primary Defects of Cellular Immunity'),
        'DiGeorge': (165, 'Primary Defects of Cellular Immunity'),
        'DiGeorge (22q11.2 Deletion)': (165, 'Primary Defects of Cellular Immunity'),

        # B-cell / Antibody deficiencies - Ch. 166
        'XLA': (166, 'B-Cell and Antibody Deficiencies'),
        'XLA (ברוטון)': (166, 'B-Cell and Antibody Deficiencies'),
        'CVID': (166, 'B-Cell and Antibody Deficiencies'),
        'IgA Deficiency': (166, 'B-Cell and Antibody Deficiencies'),
        'Selective IgA Deficiency': (166, 'B-Cell and Antibody Deficiencies'),
        'IgG Subclass Deficiency והיפוגמאגלובולינמיה חולפת': (166, 'B-Cell and Antibody Deficiencies'),
        'Hyper-IgM (XL)': (166, 'B-Cell and Antibody Deficiencies'),
        'Hyper-IgM (AR)': (166, 'B-Cell and Antibody Deficiencies'),
        'הפרעות בייצור נוגדנים': (166, 'B-Cell and Antibody Deficiencies'),

        # NK cells - Ch. 167
        # Ch. 167 is NK cells

        # Neutrophils - Ch. 168
        'CGD': (168, 'Neutrophils'),
        'LAD': (168, 'Neutrophils'),
        'Chediak-Higashi': (168, 'Neutrophils'),

        # Complement - Ch. 170 (The Complement System)
        'Hereditary Angioedema': (170, 'The Complement System'),
        'חסרי משלים': (170, 'The Complement System'),

        # Leukopenia - Ch. 171
        # Leukocytosis - Ch. 172

        # Combined immunodeficiencies
        'WAS': (165, 'Primary Defects of Cellular Immunity'),
        'Ataxia-Telangiectasia': (165, 'Primary Defects of Cellular Immunity'),
        'Hyper-IgE Syndrome': (165, 'Primary Defects of Cellular Immunity'),
        'XLP': (165, 'Primary Defects of Cellular Immunity'),
        'ALPS': (174, 'Immune Dysregulation'),
        'IPEX': (174, 'Immune Dysregulation'),
        'DADA2': (174, 'Immune Dysregulation'),
        'APECED': (174, 'Immune Dysregulation'),
        'CMC ו-APECED': (174, 'Immune Dysregulation'),

        # Innate immunity - Ch. 175
        'חסרי חיסון מולדים': (175, 'Defects of Innate Immunity'),

        # HSCT - Ch. 177
        'השתלת מח עצם': (177, 'Principles and Clinical Indications of Hematopoietic Stem Cell Transplantation'),

        # Food protein enteropathy (GI manifestation)
        'אנטרופתיה ע"ר חלבוני מזון': (186, 'Adverse Reactions to Foods'),
        'FPIES': (186, 'Adverse Reactions to Foods'),
        'גסטרואנטרופתיות אאוזינופיליות': (383, 'Eosinophilic Gastroenteritis'),

        # General evaluation
        'פגמים במערכת החיסון': (164, 'Orientation to the Consideration of Inborn Errors of Immunity'),
        'חסר חיסוני ראשוני': (164, 'Orientation to the Consideration of Inborn Errors of Immunity'),
    }
    disease_map.update(immunodeficiency_topics)

    # ─── BATCH 4: Pulmonology (pages 84-95) ───
    # Respiratory chapters: 421-468
    pulm_topics = {
        # Upper airway
        'לרינגומלציה': (434, 'Congenital Anomalies of the Larynx, Trachea, and Bronchi'),
        'היצרות סב-גלוטית': (436, 'Laryngotracheal Stenosis and Subglottic Stenosis'),
        'המנגיומה סב-גלוטית': (436, 'Laryngotracheal Stenosis and Subglottic Stenosis'),
        'שיתוך מיתר קול': (434, 'Congenital Anomalies of the Larynx, Trachea, and Bronchi'),
        'שיתוק מיתר קול': (434, 'Congenital Anomalies of the Larynx, Trachea, and Bronchi'),

        # Alpha-1 antitrypsin
        'חסר α1AT': (442, 'Alpha-1 Antitrypsin Deficiency and Emphysema'),

        # CLE = Congenital Lobar Emphysema
        'CLE': (444, 'Congenital Disorders of the Lung'),

        # Pleural effusion/empyema
        'תפליט פלאורלי': (451, 'Pleurisy, Pleural Effusions, and Empyema'),
        'אמפיימה': (451, 'Pleurisy, Pleural Effusions, and Empyema'),

        # Bronchiolitis obliterans
        'BO': (443, 'Other Distal Airway Diseases'),
        'BO/BOOP': (443, 'Other Distal Airway Diseases'),
        'BOOP/COP': (443, 'Other Distal Airway Diseases'),
        'BOS': (443, 'Other Distal Airway Diseases'),

        # Eosinophilic lung disease
        'Acute Eosinophilic Pneumonia': (448, 'Immune and Inflammatory Lung Disease'),
        'Chronic Eosinophilic Pneumonia': (448, 'Immune and Inflammatory Lung Disease'),
        'Lofler Syndrome': (448, 'Immune and Inflammatory Lung Disease'),

        # SJMS = Swyer-James-MacLeod Syndrome
        'SJMS': (452, 'Bronchiectasis'),

        # Pericarditis topics (on page ~92 of pulmonary section — actually cardiovascular overlap)
        'פריקרדיטיס אקוטית': (489, 'Diseases of the Pericardium'),
        'פריקרדיטיס קונסטריקטיבית': (489, 'Diseases of the Pericardium'),
        'Pericardiotomy Syndrome': (489, 'Diseases of the Pericardium'),
    }
    disease_map.update(pulm_topics)

    # ─── BATCH 6a: Hematology (page 119) ───
    # Hematology chapters: 495-536
    heme_topics = {
        'הערכת אנמיה': (495, 'Development of the Hematopoietic System'),
        'מורפולוגיית משטח דם': (495, 'Development of the Hematopoietic System'),
    }
    disease_map.update(heme_topics)

    # ─── BATCH 7: Oncology (page 129) ───
    # Oncology chapters: 540-556 / Spleen: 534-536
    onc_topics = {
        'ספלנומגליה': (535, 'Splenomegaly'),
    }
    disease_map.update(onc_topics)

    # ─── BATCH 3b: Cardiology (page 80) ───
    # Cardiovascular chapters: 469-494
    cardio_topics = {
        'Vascular Rings': (481, 'Other Congenital Heart and Vascular Malformations'),
    }
    disease_map.update(cardio_topics)

    return disease_map


# ═══════════════════════════════════════════════════════════════════
# STEP 3: Page-based fallback mapping
# ═══════════════════════════════════════════════════════════════════

def build_page_fallback_map():
    """
    Fallback: if disease name doesn't match, use page number to determine
    the most likely Nelson chapter section.
    """
    page_map = {
        # Pages 96-97: Sleep Medicine → Ch. 31
        96: (31, 'Sleep Medicine'),
        97: (31, 'Sleep Medicine'),
        # Pages 97-98: Allergy overview → Ch. 182
        98: (182, 'Allergy and the Immunologic Basis of Atopic Disease'),
        # Pages 98-99: Asthma → Ch. 185
        99: (185, 'Childhood Asthma'),
        # Pages 99-100: Allergic rhinitis + Food allergy → Ch. 184/186
        100: (186, 'Adverse Reactions to Foods'),
        # Pages 101: Insect/Drug allergy → Ch. 187/193
        101: (193, 'Adverse and Allergic Reactions to Drugs'),
        # Pages 102-103: Drug allergy + Urticaria/Anaphylaxis → Ch. 189/190
        102: (189, 'Urticaria (Hives) and Angioedema'),
        103: (190, 'Anaphylaxis'),
        # Pages 104-105: Immunodeficiency overview → Ch. 164
        104: (164, 'Orientation to the Consideration of Inborn Errors of Immunity'),
        105: (166, 'B-Cell and Antibody Deficiencies'),
        # Pages 106-107: Combined immunodeficiency → Ch. 165
        106: (165, 'Primary Defects of Cellular Immunity'),
        107: (165, 'Primary Defects of Cellular Immunity'),
        # Pages 108-109: Phagocyte defects → Ch. 168
        108: (168, 'Neutrophils'),
        109: (174, 'Immune Dysregulation'),
        # Pages 110-111: HSCT + complement → Ch. 170/177
        110: (170, 'The Complement System'),
        111: (177, 'Principles and Clinical Indications of Hematopoietic Stem Cell Transplantation'),
        # Pages 87-95: Pulmonary
        87: (434, 'Congenital Anomalies of the Larynx, Trachea, and Bronchi'),
        88: (439, 'Wheezing, Bronchiolitis, and Bronchitis'),
        89: (449, 'Community-Acquired Pneumonia'),
        90: (451, 'Pleurisy, Pleural Effusions, and Empyema'),
        91: (454, 'Cystic Fibrosis'),
        92: (489, 'Diseases of the Pericardium'),
        93: (456, 'Diffuse Lung Diseases in Childhood'),
        94: (448, 'Immune and Inflammatory Lung Disease'),
        95: (443, 'Other Distal Airway Diseases'),
        # Page 80: Cardiology
        80: (481, 'Other Congenital Heart and Vascular Malformations'),
        # Page 119: Hematology
        119: (495, 'Development of the Hematopoietic System'),
        # Page 129: Oncology/Spleen
        129: (535, 'Splenomegaly'),
    }
    return page_map


# ═══════════════════════════════════════════════════════════════════
# STEP 4: Fix APKG files
# ═══════════════════════════════════════════════════════════════════

def extract_disease_and_page(text_field):
    """Extract disease name and page number from the Text field."""
    # Pattern: [עמ' NNN] DiseaseName — Category<br><br>...
    page_m = re.search(r"\[עמ'\s*(\d+)\]", text_field)
    page = int(page_m.group(1)) if page_m else None

    # Get disease name: between ] and either — or <br>
    disease = ""
    title_m = re.search(r'\]\s*(.+?)(?:\s*—|\s*–|<br>)', text_field)
    if title_m:
        disease = title_m.group(1).strip()

    return disease, page


def fix_apkg(apkg_path, disease_map, page_fallback, pdf_map, backup_dir):
    """Fix missing NelsonChapter and ChapterURL in an APKG file."""
    fname = os.path.basename(apkg_path)
    print(f"\n{'='*60}")
    print(f"Processing: {fname}")
    print(f"{'='*60}")

    # Backup
    backup_path = os.path.join(backup_dir, fname)
    shutil.copy2(apkg_path, backup_path)
    print(f"  Backed up to: {backup_path}")

    # Extract APKG
    tmpdir = tempfile.mkdtemp()
    with zipfile.ZipFile(apkg_path, 'r') as z:
        z.extractall(tmpdir)

    db_path = os.path.join(tmpdir, 'collection.anki2')
    db = sqlite3.connect(db_path)
    cur = db.cursor()

    # Read all notes
    cur.execute("SELECT id, flds FROM notes")
    notes = cur.fetchall()

    fixed_count = 0
    failed = []

    for note_id, flds in notes:
        parts = flds.split('\x1f')
        if len(parts) < 7:
            continue

        nelson_ch = parts[3].strip()
        chapter_url = parts[6].strip()

        # Only fix notes with empty NelsonChapter
        if nelson_ch:
            continue

        text = parts[0]
        disease, page = extract_disease_and_page(text)

        # Try disease name match first
        ch_num = None
        ch_title = None

        if disease in disease_map:
            ch_num, ch_title = disease_map[disease]
        elif disease.lower() in {k.lower(): v for k, v in disease_map.items()}:
            for k, v in disease_map.items():
                if k.lower() == disease.lower():
                    ch_num, ch_title = v
                    break

        # Fallback: page-based lookup
        if ch_num is None and page and page in page_fallback:
            ch_num, ch_title = page_fallback[page]

        if ch_num is None:
            failed.append((note_id, disease, page))
            continue

        # Build NelsonChapter string
        new_nelson_ch = f"Ch. {ch_num} - {ch_title}"

        # Build ChapterURL (with fallback for chapters without their own PDF)
        new_chapter_url = ""
        if ch_num in pdf_map:
            new_chapter_url = make_chapter_url(pdf_map[ch_num])
        elif ch_num in CHAPTER_PDF_FALLBACK and CHAPTER_PDF_FALLBACK[ch_num] in pdf_map:
            fallback_ch = CHAPTER_PDF_FALLBACK[ch_num]
            new_chapter_url = make_chapter_url(pdf_map[fallback_ch])

        # Update fields
        parts[3] = new_nelson_ch
        parts[6] = new_chapter_url
        new_flds = '\x1f'.join(parts)

        cur.execute("UPDATE notes SET flds = ? WHERE id = ?", (new_flds, note_id))
        fixed_count += 1

    db.commit()
    db.close()

    # Repackage as APKG
    with zipfile.ZipFile(apkg_path, 'w', zipfile.ZIP_DEFLATED) as zout:
        for root, dirs, files in os.walk(tmpdir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, tmpdir)
                zout.write(file_path, arcname)

    # Cleanup
    shutil.rmtree(tmpdir)

    print(f"  Fixed: {fixed_count} notes")
    if failed:
        print(f"  FAILED to map ({len(failed)} notes):")
        for nid, dis, pg in failed:
            print(f"    Note {nid}: disease='{dis}', page={pg}")

    return fixed_count, failed


def main():
    print("="*60)
    print("APKG NelsonChapter/ChapterURL Fix Script")
    print("="*60)

    # Build lookup tables
    pdf_map = build_pdf_filename_map()
    print(f"Loaded {len(pdf_map)} PDF filename mappings")

    disease_map = build_disease_chapter_map(pdf_map)
    print(f"Loaded {len(disease_map)} disease-to-chapter mappings")

    page_fallback = build_page_fallback_map()
    print(f"Loaded {len(page_fallback)} page-based fallback mappings")

    # Create backup directory
    backup_dir = os.path.join(OUTPUT_DIR, 'backup')
    os.makedirs(backup_dir, exist_ok=True)
    print(f"Backup directory: {backup_dir}")

    # Files to fix (in order from most affected to least)
    apkg_files = [
        'batch5a_immunology_p1_redo.apkg',
        'batch5b_immunology_p2_redo.apkg',
        'batch4_pulmonology_redo.apkg',
        'batch6a_hematology_p1.apkg',
        'batch7_oncology.apkg',
        'batch3b_cardiology_p2_redo.apkg',
    ]

    total_fixed = 0
    total_failed = 0
    results = []

    for fname in apkg_files:
        apkg_path = os.path.join(OUTPUT_DIR, fname)
        if not os.path.exists(apkg_path):
            print(f"\n  SKIPPED: {fname} not found!")
            continue

        fixed, failed = fix_apkg(apkg_path, disease_map, page_fallback, pdf_map, backup_dir)
        total_fixed += fixed
        total_failed += len(failed)
        results.append((fname, fixed, len(failed)))

    # Summary
    print(f"\n\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    for fname, fixed, failed in results:
        status = "OK" if failed == 0 else f"{failed} UNRESOLVED"
        print(f"  {fname}: {fixed} fixed, {status}")
    print(f"\nTotal fixed: {total_fixed}")
    print(f"Total unresolved: {total_failed}")

    return total_failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
