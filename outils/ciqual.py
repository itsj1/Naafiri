"""Construit ciqual.json (table CIQUAL de l'ANSES, licence Ouverte Etalab) pour Naafiri.

Entrée : le JSON complet de la table CIQUAL 2025 (format XML officiel converti : composition[nom] = {valeur, min, max, confiance}).
Sortie : ciqual.json compact, chargé par l'appli à la première recherche.
  { "v": version, "c": [clés], "u": [facteur vers grammes], "a": [[code, nom, valeurs…]] }
  Valeurs dans l'unité de la colonne CIQUAL (g, mg ou µg pour 100 g) ; multiplier par u[i] pour avoir des grammes.
Usage : python3 outils/ciqual.py ciqual_2025_complete.json ciqual.json
"""
import json, sys, re

# clé Naafiri (k, p, c, f puis clés Open Food Facts des nutriments détaillés) → colonnes CIQUAL possibles, facteur vers g
COLS = [
 ('k', ['Energie, Règlement UE N° 1169/2011 (kcal/100 g)'], 1),
 ('p', ['Protéines, N x 6.25 (g/100 g)', 'Protéines, N x facteur de Jones (g/100 g)'], 1),
 ('c', ['Glucides (g/100 g)'], 1),
 ('f', ['Lipides (g/100 g)'], 1),
 ('fiber', ['Fibres alimentaires (g/100 g)'], 1),
 ('sugars', ['Sucres (g/100 g)'], 1),
 ('saturated-fat', ['AG saturés (g/100 g)'], 1),
 ('monounsaturated-fat', ['AG monoinsaturés (g/100 g)'], 1),
 ('polyunsaturated-fat', ['AG polyinsaturés (g/100 g)'], 1),
 ('alcohol', ['Alcool (éthanol) (g/100 g)', 'Alcool (g/100 g)'], 1),
 ('cholesterol', ['Cholestérol (mg/100 g)'], 1e-3),
 ('water', ['Eau (g/100 g)'], 1),
 ('salt', ['Sel chlorure de sodium (g/100 g)'], 1),
 ('sodium', ['Sodium (mg/100 g)'], 1e-3),
 ('vitamin-a', ['Activité vitaminique A, équivalents rétinol (µg/100 g)', 'Rétinol (µg/100 g)'], 1e-6),
 ('vitamin-b1', ['Vitamine B1 ou Thiamine (mg/100 g)'], 1e-3),
 ('vitamin-b9', ['Vitamine B9 ou Folates totaux (µg/100 g)', 'Folates intrinsèques (µg/100 g)'], 1e-6),
 ('vitamin-b12', ['Vitamine B12 (µg/100 g)'], 1e-6),
 ('vitamin-b2', ['Vitamine B2 ou Riboflavine (mg/100 g)'], 1e-3),
 ('vitamin-pp', ['Vitamine B3 ou PP ou Niacine (mg/100 g)'], 1e-3),
 ('pantothenic-acid', ['Vitamine B5 ou Acide pantothénique (mg/100 g)'], 1e-3),
 ('vitamin-b6', ['Vitamine B6 (mg/100 g)'], 1e-3),
 ('vitamin-c', ['Vitamine C (mg/100 g)'], 1e-3),
 ('vitamin-d', ['Vitamine D (µg/100 g)'], 1e-6),
 ('vitamin-e', ['Vitamine E (mg/100 g)', 'Alpha-tocophérol (vitamine E) (mg/100 g)'], 1e-3),
 ('vitamin-k', ['Vitamine K1 (µg/100 g)'], 1e-6),   # K2 ajoutée ci-dessous si connue
 ('calcium', ['Calcium (mg/100 g)'], 1e-3),
 ('chloride', ['Chlorure (mg/100 g)'], 1e-3),
 ('copper', ['Cuivre (mg/100 g)'], 1e-3),
 ('iron', ['Fer (mg/100 g)'], 1e-3),
 ('iodine', ['Iode (µg/100 g)'], 1e-6),
 ('magnesium', ['Magnésium (mg/100 g)'], 1e-3),
 ('manganese', ['Manganèse (mg/100 g)'], 1e-3),
 ('phosphorus', ['Phosphore (mg/100 g)'], 1e-3),
 ('potassium', ['Potassium (mg/100 g)'], 1e-3),
 ('selenium', ['Sélénium (µg/100 g)'], 1e-6),
 ('zinc', ['Zinc (mg/100 g)'], 1e-3),
]

def val(comp, name):
    v = (comp.get(name) or {}).get('valeur', '')
    v = str(v).strip().replace(',', '.')
    if v in ('', '-'): return None
    if v.lower() == 'traces': return 0.0
    if v.startswith('<'): return 0.0          # sous le seuil de quantification
    try: return float(v)
    except ValueError: return None

def rnd(x):
    if x is None: return None
    if x == 0: return 0
    r = float(f'{x:.3g}')
    return int(r) if r == int(r) else r

src, out = sys.argv[1], sys.argv[2]
D = json.load(open(src, encoding='utf-8'))
rows = []
for d in D:
    comp = d['composition']
    vals = []
    for key, names, _ in COLS:
        v = None
        for n in names:
            v = val(comp, n)
            if v is not None: break
        if key == 'vitamin-k':
            k2 = val(comp, 'Vitamine K2 (µg/100 g)')
            if k2 is not None: v = (v or 0) + k2
        vals.append(rnd(v))
    if vals[0] is None: continue              # sans calories : inutile pour l'appli
    name = re.sub(r'\s+', ' ', d['alim_nom_fr']).strip()
    rows.append([int(d['alim_code']), name] + vals)
rows.sort(key=lambda r: r[1].lower())
json.dump({'v': 'CIQUAL 2025 (Anses)', 'c': [c[0] for c in COLS], 'u': [c[2] for c in COLS], 'a': rows},
          open(out, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print(len(rows), 'aliments écrits dans', out)
