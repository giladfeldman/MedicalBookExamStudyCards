#!/usr/bin/env python3
"""Add missing disease aliases to chapter map for batch 3a."""
import json

with open('work/current_chapter_map.json', 'r', encoding='utf-8') as f:
    cmap = json.load(f)

d = cmap['diseases']

def get(key):
    return d[key].copy()

# Circulation aliases
circ = get('סירקולציה עוברית')
d['סירקולציה מעברית'] = {**circ, 'google_search_url': 'https://www.google.com/search?q=Nelson+Textbook+Pediatrics+transitional+circulation+neonatal'}
d['סירקולציה נאונטלית'] = {**circ, 'google_search_url': 'https://www.google.com/search?q=Nelson+Textbook+Pediatrics+neonatal+circulation+postnatal'}

# ASD subtypes
asd = get('ASD')
d['ASD Secundum'] = {**asd, 'google_search_url': 'https://www.google.com/search?q=Nelson+Textbook+Pediatrics+ASD+secundum+atrial+septal+defect'}
d['Ostium Primum'] = {**asd, 'google_search_url': 'https://www.google.com/search?q=Nelson+Textbook+Pediatrics+ostium+primum+ASD+cleft+mitral'}
d['Sinus Venosus ASD'] = {**asd, 'google_search_url': 'https://www.google.com/search?q=Nelson+Textbook+Pediatrics+sinus+venosus+ASD+anomalous+pulmonary+vein'}
d['PAPVR ו-Scimitar Syndrome'] = {**asd, 'google_search_url': 'https://www.google.com/search?q=Nelson+Textbook+Pediatrics+PAPVR+Scimitar+syndrome'}

# VSD subtypes
vsd = get('VSD')
d['Supracristal VSD with AR'] = {**vsd, 'google_search_url': 'https://www.google.com/search?q=Nelson+Textbook+Pediatrics+supracristal+VSD+aortic+regurgitation'}

# Rare L-R shunt lesions
lr = get('שאנט משמאל לימין') if 'שאנט משמאל לימין' in d else get('ASD')
d['Aorto-Pulmonary Window'] = {**lr, 'sub_deck': 'נלסון 21::קרדיולוגיה::שאנט משמאל לימין', 'google_search_url': 'https://www.google.com/search?q=Nelson+Textbook+Pediatrics+aortopulmonary+window'}
d['Coronary Artery Fistula'] = {**lr, 'sub_deck': 'נלסון 21::קרדיולוגיה::שאנט משמאל לימין', 'google_search_url': 'https://www.google.com/search?q=Nelson+Textbook+Pediatrics+coronary+artery+fistula'}
d['Ruptured Sinus of Valsalva'] = {**lr, 'sub_deck': 'נלסון 21::קרדיולוגיה::שאנט משמאל לימין', 'google_search_url': 'https://www.google.com/search?q=Nelson+Textbook+Pediatrics+ruptured+sinus+Valsalva'}

# PS subtypes
ps = get('PS')
d['PPS'] = {**ps, 'google_search_url': 'https://www.google.com/search?q=Nelson+Textbook+Pediatrics+peripheral+pulmonic+stenosis'}
d['Infundibular PS ו-Double-Chamber RV'] = {**ps, 'google_search_url': 'https://www.google.com/search?q=Nelson+Textbook+Pediatrics+infundibular+PS+double+chamber+RV'}
d['Infundibular PS / Double-Chamber RV'] = {**ps, 'google_search_url': 'https://www.google.com/search?q=Nelson+Textbook+Pediatrics+infundibular+PS+double+chamber+RV'}
d['PS with Intracardiac Shunt'] = {**ps, 'google_search_url': 'https://www.google.com/search?q=Nelson+Textbook+Pediatrics+pulmonic+stenosis+intracardiac+shunt'}

# CoA aliases
coa = get('CoA')
d['Coarctation'] = {**coa}
d['CoA עם מחלה קשה'] = {**coa, 'google_search_url': 'https://www.google.com/search?q=Nelson+Textbook+Pediatrics+coarctation+aorta+severe+neonatal'}
d['Congenital Mitral Stenosis'] = {**coa, 'sub_deck': 'נלסון 21::קרדיולוגיה::מומים חסימתיים', 'google_search_url': 'https://www.google.com/search?q=Nelson+Textbook+Pediatrics+congenital+mitral+stenosis'}

# Regurgitant aliases
reg = get('מומים רגורגיטיביים') if 'מומים רגורגיטיביים' in d else get('MR')
d['היעדר מסתם פולמונלי'] = {**reg, 'sub_deck': 'נלסון 21::קרדיולוגיה::מומים רגורגיטיביים', 'google_search_url': 'https://www.google.com/search?q=Nelson+Textbook+Pediatrics+absent+pulmonary+valve+syndrome'}
d['Tricuspid Regurgitation'] = {**reg, 'sub_deck': 'נלסון 21::קרדיולוגיה::מומים רגורגיטיביים', 'google_search_url': 'https://www.google.com/search?q=Nelson+Textbook+Pediatrics+tricuspid+regurgitation+congenital'}

# Cyanotic decreased flow aliases
tof = get('TOF')
d['TOF with PA'] = {**tof, 'google_search_url': 'https://www.google.com/search?q=Nelson+Textbook+Pediatrics+tetralogy+Fallot+pulmonary+atresia'}
d['PA with Intact Septum'] = {**tof, 'google_search_url': 'https://www.google.com/search?q=Nelson+Textbook+Pediatrics+pulmonary+atresia+intact+ventricular+septum'}

# Tricuspid Atresia alias
ta = get('Tricuspid Atresia') if 'Tricuspid Atresia' in d else get('TOF')
d['Tricuspid Atresia עם TGA'] = {**ta, 'google_search_url': 'https://www.google.com/search?q=Nelson+Textbook+Pediatrics+tricuspid+atresia+transposition'}

with open('work/current_chapter_map.json', 'w', encoding='utf-8') as f:
    json.dump(cmap, f, ensure_ascii=False, indent=2)

print(f'Added 22 aliases. Total keys: {len(d)}')
