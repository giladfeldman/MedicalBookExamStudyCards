# Independent Audit: Nelson Pediatrics Anki Flashcard Deck

## Your Role

You are an independent quality auditor for a medical Anki flashcard deck. The deck was generated from a 265-page Hebrew medical summary PDF (Nelson Pediatrics, 22nd edition summary). Your job is to find **any gaps, errors, or quality issues** that the creators may have missed. Be thorough, skeptical, and constructive.

You have access to:
- The source PDF (`input/source.pdf`, 265 pages, Hebrew, ~1.2M characters)
- All card markdown files (`output/*_cards.md`, 36 files, ~4,400 cards total)
- The automated audit report (`work/table_audit_report.json`)

---

## Project Context

### What this deck is
- Anki cloze-deletion flashcards for Israeli medical students studying pediatrics
- Source: a Hebrew-language summary of Nelson's Textbook of Pediatrics (22nd ed)
- Language: Hebrew card text with English search keywords
- Cards are organized into sub-decks per disease/topic within medical specialties

### Card format
Each card has this markdown format:
```
N. [עמ' XXX] Disease Name — Category - Card text with **[cloze deletion]** and more **[cloze2]** {english search keywords}
   > Extra: Additional context, clinical pearls, differential diagnosis tips.
```

Example real cards:
```
1. [עמ' 2] אימונוגלובולינים — טיפול - IMIg: מתן תחליפי בחסר חיסוני במינון **[100]** מ"ג/ק"ג פעם בחודש. פרופילקסיס ל-Measles תוך **[6]** ימים מחשיפה במינון **[0.5]** מ"ל/ק"ג {IMIg dose immunodeficiency measles prophylaxis}
   > Extra: פרופילקסיס ל-HAV במבוגרים גם אפשרי, אך בילדים מומלץ חיסון פעיל (6-12 חודשים) שלא ייחשב במנין החיסונים.

7. [עמ' 2] חום ללא מקור — אפידמיולוגיה - SBI מתקיים ב-**[7-13%]** מהתינוקות עד חודש עם חום. מרבית המקרים (**[5-13%]**) ע"ר UTI, בקטרמיה **[1-2%]**, מנינגיטיס **[0.2-0.5%]** {SBI febrile neonate UTI bacteremia meningitis incidence}
   > Extra: UTI הוא ה-SBI השכיח ביותר בתינוקות חום — חשוב תמיד לקחת בדיקת שתן גם אם אין סימנים אורולוגיים.
```

### Card rules (enforced during generation)
- **Max 5 cloze deletions per card** (target 2-4)
- **7 fields per note**: Text, Context, Extra, NelsonChapter, SearchKeywords, GoogleURL, ChapterURL
- One concept per card
- All facts from the PDF should have corresponding cards
- Extra field must be source-bound (from the PDF or Nelson textbook)
- Treatment/drugs/dosing must be cloze-tested (not only in Extra)

### How cards were generated
The 265 pages were processed in 35+ batches by AI agents (Claude). Each batch:
1. Extracted text + images from the PDF
2. Mapped diseases to Nelson chapter numbers
3. Generated cards (max 4 pages per sub-agent to prevent quality degradation)
4. Built APKG files with automated validation

---

## What to Audit

### 1. CONTENT COVERAGE (highest priority)

**Goal**: Every medical fact in the PDF should be testable via at least one card.

**Method**: For each section below, read the PDF pages and compare against the card files. Look for:
- **Missing topics**: An entire disease, syndrome, or clinical entity mentioned in the PDF but with zero cards
- **Missing subtopics**: A disease is covered but some aspect (etiology, clinical features, diagnosis, treatment, prognosis) is not
- **Missing table/figure data**: Tables contain structured data (drug dosages, lab values, differential diagnosis grids, classification systems) that may have been skipped or only partially covered
- **Missing numerical data**: Specific percentages, dosages, age cutoffs, lab reference values that appear in the PDF but aren't cloze-tested in any card

**Files to cross-reference**:

| Section | PDF Pages | Card File(s) |
|---------|-----------|--------------|
| Infectious Diseases | 1-47 | batch1a_cards.md through batch1g_infectious_p47_cards.md |
| Neurology | 48-66 | batch2a_cards.md, batch2b_redo_cards.md |
| Cardiology | 67-86 | batch3a_redo_cards.md, batch3b_redo_cards.md |
| Pulmonology | 87-95 | batch4_redo_cards.md |
| Immunology & Allergy | 96-111 | batch5a_redo_cards.md, batch5b_redo_cards.md |
| Hematology | 112-128 | batch6a_hematology_p1_cards.md, batch6b_hematology_p2_cards.md |
| Oncology | 129-136 | batch7_oncology_cards.md |
| Gastroenterology | 137-155 | batch8a_gastro_p1_cards.md, batch8b_gastro_p2_cards.md |
| Nutrition | 156-161 | batch9_nutrition_cards.md |
| Nephrology | 162-178 | pilot_v2_cards.md (pp.162-164), batch10a_nephrology_p1_cards.md, batch10b_nephrology_p2_cards.md |
| Endocrinology | 179-205 | batch11a_cards.md, batch11b_cards.md, batch11c_cards.md |
| Rheumatology | 206-219 | batch12a_cards.md, batch12b_cards.md |
| Metabolic Diseases | 220-233 | batch13a_cards.md, batch13b_cards.md |
| Neonatology | 234-246 | batch14a_cards.md, batch14b_cards.md |
| Orthopedics + Eyes + Skin | 247-257 | batch15_cards.md, batch16_cards.md |
| Toxicology + Behavioral + Genetics | 258-265 | batch16_cards.md, batch17_cards.md |

**Pages with zero cards** (known, verified to be non-content):
- Page 1: Table of contents
- Pages 5, 10, 28-31, 40, 47, 67, 80, 82, 88, 101, 106, 217, 225, 245, 251, 264: Most are near-blank (page number only, or image-only pages where content is captured via adjacent pages)

**IMPORTANT**: Many pages in the PDF appear to have very little extractable text (< 100 chars) because the content is in images/complex layouts. The card generation used page IMAGES as primary input, not just extracted text. So cards may cover content that doesn't appear in text extraction. When auditing, read the actual PDF pages visually, not just text output.

### 2. TABLE COVERAGE (specific concern)

A doctor reviewing the deck flagged potential gaps in table coverage. Our automated audit found:
- **96.2% table coverage** (3,466 / 3,602 meaningful cells covered across 197 pages)
- 196 GREEN pages (>70%), 1 YELLOW page (page 188, 67%), 0 RED pages

**Pages to spot-check** (lower coverage in automated audit):
- Page 7 (77%): CNS infections comparison table — large 26x11 table
- Page 188 (67%): Mineralocorticoid disorders classification
- Page 203 (71%): Diabetes diagnostic criteria (HbA1c, OGTT, fasting glucose)
- Page 252 (77%): Ophthalmology classification table

For each flagged page, manually compare the table content in the PDF against the cards and determine:
- Are the uncovered cells truly important medical facts, or just headers/labels?
- Is the information present in the cards but phrased differently (synonym, paraphrase)?
- Are there real gaps that need new cards?

### 3. FACTUAL ACCURACY (spot-check)

Pick 20-30 cards at random across different sections and verify:
- Does the cloze-deleted value match the PDF source? (e.g., if the card says **[7-13%]**, does the PDF actually say 7-13%?)
- Is the Extra field content supported by the source material?
- Are disease-treatment associations correct?
- Are lab values and diagnostic criteria accurately transcribed?

### 4. CARD QUALITY (spot-check)

For 20-30 cards across different sections, evaluate:
- **Testability**: Does each cloze test a specific, discriminative fact? Or is it testing something obvious/generic?
- **Atomicity**: Does each card test ONE concept, or are multiple concepts crammed together?
- **Cloze selection**: Are the right words cloze-deleted? (Should be: differentiators, specific numbers, drug names, pathognomonic findings — NOT: common words, articles, generic verbs)
- **Self-containment**: Can the card be answered without seeing other cards?
- **Extra field quality**: Does it add useful context (differential diagnosis tips, clinical pearls) or is it just restating the card text?

### 5. STRUCTURAL ISSUES (broad sweep)

- **Duplicate cards**: Are any facts covered by multiple nearly-identical cards? (Some overlap at topic boundaries is expected)
- **Inconsistent terminology**: Does the same disease/drug/concept get different Hebrew transliterations across cards?
- **Missing treatments**: For diseases where treatment is discussed in the PDF, is there at least one card testing the treatment?
- **Missing epidemiology**: For diseases where incidence/prevalence is given, is it cloze-tested?
- **Orphaned topics**: Are there topics in the PDF that don't map to any card file? (Check the section boundaries above)

### 6. ANYTHING ELSE

Look for issues we haven't thought of. Some possibilities:
- Cards that would be confusing or misleading to a student
- Hebrew language errors or awkward phrasing
- English keywords that don't match the card content
- Information that appears outdated relative to Nelson 22nd ed
- Cards that test trivia rather than clinically important facts
- Systematic patterns (e.g., certain card categories consistently missing across all sections)

---

## How to Work

### Recommended approach

1. **Start broad**: Skim 5-6 representative PDF pages from different sections. For each page, count the distinct medical facts, then check how many appear as cards. This gives you a baseline "coverage feel."

2. **Go deep on flagged areas**: Focus extra attention on:
   - Table-heavy pages (pages 7, 45, 47, 49, 53, 83, 144, 165, 203, 233, 248)
   - Section boundaries (where one batch ends and another begins — these are highest risk for dropped content)
   - The sections with lowest card density: Immunology part 2 (pages 104-111, only 58 cards for 8 pages)

3. **Spot-check accuracy**: Pick specific numbers, drug names, or diagnostic criteria from the PDF and search for them in the card files.

4. **Report by section**: Organize your findings by medical section so we can target fixes.

### What a useful finding looks like

**Good finding** (actionable):
> "Page 142 (Gastroenterology) contains a table of hepatitis serological markers (HBsAg, anti-HBs, HBeAg, etc.) with 6 rows. Only 2 of the 6 marker patterns have corresponding cards. The patterns for 'Window Period' and 'Chronic Active Hepatitis' are missing."

**Less useful finding** (too vague):
> "Some gastroenterology content seems to be missing."

### Output format

Please organize your report as:

```
## Executive Summary
- Overall coverage assessment (1-2 sentences)
- Number of critical gaps found
- Number of minor issues found

## Critical Gaps (missing medical content)
For each gap:
- PDF page number
- Section/disease
- What's missing (specific facts, not vague descriptions)
- Severity: HIGH (entire topic missing) / MEDIUM (subtopic missing) / LOW (single fact missing)

## Table Coverage Issues
For each flagged table:
- PDF page number
- Table description
- Which cells/rows are uncovered
- Assessment: real gap vs. paraphrase vs. header noise

## Accuracy Issues
For each error found:
- Card number and file
- What the card says vs. what the PDF says
- Severity

## Quality Issues
For each issue:
- Card number and file
- Description of the problem
- Suggested fix

## Other Observations
- Patterns noticed
- Suggestions for improvement
- Things that are working well
```

---

## Technical Notes

- The PDF is in Hebrew (right-to-left). Page numbers appear in the bottom margin.
- PyMuPDF text extraction sometimes reverses Hebrew character order — if text looks garbled, try reading it right-to-left character by character.
- The `[עמ' XXX]` reference at the start of each card indicates which PDF page that fact comes from.
- Card numbering restarts within each batch file.
- Some batch files have "_redo" suffix — these are the canonical versions that replaced earlier attempts.
- `pilot_cards.md` and `pilot_v2_cards.md` both cover pages 162-164; `pilot_v2_cards.md` is the canonical version.
