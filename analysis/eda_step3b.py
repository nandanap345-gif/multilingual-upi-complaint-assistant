#!/usr/bin/env python3
"""Step 3B EDA (read-only).
Generates JSON results, a markdown report, and figures under analysis/figures.
This script does NOT modify any files under data/raw_data/.
"""
import csv, os, json, math, statistics, collections, datetime, re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RAW = os.path.join(ROOT, 'data', 'raw_data')
FIG_DIR = os.path.join(ROOT, 'analysis', 'figures')
os.makedirs(FIG_DIR, exist_ok=True)

def read_csv(path):
    with open(path, 'r', encoding='utf-8', newline='') as f:
        r = csv.reader(f)
        header = next(r, [])
        rows = [row for row in r]
    return header, rows

def col_stats(rows, col_index):
    vals = [row[col_index] for row in rows if len(row) > col_index]
    missing = sum(1 for v in vals if v is None or v == '')
    return {'count': len(vals), 'missing': missing}

def text_length_stats(texts):
    chars = [len(t) for t in texts]
    words = [len(t.split()) for t in texts]
    def stats(lst):
        return {
            'min': min(lst) if lst else 0,
            'max': max(lst) if lst else 0,
            'mean': statistics.mean(lst) if lst else 0,
            'median': statistics.median(lst) if lst else 0,
            'stdev': statistics.pstdev(lst) if lst else 0
        }
    return {'char': stats(chars), 'word': stats(words)}

def detect_text_characteristics(texts):
    pct_nonascii = sum(1 for t in texts if any(ord(c) > 127 for c in t))
    pct_digits = sum(1 for t in texts if re.search(r'\d', t))
    pct_punct = sum(1 for t in texts if re.search(r'[!"#$%&\'\(\)\*\+,\-\./:;<=>?@\[\\\]^_`{|}~]', t))
    pct_has_upper_acro = sum(1 for t in texts if re.search(r'\b[A-Z]{2,}\b', t))
    return {
        'count': len(texts),
        'non_ascii_count': pct_nonascii,
        'has_digits_count': pct_digits,
        'has_punctuation_count': pct_punct,
        'has_upper_acronym_count': pct_has_upper_acro
    }

def analyze_banking(train_path, test_path):
    header_t, rows_t = read_csv(train_path)
    header_e, rows_e = read_csv(test_path)
    # Basic counts
    train_rows = len(rows_t)
    test_rows = len(rows_e)
    # Column names and dtypes (string)
    columns = header_t if header_t else header_e
    # Missing values per column
    missing = {c: 0 for c in columns}
    for row in rows_t + rows_e:
        for i,c in enumerate(columns):
            if i >= len(row) or row[i] == '':
                missing[c] += 1
    # Duplicate complaint-text counts
    texts_t = [row[0].strip() for row in rows_t if len(row) >= 1]
    texts_e = [row[0].strip() for row in rows_e if len(row) >= 1]
    dup_train = sum(1 for v in collections.Counter(texts_t).values() if v > 1)
    dup_test = sum(1 for v in collections.Counter(texts_e).values() if v > 1)
    dup_combined = sum(1 for v in collections.Counter(texts_t + texts_e).values() if v > 1)
    unique_texts = len(set(texts_t + texts_e))
    # Intents
    intents_t = [row[1].strip() for row in rows_t if len(row) >= 2]
    intents_e = [row[1].strip() for row in rows_e if len(row) >= 2]
    intent_counts = collections.Counter(intents_t + intents_e)
    # Text length stats
    all_texts = texts_t + texts_e
    tl_stats = text_length_stats(all_texts)
    char_stats = tl_stats['char']
    word_stats = tl_stats['word']
    # Identify unusually short/long using descriptive stats (mean +/- 2*stdev)
    chars = [len(t) for t in all_texts]
    mean = char_stats['mean']; stdev = char_stats['stdev']
    short_thresh = max(0, mean - 2 * stdev)
    long_thresh = mean + 2 * stdev
    unusually_short = [t for t in all_texts if len(t) <= short_thresh][:10]
    unusually_long = [t for t in all_texts if len(t) >= long_thresh][:10]
    # Representative examples for a few intents (top 3 intents)
    top_intents = [it for it, _ in intent_counts.most_common(3)]
    examples = {}
    for it in top_intents:
        ex = []
        for row in rows_t + rows_e:
            if len(row) >= 2 and row[1].strip() == it:
                ex.append(row[0])
            if len(ex) >= 5:
                break
        examples[it] = ex

    return {
        'train_rows': train_rows,
        'test_rows': test_rows,
        'columns': columns,
        'missing_values': missing,
        'dup_train_texts': dup_train,
        'dup_test_texts': dup_test,
        'dup_combined_texts': dup_combined,
        'unique_texts': unique_texts,
        'unique_intents': len(set(intents_t + intents_e)),
        'intent_counts': intent_counts,
        'char_stats': char_stats,
        'word_stats': word_stats,
        'unusually_short_examples': unusually_short,
        'unusually_long_examples': unusually_long,
        'representative_examples': examples
    }

def analyze_karan(path):
    header, rows = read_csv(path)
    cols = header
    texts = []
    intents = []
    langs = []
    # Determine column indices from header when available
    if header and len(header) >= 1:
        # normalize header names to lower-case for matching
        hmap = {h.strip().lower(): i for i, h in enumerate(header)}
        qidx = hmap.get('query', hmap.get('text', 0))
        intent_idx = hmap.get('intent', hmap.get('category', None))
        lang_idx = hmap.get('language', None)
    else:
        qidx = 0
        intent_idx = 1
        lang_idx = None
    for row in rows:
        if len(row) <= qidx:
            continue
        query = row[qidx].strip()
        texts.append(query)
        if intent_idx is not None and len(row) > intent_idx:
            intents.append(row[intent_idx].strip())
        else:
            intents.append('')
        if lang_idx is not None and len(row) > lang_idx:
            langs.append(row[lang_idx].strip())
        else:
            langs.append('')
    dup_texts = sum(1 for v in collections.Counter(texts).values() if v > 1)
    unique_texts = len(set(texts))
    intent_counts = collections.Counter(intents)
    lang_counts = collections.Counter(langs)
    tl_stats = text_length_stats(texts)
    return {
        'rows': len(rows),
        'columns': cols,
        'missing_values': {c: 0 for c in cols},
        'dup_texts': dup_texts,
        'unique_texts': unique_texts,
        'unique_intents': len(set(intents)),
        'intent_counts': intent_counts,
        'lang_counts': lang_counts,
        'char_stats': tl_stats['char'],
        'word_stats': tl_stats['word']
    }

def cross_compare(banking_res, karan_res):
    return {
        'banking_rows': banking_res['train_rows'] + banking_res['test_rows'],
        'banking_intents': banking_res['unique_intents'],
        'banking_avg_char_len': banking_res['char_stats']['mean'],
        'karan_rows': karan_res['rows'],
        'karan_intents': karan_res['unique_intents'],
        'karan_avg_char_len': karan_res['char_stats']['mean'],
        'banking_dup_count': banking_res['dup_combined_texts'],
        'karan_dup_count': karan_res['dup_texts']
    }

def main():
    train_p = os.path.join(RAW, 'banking77_train.csv')
    test_p = os.path.join(RAW, 'banking77_test.csv')
    karan_p = os.path.join(RAW, 'karanverma19_multilingual_customer_support_intent_dataset.csv')
    banking = analyze_banking(train_p, test_p)
    karan = analyze_karan(karan_p) if os.path.exists(karan_p) else None
    cross = cross_compare(banking, karan) if karan else None
    out = {
        'generated_on': datetime.datetime.utcnow().isoformat() + 'Z',
        'banking': banking,
        'karanverma19': karan,
        'cross_comparison': cross
    }
    # JSON results
    res_path = os.path.join(ROOT, 'analysis', 'step3b_results.json')
    with open(res_path, 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=2, default=str)
    print('WROTE', res_path)
    # Attempt to generate simple plots if matplotlib is available
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        # Intent frequency bar chart (top 20)
        intents = out['banking']['intent_counts']
        items = intents.most_common(20)
        labels = [i for i,_ in items]
        vals = [v for _,v in items]
        plt.figure(figsize=(10,6))
        plt.barh(range(len(vals))[::-1], vals, color='C0')
        plt.yticks(range(len(labels))[::-1], labels)
        plt.xlabel('Frequency')
        plt.title('Top 20 BANKING77 intents')
        plt.tight_layout()
        p1 = os.path.join(FIG_DIR, 'banking_top20_intents.png')
        plt.savefig(p1)
        plt.close()
        # Text length histogram
        all_texts = [t for t in (out['banking']['representative_examples'].get(labels[0], []) )]
        # Use char lengths from banking
        char_mean = out['banking']['char_stats']['mean']
        # For a proper histogram, recompute char lengths from raw files
        # Re-read combined texts
        header_t, rows_t = read_csv(os.path.join(RAW, 'banking77_train.csv'))
        header_e, rows_e = read_csv(os.path.join(RAW, 'banking77_test.csv'))
        combined_texts = [r[0] for r in rows_t+rows_e if len(r)>=1]
        lengths = [len(t) for t in combined_texts]
        plt.figure(figsize=(8,5))
        plt.hist(lengths, bins=40, color='C1')
        plt.xlabel('Character count')
        plt.ylabel('Number of texts')
        plt.title('BANKING77 text length distribution')
        plt.tight_layout()
        p2 = os.path.join(FIG_DIR, 'banking_text_length_hist.png')
        plt.savefig(p2)
        plt.close()
        # karan language distribution
        if out.get('karanverma19'):
            langs = out['karanverma19']['lang_counts']
            labels = list(langs.keys())
            vals = [langs[k] for k in labels]
            plt.figure(figsize=(6,4))
            plt.pie(vals, labels=labels, autopct='%d', startangle=90)
            plt.title('karanverma19 language distribution')
            plt.tight_layout()
            p3 = os.path.join(FIG_DIR, 'karan_language_pie.png')
            plt.savefig(p3)
            plt.close()
            # karan intent/category-frequency bar chart
            intents_counts = out['karanverma19']['intent_counts']
            intent_labels = list(intents_counts.keys())
            intent_vals = [intents_counts[k] for k in intent_labels]
            plt.figure(figsize=(8,4))
            plt.bar(range(len(intent_vals)), intent_vals, color='C2')
            plt.xticks(range(len(intent_labels)), intent_labels, rotation=45, ha='right')
            plt.ylabel('Frequency')
            plt.title('karanverma19 intent/category frequency')
            plt.tight_layout()
            p4 = os.path.join(FIG_DIR, 'karan_intent_freq.png')
            plt.savefig(p4)
            plt.close()
            # karan query text-length distribution
            # Re-read queries to compute lengths
            header_k, rows_k = read_csv(os.path.join(RAW, 'karanverma19_multilingual_customer_support_intent_dataset.csv'))
            if header_k and 'query' in [h.lower() for h in header_k]:
                qidx = [h.lower() for h in header_k].index('query')
            else:
                qidx = 0
            queries = [row[qidx] for row in rows_k if len(row) > qidx]
            q_lengths = [len(q) for q in queries]
            plt.figure(figsize=(8,4))
            plt.hist(q_lengths, bins=10, color='C3')
            plt.xlabel('Character count')
            plt.ylabel('Number of queries')
            plt.title('karanverma19 query text length distribution')
            plt.tight_layout()
            p5 = os.path.join(FIG_DIR, 'karan_query_length_hist.png')
            plt.savefig(p5)
            plt.close()
            # language x intent heatmap (if small)
            try:
                langs_list = list(out['karanverma19']['lang_counts'].keys())
                intents_list = list(out['karanverma19']['intent_counts'].keys())
                matrix = []
                for li in langs_list:
                    row_counts = []
                    for ii in intents_list:
                        # count occurrences in raw rows
                        cnt = 0
                        for r in rows_k:
                            # find indices again
                            if len(header_k) > 0:
                                idx_query = [h.lower() for h in header_k].index('query') if 'query' in [h.lower() for h in header_k] else 0
                                idx_intent = [h.lower() for h in header_k].index('intent') if 'intent' in [h.lower() for h in header_k] else 1
                                idx_lang = [h.lower() for h in header_k].index('language') if 'language' in [h.lower() for h in header_k] else None
                            else:
                                idx_query, idx_intent, idx_lang = 0, 1, None
                            if len(r) > idx_intent and len(r) > (idx_lang if idx_lang is not None else 0):
                                rlang = r[idx_lang].strip() if idx_lang is not None else ''
                                rintent = r[idx_intent].strip()
                                if rlang == li and rintent == ii:
                                    cnt += 1
                        row_counts.append(cnt)
                    matrix.append(row_counts)
                # plot heatmap
                import numpy as np
                mat = np.array(matrix)
                plt.figure(figsize=(8,4))
                plt.imshow(mat, aspect='auto', cmap='Blues')
                plt.colorbar(label='Count')
                plt.yticks(range(len(langs_list)), langs_list)
                plt.xticks(range(len(intents_list)), intents_list, rotation=45, ha='right')
                plt.title('karanverma19 language × intent counts')
                plt.tight_layout()
                p6 = os.path.join(FIG_DIR, 'karan_lang_intent_heatmap.png')
                plt.savefig(p6)
                plt.close()
            except Exception:
                pass
        print('PLOTS_SAVED to', FIG_DIR)
    except Exception as e:
        print('PLOTTING_SKIPPED:', e)

if __name__ == '__main__':
    main()
