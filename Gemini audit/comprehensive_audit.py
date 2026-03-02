import json
import glob
import re

cards_by_page = {}
card_count_by_page = {}

for file in glob.glob('*_cards.md'):
    with open(file, 'r', encoding='utf-8') as f:
        # We also need to get the Extra lines, but for simple keyword search, we'll just read everything
        # and not worry about Extra lines linking to the previous card. We can just keep all page text together.
        current_page = None
        for line in f:
            match = re.search(r"\[עמ'\s+(\d+)\](.*)", line)
            if match:
                current_page = int(match.group(1))
                cards_by_page.setdefault(current_page, []).append(line)
                card_count_by_page[current_page] = card_count_by_page.get(current_page, 0) + 1
            elif current_page is not None and line.strip().startswith("> Extra:"):
                cards_by_page[current_page].append(line)

with open('table_audit_report.json', 'r', encoding='utf-8') as f:
    report = json.load(f)

genuine_gaps = []
false_alarms = []

for p in report['pages']:
    page_num = p['page']
    samples = p.get('uncovered_samples', [])
    page_cards = cards_by_page.get(page_num, [])
    page_text = " ".join(page_cards)
    
    for sample in samples:
        text = sample['text'].strip()
        clean_text = re.sub(r'[^\w\sא-תA-Za-z]', '', text)
        words = clean_text.split()
        
        sig_words = [w for w in words if len(w) >= 2]
        if not sig_words:
            false_alarms.append((page_num, text, "Too short/Headers"))
            continue
            
        found_words = [w for w in sig_words if w in page_text]
        coverage = len(found_words) / len(sig_words)
        
        if coverage < 0.5:
            genuine_gaps.append((page_num, text, coverage))
        else:
            false_alarms.append((page_num, text, "Paraphrased/Found"))

with open('comprehensive_audit_results.txt', 'w', encoding='utf-8') as f:
    f.write("=== Critical Gaps: Table Missing Data ===\n")
    for gap in genuine_gaps:
        f.write(f"Page {gap[0]}: {gap[1]} (Coverage: {gap[2]:.2f})\n")
    
    f.write("\n=== Missing Pages or Low Density Pages ===\n")
    for page in range(1, 266):
        if page in [1, 5, 10, 28, 29, 30, 31, 40, 47, 67, 80, 82, 88, 101, 106, 217, 225, 245, 251, 264]:
            continue
        count = card_count_by_page.get(page, 0)
        if count == 0:
            f.write(f"Page {page} has NO cards.\n")
        elif count < 5:
            f.write(f"Page {page} has low card density: {count} cards.\n")
