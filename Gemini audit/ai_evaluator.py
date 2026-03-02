import json
import glob
import re

cards_by_page = {}

for file in glob.glob('*_cards.md'):
    with open(file, 'r', encoding='utf-8') as f:
        current_page = None
        for line in f:
            match = re.search(r"\[עמ'\s+(\d+)\](.*)", line)
            if match:
                current_page = int(match.group(1))
                cards_by_page.setdefault(current_page, []).append(line.strip())
            elif current_page is not None and line.strip().startswith("> Extra:"):
                cards_by_page[current_page].append(line.strip())

with open('table_audit_report.json', 'r', encoding='utf-8') as f:
    report = json.load(f)

with open('ai_review_task.txt', 'w', encoding='utf-8') as f:
    for p in report['pages']:
        page_num = p['page']
        samples = p.get('uncovered_samples', [])
        page_text = " ".join(cards_by_page.get(page_num, []))
        
        genuine_gaps = []
        for sample in samples:
            text = sample['text'].strip()
            clean_text = re.sub(r'[^\w\sא-תA-Za-z]', '', text)
            words = clean_text.split()
            sig_words = [w for w in words if len(w) >= 2]
            if sig_words:
                found_words = [w for w in sig_words if w in page_text]
                coverage = len(found_words) / len(sig_words)
                if coverage < 0.5:
                    genuine_gaps.append(text)
        
        if genuine_gaps:
            f.write(f"\n================ PAGE {page_num} ================\n")
            f.write("MISSING SAMPLES FROM TABLE:\n")
            for gap in genuine_gaps:
                f.write(f" - {gap}\n")
            f.write("\nCARDS FOR THIS PAGE:\n")
            for card in cards_by_page.get(page_num, []):
                f.write(f"{card}\n")
