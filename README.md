# Nelson Pediatrics Anki Flashcard Deck

Comprehensive Anki flashcard deck generated from a 265-page Hebrew medical summary of Nelson's Textbook of Pediatrics (22nd Edition), using Claude Code CLI with an automated multi-phase pipeline.

## Final Output

- **4,357 notes** across **13,795 cloze review cards**
- **265/265 pages** covered (100%)
- **36 APKG files** in `output/` — all pass strict verification
- **21 medical specialties** organized into sub-decks

## How to Use

1. Download APKG files from `output/`
2. Import into [Anki](https://apps.ankiweb.net/) (File → Import)
3. Cards appear under the deck `נלסון 21::` with sub-decks per specialty and disease

## Card Model (7 Fields)

| Field | Description |
|-------|-------------|
| Text | Hebrew medical content with cloze deletions |
| Context | Disease \| Subtopic \| Page reference |
| Extra | Clinical pearl or exam-relevant insight |
| NelsonChapter | "Ch. NNN. Chapter Name" |
| SearchKeywords | English medical terms for Google |
| GoogleURL | Auto-generated Google search link |
| ChapterURL | Link to Nelson online chapter |

## Specialties Covered

| # | Specialty | Pages | Notes |
|---|-----------|-------|-------|
| 1 | מחלות זיהומיות (Infectious Diseases) | 1-47 | 884 |
| 2 | נוירולוגיה (Neurology) | 48-66 | 252 |
| 3 | קרדיולוגיה (Cardiology) | 67-86 | 252 |
| 4 | ריאות (Pulmonology) | 87-95 | 135 |
| 5 | אימונולוגיה (Immunology & Allergy) | 96-111 | 184 |
| 6 | המטולוגיה (Hematology) | 112-128 | 256 |
| 7 | אונקולוגיה (Oncology) | 129-136 | 174 |
| 8 | גסטרו-אנטרולוגיה (Gastroenterology) | 137-155 | 295 |
| 9 | תזונה (Nutrition) | 156-161 | 97 |
| 10 | נפרולוגיה (Nephrology) | 162-178 | 297 |
| 11 | אנדוקרינולוגיה (Endocrinology) | 179-205 | 449 |
| 12 | ראומטולוגיה (Rheumatology) | 206-219 | 215 |
| 13 | מחלות מטבוליות (Metabolic Diseases) | 220-233 | 264 |
| 14 | נאונטולוגיה (Neonatology) | 234-246 | 239 |
| 15 | אורתופדיה + עיניים + עור (Ortho/Ophth/Derm) | 247-259 | 275 |
| 16 | התנהגות + גנטיקה + חירום (Behavioral/Genetics/Emergency) | 260-265 | 109 |

## Pipeline Architecture

```
PDF → Extract (PyMuPDF) → Chapter Map → Card Writing (Claude sub-agents)
    → Build APKG (genanki) → Verify (strict) → output/*.apkg
```

### Key Design Decisions
- **Sub-agent architecture**: Each card-writing phase runs in isolated context (3-4 pages max)
- **Gold standard reference**: 8 example cards from best batch included in every sub-agent
- **Anti-degradation**: Formula-based density minimums, cloze distribution validation
- **Two-level verification**: `validate_density.py` + `verify.py --strict`
- **Progress tracking**: `progress.json` enables interrupt recovery at any phase

## Project Structure

```
├── output/           ← 36 APKG files + card markdown archives
├── input/            ← Source PDF + Nelson chapter index
├── work/             ← Page images (PNG), gold standard, last batch state
├── scripts/          ← Pipeline scripts (extract, build, verify, fix)
├── CLAUDE.md         ← Claude Code instructions
├── prompt.md         ← Card writing rules (11 rules)
├── orchestrator.md   ← Phase-by-phase pipeline logic
├── progress.json     ← Machine-readable project state
├── lessons.md        ← Comprehensive lessons learned
└── todo.md           ← Human-readable progress tracker
```

## Scripts

| Script | Purpose |
|--------|---------|
| `extract.py` | PDF text extraction + image page PNG export |
| `build_apkg.py` | Parse markdown → 7-field APKG with sub-decks |
| `verify.py` | APKG structure + content verification (strict mode) |
| `validate_density.py` | Card density + cloze distribution checker |
| `fix_missing_chapters.py` | Patch missing NelsonChapter/ChapterURL in APKGs |
| `fix_cloze_distribution.py` | Surgically reduce excess cloze counts |

## Dependencies

```bash
pip install pymupdf genanki
```

## Quality Metrics

- **Avg clozes/note**: 3.2 (target 2.5-3.2)
- **Cards ≤3 clozes**: >70% (target ≥50%)
- **Cards at max 5 clozes**: <5% (target ≤20%)
- **All 7 fields populated**: 100%
- **Strict verification**: 36/36 PASS

## Built With

- [Claude Code CLI](https://claude.ai/claude-code) (Anthropic) — card generation and pipeline orchestration
- [genanki](https://github.com/kerrickstaley/genanki) — APKG creation
- [PyMuPDF](https://pymupdf.readthedocs.io/) — PDF text and image extraction

## License

This project generates study materials from copyrighted medical textbook content. The flashcards are for personal educational use only.
