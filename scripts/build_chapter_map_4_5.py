#!/usr/bin/env python3
"""Build chapter map for sections 4 (Pulmonology) and 5 (Immunology/Allergy)."""
import json

cmap = {"batch": "4_5_pulmonology_immunology", "diseases": {}}
d = cmap["diseases"]

resp_url = "https://drive.google.com/drive/search?q=Part%2017-%20The%20Respiratory%20System.pdf"
imm_url = "https://drive.google.com/drive/search?q=PART%20XII%20-%20Immunology%20(164-181)"
allergy_url = "https://drive.google.com/drive/search?q=PART%20XIII%20-%20Allergic%20Disorders%20(182-193)"

def add(name, primary, related, sub_deck, search_kw, chapter_url=None):
    if chapter_url is None:
        chapter_url = resp_url
    d[name] = {
        "primary_chapter": primary,
        "related_chapters": related,
        "chapter_url": chapter_url,
        "sub_deck": sub_deck,
        "google_search_url": "https://www.google.com/search?q=Nelson+Textbook+Pediatrics+" + search_kw.replace(" ", "+")
    }

# ===================== SECTION 4: PULMONOLOGY =====================

# Pericardial diseases
peri = "נלסון 21::ריאות::מחלות הפריקרד"
add("פריקרדיטיס", "489. Diseases of the Pericardium", [], peri, "pericarditis acute viral children")
add("Pericarditis", "489. Diseases of the Pericardium", [], peri, "pericarditis acute viral children")
add("פריקרדיטיס אקוטית", "489. Diseases of the Pericardium", [], peri, "acute pericarditis children viral")
add("פריקרדיטיס קונסטריקטיבית", "489. Diseases of the Pericardium", [], peri, "constrictive pericarditis children")
add("תפליט פריקרדיאלי", "489. Diseases of the Pericardium", [], peri, "pericardial effusion tamponade children")
add("טמפונדה קרדיאלית", "489. Diseases of the Pericardium", [], peri, "cardiac tamponade Beck triad pulsus paradoxus")
add("מחלות הפריקרד", "489. Diseases of the Pericardium", [], peri, "pericardial diseases children")

# SIDS and BRUE
sids = "נלסון 21::ריאות::SIDS ו-BRUE"
add("SIDS", "423. Sudden Infant Death Syndrome", ["424. Brief Resolved Unexplained Events"], sids, "SIDS sudden infant death syndrome back to sleep")
add("Sudden Infant Death Syndrome", "423. Sudden Infant Death Syndrome", [], sids, "SIDS sudden infant death risk factors")
add("BRUE", "424. Brief Resolved Unexplained Events and Other Acute Events in Infants", ["423. Sudden Infant Death Syndrome"], sids, "BRUE brief resolved unexplained event infant")
add("Brief Resolved Unexplained Event", "424. Brief Resolved Unexplained Events and Other Acute Events in Infants", [], sids, "BRUE ALTE brief resolved unexplained event")

# Upper airway
upper = "נלסון 21::ריאות::הפרעות בדרכי נשימה עליונות"
add("Choanal Atresia", "425. Congenital Disorders of the Nose", [], upper, "choanal atresia CHARGE syndrome bilateral")
add("אטרזיה כואנלית", "425. Congenital Disorders of the Nose", [], upper, "choanal atresia congenital nasal")
add("גופים זרים באף", "426. Acquired Disorders of the Nose", [], upper, "nasal foreign body children")
add("אפיסטקסיס", "426. Acquired Disorders of the Nose", [], upper, "epistaxis nosebleed children Kiesselbach")
add("Epistaxis", "426. Acquired Disorders of the Nose", [], upper, "epistaxis nosebleed Kiesselbach plexus")
add("Croup", "433. Acute Inflammatory Upper Airway Obstruction", [], upper, "croup laryngotracheobronchitis parainfluenza steeple sign")
add("קרופ", "433. Acute Inflammatory Upper Airway Obstruction", [], upper, "croup laryngotracheobronchitis dexamethasone")
add("Epiglottitis", "433. Acute Inflammatory Upper Airway Obstruction", [], upper, "epiglottitis Haemophilus influenzae thumb sign")
add("אפיגלוטיטיס", "433. Acute Inflammatory Upper Airway Obstruction", [], upper, "epiglottitis acute supraglottitis")
add("Bacterial Tracheitis", "433. Acute Inflammatory Upper Airway Obstruction", [], upper, "bacterial tracheitis S aureus toxic child")
add("טרכאיטיס חיידקית", "433. Acute Inflammatory Upper Airway Obstruction", [], upper, "bacterial tracheitis pseudomembrane")
add("Peritonsillar Abscess", "431. Tonsils and Adenoids", ["432. Retropharyngeal Abscess"], upper, "peritonsillar abscess quinsy trismus")
add("אבצס פריטונסילרי", "431. Tonsils and Adenoids", [], upper, "peritonsillar abscess drainage")
add("Retropharyngeal Abscess", "432. Retropharyngeal Abscess", [], upper, "retropharyngeal abscess widened prevertebral space")
add("אבצס רטרופרינגיאלי", "432. Retropharyngeal Abscess", [], upper, "retropharyngeal abscess CT drainage")
add("הפרעות בדרכי נשימה עליונות", "433. Acute Inflammatory Upper Airway Obstruction", [], upper, "upper airway obstruction croup epiglottitis")
add("הפרעות מולדות ונרכשות באף", "425. Congenital Disorders of the Nose", ["426. Acquired Disorders of the Nose"], upper, "congenital acquired nasal disorders")

# Lower airway
lower = "נלסון 21::ריאות::הפרעות בדרכי נשימה תחתונות"
add("Laryngomalacia", "434. Congenital Anomalies of the Larynx, Trachea, and Bronchi", [], lower, "laryngomalacia infant stridor supraglottoplasty")
add("לרינגומלציה", "434. Congenital Anomalies of the Larynx, Trachea, and Bronchi", [], lower, "laryngomalacia stridor infant")
add("Tracheomalacia", "437. Bronchomalacia and Tracheomalacia", [], lower, "tracheomalacia bronchomalacia airway collapse")
add("טרכאומלציה", "437. Bronchomalacia and Tracheomalacia", [], lower, "tracheomalacia bronchomalacia")
add("Bronchomalacia", "437. Bronchomalacia and Tracheomalacia", [], lower, "bronchomalacia expiratory wheeze")
add("ברונכומלציה", "437. Bronchomalacia and Tracheomalacia", [], lower, "bronchomalacia airway")
add("טרכאומלציה וברונכומלציה", "437. Bronchomalacia and Tracheomalacia", [], lower, "tracheomalacia bronchomalacia")
add("Plastic Bronchitis", "440. Plastic Bronchitis", [], lower, "plastic bronchitis cast expectoration")
add("ברונכיטיס פלסטית", "440. Plastic Bronchitis", [], lower, "plastic bronchitis Fontan")
add("Foreign Body Aspiration", "435. Foreign Bodies in the Airway", [], lower, "foreign body aspiration right bronchus peanut")
add("גופים זרים בדרכי הנשימה", "435. Foreign Bodies in the Airway", [], lower, "airway foreign body rigid bronchoscopy")
add("Subglottic Stenosis", "436. Laryngotracheal Stenosis and Subglottic Stenosis", [], lower, "subglottic stenosis post intubation congenital")
add("היצרות סובגלוטית", "436. Laryngotracheal Stenosis and Subglottic Stenosis", [], lower, "subglottic stenosis laryngotracheal")
add("מומים מולדים של דרכי נשימה תחתונות", "434. Congenital Anomalies of the Larynx, Trachea, and Bronchi", [], lower, "congenital airway anomalies")
add("חסימות נרכשות של דרכי הנשימה התחתונות", "435. Foreign Bodies in the Airway", ["436. Laryngotracheal Stenosis and Subglottic Stenosis"], lower, "acquired lower airway obstruction")

# Distal airway diseases
distal = "נלסון 21::ריאות::מחלות דרכי אוויר דיסטליות"
add("Emphysema", "441. Emphysema and Overinflation", [], distal, "emphysema overinflation pediatric")
add("אמפיזמה", "441. Emphysema and Overinflation", [], distal, "emphysema pediatric")
add("α1-Antitrypsin Deficiency", "442. α1-Antitrypsin Deficiency and Emphysema", [], distal, "alpha1 antitrypsin deficiency PiZZ emphysema liver")
add("חסר α1-Anti-Trypsin", "442. α1-Antitrypsin Deficiency and Emphysema", [], distal, "alpha1 antitrypsin deficiency")
add("α1-Anti-Trypsin (α1AT) Deficiency", "442. α1-Antitrypsin Deficiency and Emphysema", [], distal, "alpha1 antitrypsin deficiency PiZZ")
add("Bronchiolitis Obliterans", "443. Other Distal Airway Diseases", [], distal, "bronchiolitis obliterans post infectious adenovirus")
add("Bronchiolitis Obliterans (BO)", "443. Other Distal Airway Diseases", [], distal, "bronchiolitis obliterans post infectious")
add("BO", "443. Other Distal Airway Diseases", [], distal, "bronchiolitis obliterans")
add("Congenital Lobar Emphysema", "441. Emphysema and Overinflation", ["444. Congenital Disorders of the Lung"], distal, "congenital lobar emphysema CLE LUL neonatal")
add("Congenital Lobar Emphysema (CLE)", "441. Emphysema and Overinflation", ["444. Congenital Disorders of the Lung"], distal, "congenital lobar emphysema CLE")
add("אמפיזמה לוברית מולדת", "441. Emphysema and Overinflation", [], distal, "congenital lobar emphysema")
add("מחלות של דרכי האויר הדיסטליות", "441. Emphysema and Overinflation", ["442. α1-Antitrypsin Deficiency and Emphysema", "443. Other Distal Airway Diseases"], distal, "distal airway diseases emphysema")

# Congenital lung and ILD
ild = "נלסון 21::ריאות::מחלות ריאה אינטרסטיציאליות"
add("CPAM", "444. Congenital Disorders of the Lung", [], ild, "CPAM congenital pulmonary airway malformation CCAM")
add("Congenital Pulmonary Airway Malformation", "444. Congenital Disorders of the Lung", [], ild, "CPAM CCAM congenital lung malformation")
add("Congenital Pulmonary Airway Malformation (CPAM)", "444. Congenital Disorders of the Lung", [], ild, "CPAM CCAM types prenatal")
add("Pulmonary Sequestration", "444. Congenital Disorders of the Lung", [], ild, "pulmonary sequestration intralobar extralobar systemic artery")
add("סקווסטרציה ריאתית", "444. Congenital Disorders of the Lung", [], ild, "pulmonary sequestration")
add("ILD", "448. Immune and Inflammatory Lung Disease", [], ild, "interstitial lung disease childhood chILD")
add("מחלות ריאה אינטרסטיציאליות", "448. Immune and Inflammatory Lung Disease", [], ild, "childhood ILD interstitial lung disease")
add("Pulmonary Hemosiderosis", "448. Immune and Inflammatory Lung Disease", [], ild, "pulmonary hemosiderosis idiopathic hemoptysis iron deficiency")
add("המוזידרוזיס ריאתי", "448. Immune and Inflammatory Lung Disease", [], ild, "pulmonary hemosiderosis Heiner syndrome")
add("Pulmonary Alveolar Proteinosis", "448. Immune and Inflammatory Lung Disease", [], ild, "pulmonary alveolar proteinosis crazy paving whole lung lavage")
add("פרוטאינוזיס אלוואולרית", "448. Immune and Inflammatory Lung Disease", [], ild, "pulmonary alveolar proteinosis")
add("מומים מולדים של הריאה", "444. Congenital Disorders of the Lung", [], ild, "congenital lung malformations CPAM sequestration")

# Eosinophilic lung diseases
eos = "נלסון 21::ריאות::מחלות ריאה אאוזינופיליות"
add("Eosinophilic Pneumonia", "448.4. Eosinophilic Lung Disease", [], eos, "eosinophilic pneumonia acute chronic BAL")
add("פנאומוניה אאוזינופילית", "448.4. Eosinophilic Lung Disease", [], eos, "eosinophilic pneumonia")
add("Acute Eosinophilic Pneumonia", "448.4. Eosinophilic Lung Disease", [], eos, "acute eosinophilic pneumonia bilateral infiltrates")
add("Chronic Eosinophilic Pneumonia", "448.4. Eosinophilic Lung Disease", [], eos, "chronic eosinophilic pneumonia peripheral infiltrates")
add("Löffler Syndrome", "448.4. Eosinophilic Lung Disease", [], eos, "Loffler syndrome transient pulmonary infiltrates Ascaris")
add("Löfler Syndrome", "448.4. Eosinophilic Lung Disease", [], eos, "Loffler syndrome Ascaris eosinophilia")
add("Tropical Eosinophilia", "448.4. Eosinophilic Lung Disease", [], eos, "tropical pulmonary eosinophilia Wuchereria Brugia")
add("ABPA", "448.4. Eosinophilic Lung Disease", [], eos, "ABPA allergic bronchopulmonary aspergillosis CF asthma central bronchiectasis")
add("Allergic Bronchopulmonary Aspergillosis", "448.4. Eosinophilic Lung Disease", [], eos, "ABPA Aspergillus IgE bronchiectasis")
add("Pulmonary Embolism", "459. Pulmonary Embolism, Infarction, and Hemorrhage", [], eos, "pulmonary embolism pediatric DVT")
add("תסחיף ריאתי", "459. Pulmonary Embolism, Infarction, and Hemorrhage", [], eos, "pulmonary embolism")
add("מחלות ריאה אאוזינופיליות", "448.4. Eosinophilic Lung Disease", [], eos, "eosinophilic lung disease")

# CF and PCD
cf = "נלסון 21::ריאות::CF ו-PCD"
add("Cystic Fibrosis", "454. Cystic Fibrosis", [], cf, "cystic fibrosis CFTR F508del sweat test")
add("CF", "454. Cystic Fibrosis", [], cf, "cystic fibrosis CF CFTR modulators")
add("Cystic Fibrosis (CF)", "454. Cystic Fibrosis", [], cf, "cystic fibrosis CFTR sweat chloride")
add("סיסטיק פיברוזיס", "454. Cystic Fibrosis", [], cf, "cystic fibrosis")
add("Primary Ciliary Dyskinesia", "455. Primary Ciliary Dyskinesia", [], cf, "primary ciliary dyskinesia Kartagener situs inversus")
add("Primary Ciliary Dyskinesia (PCD)", "455. Primary Ciliary Dyskinesia", [], cf, "PCD primary ciliary dyskinesia")
add("PCD", "455. Primary Ciliary Dyskinesia", [], cf, "PCD ciliary dyskinesia nasal NO dynein")
add("דיסקינזיה ריסית ראשונית", "455. Primary Ciliary Dyskinesia", [], cf, "primary ciliary dyskinesia")
add("Kartagener Syndrome", "455. Primary Ciliary Dyskinesia", [], cf, "Kartagener syndrome situs inversus bronchiectasis sinusitis")

# ===================== SECTION 5: IMMUNOLOGY & ALLERGY =====================

# Sleep disorders
sleep = "נלסון 21::אימונולוגיה ואלרגיה::הפרעות נשימה בשינה"
add("CCHS", "31. Sleep Medicine", [], sleep, "CCHS congenital central hypoventilation PHOX2B Ondine curse", resp_url)
add("Congenital Central Hypoventilation Syndrome", "31. Sleep Medicine", [], sleep, "CCHS PHOX2B Hirschsprung neural crest", resp_url)
add("Congenital Central Hypoventilation Syndrome (CCHS)", "31. Sleep Medicine", [], sleep, "CCHS congenital central hypoventilation", resp_url)
add("OSAS", "31. Sleep Medicine", [], sleep, "OSAS obstructive sleep apnea children adenotonsillar", resp_url)
add("Obstructive Sleep Apnea Syndrome (OSAS)", "31. Sleep Medicine", [], sleep, "OSAS obstructive sleep apnea polysomnography", resp_url)
add("Obstructive Sleep Apnea", "31. Sleep Medicine", [], sleep, "obstructive sleep apnea polysomnography adenotonsillectomy", resp_url)
add("פראסומניות", "31. Sleep Medicine", [], sleep, "parasomnias sleepwalking night terrors children", resp_url)
add("Parasomnias", "31. Sleep Medicine", [], sleep, "parasomnias children sleepwalking", resp_url)
add("הפרעות נשימה בשינה", "31. Sleep Medicine", [], sleep, "sleep disordered breathing children", resp_url)
add("רפואת שינה", "31. Sleep Medicine", [], sleep, "sleep medicine pediatric", resp_url)

# Asthma
asthma = "נלסון 21::אימונולוגיה ואלרגיה::אסטמה"
add("אסטמה", "185. Childhood Asthma", [], asthma, "childhood asthma ICS SABA step therapy", allergy_url)
add("Asthma", "185. Childhood Asthma", [], asthma, "childhood asthma bronchodilators inhaled corticosteroids", allergy_url)
add("Childhood Asthma", "185. Childhood Asthma", [], asthma, "childhood asthma management stepwise", allergy_url)
add("תרופות אסטמה", "185. Childhood Asthma", [], asthma, "asthma medications SABA ICS LABA LTRA", allergy_url)
add("Step Therapy", "185. Childhood Asthma", [], asthma, "asthma step therapy stepwise approach", allergy_url)
add("SABA", "185. Childhood Asthma", [], asthma, "SABA salbutamol albuterol short acting beta agonist", allergy_url)
add("ICS", "185. Childhood Asthma", [], asthma, "ICS inhaled corticosteroids fluticasone budesonide", allergy_url)
add("LABA", "185. Childhood Asthma", [], asthma, "LABA long acting beta agonist salmeterol formoterol", allergy_url)
add("LTRA", "185. Childhood Asthma", [], asthma, "LTRA montelukast leukotriene receptor antagonist", allergy_url)

# Allergy
allergy = "נלסון 21::אימונולוגיה ואלרגיה::אלרגיה"
add("אלרגיה", "182. Allergy and the Immunologic Basis of Atopic Disease", ["183. Diagnosis of Allergic Disease"], allergy, "allergy atopic disease IgE hypersensitivity", allergy_url)
add("Allergy", "182. Allergy and the Immunologic Basis of Atopic Disease", [], allergy, "allergy atopic disease hygiene hypothesis", allergy_url)
add("Allergic Rhinitis", "184. Allergic Rhinitis", [], allergy, "allergic rhinitis intranasal corticosteroids antihistamines", allergy_url)
add("נזלת אלרגית", "184. Allergic Rhinitis", [], allergy, "allergic rhinitis nasal steroids", allergy_url)
add("אאוזינופיליה", "169. Eosinophils", ["182. Allergy and the Immunologic Basis of Atopic Disease"], allergy, "eosinophilia peripheral AEC causes", allergy_url)
add("Eosinophilia", "169. Eosinophils", [], allergy, "eosinophilia differential diagnosis", allergy_url)
add("Allergic Conjunctivitis", "184. Allergic Rhinitis", [], allergy, "allergic conjunctivitis vernal keratoconjunctivitis", allergy_url)
add("אלרגיות עיניות", "184. Allergic Rhinitis", [], allergy, "allergic conjunctivitis ocular allergy", allergy_url)

# Urticaria and Anaphylaxis
anaph = "נלסון 21::אימונולוגיה ואלרגיה::אנפילקסיס ואורטיקריה"
add("אורטיקריה", "189. Urticaria (Hives) and Angioedema", [], anaph, "urticaria hives angioedema acute chronic", allergy_url)
add("Urticaria", "189. Urticaria (Hives) and Angioedema", [], anaph, "urticaria hives wheals", allergy_url)
add("אנגיואדמה", "189. Urticaria (Hives) and Angioedema", [], anaph, "angioedema hereditary C1 inhibitor bradykinin", allergy_url)
add("Angioedema", "189. Urticaria (Hives) and Angioedema", [], anaph, "angioedema HAE C1 inhibitor", allergy_url)
add("HAE", "189. Urticaria (Hives) and Angioedema", [], anaph, "hereditary angioedema C1 inhibitor deficiency", allergy_url)
add("Hereditary Angioedema", "189. Urticaria (Hives) and Angioedema", [], anaph, "HAE hereditary angioedema C1INH icatibant", allergy_url)
add("אנפילקסיס", "190. Anaphylaxis", [], anaph, "anaphylaxis epinephrine biphasic reaction", allergy_url)
add("Anaphylaxis", "190. Anaphylaxis", [], anaph, "anaphylaxis epinephrine IM food allergy", allergy_url)
add("אורטיקריה ואנגיואדמה", "189. Urticaria (Hives) and Angioedema", [], anaph, "urticaria angioedema", allergy_url)

# Food and Drug allergy
food = "נלסון 21::אימונולוגיה ואלרגיה::אלרגיית מזון ותרופות"
add("Serum Sickness", "191. Serum Sickness", [], food, "serum sickness immune complex type III hypersensitivity", allergy_url)
add("מחלת סרום", "191. Serum Sickness", [], food, "serum sickness", allergy_url)
add("אלרגיה למזונות", "192. Food Allergy and Adverse Reactions to Foods", [], food, "food allergy peanut milk egg IgE oral immunotherapy", allergy_url)
add("Food Allergy", "192. Food Allergy and Adverse Reactions to Foods", [], food, "food allergy children peanut anaphylaxis", allergy_url)
add("אלרגיות מזון", "192. Food Allergy and Adverse Reactions to Foods", [], food, "food allergy IgE FPIES", allergy_url)
add("FPIES", "192. Food Allergy and Adverse Reactions to Foods", [], food, "FPIES food protein induced enterocolitis profuse vomiting", allergy_url)
add("אלרגיה לתרופות", "193. Adverse and Allergic Reactions to Drugs", [], food, "drug allergy adverse reaction penicillin", allergy_url)
add("Drug Allergy", "193. Adverse and Allergic Reactions to Drugs", [], food, "drug allergy SJS TEN DRESS", allergy_url)
add("SJS/TEN", "193. Adverse and Allergic Reactions to Drugs", [], food, "Stevens Johnson syndrome toxic epidermal necrolysis", allergy_url)
add("DRESS", "193. Adverse and Allergic Reactions to Drugs", [], food, "DRESS drug reaction eosinophilia systemic symptoms", allergy_url)

# Primary immunodeficiency - antibody
ab = "נלסון 21::אימונולוגיה ואלרגיה::חסרים חיסוניים ראשוניים - נוגדנים"
add("XLA", "166. B-Cell and Antibody Deficiencies", [], ab, "XLA Bruton agammaglobulinemia BTK absent B cells", imm_url)
add("Bruton Agammaglobulinemia", "166. B-Cell and Antibody Deficiencies", [], ab, "XLA Bruton X-linked agammaglobulinemia BTK", imm_url)
add("CVID", "166. B-Cell and Antibody Deficiencies", [], ab, "CVID common variable immunodeficiency hypogammaglobulinemia", imm_url)
add("Common Variable Immunodeficiency", "166. B-Cell and Antibody Deficiencies", [], ab, "CVID common variable immunodeficiency IVIG", imm_url)
add("Selective IgA Deficiency", "166. B-Cell and Antibody Deficiencies", [], ab, "selective IgA deficiency most common PIDD", imm_url)
add("חסר IgA סלקטיבי", "166. B-Cell and Antibody Deficiencies", [], ab, "IgA deficiency celiac autoimmunity", imm_url)
add("חסר IgA", "166. B-Cell and Antibody Deficiencies", [], ab, "selective IgA deficiency", imm_url)
add("Hyper-IgM Syndrome", "166. B-Cell and Antibody Deficiencies", [], ab, "hyper IgM syndrome CD40L Pneumocystis Cryptosporidium", imm_url)
add("תסמונת Hyper-IgM", "166. B-Cell and Antibody Deficiencies", [], ab, "hyper IgM CD40 ligand", imm_url)
add("Transient Hypogammaglobulinemia of Infancy", "166. B-Cell and Antibody Deficiencies", [], ab, "transient hypogammaglobulinemia infancy physiologic", imm_url)
add("הפרעות ראשוניות בייצור נוגדנים", "166. B-Cell and Antibody Deficiencies", [], ab, "primary antibody deficiency B cell", imm_url)

# Primary immunodeficiency - cellular
tcell = "נלסון 21::אימונולוגיה ואלרגיה::חסרים חיסוניים ראשוניים - תאיים"
add("SCID", "165. Primary Defects of Cellular Immunity", [], tcell, "SCID severe combined immunodeficiency HSCT gene therapy", imm_url)
add("Severe Combined Immunodeficiency", "165. Primary Defects of Cellular Immunity", [], tcell, "SCID X-linked IL2RG ADA RAG absent thymus", imm_url)
add("DiGeorge Syndrome", "165. Primary Defects of Cellular Immunity", [], tcell, "DiGeorge 22q11.2 deletion thymic hypoplasia CATCH22", imm_url)
add("תסמונת DiGeorge", "165. Primary Defects of Cellular Immunity", [], tcell, "DiGeorge 22q11 conotruncal cardiac", imm_url)
add("22q11.2 Deletion", "165. Primary Defects of Cellular Immunity", [], tcell, "22q11 deletion DiGeorge velocardiofacial", imm_url)
add("Chromosome 22q11.2 Deletion Syndrome (DiGeorge)", "165. Primary Defects of Cellular Immunity", [], tcell, "22q11.2 deletion DiGeorge syndrome", imm_url)
add("CMC", "165. Primary Defects of Cellular Immunity", [], tcell, "chronic mucocutaneous candidiasis AIRE APECED", imm_url)
add("Chronic Mucocutaneous Candidiasis", "165. Primary Defects of Cellular Immunity", [], tcell, "CMC chronic mucocutaneous candidiasis", imm_url)
add("Chronic Mucocutaneous Candidiasis (CMC)", "165. Primary Defects of Cellular Immunity", [], tcell, "CMC chronic mucocutaneous candidiasis AIRE", imm_url)
add("Wiskott-Aldrich Syndrome", "165. Primary Defects of Cellular Immunity", [], tcell, "Wiskott Aldrich WAS eczema thrombocytopenia immunodeficiency", imm_url)
add("הפרעות ראשוניות בחיסוניות תאית", "165. Primary Defects of Cellular Immunity", [], tcell, "T cell immunodeficiency cellular", imm_url)
add("APECED", "165. Primary Defects of Cellular Immunity", [], tcell, "APECED autoimmune polyendocrinopathy candidiasis AIRE", imm_url)
add("Autoimmune Polyendocrinopathy", "165. Primary Defects of Cellular Immunity", [], tcell, "APECED APS1 autoimmune polyendocrinopathy", imm_url)
add("Autoimmune Polyendocrinopathy-Candidiasis-Ectodermal Dystrophy (APECED)", "165. Primary Defects of Cellular Immunity", [], tcell, "APECED autoimmune polyendocrinopathy", imm_url)
add("סימני אזהרה לחסר חיסוני", "164. Orientation to the Consideration of Inborn Errors of Immunity", [], tcell, "warning signs immunodeficiency recurrent infections", imm_url)

# Autoimmune/dysregulation
auto = "נלסון 21::אימונולוגיה ואלרגיה::חסרים חיסוניים - אוטואימוניות"
add("ALPS", "164. Orientation to the Consideration of Inborn Errors of Immunity", [], auto, "ALPS autoimmune lymphoproliferative FAS double negative T cells", imm_url)
add("Autoimmune Lymphoproliferative Syndrome", "164. Orientation to the Consideration of Inborn Errors of Immunity", [], auto, "ALPS FAS FASL lymphadenopathy splenomegaly cytopenias", imm_url)
add("Autoimmune Lymphoproliferative Syndrome (ALPS)", "164. Orientation to the Consideration of Inborn Errors of Immunity", [], auto, "ALPS FAS autoimmune lymphoproliferative", imm_url)
add("IPEX", "164. Orientation to the Consideration of Inborn Errors of Immunity", [], auto, "IPEX FOXP3 Treg enteropathy diabetes eczema", imm_url)
add("Immune Dysregulation Polyendocrinopathy Enteropathy XL", "164. Orientation to the Consideration of Inborn Errors of Immunity", [], auto, "IPEX FOXP3 immune dysregulation", imm_url)
add("Immune Dysregulation Polyendocrinopathy Enteropathy XL (IPEX)", "164. Orientation to the Consideration of Inborn Errors of Immunity", [], auto, "IPEX FOXP3 Treg", imm_url)
add("חסרים חיסוניים הקשורים באוטו-אימוניות", "164. Orientation to the Consideration of Inborn Errors of Immunity", [], auto, "immunodeficiency autoimmunity dysregulation", imm_url)

# Neutrophil disorders
neut = "נלסון 21::אימונולוגיה ואלרגיה::הפרעות בתפקוד נויטרופילים"
add("CGD", "170. Disorders of Phagocyte Function", [], neut, "CGD chronic granulomatous disease NADPH oxidase catalase positive", imm_url)
add("Chronic Granulomatous Disease", "170. Disorders of Phagocyte Function", [], neut, "CGD NADPH oxidase DHR NBT Aspergillus Serratia", imm_url)
add("Chronic Granulomatous Disease (CGD)", "170. Disorders of Phagocyte Function", [], neut, "CGD chronic granulomatous disease", imm_url)
add("LAD", "170. Disorders of Phagocyte Function", [], neut, "LAD leukocyte adhesion deficiency CD18 delayed cord separation", imm_url)
add("Leukocyte Adhesion Deficiency", "170. Disorders of Phagocyte Function", [], neut, "LAD leukocyte adhesion deficiency", imm_url)
add("Leukocyte Adhesion Deficiency (LAD)", "170. Disorders of Phagocyte Function", [], neut, "LAD leukocyte adhesion deficiency CD18", imm_url)
add("Chediak-Higashi Syndrome", "170. Disorders of Phagocyte Function", [], neut, "Chediak Higashi giant granules albinism neurodegeneration", imm_url)
add("Chédiak-Higashi Syndrome", "170. Disorders of Phagocyte Function", [], neut, "Chediak Higashi giant granules partial albinism", imm_url)
add("תסמונת Chediak-Higashi", "170. Disorders of Phagocyte Function", [], neut, "Chediak Higashi syndrome", imm_url)
add("הפרעות בתפקוד נויטרופילים", "170. Disorders of Phagocyte Function", [], neut, "phagocyte function disorders neutrophil", imm_url)

# Complement disorders
comp = "נלסון 21::אימונולוגיה ואלרגיה::הפרעות במשלים"
add("Complement Deficiency", "173. Complement System", [], comp, "complement deficiency C2 C3 C5-C9 Neisseria", imm_url)
add("הפרעות בתפקוד משלים", "173. Complement System", [], comp, "complement system deficiency", imm_url)
add("חסר C2", "173. Complement System", [], comp, "C2 deficiency complement SLE", imm_url)
add("חסר C3", "173. Complement System", [], comp, "C3 deficiency pyogenic infections", imm_url)
add("חסר C5-C9", "173. Complement System", [], comp, "terminal complement deficiency Neisseria meningococcal", imm_url)
add("MBL Deficiency", "173. Complement System", [], comp, "mannose binding lectin MBL deficiency", imm_url)
add("חסר Properdin", "173. Complement System", [], comp, "properdin factor D deficiency Neisseria X-linked", imm_url)
add("חסר Factor D", "173. Complement System", [], comp, "factor D deficiency Neisseria", imm_url)

with open("work/current_chapter_map.json", "w", encoding="utf-8") as f:
    json.dump(cmap, f, ensure_ascii=False, indent=2)

print(f"Created chapter map with {len(d)} entries")

# Count sub-decks
sub_decks = set()
for v in d.values():
    sub_decks.add(v["sub_deck"])
print(f"Sub-decks: {len(sub_decks)}")
for sd in sorted(sub_decks):
    count = sum(1 for v in d.values() if v["sub_deck"] == sd)
    print(f"  {sd}: {count} keys")
