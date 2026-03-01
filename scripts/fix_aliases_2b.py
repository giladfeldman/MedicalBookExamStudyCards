#!/usr/bin/env python3
"""Add missing disease aliases to chapter map for batch 2b."""
import json

with open('work/current_chapter_map.json', 'r', encoding='utf-8') as f:
    cmap = json.load(f)

d = cmap['diseases']

# Helper to get base from an existing key
def get_base(key):
    return d[key].copy()

# === Neurocutaneous aliases ===
ncs_base = get_base('Sturge-Weber Syndrome')
d['Sturge-Weber'] = {**ncs_base, 'sub_deck': 'נלסון 21::נוירולוגיה::סינדרומים נוירו-קוטנאיים'}

d['VHL'] = {
    'primary_chapter': '636. Neurocutaneous Syndromes',
    'related_chapters': [],
    'chapter_url': ncs_base['chapter_url'],
    'sub_deck': 'נלסון 21::נוירולוגיה::סינדרומים נוירו-קוטנאיים',
    'google_search_url': 'https://www.google.com/search?q=Nelson+Textbook+Pediatrics+Von+Hippel+Lindau+syndrome'
}

# === Movement disorders aliases ===
mvt_base = get_base('הפרעות תנועה')

d['אטקסיה-טלנג\'יאקטזיה'] = {**mvt_base, 'google_search_url': 'https://www.google.com/search?q=Nelson+Textbook+Pediatrics+ataxia+telangiectasia+ATM+gene'}
d['פרידריך אטקסיה'] = {**mvt_base, 'google_search_url': 'https://www.google.com/search?q=Nelson+Textbook+Pediatrics+Friedreich+ataxia+frataxin+GAA'}
d['אטקסיה צרבלרית אקוטית'] = {**mvt_base, 'google_search_url': 'https://www.google.com/search?q=Nelson+Textbook+Pediatrics+acute+cerebellar+ataxia+post+infectious'}
d['כוריאה ע"ש סידנהאם'] = {**mvt_base, 'google_search_url': 'https://www.google.com/search?q=Nelson+Textbook+Pediatrics+Sydenham+chorea+rheumatic+fever'}
d['Opsoclonus-Myoclonus-Ataxia Syndrome'] = {**mvt_base, 'google_search_url': 'https://www.google.com/search?q=Nelson+Textbook+Pediatrics+opsoclonus+myoclonus+neuroblastoma'}
d['Essential Tremor'] = {**mvt_base, 'google_search_url': 'https://www.google.com/search?q=Nelson+Textbook+Pediatrics+essential+tremor+children'}
d['אתטוזיס ודיסטוניה'] = {**mvt_base, 'google_search_url': 'https://www.google.com/search?q=Nelson+Textbook+Pediatrics+dystonia+athetosis+children'}
d['Benign Neonatal Sleep Myoclonus'] = {**mvt_base, 'google_search_url': 'https://www.google.com/search?q=Nelson+Textbook+Pediatrics+benign+neonatal+sleep+myoclonus'}

# === Encephalopathies aliases ===
enc_base = get_base('אנצפלופתיות')

d['Leigh Disease'] = {**enc_base, 'google_search_url': 'https://www.google.com/search?q=Nelson+Textbook+Pediatrics+Leigh+disease+subacute+necrotizing+encephalopathy'}
d['Anti-NMDAR אנצפליטיס'] = {**enc_base, 'google_search_url': 'https://www.google.com/search?q=Nelson+Textbook+Pediatrics+anti+NMDAR+encephalitis+autoimmune'}
d['Anti-NMDAR'] = {**enc_base, 'google_search_url': 'https://www.google.com/search?q=Nelson+Textbook+Pediatrics+anti+NMDA+receptor+encephalitis+treatment'}

# === Demyelinating aliases ===
dem_base = get_base('מחלות דה-מייאלינטיביות')

d['Acute Flaccid Myelitis'] = {**dem_base, 'google_search_url': 'https://www.google.com/search?q=Nelson+Textbook+Pediatrics+acute+flaccid+myelitis+enterovirus+D68'}
d['MOG-Associated'] = {**dem_base, 'google_search_url': 'https://www.google.com/search?q=Nelson+Textbook+Pediatrics+MOG+antibody+associated+disorder+children'}
d['POMS vs NMOSD vs MOG'] = {**dem_base, 'google_search_url': 'https://www.google.com/search?q=Nelson+Textbook+Pediatrics+pediatric+MS+NMOSD+MOG+comparison'}

# === Stroke aliases ===
str_base = get_base('שבץ')

d['שבץ בילדים'] = {**str_base, 'google_search_url': 'https://www.google.com/search?q=Nelson+Textbook+Pediatrics+pediatric+stroke+risk+factors'}
d['AIS פרינטאלי'] = {**str_base, 'google_search_url': 'https://www.google.com/search?q=Nelson+Textbook+Pediatrics+perinatal+arterial+ischemic+stroke'}

# === Myopathy aliases ===
myo_base = get_base('מיופתיות')

d['Myotonic Dystrophy DM1'] = {
    'primary_chapter': '649. Muscular Dystrophies',
    'related_chapters': ['648. Developmental Disorders of Muscle'],
    'chapter_url': myo_base['chapter_url'],
    'sub_deck': 'נלסון 21::נוירולוגיה::מיופתיות',
    'google_search_url': 'https://www.google.com/search?q=Nelson+Textbook+Pediatrics+myotonic+dystrophy+DM1+CTG+repeat'
}

# === Neuromuscular aliases ===
nm_base = get_base('Myasthenia Gravis')

d['SMA Type 1'] = {
    'primary_chapter': '652. Disorders of Neuromuscular Transmission and of Motor Neurons',
    'related_chapters': [],
    'chapter_url': nm_base['chapter_url'],
    'sub_deck': 'נלסון 21::נוירולוגיה::הפרעות נוירומוסקולריות',
    'google_search_url': 'https://www.google.com/search?q=Nelson+Textbook+Pediatrics+SMA+type+1+Werdnig+Hoffmann'
}
d['SMA Types 2-4'] = {
    'primary_chapter': '652. Disorders of Neuromuscular Transmission and of Motor Neurons',
    'related_chapters': [],
    'chapter_url': nm_base['chapter_url'],
    'sub_deck': 'נלסון 21::נוירולוגיה::הפרעות נוירומוסקולריות',
    'google_search_url': 'https://www.google.com/search?q=Nelson+Textbook+Pediatrics+SMA+types+2+3+4+Kugelberg+Welander'
}

with open('work/current_chapter_map.json', 'w', encoding='utf-8') as f:
    json.dump(cmap, f, ensure_ascii=False, indent=2)

print(f'Added 21 aliases. Total keys: {len(d)}')
