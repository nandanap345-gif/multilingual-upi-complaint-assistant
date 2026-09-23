import csv
import sys
import os
import importlib.util

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CSV_PATH = os.path.join(ROOT, 'data', 'raw', 'seed_dataset.csv')

# Load config
spec = importlib.util.spec_from_file_location('cfg', os.path.join(ROOT, 'src', 'config.py'))
cfg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cfg)

REQUIRED_COLS = ['complaint_id','complaint_text','language','script','is_code_mixed','intent','source_type','provenance']

errors = []
rows = []

with open(CSV_PATH, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    headers = reader.fieldnames
    if headers is None:
        errors.append('CSV has no headers')
    else:
        # Normalize headers
        headers_norm = [h.strip() for h in headers]
        if headers_norm != REQUIRED_COLS:
            errors.append(f'CSV headers do not match required columns. Found: {headers}')
    for i, r in enumerate(reader, start=2):
        rows.append(r)

# Check complaint_id uniqueness
ids = [ (r.get('complaint_id') or '').strip() for r in rows]
dup_ids = set([x for x in ids if x and ids.count(x) > 1])
if dup_ids:
    errors.append(f'Duplicate complaint_id values: {dup_ids}')

# Check no empty complaint_text
empty_texts = [ (r.get('complaint_id') or '').strip() for r in rows if not (r.get('complaint_text') or '').strip()]
if empty_texts:
    errors.append(f'Empty complaint_text for IDs: {empty_texts}')

# Check all 13 intents present
present_intents = set([(r.get('intent') or '').strip() for r in rows])
missing_intents = set(cfg.INTENT_LABELS) - present_intents
if missing_intents:
    errors.append(f'Missing intents: {missing_intents}')

# Check language and script validity
invalid_lang = set([(r.get('language') or '').strip() for r in rows]) - set(cfg.LANGUAGES)
if invalid_lang:
    errors.append(f'Invalid language values found: {invalid_lang}')

invalid_script = set([(r.get('script') or '').strip() for r in rows]) - set(cfg.SCRIPTS)
if invalid_script:
    errors.append(f'Invalid script values found: {invalid_script}')

# Check is_code_mixed boolean values
valid_bool = {'true','false','True','False','1','0'}
invalid_bool = set([(r.get('is_code_mixed') or '').strip() for r in rows]) - valid_bool
if invalid_bool:
    errors.append(f'Invalid is_code_mixed values: {invalid_bool}')

# Check duplicate complaint_text
texts = [(r.get('complaint_text') or '').strip() for r in rows]
dup_texts = set([t for t in texts if t and texts.count(t) > 1])
if dup_texts:
    errors.append(f'Duplicate complaint_text values found (count={len(dup_texts)}).')

# Check source_type and provenance
src_types = set([(r.get('source_type') or '').strip() for r in rows])
if src_types != {'researcher_created'}:
    errors.append(f'Invalid source_type values found: {src_types} (expected only researcher_created)')

prov_bad = [ (r.get('complaint_id') or '').strip() for r in rows if (r.get('provenance') or '').strip() != 'fictional researcher-created complaint for development/testing']
if prov_bad:
    errors.append(f'provenance field missing or incorrect for IDs: {prov_bad}')

# Summary outputs required by user
print('dataset_path:', CSV_PATH)
print('total_complaints:', len(rows))

# counts per intent
from collections import Counter
intent_counts = Counter([r['intent'].strip() for r in rows])
for intent in cfg.INTENT_LABELS:
    print('intent_count', intent, intent_counts.get(intent, 0))

# language distribution
lang_counts = Counter([r['language'].strip() for r in rows])
for lang, cnt in lang_counts.items():
    print('language_count', lang, cnt)

# code-mixed count
code_mixed_count = sum(1 for r in rows if r['is_code_mixed'].strip().lower() in ('true','1'))
print('code_mixed_count:', code_mixed_count)

# Validation result
if errors:
    print('\nVALIDATION FAILED:')
    for e in errors:
        print('-', e)
    sys.exit(1)
else:
    print('\nVALIDATION PASSED')
    sys.exit(0)
