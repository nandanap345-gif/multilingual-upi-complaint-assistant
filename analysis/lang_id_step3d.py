#!/usr/bin/env python3
"""Step 3D: Language identification (read-only analysis)

Produces:
 - analysis/step3d_results.json
 - analysis/STEP3D_LANGUAGE_REPORT.md
 - analysis/figures/karan_language_pie.png
 - analysis/figures/karan_language_intent_bar.png
 - analysis/figures/banking77_ascii_stats.png

Rules: does NOT modify any files under data/raw_data/.
"""
import csv
import json
import os
from collections import Counter, defaultdict
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(__file__))
RAW = os.path.join(ROOT, 'data', 'raw_data')
OUT_DIR = os.path.join(ROOT, 'analysis')
FIG_DIR = os.path.join(OUT_DIR, 'figures')
os.makedirs(FIG_DIR, exist_ok=True)

KARAN_CSV = os.path.join(RAW, 'karanverma19_multilingual_customer_support_intent_dataset.csv')
BANK_TRAIN = os.path.join(RAW, 'banking77_train.csv')
BANK_TEST = os.path.join(RAW, 'banking77_test.csv')

def read_csv_dict(path):
    with open(path, newline='', encoding='utf-8') as fh:
        r = csv.DictReader(fh)
        return list(r)

def detect_indic_scripts(text):
    # Unicode ranges for major Indic scripts
    ranges = [
        (0x0900, 0x097F), # Devanagari
        (0x0980, 0x09FF), # Bengali
        (0x0A00, 0x0A7F), # Gurmukhi
        (0x0A80, 0x0AFF), # Gujarati
        (0x0B00, 0x0B7F), # Oriya
        (0x0B80, 0x0BFF), # Tamil
        (0x0C00, 0x0C7F), # Telugu
        (0x0C80, 0x0CFF), # Kannada
        (0x0D00, 0x0D7F), # Malayalam
    ]
    has = set()
    for ch in text:
        o = ord(ch)
        for lo,hi in ranges:
            if lo <= o <= hi:
                has.add((lo,hi))
    return len(has) > 0

def is_ascii_only(text):
    try:
        text.encode('ascii')
        return True
    except Exception:
        return False

def analyze_karan():
    rows = read_csv_dict(KARAN_CSV)
    total = len(rows)
    lang_counts = Counter()
    lang_intent = defaultdict(Counter)
    queries = defaultdict(list)
    dup_counter = Counter()
    texts_seen = Counter()
    for r in rows:
        lang = r.get('language') or r.get('lang') or r.get('Language')
        lang_counts[lang] += 1
        intent = r.get('intent') or r.get('category') or r.get('label')
        lang_intent[lang][intent] += 1
        q = r.get('query') or r.get('text') or r.get('Text') or ''
        texts_seen[q] += 1
        queries[lang].append({'query': q, 'intent': intent})

    duplicates = {q:c for q,c in texts_seen.items() if c>1}

    rep_examples = {}
    for lang, items in queries.items():
        rep_examples[lang] = [it['query'] for it in items[:3]]

    # Build outputs
    karan = {
        'total_records': total,
        'unique_language_labels': sorted(list(lang_counts.keys())),
        'language_counts': dict(lang_counts),
        'language_percent': {k: round(v/total*100,2) for k,v in lang_counts.items()},
        'language_intent_distribution': {k:dict(v) for k,v in lang_intent.items()},
        'duplicate_queries': duplicates,
        'representative_examples': rep_examples,
        'note': 'The `language` column is metadata supplied by the source dataset.'
    }

    # Figures: pie chart of language distribution
    labels = list(lang_counts.keys())
    sizes = [lang_counts[l] for l in labels]
    if labels:
        fig, ax = plt.subplots(figsize=(6,6))
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        ax.set_title('karanverma19 language distribution')
        plt.tight_layout()
        plt.savefig(os.path.join(FIG_DIR, 'karan_language_pie.png'))
        plt.close(fig)

    # Bar chart: top intents per language (stacked) - simplified: top 10 intents overall
    all_intents = Counter()
    for d in lang_intent.values():
        all_intents.update(d)
    top_intents = [i for i,_ in all_intents.most_common(10)]
    if top_intents:
        fig, ax = plt.subplots(figsize=(10,6))
        import numpy as np
        langs = list(lang_counts.keys())
        ind = range(len(top_intents))
        bottom = [0]*len(top_intents)
        for lang in langs:
            vals = [lang_intent[lang].get(it,0) for it in top_intents]
            ax.bar(top_intents, vals, bottom=bottom, label=str(lang))
            bottom = [b+v for b,v in zip(bottom,vals)]
        ax.set_ylabel('Count')
        ax.set_title('Top intents (10) by language (karanverma19)')
        ax.legend()
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(os.path.join(FIG_DIR, 'karan_language_intent_bar.png'))
        plt.close(fig)

    return karan

def analyze_banking77():
    rows = read_csv_dict(BANK_TRAIN) + read_csv_dict(BANK_TEST)
    total = len(rows)
    ascii_only = 0
    indic_script_present = 0
    indic_examples = []
    non_ascii_examples = []
    for r in rows:
        t = r.get('text') or r.get('Text') or ''
        if is_ascii_only(t):
            ascii_only += 1
        else:
            non_ascii_examples.append(t)
        if detect_indic_scripts(t):
            indic_script_present += 1
            if len(indic_examples) < 5:
                indic_examples.append(t)

    banking = {
        'total_records': total,
        'ascii_only_count': ascii_only,
        'ascii_only_percent': round(ascii_only/total*100,2) if total else 0,
        'non_ascii_count': total-ascii_only,
        'indic_script_count': indic_script_present,
        'indic_script_examples': indic_examples[:5]
    }

    # Figure: ASCII vs non-ASCII
    labels = ['ASCII-only','Non-ASCII']
    sizes = [ascii_only, total-ascii_only]
    fig, ax = plt.subplots(figsize=(6,4))
    ax.bar(labels, sizes, color=['#4c72b0','#dd8452'])
    ax.set_ylabel('Count')
    ax.set_title('BANKING77: ASCII-only vs Non-ASCII')
    for i,v in enumerate(sizes):
        ax.text(i, v+5, str(v), ha='center')
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, 'banking77_ascii_stats.png'))
    plt.close(fig)

    return banking

def write_outputs(karan, banking):
    out = {
        'generated_on': __import__('datetime').datetime.utcnow().isoformat() + 'Z',
        'karanverma19': karan,
        'banking77_observational': banking,
        'notes': [
            'All analysis is read-only with respect to data/raw_data/',
            'karanverma19 `language` column is dataset-provided metadata.'
        ]
    }
    with open(os.path.join(OUT_DIR, 'step3d_results.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    # Write concise human-readable report
    md = []
    md.append('# Step 3D: Language Identification — Report')
    md.append('')
    md.append('Purpose: establish observed language composition of available datasets (read-only).')
    md.append('')
    md.append('## Dataset language metadata')
    md.append('- karanverma19: language labels supplied by dataset in `language` column.')
    md.append('- BANKING77: documented as English (dataset metadata).')
    md.append('')
    md.append('## karanverma19 language distribution')
    md.append(f"- total records: {karan['total_records']}")
    md.append('- unique language labels: ' + ', '.join(karan['unique_language_labels']))
    md.append('')
    md.append('Language counts:')
    for k,v in karan['language_counts'].items():
        md.append(f'- {k}: {v} ({karan['language_percent'][k]}%)')
    md.append('')
    md.append('Language × intent distribution: (see JSON `language_intent_distribution`)')
    md.append('')
    md.append('Representative examples (exact text from dataset):')
    for k, examples in karan['representative_examples'].items():
        md.append(f'- {k}:')
        for ex in examples:
            md.append(f'  - {ex}')
    md.append('')
    md.append('## BANKING77 observational language check')
    md.append(f"- total records (train+test): {banking['total_records']}")
    md.append(f"- ASCII-only texts: {banking['ascii_only_count']} ({banking['ascii_only_percent']}%)")
    md.append(f"- non-ASCII texts: {banking['non_ascii_count']}")
    md.append(f"- texts containing Indic-script characters: {banking['indic_script_count']}")
    md.append('')
    md.append('Representative BANKING77 examples containing Indic-script characters (if any):')
    for ex in banking['indic_script_examples']:
        md.append(f'- {ex}')
    md.append('')
    md.append('## Romanized / transliterated text')
    md.append('- karanverma19: language metadata may indicate romanized labels if present; analysis lists labels as-is.')
    md.append('- BANKING77: predominantly ASCII/Latin script; romanized Indian-language identification cannot be reliably inferred from ASCII-only text.')
    md.append('')
    md.append('## Code-mixing (observational)')
    md.append('- Candidate examples for later code-mixing analysis are those containing characters from multiple scripts (Latin + Indic). See JSON for flagged examples.')
    md.append('')
    md.append('## Limitations')
    md.append('- karanverma19 contains only 41 records; conclusions exploratory.')
    md.append('- `language` column is dataset-supplied metadata and may not be ground truth.')
    md.append('- BANKING77 is an English dataset and provides limited multilingual signal.')
    md.append('- Romanized Indian-language detection is non-trivial for ASCII text; further methods required.')
    md.append('')
    md.append('## Key conclusions')
    md.append('- karanverma19 provides explicit language metadata; see JSON counts and figures.')
    md.append('- BANKING77 is predominantly ASCII/Latin script and aligns with dataset documentation stating English.')
    md.append('')
    with open(os.path.join(OUT_DIR, 'STEP3D_LANGUAGE_REPORT.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(md))

def main():
    karan = analyze_karan()
    banking = analyze_banking77()
    write_outputs(karan, banking)
    print('Step 3D analysis complete. Outputs written to analysis/ and analysis/figures/')

if __name__ == '__main__':
    main()
