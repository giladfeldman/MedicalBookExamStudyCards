# Claude Code Prompts for Nelson Anki Project

## PILOT RUN (first time — validates the full pipeline)

Paste this into Claude Code:

```
Read CLAUDE.md, prompt.md, and orchestrator.md carefully. Then run the pilot batch:

PILOT BATCH: Pages 162-164 (Nephrology — obesity overview on p162, hematuria workup on p163, glomerular diseases on p164)

Execute ALL 5 phases using Task tool sub-agents for each phase:

Phase 1 - EXTRACTION:
Run scripts/extract.py for pages 162-164. Save to work/current_extraction.json. Update progress.json.

Phase 2 - CHAPTER MAPPING:
Read work/current_extraction.json to identify diseases/topics. Search input/chapter_index.txt and input/pdf_filenames.txt for matching Nelson chapters. Build work/current_chapter_map.json with this structure per disease:
{
  "diseases": {
    "Disease_Key": {
      "primary_chapter": "559. Chapter Title",
      "related_chapters": ["557. Related"],
      "chapter_url": "https://drive.google.com/drive/search?q=Chapter%20559%20...",
      "sub_deck": "נלסון 21::נפרולוגיה::Disease Name"
    }
  }
}
Update progress.json.

Phase 3 - CARD WRITING:
Read prompt.md rules carefully (especially MAX 5 clozes, self-contained cards, Extra field, markdown format). Read work/current_extraction.json for all 3 pages. Write cards to work/current_cards.md.

Rules reminder:
- MAX 5 cloze deletions per note (target 2-4)
- Every fact from PDF gets a card (100% coverage)
- Each card self-contained with disease name + category in title
- Extra field: 1-2 sentences of supplementary context per card
- English keywords in {curly braces} at end
- Format: N. [עמ' XXX] Disease — Category - text with **[cloze]** {keywords}
  > Extra: supplementary context

After writing, run page coverage audit: every page must have cards.
Update progress.json.

Phase 4 - APKG BUILD:
Run: python scripts/build_apkg.py work/current_cards.md work/current_chapter_map.json output/pilot_nephrology.apkg נפרולוגיה pilot
Verify: all notes ≤5 clozes, all 7 fields populated, sub-decks created.
Copy work/current_cards.md to output/pilot_cards.md.
Update progress.json.

Phase 5 - VERIFICATION:
Run: python scripts/verify.py output/pilot_nephrology.apkg
Update progress.json to mark pilot complete.
Update todo.md with results.
Print final summary: notes count, cloze count, avg clozes/note, sub-decks, pages covered.
```

## BATCH PROCESSING (after pilot is approved)

Paste this to process the next batch:

```
Read CLAUDE.md, orchestrator.md, and progress.json. Process the next pending batch following all 5 phases with Task tool sub-agents. Follow the exact same pipeline as the pilot. Save all outputs. Update progress.json after each phase.
```

## RESUME AFTER INTERRUPTION

```
Read progress.json. There should be an in-progress batch. Check which phases are complete and resume from the first incomplete phase. Do NOT re-run completed phases — read their output files from work/. Continue the pipeline to completion.
```

## FULL PRODUCTION RUN (process all remaining sections)

```
Read CLAUDE.md, orchestrator.md, and progress.json. Process ALL remaining pending sections one batch at a time. For each batch:
1. Follow all 5 phases with Task tool sub-agents
2. Save outputs after each phase
3. Update progress.json after each phase
4. After each batch completes, immediately start the next one
5. For sections >8 pages, split into sub-batches of 5-8 pages each
Continue until all 21 sections are complete or you run out of context.
If context is getting low, save all current work and stop cleanly — the next run will resume.
```
