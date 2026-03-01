# Nelson Anki — Batch Orchestrator

## Startup Sequence (EVERY run)

```
1. Read progress.json
2. Identify: Is there an incomplete batch? → Resume it from last completed phase
3. If no incomplete batch → Start the next batch from progress.json.next_batch
4. Execute phases sequentially, saving after each
```

## Recovery Logic

**If progress.json shows a batch with status "in_progress":**

Check which phases are complete (each phase has its own status):
- `extraction: "complete"` → Skip extraction, use work/page_NNN.png + work/current_extraction.json
- `chapter_map: "complete"` → Skip mapping, use work/current_chapter_map.json
- `nelson_reading: "complete"` → Skip Nelson chapter reading, use work/current_nelson_context.md
- `cards: "complete"` → Skip card writing, use work/current_cards.md
- `apkg: "complete"` → Skip building, proceed to verification
- `verified: "complete"` → Batch is done, update status to "complete"

**NEVER re-do a completed phase.** Read its output from the work/ directory.

**If a phase file is missing but marked complete**, re-run that phase only.

---

## Phase 1: Image-First Extraction

The source PDF contains complex visual structures (multi-column comparison tables, flowcharts, decision trees). **Text extraction alone destroys this structure.** We use an image-first approach.

### Steps:
1. Export EVERY page as a high-DPI PNG (200 DPI) → `work/page_NNN.png`
2. Also extract text via PyMuPDF → `work/current_extraction.json` (supplementary cross-check)
3. The card-writing agent will receive BOTH the images and the text

### As a sub-agent or inline:

```python
import fitz, json, os

def extract_batch(pdf_path, start_page, end_page, output_dir="work"):
    os.makedirs(output_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    data = {"pages": {}, "summary": {"total_pages": 0, "text_pages": 0, "image_pages": 0, "total_chars": 0}}

    for p in range(start_page, end_page + 1):
        idx = p - 1
        page = doc[idx]
        text = page.get_text()
        char_count = len(text.strip())

        # ALWAYS export as PNG (image-first approach)
        pix = page.get_pixmap(dpi=200)
        img_path = os.path.join(output_dir, f"page_{p}.png")
        pix.save(img_path)

        data["pages"][str(p)] = {
            "type": "text" if char_count >= 200 else "image",
            "chars": char_count,
            "text": text.strip(),
            "image": img_path  # ALWAYS present now
        }
        data["summary"]["total_pages"] += 1
        data["summary"]["total_chars"] += char_count
        if char_count >= 200:
            data["summary"]["text_pages"] += 1
        else:
            data["summary"]["image_pages"] += 1

    doc.close()
    output_file = os.path.join(output_dir, "current_extraction.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return data
```

### Output files:
- `work/page_NNN.png` — High-DPI image of EVERY page (primary source for card writing)
- `work/current_extraction.json` — Text extraction + image paths (supplementary)

### After extraction completes:
```python
progress["current_batch"]["phases"]["extraction"] = "complete"
save_progress()
```

---

## Phase 2: Chapter Mapping

### As a sub-agent (Task tool):

```
Task: Build Nelson chapter map for batch {BATCH_ID}

Instructions:
1. Read work/current_extraction.json (just the disease/topic names, not full text)
2. Read input/chapter_index.txt
3. Read input/pdf_filenames.txt (for Google Drive links)
4. For each disease/topic found in the extraction:
   a. Search chapter_index.txt for matching chapter numbers + titles
   b. Find the matching PDF filename from pdf_filenames.txt
   c. Build the ChapterURL as: https://drive.google.com/drive/search?q={filename}
5. Save to work/current_chapter_map.json

Output format: see below
```

### Chapter map JSON format:
```json
{
  "batch_id": "11_endocrinology",
  "diseases": {
    "Diabetes_Type_1": {
      "primary_chapter": "607. Diabetes Mellitus",
      "related_chapters": ["606. Introduction to the Endocrine System"],
      "chapter_url": "https://drive.google.com/drive/search?q=Chapter%20607%20-%20Diabetes%20Mellitus",
      "sub_deck": "נלסון 21::אנדוקרינולוגיה::סוכרת סוג 1"
    }
  }
}
```

### After mapping completes:
```python
progress["current_batch"]["phases"]["chapter_map"] = "complete"
save_progress()
```

---

## Phase 2.5: Nelson Chapter Reading (Extra Field Enrichment)

Read the relevant Nelson 22nd Ed chapter(s) to provide authoritative content for the Extra field and to verify ambiguous summary PDF facts.

### Steps:
1. From the chapter_map, identify the primary Nelson chapters for this batch
2. Locate the per-chapter PDFs in `input/Nelson book chapters/`
3. Read key sections (epidemiology, clinical, pathology, treatment — matching the batch topics)
4. Extract concise clinical pearls, differential diagnosis tips, and exam-relevant highlights
5. Save a condensed summary to `work/current_nelson_context.md`

### As a sub-agent (Task tool):

```
Task: Read Nelson chapters for batch {BATCH_ID} Extra field enrichment

Instructions:
1. Read work/current_chapter_map.json to identify relevant chapters
2. Find and read the matching chapter PDFs from input/Nelson book chapters/
3. For each disease/topic in the batch, extract:
   a. Key differential diagnosis points (how to distinguish from similar conditions)
   b. Clinical pearls that explain WHY specific facts matter
   c. Exam-relevant highlights ("classic presentation", "pathognomonic finding")
4. Save to work/current_nelson_context.md as structured notes per disease
5. Keep it concise — the card-writing agent only needs targeted pearls, not full chapter text

Output format:
## IgA Nephropathy
- Differential: C3 normal (vs PIGN where C3 low) — key exam distinction
- Pearl: Synpharyngitic hematuria (same day as infection) vs PIGN (1-3 week latency)
- Pathognomonic: Mesangial IgA on IF

## Alport Syndrome
- Differential: ...
```

### IMPORTANT constraints:
- Only read chapters relevant to the current batch (typically 1-4 chapters)
- Focus on content that enriches the Extra field — not on duplicating the summary PDF
- Source-bound: only include facts actually stated in the Nelson chapter text

### After Nelson reading completes:
```python
progress["current_batch"]["phases"]["nelson_reading"] = "complete"
save_progress()
```

---

## Phase 3: Card Writing (Image-First + Nelson Context) — ANTI-DEGRADATION ARCHITECTURE

This is the most context-heavy phase and the one most vulnerable to quality drift.
**Every sub-agent MUST receive the gold standard reference to anchor style.**

### Sub-batch strategy (STRICT — max 3-4 pages per sub-agent):
- **1-4 pages** → 1 sub-agent
- **5-8 pages** → 2 sub-agents (3-4 pages each)
- **9-12 pages** → 3 sub-agents (3-4 pages each)
- **NEVER give a sub-agent more than 4 pages** — context pressure causes bloat and omission

Each sub-batch is a separate Task tool invocation writing to work/cards_part1.md, work/cards_part2.md, etc.

### Sub-agent context (EXACTLY these files, nothing more):
1. **prompt.md** — Rules section only (Cloze Selection Strategy + Card Generation Rules)
2. **work/gold_standard_reference.md** — MANDATORY — concrete style examples
3. **work/page_NNN.png** — Page images for THIS sub-batch only
4. **work/current_extraction.json** — Text for THIS sub-batch's pages only
5. **work/current_chapter_map.json** — Disease→chapter mapping
6. **work/current_nelson_context.md** — Nelson context for Extra field

### As a sub-agent (Task tool):

```
Task: Write Anki cards for pages {START}-{END} of batch {BATCH_ID}

CRITICAL CONTEXT — READ THESE FILES IN ORDER:
1. Read work/gold_standard_reference.md FIRST — this shows the EXACT style to match
2. Read prompt.md — specifically "Cloze Selection Strategy" and "Card Generation Rules"
3. VIEW the page images work/page_NNN.png — these are your PRIMARY source
   - Read tables column by column, preserving structure
   - Read flowcharts node by node, creating cards for each decision/fact
   - Read comparison tables row by row across all columns
4. Use work/current_extraction.json as supplementary text cross-check
5. Read work/current_chapter_map.json for disease→chapter mapping
6. Read work/current_nelson_context.md for Extra field content

DENSITY REQUIREMENTS (non-negotiable):
- Quick check: **2.5 notes per 1,000 source chars** minimum
- Pages with 6000+ chars → at least 15 notes
- Pages with 4000-6000 chars → at least 10 notes
- Pages with 2000-4000 chars → at least 5 notes
- Count the source chars from extraction.json BEFORE writing and set your target

CLOZE DISTRIBUTION (non-negotiable):
- MAX 5 cloze deletions per note (2-4 is optimal, target avg 2.5-3.2)
- At least 50% of cards must have ≤3 clozes
- No more than 20% of cards may have 5 clozes
- If a card hits 4-5 clozes, SPLIT IT into two cards

CARD STYLE (match gold standard):
- Target 250-320 chars per card text. Split cards exceeding 380 chars.
- ONE concept per card (describe what it tests in ≤5 words)
- Use DISCRIMINATIVE clozing: differentiators, exam-testable numbers, specific findings
- AVOID clozing obvious/generic terms
- Treatment/drugs/dosing MUST be cloze-tested cards (Rule 11) — NEVER only in Extra
- Extra field: source-bound ONLY (from summary PDF or Nelson chapter)
- Every fact from the PDF must appear in at least one card
- Every card must be self-contained
- Include disease name + category in title
- English search keywords in {curly braces} at end

AFTER WRITING — SELF-CHECK:
Before saving, count your cards per page vs source chars. If any page is below
the 2.5 notes/1k chars threshold, go back and write more cards for that page.

Save to work/cards_partN.md
Report: cards per page, total cards, max clozes, avg clozes

Card format:
N. [עמ' XXX] Disease — Category - Card text with **[cloze1]** and **[cloze2]** {english keywords}
   > Extra: Source-bound clinical pearl or differential comparison.
```

### Page coverage audit + density validation (after all parts written):
```python
# Concatenate all parts
import re, glob, subprocess
parts = sorted(glob.glob("work/cards_part*.md"))
all_cards = ""
for p in parts:
    all_cards += open(p, encoding='utf-8').read() + "\n"
with open("work/current_cards.md", "w", encoding='utf-8') as out:
    out.write(all_cards)

# Verify every text page has cards
pages_with_cards = set()
for match in re.finditer(r"\[עמ'\s*(\d+)\]", all_cards):
    pages_with_cards.add(int(match.group(1)))

for page_num in range(start_page, end_page + 1):
    if page_num not in pages_with_cards:
        print(f"⚠️ MISSING COVERAGE: Page {page_num} has no cards!")

# Run density validation
result = subprocess.run(
    ["python", "scripts/validate_density.py", "work/current_cards.md",
     "work/current_extraction.json", str(start_page), str(end_page)],
    capture_output=True, text=True
)
print(result.stdout)
if result.returncode != 0:
    print("❌ DENSITY VALIDATION FAILED — must fix before proceeding to APKG build")
    # Do NOT proceed to Phase 4 until density passes
```

### If density validation FAILS:
1. Identify which pages are below minimum
2. Re-run a targeted sub-agent for ONLY those pages
3. Append the new cards to work/current_cards.md
4. Re-run validation
5. Only proceed to Phase 4 when validation passes

### After card writing completes (ONLY if validation passes):
```python
progress["current_batch"]["phases"]["cards"] = "complete"
progress["current_batch"]["cards_written"] = total_cards
save_progress()
```

---

## Phase 4: APKG Build

### As a sub-agent (Task tool):

```
Task: Build APKG from work/current_cards.md for batch {BATCH_ID}

Instructions:
1. Read prompt.md — specifically the "Anki Note Model" section for the 7-field model
2. Read work/current_cards.md
3. Read work/current_chapter_map.json
4. Run scripts/build_apkg.py (or the inline code from prompt.md)
5. VALIDATION CHECKS:
   - No note has >5 clozes
   - All 7 fields are populated (Text, Context, Extra, NelsonChapter, SearchKeywords, GoogleURL, ChapterURL)
   - Model has correct field names
   - Context/Extra/Chapter NOT on front template
   - GoogleURL and ChapterURL are on back template
6. Save to output/batchNN_name.apkg
7. Copy work/current_cards.md to output/batchNN_cards.md
8. Report: notes count, cloze count, avg clozes/note, max clozes, pass/fail

If validation FAILS: report the specific failures and STOP. Do not update progress.
```

### After build completes (only if validation passes):
```python
progress["current_batch"]["phases"]["apkg"] = "complete"
progress["current_batch"]["notes_count"] = notes
progress["current_batch"]["cloze_count"] = clozes
save_progress()
```

---

## Phase 5: Verification & Progress Update

### As a sub-agent (Task tool):

```
Task: Verify batch {BATCH_ID} and update progress

Instructions:
1. Run scripts/verify.py on the APKG file
2. Verify:
   - Note count matches expected
   - All 7 fields present in every note
   - No note >5 clozes
   - Template structure correct
   - Sample 3 notes for content quality
3. Update progress.json:
   - Set current batch status to "complete"
   - Increment completed sections/pages counts
   - Set next_batch to the following section
4. Update todo.md with the batch results
5. Clean work/ directory (optional — keep for debugging)
```

### After verification:
```python
progress["current_batch"]["phases"]["verified"] = "complete"
progress["current_batch"]["status"] = "complete"
progress["completed_batches"].append(progress["current_batch"])
progress["current_batch"] = None
progress["stats"]["sections_complete"] += 1  # only when full section done
progress["stats"]["pages_processed"] += batch_page_count
progress["stats"]["total_notes"] += notes_count
progress["stats"]["total_clozes"] += cloze_count
save_progress()
```

---

## Batch Sizing Guidelines

| Source pages | Recommended split | Card-writing sub-agents |
|-------------|-------------------|--------------------------|
| 1-4 pages | Single batch | 1 sub-agent (max 4 pages) |
| 5-8 pages | Single batch | 2 sub-agents (3-4 pages each) |
| 9-12 pages | Single batch | 3 sub-agents (3-4 pages each) |
| 13-16 pages | Split into 2 batches | 2 sub-agents per batch |
| 17+ pages | Split into 3+ batches | 2 sub-agents per batch |

**HARD RULE: Never give a card-writing sub-agent more than 4 pages.**

## Anti-Degradation Checklist (run before EVERY card-writing phase)

Before spawning any card-writing sub-agent, verify:
- [ ] Gold standard reference file exists at work/gold_standard_reference.md
- [ ] Sub-agent prompt includes "Read gold_standard_reference.md FIRST"
- [ ] Sub-agent receives no more than 4 pages
- [ ] Density targets are stated explicitly in the sub-agent prompt (chars/page → min notes)
- [ ] Cloze distribution caps are stated (50% ≤3, max 20% at 5)
- [ ] Treatment-must-be-carded rule is mentioned
- [ ] Post-writing density validation is planned

## Sub-Agent Containment Protocol

**Every sub-agent MUST be scoped to exactly ONE phase.** This prevents agents from "helpfully" completing the entire pipeline.

### Mandatory containment header (include in EVERY sub-agent prompt):
```
SCOPE: You are a {PHASE_NAME}-only agent for batch {BATCH_ID}.
- You MUST only perform {PHASE_NAME} tasks
- You MUST NOT read or modify progress.json
- You MUST NOT read orchestrator.md or CLAUDE.md
- You MUST NOT proceed to any subsequent phase
- You MUST NOT spawn additional sub-agents
- Your ONLY output files: {LIST_ALLOWED_OUTPUT_FILES}
- When done, report your results and STOP
```

### Files sub-agents must NEVER receive:
- `orchestrator.md` — contains the full pipeline; giving it to a sub-agent enables rogue completion
- `CLAUDE.md` — contains project-wide instructions that could trigger autonomous behavior
- `progress.json` — sub-agents must not read or write project state

### Output file restrictions per phase:
| Phase | Allowed output files |
|-------|---------------------|
| Extraction | `work/current_extraction.json`, `work/page_NNN.png` |
| Chapter Map | `work/current_chapter_map.json` |
| Nelson Reading | `work/current_nelson_context.md` |
| Card Writing | `work/cards_partN.md` (single part per agent) |
| APKG Build | `output/batchNN_name.apkg`, `output/batchNN_cards.md` |

### Sub-Agent Launch Checklist:
Before spawning any sub-agent, verify:
- [ ] Prompt contains the containment header with correct PHASE_NAME and BATCH_ID
- [ ] Prompt does NOT reference orchestrator.md or CLAUDE.md
- [ ] Prompt does NOT ask agent to read/update progress.json
- [ ] Allowed output files are explicitly listed
- [ ] Agent receives ONLY the files needed for its specific phase

### Rogue Agent Detection:
After a sub-agent returns, check for these red flags:
1. Agent reports completing multiple phases (e.g., "I also built the APKG")
2. Agent created files outside its allowed output list
3. Agent modified progress.json
4. Agent's response mentions reading orchestrator.md or CLAUDE.md
5. Agent's output is suspiciously large relative to the phase scope

If any red flag is detected: discard the agent's output, re-run the phase with a stricter prompt.

---

## Error Handling

- **Script fails**: Log error, do NOT update progress, report to user
- **Validation fails**: Log failures, do NOT update progress, report specific issues
- **Density validation fails**: Re-run card writing for failing pages ONLY, append to current_cards.md
- **Context running low**: Save all current work to work/ directory, update progress with partial status, suggest resuming in new session
- **Interruption**: progress.json always reflects the last completed state. Next run picks up from there.

## Section Schedule

Processing order. Each section may be split into multiple batches based on page count.

| # | Section | Pages | Est. Batches |
|---|---------|-------|-------------|
| 0 | Pilot (validation run) | 162-164 | 1 |
| 1 | מחלות זיהומיות | 1-46 | 6 |
| 2 | נוירולוגיה | 48-66 | 3 |
| 3 | קרדיולוגיה | 67-86 | 3 |
| 4 | ריאות | 87-95 | 2 |
| 5 | אימונולוגיה ואלרגיה | 96-111 | 2 |
| 6 | המטולוגיה | 112-128 | 3 |
| 7 | אונקולוגיה | 129-136 | 2 |
| 8 | גסטרו-אנטרולוגיה | 137-155 | 3 |
| 9 | תזונה | 156-161 | 1 |
| 10 | נפרולוגיה | 162-178 | 3 |
| 11 | אנדוקרינולוגיה | 179-205 | 4 |
| 12 | ראומטולוגיה | 206-219 | 2 |
| 13 | מחלות מטבוליות | 220-233 | 2 |
| 14 | נאונטולוגיה | 234-246 | 2 |
| 15 | אורתופדיה | 247-253 | 1 |
| 16 | עיניים | 254-256 | 1 |
| 17 | עור | 257 | 1 |
| 18 | הרעלות | 258-259 | 1 |
| 19 | התנהגות/פסיכיאטריה | 260-262 | 1 |
| 20 | גנטיקה | 263-265 | 1 |
