#!/usr/bin/env python3
"""Add missing disease aliases to chapter map for batch 3b."""
import json

with open('work/current_chapter_map.json', 'r', encoding='utf-8') as f:
    cmap = json.load(f)

d = cmap['diseases']

def get(key):
    return d[key].copy()

# TGA subtypes
dtga = get('D-TGA')
d['D-TGA Simple'] = {**dtga, 'google_search_url': 'https://www.google.com/search?q=Nelson+Textbook+Pediatrics+D-TGA+simple+transposition+intact+septum'}
d['TGA with VSD'] = {**dtga, 'google_search_url': 'https://www.google.com/search?q=Nelson+Textbook+Pediatrics+TGA+with+VSD+transposition'}

# TAPVR subtype
tapvr = get('TAPVR')
d['TAPVR חסום'] = {**tapvr, 'google_search_url': 'https://www.google.com/search?q=Nelson+Textbook+Pediatrics+TAPVR+obstructed+total+anomalous+pulmonary+venous+return'}

# Single Ventricle subtype
sv = get('Single Ventricle')
d['Single Ventricle (DILV)'] = {**sv, 'google_search_url': 'https://www.google.com/search?q=Nelson+Textbook+Pediatrics+single+ventricle+DILV+double+inlet+left+ventricle'}

# Heterotaxy - aortic arch
het = get('הטרוטקסיה')
d['קשת אאורטה ימנית'] = {**het, 'sub_deck': 'נלסון 21::קרדיולוגיה::הטרוטקסיה ואנומליות', 'google_search_url': 'https://www.google.com/search?q=Nelson+Textbook+Pediatrics+right+aortic+arch+vascular+ring'}

# ALCAPA
cor = get('Coronary Anomalies')
d['ALCAPA'] = {**cor, 'sub_deck': 'נלסון 21::קרדיולוגיה::הטרוטקסיה ואנומליות', 'google_search_url': 'https://www.google.com/search?q=Nelson+Textbook+Pediatrics+ALCAPA+anomalous+left+coronary+artery+pulmonary'}

# ECG pediatric
ecg = get('ECG')
d['אק"ג ילדים'] = {**ecg, 'google_search_url': 'https://www.google.com/search?q=Nelson+Textbook+Pediatrics+pediatric+ECG+interpretation+normal+values'}

# Arrhythmia subtypes
arr = get('SVT')
d['Sinus Bradycardia'] = {**arr, 'sub_deck': 'נלסון 21::קרדיולוגיה::הפרעות קצב', 'google_search_url': 'https://www.google.com/search?q=Nelson+Textbook+Pediatrics+sinus+bradycardia+pediatric'}
d['Sick Sinus Syndrome'] = {**arr, 'sub_deck': 'נלסון 21::קרדיולוגיה::הפרעות קצב', 'google_search_url': 'https://www.google.com/search?q=Nelson+Textbook+Pediatrics+sick+sinus+syndrome+pediatric'}
d['Atrial Ectopic Tachycardia'] = {**arr, 'sub_deck': 'נלסון 21::קרדיולוגיה::הפרעות קצב', 'google_search_url': 'https://www.google.com/search?q=Nelson+Textbook+Pediatrics+atrial+ectopic+tachycardia'}
d['Chaotic/Multifocal Atrial Tachycardia'] = {**arr, 'sub_deck': 'נלסון 21::קרדיולוגיה::הפרעות קצב', 'google_search_url': 'https://www.google.com/search?q=Nelson+Textbook+Pediatrics+chaotic+multifocal+atrial+tachycardia'}

# PAC/PVC plural forms
pac = get('PAC')
d['PACs'] = {**pac}
pvc = get('PVC')
d['PVCs'] = {**pvc}

# AV Block subtypes
avb = get('AV Block')
d['AV Block דרגה 1'] = {**avb, 'google_search_url': 'https://www.google.com/search?q=Nelson+Textbook+Pediatrics+first+degree+AV+block'}
d['AV Block דרגה 2'] = {**avb, 'google_search_url': 'https://www.google.com/search?q=Nelson+Textbook+Pediatrics+second+degree+AV+block+Mobitz'}
d['AV Block דרגה 3'] = {**avb, 'google_search_url': 'https://www.google.com/search?q=Nelson+Textbook+Pediatrics+complete+heart+block+third+degree'}
d['Complete AVB'] = {**avb, 'google_search_url': 'https://www.google.com/search?q=Nelson+Textbook+Pediatrics+complete+AV+block+pediatric'}
d['Complete AVB מולד'] = {**avb, 'google_search_url': 'https://www.google.com/search?q=Nelson+Textbook+Pediatrics+congenital+complete+heart+block+neonatal+lupus'}

# VF
vt = get('Ventricular Tachycardia')
d['VF'] = {**vt, 'sub_deck': 'נלסון 21::קרדיולוגיה::הפרעות קצב', 'google_search_url': 'https://www.google.com/search?q=Nelson+Textbook+Pediatrics+ventricular+fibrillation+pediatric'}

# Acquired QT prolongation
lqts = get('LQTS')
d['הארכת QT נרכשת'] = {**lqts, 'google_search_url': 'https://www.google.com/search?q=Nelson+Textbook+Pediatrics+acquired+QT+prolongation+drug+induced'}

# Cardiomyopathies general
dcm = get('Dilated Cardiomyopathy')
d['קרדיומיופתיות'] = {**dcm, 'sub_deck': 'נלסון 21::קרדיולוגיה::קרדיומיופתיות', 'google_search_url': 'https://www.google.com/search?q=Nelson+Textbook+Pediatrics+cardiomyopathy+pediatric+classification'}

with open('work/current_chapter_map.json', 'w', encoding='utf-8') as f:
    json.dump(cmap, f, ensure_ascii=False, indent=2)

print(f'Added 21 aliases. Total keys: {len(d)}')
