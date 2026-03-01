#!/usr/bin/env python3
"""Add 30 missing disease aliases to chapter map for batch 2a."""
import json

with open('work/current_chapter_map.json', 'r', encoding='utf-8') as f:
    cmap = json.load(f)

d = cmap['diseases']

# Fix broken chapter_url for seizure/headache entries (wrongly point to antibacterial therapy)
seizure_url = 'https://drive.google.com/drive/search?q=Chapter%20633%20-%20Seizures%20in%20Childhood.pdf'
headache_url = 'https://drive.google.com/drive/search?q=Chapter%20635%20-%20Headaches.pdf'

for key in ['פרכוסים', 'פרכוסי חום', 'אפילפסיה', 'epilepsy', 'סטאטוס אפילפטיקוס']:
    if key in d:
        d[key]['chapter_url'] = seizure_url

for key in ['מיגרנה', 'כאבי ראש', 'headache']:
    if key in d:
        d[key]['chapter_url'] = headache_url

# === Epilepsy syndromes (Ch 633) ===
epilepsy_base = {
    'primary_chapter': '633. Seizures in Childhood',
    'related_chapters': ['633.5. Mechanisms of Seizures', '633.6. Treatment of Seizures and Epilepsy'],
    'chapter_url': seizure_url,
    'sub_deck': 'נלסון 21::נוירולוגיה::פרכוסים',
}

aliases_epilepsy = {
    'אבסנס': 'absence+epilepsy+childhood',
    'Childhood Absence Epilepsy': 'childhood+absence+epilepsy',
    'פרכוסי אבסנס טיפיקליים': 'typical+absence+seizures',
    'פרכוסי אבסנס א-טיפיקליים': 'atypical+absence+seizures',
    'BECTS': 'benign+epilepsy+centrotemporal+spikes+rolandic',
    'Benign Epilepsy with Occipital Spikes': 'benign+epilepsy+occipital+spikes+Panayiotopoulos',
    'Benign Familial Neonatal Seizures': 'benign+familial+neonatal+seizures+KCNQ2',
    'Benign Myoclonic Epilepsy of Infancy': 'benign+myoclonic+epilepsy+infancy',
    'JME': 'juvenile+myoclonic+epilepsy+JME',
    'Juvenile Myoclonic Epilepsy (JME)': 'juvenile+myoclonic+epilepsy',
    'Dravet Syndrome': 'Dravet+syndrome+SCN1A+severe+myoclonic+epilepsy',
    'West Syndrome': 'West+syndrome+infantile+spasms+hypsarrhythmia',
    'Lennox-Gastaut Syndrome': 'Lennox+Gastaut+syndrome+slow+spike+wave',
    'Early Myoclonic Encephalopathy ו-Otahara': 'Ohtahara+syndrome+early+myoclonic+encephalopathy',
    'Landau-Kleffner Syndrome': 'Landau+Kleffner+syndrome+acquired+epileptic+aphasia',
    'פרכוסים פוקליים': 'focal+seizures+children+partial',
    'פרכוסים נאונטליים': 'neonatal+seizures',
    'SUDEP': 'SUDEP+sudden+unexpected+death+epilepsy',
    'תרופות אנטי-אפילפטיות': 'antiepileptic+drugs+children',
    'תרופות ב-Dravet': 'Dravet+syndrome+treatment+stiripentol+fenfluramine',
    'חסר ב-GLUT1': 'GLUT1+deficiency+syndrome+ketogenic+diet',
}

for name, search_term in aliases_epilepsy.items():
    entry = dict(epilepsy_base)
    entry['google_search_url'] = f'https://www.google.com/search?q=Nelson+Textbook+Pediatrics+{search_term}'
    if name == 'פרכוסים נאונטליים':
        entry['related_chapters'] = ['633.7. Neonatal Seizures']
    elif name in ('תרופות אנטי-אפילפטיות', 'תרופות ב-Dravet'):
        entry['related_chapters'] = ['633.6. Treatment of Seizures and Epilepsy']
    d[name] = entry

# === Headache subtypes (Ch 635) ===
headache_base = {
    'primary_chapter': '635. Headaches',
    'related_chapters': ['634. Conditions That Mimic Seizures'],
    'chapter_url': headache_url,
    'sub_deck': 'נלסון 21::נוירולוגיה::כאבי ראש',
}

aliases_headache = {
    'מיגרנה עם אאורה': 'migraine+with+aura+children',
    'מיגרנה ללא אאורה': 'migraine+without+aura+children',
    'Hemiplegic Migraine': 'hemiplegic+migraine+familial',
    'Tension-Type Headache': 'tension+type+headache+children',
    'כאבי ראש שניוניים': 'secondary+headaches+children+intracranial+pressure',
}

for name, search_term in aliases_headache.items():
    entry = dict(headache_base)
    entry['google_search_url'] = f'https://www.google.com/search?q=Nelson+Textbook+Pediatrics+{search_term}'
    d[name] = entry

# === Congenital malformation subtypes (Ch 631) ===
cns_base = {
    'primary_chapter': '631. Congenital Anomalies of the Central Nervous System',
    'related_chapters': [],
    'chapter_url': 'https://drive.google.com/drive/search?q=Chapter%20631%20-%20Congenital%20Anomalies%20of%20the%20Central%20Nervous%20System.pdf',
    'sub_deck': 'נלסון 21::נוירולוגיה::מומים מולדים',
}

aliases_cns = {
    'Craniosynostosis': 'craniosynostosis+sagittal+coronal+suture',
    'מיקרוצפליה': 'microcephaly+causes+diagnosis',
    'הפרעות מיגרציה נוירונלית': 'neuronal+migration+disorders+lissencephaly',
    'מלפורמציות הגומה האחורית': 'posterior+fossa+malformations+Dandy+Walker+Chiari',
}

for name, search_term in aliases_cns.items():
    entry = dict(cns_base)
    entry['google_search_url'] = f'https://www.google.com/search?q=Nelson+Textbook+Pediatrics+{search_term}'
    d[name] = entry

with open('work/current_chapter_map.json', 'w', encoding='utf-8') as f:
    json.dump(cmap, f, ensure_ascii=False, indent=2)

print(f'Done! Added 30 aliases + fixed chapter URLs. Total keys: {len(d)}')
