import importlib.util
import sys
import os

ROOT = os.path.abspath(os.path.dirname(__file__) + "\..")
print('ROOT', ROOT)

# Load config
spec = importlib.util.spec_from_file_location('cfg', os.path.join(ROOT, 'src', 'config.py'))
cfg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cfg)

# Check intents length
print('INTENT_LABELS count:', len(cfg.INTENT_LABELS))

# Files to check for label consistency
files = [
    os.path.join(ROOT, 'README.md'),
    os.path.join(ROOT, 'docs', 'project_specification.md'),
    os.path.join(ROOT, 'data', 'schema.md'),
    os.path.join(ROOT, 'src', 'config.py'),
]

missing = []
for label in cfg.INTENT_LABELS:
    found = False
    for fp in files:
        try:
            with open(fp, 'r', encoding='utf-8') as f:
                content = f.read()
            if label in content:
                found = True
                break
        except FileNotFoundError:
            continue
    if not found:
        missing.append(label)

print('Labels missing from docs:', missing)

# Check CSV header
csv_path = os.path.join(ROOT, 'data', 'raw', 'dataset_template.csv')
with open(csv_path, 'r', encoding='utf-8') as f:
    lines = [l.rstrip('\n') for l in f.readlines()]

print('CSV header:', lines[0])
print('CSV rows count (including header):', len(lines))
if len(lines) > 1:
    print('ERROR: dataset_template.csv contains data rows; it should only contain headers')

# Check forbidden ML libs are NOT installed in the venv
forbidden = ['torch', 'transformers', 'tensorflow', 'sentence_transformers', 'sentence-transformers']
for lib in forbidden:
    try:
        __import__(lib)
        print('WARNING: forbidden library import succeeded:', lib)
    except Exception:
        print('NOT INSTALLED (as expected):', lib)

# Check venv exists
venv_exists = os.path.isdir(os.path.join(ROOT, '.venv'))
print('.venv exists:', venv_exists)

print('Validation script completed')
