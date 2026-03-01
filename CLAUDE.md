# Nelson Anki Flashcard Project — Claude Code Instructions

## Project Overview

Generate a comprehensive Anki flashcard deck from a 265-page Hebrew medical PDF (Nelson Pediatrics summary). Cards have 7 fields, max 5 cloze deletions per note, organized into sub-decks per disease.

## CRITICAL RULES (read before doing anything)

1. **ALWAYS read `progress.json` first** — it tracks exactly what's done and what's in progress
2. **NEVER skip content** — if interrupted, resume from the exact phase that was incomplete
3. **Save after EVERY phase** — extraction, cards, APKG each get saved immediately to `work/`
4. **Max 5 cloze deletions per note** — the build script validates this; target 2-4
5. **All 7 fields populated** for every note (Text, Context, Extra, NelsonChapter, SearchKeywords, GoogleURL, ChapterURL)
6. **Update progress.json after every phase** — this is how we recover from interruptions
7. **Use Task tool for each phase** to keep context manageable — see orchestrator.md
8. **100% content coverage, 0% hallucination** — every fact from the PDF gets a card

## Directory Structure

```
nelson_project/
├── CLAUDE.md                    ← You are here
├── prompt.md                    ← Card specs, 7-field model, templates, rules
├── orchestrator.md              ← Phase-by-phase batch processing logic
├── progress.json                ← Machine-readable state (THE source of truth)
├── todo.md                      ← Human-readable progress tracker
├── input/
│   ├── source.pdf               ← The 265-page Hebrew PDF (symlinked)
│   ├── chapter_index.txt        ← Nelson 22nd Ed contributor index
│   └── pdf_filenames.txt        ← Google Drive chapter PDF filenames
├── output/                      ← Final APKG + cards.md files per batch
├── work/                        ← Temp files: extraction JSON, cards parts, chapter maps
└── scripts/
    ├── extract.py               ← PDF text extraction + image page export
    ├── build_apkg.py            ← Parse markdown → 7-field APKG with sub-decks
    ├── verify.py                ← APKG structure + content verification
    └── update_progress.py       ← CLI tool to update progress.json
```

## How to Run

### Process next batch:
```bash
claude "Read CLAUDE.md, then orchestrator.md, then progress.json. Process the next pending batch."
```

### Resume after interruption:
```bash
claude "Read progress.json. Resume the in-progress batch from its last completed phase."
```

### Run the pilot (first time):
```bash
claude "Read CLAUDE.md, then prompt.md, then orchestrator.md. Run the pilot batch (pages 162-164) to validate the full pipeline. After completion, present the APKG for user review."
```

## Sub-Agent Architecture (IMPORTANT)

To manage context, use the **Task tool** to spawn focused sub-agents for each phase.
Each sub-agent gets ONLY the files it needs — NOT the entire project context.

### Phase 1: Extraction Agent
- Reads: input/source.pdf (page range only)
- Writes: work/current_extraction.json + work/page_NNN.png for image pages
- Context: ~small

### Phase 2: Chapter Mapping Agent
- Reads: work/current_extraction.json (disease names only), input/chapter_index.txt, input/pdf_filenames.txt
- Writes: work/current_chapter_map.json
- Context: ~medium

### Phase 3: Card Writing Agent (heaviest — split if >5 pages)
- Reads: prompt.md (rules section), work/current_extraction.json (subset of pages), work/current_chapter_map.json
- Writes: work/cards_part1.md, work/cards_part2.md, etc.
- Context: ~large — split into sub-batches of 3-4 pages if needed
- **After all parts**: concatenate into work/current_cards.md and run page coverage audit

### Phase 4: APKG Build Agent
- Reads: work/current_cards.md, work/current_chapter_map.json, scripts/build_apkg.py
- Writes: output/batchNN_name.apkg + output/batchNN_cards.md
- Context: ~medium

### Phase 5: Verification + Progress Update
- Reads: output APKG, progress.json, todo.md
- Writes: updated progress.json, updated todo.md
- Context: ~small

## Dependencies

```bash
pip install pymupdf genanki
```

## Key Specifications

- **MODEL_ID**: 1607392322 (must be identical across ALL batches)
- **Model name**: Nelson Cloze v5
- **Fields**: Text, Context, Extra, NelsonChapter, SearchKeywords, GoogleURL, ChapterURL
- **Deck hierarchy**: `נלסון 21::{specialty}::{disease/topic}`
- **Tags**: `disease::X`, `category::Y`, `page::Z`
- **Cloze density**: MAX 5 per note, target 2-4

## Sub-Agent Safety Rules

**These rules prevent sub-agents from going rogue and completing the entire pipeline autonomously.**

1. **NEVER pass `orchestrator.md` or `CLAUDE.md` to a sub-agent** — these files contain full pipeline logic that enables autonomous completion of multiple phases
2. **NEVER pass `progress.json` to a sub-agent** — only the orchestrator (main agent) reads/writes project state
3. **Each sub-agent does EXACTLY ONE phase** — extraction OR chapter mapping OR card writing OR APKG build. Never more than one.
4. **Every sub-agent prompt MUST include the containment header** from orchestrator.md's "Sub-Agent Containment Protocol" section
5. **Explicitly list allowed output files** in every sub-agent prompt — agents must not create files outside their scope
6. **After a sub-agent returns, check for rogue behavior**:
   - Did it complete multiple phases? → Discard output, re-run with stricter prompt
   - Did it create unexpected files? → Investigate before using
   - Did it report reading orchestrator.md/CLAUDE.md? → Discard, re-run
7. **Card-writing sub-agents get max 4 pages** — larger context causes quality degradation
8. **Only Phase 5 (Verification) may update progress.json** — and only via the main orchestrator, not a sub-agent

## Recovery Protocol

If progress.json shows `current_batch.status == "in_progress"`:
1. Check which phases have `"complete"` status
2. For each completed phase, its output file should exist in work/
3. Resume from the first non-complete phase
4. If a file is missing but phase marked complete, re-run ONLY that phase
5. NEVER re-do a completed phase unless its output file is missing
