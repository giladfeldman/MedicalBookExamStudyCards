# Nelson Pediatrics → Anki Flashcard Generation — Master Prompt v6

## ⚠️ TASK PHILOSOPHY — READ THIS FIRST

These flashcards serve ONE purpose: **helping a human medical student memorize and recall facts during exam review sessions.** Every design decision must serve this purpose.

**Core principles:**

1. **Cards are for HUMANS, not robots.** A card with 50 blanks is impossible to study. A card with 2-4 blanks is digestible, reviewable, and effective for spaced repetition.

2. **Each Anki note generates one review card PER cloze deletion.** A note with `{{c1::...}}` and `{{c2::...}}` creates 2 separate review cards. If a note has 50 cloze deletions, the student must review 50 separate cards from that single note — each showing the full paragraph with one blank. This is overwhelming, confusing, and counterproductive.

3. **Optimal cloze density: 1–5 deletions per note, MAXIMUM 5.** This means each note generates 1–5 review cards. Target 2-4 (sweet spot).

4. **More notes with fewer clozes >> Fewer notes with many clozes.** If a page has 15 testable facts, make 5 notes with 3 clozes each — NOT 1 note with 15 clozes.

5. **Every card must be instantly comprehensible.** When studying at 2 AM before an exam, the student should understand the card in <5 seconds.

6. **100% coverage, 0% hallucination.** Every fact from the PDF gets a card. No facts are invented.

---

## Input Files

### 1. Source PDF (IMAGE-FIRST — see extraction rules below)
- **Path**: `input/source.pdf`
- **Language**: Hebrew (RTL), with English medical terminology inline
- **Pages**: 265 (PyMuPDF is 0-indexed: PDF page 1 = index 0)
- **Content**: Dense summary tables, flowcharts, and comparison tables from Nelson 21st Edition
- **CRITICAL**: The PDF contains complex multi-column tables, flowcharts, and structured layouts. Plain text extraction (`get_text()`) **destroys** table structure, column alignment, and flowchart logic. **Always use high-DPI page images as the primary source**, with text extraction only as a supplementary cross-check.

### 2. Nelson 22nd Ed Full Textbook (for Extra field enrichment)
- **Full PDF**: `input/Full-book-Nelson-Textbook-of-Pediatrics-22nd-Edition-2024.pdf` (5518 pages)
- **Per-chapter PDFs**: `input/Nelson book chapters/{Part Name}/{Chapter NNN - Title}.pdf`
- **Usage**: After identifying diseases in a batch, read the relevant Nelson chapter(s) to:
  - Verify facts from the summary PDF
  - Source high-quality Extra field content (clinical pearls, differentials)
  - Cross-check ambiguous table content
- **IMPORTANT**: Only read chapters relevant to the current batch (typically 1-4 chapters, 20-40 pages each)

### 3. Chapter Reference (Nelson 22nd Ed contributor index)
- **Path**: `input/chapter_index.txt`
- **How to extract chapter list**:
  ```bash
  grep -oE "^[0-9]{1,3}(\.[0-9]+)?\. .+" input/chapter_index.txt | sort -t'.' -k1 -n -u
  ```

### 4. PDF Filename Index (for Google Drive chapter links)
- **Path**: `input/pdf_filenames.txt`
- **Content**: One filename per line, e.g. `Chapter 559 – Isolated Glomerular Diseases.pdf`
- **Usage**: Match chapter numbers to build Drive search URLs

---

## Image-First Extraction (CRITICAL)

The source PDF contains complex visual structures that text extraction destroys:
- **Multi-column comparison tables** (e.g., page 164: IgA vs Alport vs Thin GBM vs APSGN side by side)
- **Flowcharts with decision trees** (e.g., page 162: obesity evaluation algorithm)
- **Structured differential diagnosis tables** (e.g., page 163: causes of hematuria by location)

### Extraction Protocol:
1. **Primary source**: Export each page as a high-DPI PNG image (200 DPI). The card-writing agent reads directly from the image, preserving all visual structure.
2. **Secondary source**: Text extraction via PyMuPDF serves as a supplementary cross-check — useful for catching text that may be small or hard to read in the image.
3. **The card-writing agent receives BOTH**: the page image AND extracted text. It should primarily work from the image, using text to verify specific numbers or terms.
4. **Flowcharts/algorithms**: These contain facts not captured in body text. The agent must read and create cards from every decision node, branch, and endpoint in flowcharts.

---

## Anki Note Model: `Nelson Cloze v5` — 7 Fields

**MODEL_ID = 1607392322** (must be identical across ALL batches)

| # | Field | Content | Generation |
|---|-------|---------|------------|
| 1 | **Text** | Cloze card text (Hebrew + inline English). **MAX 5 cloze deletions.** | Write self-contained Hebrew sentence. Wrap 1-5 key facts in `{{c1::...}}` syntax. |
| 2 | **Context** | `{Disease} \| {Category} \| עמ' {page}` | Extract from PDF structure. Pipe-separated. |
| 3 | **Extra** | Source-bound clinical context: "why this matters" or "key differential." Shown on back only. Must come from the PDF or Nelson chapter — never from training data. | Use one of 3 patterns: (1) why it matters clinically/for exams, (2) key differential with `בניגוד ל-X`, (3) brief Nelson chapter fact. See Rule 9. |
| 4 | **NelsonChapter** | Primary Nelson 22nd Ed chapter + 1-3 related. Pipe-separated. | Look up in chapter_index.txt. Format: `559. Title \| 557. Related` |
| 5 | **SearchKeywords** | English search keywords, 3-8 words. | `disease + fact category + key terms` |
| 6 | **GoogleURL** | Google search URL, URL-encoded. | `https://www.google.com/search?q={url_encoded_keywords}` |
| 7 | **ChapterURL** | Google Drive search URL for the Nelson chapter PDF. | `https://drive.google.com/drive/search?q={chapter_pdf_filename}` |

### Field Examples

| Field | Example Content |
|-------|----------------|
| Text | `[עמ' 164] IgA Nephropathy — אפידמיולוגיה<br><br>IgA Nephropathy היא המחלה הגלומרולרית הכרונית {{c1::השכיחה ביותר}} בילדים. יחס בנים&gt;בנות ({{c2::1:2}}), גילאי {{c3::10-35}}` |
| Context | `IgA Nephropathy \| אפידמיולוגיה \| עמ' 164` |
| Extra | `חשוב להבדיל: ב-APSGN גילאי 5-12 ויחס 1:2, ב-IgA גילאי 10-35 ויחס 1:2 — שאלת הבדלה קלאסית בבחינה.` |
| NelsonChapter | `559. Isolated Glomerular Diseases Associated With Recurrent Gross Hematuria \| 557. Introduction to Glomerular Diseases` |
| SearchKeywords | `IgA nephropathy epidemiology children age gender` |
| GoogleURL | `https://www.google.com/search?q=IgA%20nephropathy%20epidemiology%20children%20age%20gender` |
| ChapterURL | `https://drive.google.com/drive/search?q=Chapter%20559` |

---

## Sub-Deck Hierarchy

Cards are organized into granular sub-decks by disease/topic:

```
נלסון 21::{specialty}::{disease or topic}
```

Examples:
- `נלסון 21::נפרולוגיה::IgA Nephropathy`
- `נלסון 21::נפרולוגיה::Goodpasture Syndrome`
- `נלסון 21::נפרולוגיה::HUS`
- `נלסון 21::מחלות זיהומיות::GBS`
- `נלסון 21::אנדוקרינולוגיה::סוכרת סוג 1`

Each disease gets its own sub-deck. The chapter_map.json for each batch defines the sub-deck name per disease.

When a batch covers general/overview content not tied to a specific disease, use a descriptive topic:
- `נלסון 21::נפרולוגיה::מבוא ובדיקות`
- `נלסון 21::המטולוגיה::אנמיה - סיווג כללי`

---

## Anki Templates

### Front Template (qfmt) — Question side:
```html
<div dir="rtl" style="text-align:right; font-family:'David','Arial Hebrew','Arial',sans-serif; font-size:20px; line-height:1.7; padding:20px;">
{{cloze:Text}}
</div>
```

### Back Template (afmt) — Answer side:
```html
<div dir="rtl" style="text-align:right; font-family:'David','Arial Hebrew','Arial',sans-serif; font-size:20px; line-height:1.7; padding:20px;">
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
</div>
```

### CSS:
```css
.card {
    direction: rtl;
    text-align: right;
    font-family: 'David', 'Arial Hebrew', 'Noto Sans Hebrew', 'Arial', sans-serif;
    font-size: 20px;
    line-height: 1.7;
    max-width: 720px;
    margin: 0 auto;
    padding: 24px;
    color: #1a1a1a;
    background: #fafafa;
}
.card * { direction: rtl; text-align: right; }
.cloze { font-weight: bold; color: #0055bb; }
.nightMode .card { color: #e0e0e0; background: #1e1e1e; }
.nightMode .cloze { color: #5cb8ff; }
```

---

## Tags per Card (3 tags)

- `disease::{disease_name}` — e.g., `disease::IgA_Nephropathy`
- `category::{category}` — e.g., `category::אפידמיולוגיה`
- `page::{page_number}` — e.g., `page::164`

---

## Markdown Card Format

Cards are written in markdown before conversion to APKG:

```markdown
# Batch NN — Section Name עמ' X-Y

## עמ' X: Topic Name

1. [עמ' X] Disease — Category - Card text with **[cloze1]** and **[cloze2]** {english keywords}
   > Extra: Additional context or clinical pearl for this card.

2. [עמ' X] Disease — Category - Another fact **[fact]** {keywords}
   > Extra: Supplementary info.
```

**Conventions:**
- `**[text]**` = cloze deletion target → becomes `{{c1::text}}`, `{{c2::text}}`, etc.
- `{text at end}` = English search keywords → SearchKeywords field
- `[עמ' XXX]` at start = page reference → Context field + page tag
- `> Extra: ...` on line after card = Extra field content (optional but encouraged)
- After page ref: `Disease — Category - ` then card body
- `##` headers organize by page/topic (not part of card content)

---

## Cloze Selection Strategy — Discriminative Clozing

### Core Principle: Cloze What Exams Test

Not all facts are equal. **Prioritize hiding facts that distinguish between similar conditions, that exams test, and that require active recall.** Avoid hiding obvious or generic terms that any student could guess from context.

### What Makes a GOOD Cloze Target:

| Priority | Category | Example |
|----------|----------|---------|
| **Highest** | **Key differentiators** between similar diseases | C3 **[תקין]** ב-IgA vs **[נמוך]** ב-PIGN |
| **Highest** | **Specific numbers** that distinguish (thresholds, ratios, timelines) | גילאי **[5-12]**, חביון **[1-2]** שבועות |
| **High** | **Pathognomonic findings** | **[Anterior Lenticonus]** פתוגנומוני ל-Alport |
| **High** | **Gene names, mutations, chromosomes** | מוטציה ב-**[COL4A5]** |
| **High** | **Drug names and specific treatments** | **[Eculizumab]** ב-HUS גנטי |
| **Medium** | **Inheritance patterns** | הורשת **[XL]** ב-85% |
| **Medium** | **Lab value interpretations** | ASLO מוגבר ב-**[70%]** |

### What to AVOID Clozing:

| Avoid | Why | Example of BAD cloze |
|-------|-----|---------------------|
| The disease name itself | It provides context | ~~**[IgA Nephropathy]** היא המחלה...~~ |
| Generic/obvious terms | Any student could guess them | ~~השמנה מבוססת על **[BMI]**~~ |
| Category words | They're in the title already | ~~סיבות **[גנטיות]** להשמנה~~ |
| Words guessable from context | No recall challenge | ~~רבדומיוליזיס גורם ל-**[AKI]** (אס"ק כליות)~~ when the Hebrew says it |

### Cloze Density Rules — MAXIMUM 5 PER NOTE

| Rule | Description |
|------|-------------|
| **MAX 5 clozes** | Each `**[...]**` = one cloze. Never exceed 5 per card. |
| **Target 2–4** | Sweet spot for memorization. |
| **Split dense content** | 12 testable facts → 3-4 notes with 3-4 clozes each. |
| **One concept per note** | Each note tests ONE relationship, not an entire disease. |
| **Do NOT cloze the disease name** | It provides context — keep it visible. |

### The "Exam Question" Test
Before clozing a word, ask: **"Could this be a wrong answer in a multiple-choice question?"**
- If YES → cloze it (it's discriminating)
- If NO (because it's the only plausible answer) → don't cloze it

**GOOD** (3 discriminative clozes):
```
5. [עמ' 164] IgA Nephropathy — אפידמיולוגיה - המחלה הגלומרולרית הכרונית **[השכיחה ביותר]** בילדים. בנים>בנות (**[1:2]**), גילאי **[10-35]** {IgA nephropathy epidemiology children age gender}
   > Extra: חשוב להבדיל: ב-APSGN גילאי 5-12, ב-IgA גילאי 10-35 — שאלת הבדלה קלאסית בבחינה.
```

**BAD** (generic/obvious clozes):
```
5. [עמ' 162] השמנה — הגדרות - ההגדרות מבוססות על אחוזוני **[BMI]** (משקל בק"ג חלקי **[גובה]** במטרים בריבוע)
```
→ BMI and "height" are obvious — nothing discriminative here.

**BAD** (32 clozes — impossible to study):
```
6. [עמ' 166] Goodpasture ו-HUS - **[Goodpasture]**: אוטואימוני... [32 clozes in one note]
```
→ Split into 6 notes with 3-5 clozes each.

---

## Card Generation Rules

### Rule 1: 100% Coverage — ENFORCED DENSITY MINIMUMS

**Every fact, number, gene name, drug, classification must appear in at least one card.**

**Minimum density formula (MANDATORY — build script validates):**

| Source chars/page | Minimum notes/page | Expected range |
|-------------------|--------------------|----------------|
| >6000 chars | **at least 15 notes** | 15-25 |
| 4000-6000 chars | **at least 10 notes** | 10-18 |
| 2000-4000 chars | **at least 5 notes** | 5-12 |
| <2000 chars | **at least 3 notes** | 3-5 |
| Image-only pages | 0 (or cards from image content) | 0-5 |

**Quick check: 2.5 notes per 1,000 source chars.** A page with 7,000 chars → minimum 17 notes. A page with 4,000 chars → minimum 10 notes. If you're below this, you are SKIPPING CONTENT.

**Per-topic coverage requirement:** Every page must have at least one card for each of these categories that appear in the source:
- Epidemiology / prevalence / risk factors
- Genetics / pathogenesis / etiology
- Clinical presentation / symptoms
- Diagnosis / lab findings / imaging
- **Treatment / drugs / dosing** (NEVER skip treatment — see Rule 11)
- Prognosis / complications / follow-up

**After writing: run `python scripts/validate_density.py work/current_cards.md work/current_extraction.json {start_page} {end_page}` to verify.**

### Rule 2: Zero Hallucination
- Only facts from the PDF. Never add from training data.
- If text unclear, view page image to verify.

### Rule 3: Self-Contained Cards
- Every card understandable alone
- Prepend disease name + context for continuations
- Resolve pronouns ("אלו" → specify what)
- Include category in title

### Rule 4: Cloze Density — MAX 5, Distribution Enforced

**Hard limit:** MAX 5 cloze deletions per note. Build script validates this.

**Distribution caps (MANDATORY — validate_density.py checks):**
- At least **50%** of cards in a batch must have **≤3 clozes**
- No more than **20%** of cards may have **5 clozes** (the maximum)
- Target average: **2.5-3.2 clozes/card** (batch 1a gold standard = 3.2)

**Anti-bloat rule:** If you find yourself at 4-5 clozes, the card probably covers too much. Split it into two cards with 2-3 clozes each. More cards with fewer clozes is ALWAYS better than fewer cards stuffed to the max.

**Card text length guidance:**
- Target: **250-320 characters** per card text
- Soft cap: **380 characters** — cards exceeding this should be split
- If a card exceeds 380 chars, it almost certainly covers more than one concept

**"One concept per note" — concrete test:**
A card passes the one-concept test if you can describe what it tests in ≤5 words (e.g., "IgA epidemiology numbers", "CF treatment drugs", "DiGeorge genetics"). If you need 10+ words, split the card.

### Rule 5: Nelson Chapter Mapping
- Use chapter_index.txt to identify chapters
- Primary + 1-3 related chapters per card
- Format: `{num}. {title} | {num}. {title}`

### Rule 6: Search Keywords
- 3-8 English words per card
- Disease + fact category + key terms
- Build GoogleURL: `https://www.google.com/search?q={url_encoded}`

### Rule 7: Chapter URL (Google Drive)
- Match chapter number to filename in pdf_filenames.txt
- Build: `https://drive.google.com/drive/search?q={filename}`
- If no match found, leave ChapterURL empty

### Rule 8: Page Numbers
- In Context field: `... | עמ' 164`
- In tags: `page::164`

### Rule 9: Extra Field — Source-Bound Clinical Relevance

The Extra field appears on the card back after the student answers. It should make the student think **"oh, that's why this matters"** or **"that's how I distinguish this from X."**

**Three approved patterns (use one per card):**

1. **"Why does this matter?"** — Explain the clinical or exam significance of the cloze fact.
   - Example: `"C3 תקין ב-IgA הוא נקודת הבדלה מרכזית מ-PIGN — שאלה קלאסית בבחינה."`

2. **"Key differential"** — Explicitly compare to a similar condition using `בניגוד ל-X שבו Y`.
   - Example: `"בניגוד ל-PIGN שם החביון 1-3 שבועות, ב-IgA ההמטוריה מופיעה מיד עם הזיהום (synpharyngitic)."`

3. **"Clinical context"** — A brief fact from the Nelson chapter that enriches understanding.
   - Example: `"Oxford MEST-C classification קובעת פרוגנוזה לפי ממצאי ביופסיה."`

**STRICT rules:**
- **Source-bound ONLY**: Extra content must come from the summary PDF or the Nelson chapter. NEVER add facts from training data.
- **No restating**: Don't just rephrase the card text in different words.
- **No tangential trivia**: Every Extra sentence must be directly relevant to the specific fact being tested.
- **Keep it short**: 1-2 sentences maximum. The student sees this during rapid review.
- Does NOT replace making cloze cards — it supplements. Testable facts need their own cards.

### Rule 10: Sub-Decks
- Each disease/major topic gets its own sub-deck
- Format: `נלסון 21::{specialty_he}::{disease/topic}`
- chapter_map.json defines the sub_deck per disease
- General/overview content → `נלסון 21::{specialty}::מבוא`

### Rule 11: Treatment Content MUST Be Cloze-Tested

**Treatment, drugs, dosing, and management protocols are HIGH-YIELD exam content.** They must appear as cloze-tested cards — NEVER relegated only to the Extra field.

For every disease that has treatment information in the source PDF:
- **Drug names** → cloze target (e.g., `טיפול ב-**[Eculizumab]**`)
- **Dosing/duration** → cloze target (e.g., `למשך **[10-14]** ימים`)
- **First-line vs second-line** → cloze target
- **Step therapy / escalation** → separate card per step
- **Surgical indications** → cloze target

**BAD pattern (treatment buried in Extra):**
```
5. [עמ' 95] CF — אבחנה - Sweat Chloride **[>60]** mEq/L אבחנתי {CF diagnosis sweat chloride}
   > Extra: טיפול כולל DNase, Hypertonic Saline, Azithromycin.
```
→ Those 3 drugs MUST be their own cloze-tested card(s).

**GOOD pattern (treatment gets its own card):**
```
6. [עמ' 95] CF — טיפול תרופתי - Mucolytics: **[Dornase Alfa]** (DNase). להפחתת דלקת: **[Azithromycin]**. היפרטוני: **[NaCl 7%]** בשאיפה {CF treatment DNase azithromycin hypertonic saline}
```

---

## Build Script (scripts/build_apkg.py)

See scripts/build_apkg.py for the full build and validation code.

Key aspects:
- Parses markdown → 7-field notes
- Creates sub-decks per disease via genanki.Deck hierarchy
- Validates: max 5 clozes, all fields populated, correct model structure
- Page coverage audit
- APKG structure verification via sqlite3

---

## Concrete Examples (7-field format)

### Example 1: Epidemiology — discriminative numbers (3 clozes)
```
1. [עמ' 164] IgA Nephropathy — אפידמיולוגיה - המחלה הגלומרולרית הכרונית **[השכיחה ביותר]** בילדים. יחס בנים>בנות (**[1:2]**), גילאי **[10-35]** {IgA nephropathy epidemiology children age gender}
   > Extra: חשוב להבדיל: ב-APSGN גילאי 5-12, ב-IgA גילאי 10-35 — שאלת הבדלה קלאסית בבחינה.
```

### Example 2: Genetics — specific genes/loci (3 clozes)
```
2. [עמ' 164] IgA Nephropathy — גנטיקה - קורלציה לשינויים ב-**[6q22-23]**. קומפלקסים אימונים עקב ריבוי **[IgA1]** שלא עברו **[גליקוזילציה]** בסרום {IgA nephropathy genetics 6q22 IgA1 glycosylation}
   > Extra: Galactose-deficient IgA1 יוצר קומפלקסים שמשקעים במזנגיום — זו הפתוגנזה המרכזית.
```

### Example 3: Clinical — key differentiator from similar disease (3 clozes)
```
3. [עמ' 164] IgA Nephropathy — קליניקה - המטוריה גסה מופיעה **[1-2]** ימים לאחר URTI/GI (בניגוד לחביון של **[1-3 שבועות]** ב-PIGN). פרוטאינוריה בד"כ מתחת ל-**[1]** גרם/יממה {IgA nephropathy clinical hematuria URTI latency PIGN}
   > Extra: ב-PIGN חביון 1-3 שבועות מגרון / 3-6 מעור; ב-IgA המטוריה synpharyngitic — זו נקודת ההבדלה העיקרית.
```

### Example 4: Pathology — pathognomonic findings (3 clozes)
```
4. [עמ' 164] IgA Nephropathy — פתולוגיה - IF: שקיעה דיפוזית של **[IgA]** במזנגיום, לעיתים עם **[C3]**. מיק' אור: פרוליפרציה **[פוקלית וסגמנטלית]** של המזנגיום {IgA nephropathy pathology mesangial IgA C3 immunofluorescence}
   > Extra: בניגוד ל-APSGN שם השקיעה granular "lumpy-bumpy" של Ig+C3 — ב-IgA השקיעה ספציפית של IgA במזנגיום.
```

### Example 5: Lab values — key differential (3 clozes)
```
5. [עמ' 164] IgA Nephropathy — מעבדה - רמות **[C3]** בדם תקינות (בניגוד ל-PIGN). רמות IgA מוגברות רק ב-**[15%]** ואינן **[אבחנתיות]** {IgA nephropathy lab complement C3 serum IgA}
   > Extra: C3 תקין = IgA/Alport/Thin GBM. C3 נמוך = PIGN/MPGN/SLE — זו שאלת סיווג קלאסית.
```

---

## Lessons Learned (from v1-v5)

1. **#1 problem was excessive cloze density** — batches had 27-56 clozes/note. MAX 5 is non-negotiable.
2. **Context loss between sessions** — solved by progress.json + sub-agents. Each phase runs independently.
3. **Missing pages on resume** — solved by per-page coverage audit in every batch.
4. **Image pages skipped** — always export as PNG and create cards from visual content.
5. **Fields simplified away** — the 2-field shortcut (Text, Extra) lost critical metadata. All 7 fields mandatory.
6. **Flat decks** — one giant deck per section is harder to study than granular sub-decks per disease.
7. **Text extraction loses table structure** — the PDF has complex multi-column comparison tables, flowcharts, and structured layouts. Plain `get_text()` interleaves columns randomly. Solution: image-first extraction at 200 DPI.
8. **Weak cloze selection** — hiding obvious/generic terms (e.g., "BMI", "genetics") doesn't challenge recall. Solution: discriminative clozing — prioritize differentiators and exam-testable specifics.
9. **Extra field hallucination** — Extras that add unsourced facts or just restate the card are unhelpful. Solution: source-bound only, using "why it matters" or "key differential" patterns.
10. **Nelson chapters enrich Extras** — reading the relevant Nelson 22nd Ed chapter provides authoritative Extra content and helps verify ambiguous summary PDF text.
11. **Density degradation across batches** — without enforcement, card density drops ~4x over time (17.5→4.9 notes/page). Root causes: (a) cards get "bloated" — cramming more facts per card instead of splitting, (b) MAX 5 clozes treated as a target instead of a ceiling, (c) treatment/dosing/prognosis systematically skipped or buried in Extra. Solution: formula-based density minimums (Rule 1), cloze distribution caps (Rule 4), treatment-must-be-carded rule (Rule 11), and automated validation after every card-writing phase.
12. **Gold standard reference prevents drift** — every card-writing sub-agent MUST receive 10-15 example cards from batch 1a as a concrete style reference. Without this anchor, writing style drifts toward bloated, over-clozed cards.
