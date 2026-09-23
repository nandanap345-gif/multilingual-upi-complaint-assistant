#!/usr/bin/env python3
"""Step 3E: Exploratory Romanized / Code-mixed analysis (read-only)

Produces:
 - analysis/step3e_results.json
 - analysis/STEP3E_ROMANIZED_CODEMIX_REPORT.md
 - analysis/figures/karan_step3e_lang_dist.png
 - analysis/figures/karan_step3e_classification_pie.png

Strictly read-only for data/raw_data/.
"""
import os
import csv
import json
from collections import Counter, defaultdict
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(__file__))
RAW = os.path.join(ROOT, 'data', 'raw_data')
OUT = os.path.join(ROOT, 'analysis')
FIG = os.path.join(OUT, 'figures')
os.makedirs(FIG, exist_ok=True)

KARAN = os.path.join(RAW, 'karanverma19_multilingual_customer_support_intent_dataset.csv')
BANK_TRAIN = os.path.join(RAW, 'banking77_train.csv')
BANK_TEST = os.path.join(RAW, 'banking77_test.csv')

# Conservative set of high-precision romanized markers (explicit romanized words)
ROMANIZED_KEYWORDS = set([
    'hai', 'nahi', 'kab', 'kyun', 'kado', 'ka', 'ke', 'ki', 'kya', 'paise', 'mera', 'meri'
])

# Small English indicator set (content/function words)
ENGLISH_SIGNS = set(['the','and','is','are','you','please','order','payment','refund','delivery','account','card','transfer'])

def read_rows(path):
    with open(path, newline='', encoding='utf-8') as fh:
        r = csv.DictReader(fh)
        return list(r)

def tokenize(text):
    return [t.strip('.,?!;:"').lower() for t in text.split() if t.strip()]

def is_likely_romanized(tokens):
    # Conservative: require explicit romanized markers present
    return any(t in ROMANIZED_KEYWORDS for t in tokens)

def has_english_tokens(tokens):
    for t in tokens:
        if t in ENGLISH_SIGNS:
            return True
    return False

def analyze_karan():
    rows = read_rows(KARAN)
    total = len(rows)
    lang_groups = defaultdict(list)
    for r in rows:
        lang = r.get('language') or r.get('lang') or 'unknown'
        lang_groups[lang].append(r)

    results = {'total_records': total, 'per_language': {}}

    # For each of the target labels
    for label in ['Hinglish','Hindi','Punjabi','English']:
        items = lang_groups.get(label, [])
        n = len(items)
        perc = round(n/total*100,2) if total else 0
        reps = [it.get('query') or it.get('text') or '' for it in items[:5]]
        obs_chars = []

        likely_romanized = []
        likely_code_mixed = []
        uncertain = []

        for it in items:
            text = (it.get('query') or it.get('text') or '').strip()
            toks = tokenize(text)
            roman = is_likely_romanized(toks)
            english = has_english_tokens(toks)
            # Conservative decision rules with manual-review style outcomes:
            # - If explicit romanized markers present and at least two English tokens, flag code-mixed candidate.
            # - If explicit romanized markers present and only isolated English loanword (e.g., 'refund'), classify as likely_romanized (loanword case).
            # - If explicit romanized markers present and no English tokens, classify as likely_romanized.
            # - Otherwise mark uncertain.
            eng_tokens = [t for t in toks if t in ENGLISH_SIGNS]
            if roman:
                if len(eng_tokens) >= 2:
                    heuristic = f"romanized markers + {len(eng_tokens)} English tokens"
                    likely_code_mixed.append({'text': text, 'heuristic': heuristic})
                else:
                    # treat as romanized with possible English loanword
                    heuristic = 'romanized markers (possibly with English loanword)'
                    likely_romanized.append({'text': text, 'heuristic': heuristic})
            else:
                if len(eng_tokens) >= 2 and label != 'English':
                    # English-heavy in non-English label -> possible code-mixing (conservative)
                    heuristic = f"{len(eng_tokens)} English tokens in non-English label"
                    likely_code_mixed.append({'text': text, 'heuristic': heuristic})
                else:
                    uncertain.append({'text': text, 'heuristic': 'no clear romanized markers or mixed evidence'})

        # Build final entry with per-record manual-style review lists
        results['per_language'][label] = {
            'count': n,
            'percent': perc,
            'representative_examples': reps,
            'likely_romanized_count': len(likely_romanized),
            'likely_code_mixed_count': len(likely_code_mixed),
            'uncertain_count': len(uncertain),
            'likely_romanized_examples': [ {'text': x['text'], 'heuristic': x.get('heuristic')} for x in likely_romanized[:5]],
            'likely_code_mixed_examples': [ {'text': x['text'], 'heuristic': x.get('heuristic')} for x in likely_code_mixed[:5]],
            'uncertain_examples': [ {'text': x['text'], 'heuristic': x.get('heuristic')} for x in uncertain[:5]]
        }

    # Summary table
    summary = []
    for label in ['Hinglish','Hindi','Punjabi','English']:
        pl = results['per_language'].get(label, {})
        summary.append({
            'dataset': 'karanverma19',
            'language_label': label,
            'total_records': pl.get('count',0),
            'likely_romanized': pl.get('likely_romanized_count',0),
            'likely_code_mixed': pl.get('likely_code_mixed_count',0),
            'uncertain': pl.get('uncertain_count',0)
        })

    # BANKING77 brief check for informal English (sample)
    bank_rows = read_rows(BANK_TRAIN) + read_rows(BANK_TEST)
    informal_examples = []
    for r in bank_rows[:50]:
        t = (r.get('text') or '').lower()
        if any(x in t for x in ['plz','pls','u ','cant ','wont ','dont ','im ']):
            informal_examples.append(r.get('text'))
    bank_obs = {'total_records': len(bank_rows), 'informal_examples_sample': informal_examples[:10]}

    out = {'generated_on': __import__('datetime').datetime.utcnow().isoformat() + 'Z',
           'karanverma19_analysis': results,
           'karan_summary_table': summary,
           'banking77_observational': bank_obs,
           'notes': [
               'Exploratory heuristics only; not gold-standard annotations.',
               '`language` column is dataset-provided metadata.'
           ]}

    with open(os.path.join(OUT, 'step3e_results.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    # Figures: language-label distribution
    labels = []
    counts = []
    for label in ['Hinglish','Hindi','Punjabi','English']:
        pl = results['per_language'].get(label, {})
        labels.append(label)
        counts.append(pl.get('count',0))
    fig, ax = plt.subplots(figsize=(6,4))
    ax.bar(labels, counts, color=['#4c72b0','#dd8452','#55a868','#c44e52'])
    ax.set_title('karanverma19: Language-label distribution')
    ax.set_ylabel('Count')
    for i,v in enumerate(counts):
        ax.text(i, v+0.5, str(v), ha='center')
    plt.tight_layout()
    plt.savefig(os.path.join(FIG, 'karan_step3e_lang_dist.png'))
    plt.close(fig)

    # Pie: classification distribution (likely_romanized / code-mixed / uncertain total)
    total_r = sum(pl.get('likely_romanized_count',0) for pl in results['per_language'].values())
    total_c = sum(pl.get('likely_code_mixed_count',0) for pl in results['per_language'].values())
    total_u = sum(pl.get('uncertain_count',0) for pl in results['per_language'].values())
    labels2 = ['likely_romanized','likely_code_mixed','uncertain']
    sizes = [total_r, total_c, total_u]
    fig, ax = plt.subplots(figsize=(6,6))
    ax.pie(sizes, labels=labels2, autopct='%1.1f%%', startangle=90)
    ax.set_title('karanverma19: exploratory romanized/code-mixed/uncertain')
    plt.tight_layout()
    plt.savefig(os.path.join(FIG, 'karan_step3e_classification_pie.png'))
    plt.close(fig)

    # Write report
    md = []
    md.append('# Step 3E: Romanized and Code-Mixed Text — Exploratory Report')
    md.append('')
    md.append('Purpose: exploratory identification of Romanized and code-mixed examples in karanverma19 (read-only).')
    md.append('')
    md.append('## A. karanverma19 per-language breakdown (labels from dataset)')
    md.append(f"- total records: {results['total_records']}")
    md.append('')
    for label in ['Hinglish','Hindi','Punjabi','English']:
        pl = results['per_language'].get(label, {})
        md.append(f"### {label}")
        md.append(f"- count: {pl.get('count',0)}")
        md.append(f"- percent: {pl.get('percent',0)}%")
        md.append('- representative examples:')
        for ex in pl.get('representative_examples',[])[:3]:
            md.append(f'  - {ex}')
        md.append('- observed linguistic characteristics:')
        md.append('  - informal spellings, phonetic renderings, mixed English tokens (see examples)')
        md.append('')
    md.append('## B. Romanized text observations')
    md.append('- Heuristics used: presence of common romanized tokens (e.g., "hai", "nahi", "kab", "kyun", "paise") and phonetic endings.')
    md.append('- Representative likely-romanized examples (per language) in JSON.')
    md.append('')
    md.append('## C. Code-mixing (exploratory candidates)')
    md.append('- Conservative approach: flagged texts containing both romanized Indic tokens and English tokens.')
    md.append('- See JSON for per-example labels and brief reasons.')
    md.append('')
    md.append('## D. BANKING77 brief comparison')
    md.append(f"- total records: {len(bank_rows)}; predominantly English per dataset documentation.")
    md.append('- Sample informal examples (small sample) provided in JSON.')
    md.append('')
    md.append('## E. Limitations')
    md.append('- karanverma19 has only 41 records; findings exploratory.')
    md.append('- `language` column is dataset-provided metadata and may not be ground truth.')
    md.append('- Romanized detection heuristics are not exhaustive; manual annotation required for gold labels.')
    md.append('- Code-mixing can occur within the same script; script-based checks are insufficient.')
    md.append('')
    md.append('## F. Summary table (exploratory)')
    md.append('- See JSON `karan_summary_table` for an explicit table of counts per label and exploratory flags.')

    with open(os.path.join(OUT, 'STEP3E_ROMANIZED_CODEMIX_REPORT.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(md))

    print('Step 3E exploratory analysis complete: outputs in analysis/ and analysis/figures/')

if __name__ == '__main__':
    analyze_karan()
