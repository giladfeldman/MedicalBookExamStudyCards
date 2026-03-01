#!/usr/bin/env python3
"""Apply format fixes to card parts and concatenate into current_cards.md."""
import re, glob

parts = sorted(glob.glob('work/cards_part*.md'))
all_content = []

for fname in parts:
    with open(fname, 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix 1: Convert pre-converted {{cN::text}} back to **[text]**
    content = re.sub(r'\{\{c\d+::([^}]+)\}\}', r'**[\1]**', content)

    # Fix 2: Fix double-asterisk artifacts
    content = re.sub(r'\*{4}\[([^\]]+)\]\*{4}', r'**[\1]**', content)

    # Fix 3: Fix double em-dash in card lines
    lines = content.split('\n')
    fixed_lines = []
    for line in lines:
        if re.match(r'^\d+\.', line.strip()):
            parts_line = line.split(' — ')
            if len(parts_line) >= 3:
                line = parts_line[0] + ' — ' + parts_line[1] + ' - ' + ' — '.join(parts_line[2:])
        fixed_lines.append(line)
    content = '\n'.join(fixed_lines)

    with open(fname, 'w', encoding='utf-8') as f:
        f.write(content)

    all_content.append(content)
    print(f'Fixed: {fname}')

# Concatenate
combined = '\n\n'.join(all_content)
with open('work/current_cards.md', 'w', encoding='utf-8') as f:
    f.write(combined)

# Count cards
card_count = len(re.findall(r'^\d+\.', combined, re.MULTILINE))
print(f'\nConcatenated {len(parts)} parts into work/current_cards.md')
print(f'Total cards: {card_count}')

# Check page coverage
pages_found = set()
for m in re.finditer(r"\[עמ'\s*(\d+)\]", combined):
    pages_found.add(int(m.group(1)))
for p in range(57, 67):
    status = "OK" if p in pages_found else "MISSING!"
    print(f'  Page {p}: {status}')

# Check max clozes
max_clozes = 0
for line in combined.split('\n'):
    if re.match(r'^\d+\.', line.strip()):
        count = len(re.findall(r'\*\*\[', line))
        if count > max_clozes:
            max_clozes = count
        if count > 5:
            print(f'  WARNING: {count} clozes on: {line[:80]}...')
print(f'Max clozes on any card: {max_clozes}')
