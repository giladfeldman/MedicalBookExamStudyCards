#!/usr/bin/env python3
"""Update progress.json after a batch phase completes."""

import json, sys, os
from datetime import datetime, timezone

PROGRESS_FILE = "progress.json"

def load():
    with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save(data):
    data['last_updated'] = datetime.now(timezone.utc).isoformat()
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ progress.json updated at {data['last_updated']}")

def start_batch(batch_id, section_name, start_page, end_page):
    p = load()
    p['current_batch'] = {
        'batch_id': batch_id,
        'section': section_name,
        'start_page': start_page,
        'end_page': end_page,
        'page_count': end_page - start_page + 1,
        'status': 'in_progress',
        'phases': {
            'extraction': 'pending',
            'chapter_map': 'pending',
            'cards': 'pending',
            'apkg': 'pending',
            'verified': 'pending'
        },
        'notes_count': 0,
        'cloze_count': 0,
        'cards_written': 0
    }
    save(p)

def complete_phase(phase_name, **kwargs):
    p = load()
    if not p.get('current_batch'):
        print("❌ No current batch in progress!")
        return
    p['current_batch']['phases'][phase_name] = 'complete'
    for k, v in kwargs.items():
        p['current_batch'][k] = v
    save(p)

def complete_batch(notes_count, cloze_count):
    p = load()
    batch = p['current_batch']
    batch['status'] = 'complete'
    batch['notes_count'] = notes_count
    batch['cloze_count'] = cloze_count
    p['completed_batches'].append(batch)
    p['stats']['pages_processed'] += batch['page_count']
    p['stats']['total_notes'] += notes_count
    p['stats']['total_clozes'] += cloze_count
    p['current_batch'] = None
    # Set next batch
    # (orchestrator handles this logic)
    save(p)
    print(f"🎉 Batch {batch['batch_id']} complete: {notes_count} notes, {cloze_count} clozes")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "status":
        p = load()
        print(json.dumps(p, indent=2, ensure_ascii=False))
    elif cmd == "start":
        start_batch(sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]))
    elif cmd == "phase":
        complete_phase(sys.argv[2])
    elif cmd == "done":
        complete_batch(int(sys.argv[2]), int(sys.argv[3]))
