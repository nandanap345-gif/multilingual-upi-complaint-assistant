import os
import csv
import unicodedata
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
RAW = ROOT / 'data' / 'raw_data'
PROC = ROOT / 'data' / 'processed'
PROC.mkdir(parents=True, exist_ok=True)

def normalize_text(t):
    if t is None:
        return ''
    # Unicode normalize
    t = unicodedata.normalize('NFKC', t)
    # replace non-breaking spaces with normal spaces
    t = t.replace('\u00A0', ' ')
    # collapse whitespace
    t = re.sub(r'\s+', ' ', t)
    # trim
    t = t.strip()
    return t

def process_csv(inpath, outpath, text_field_names):
    with open(inpath, encoding='utf-8') as inf:
        reader = csv.DictReader(inf)
        rows = list(reader)
        headers = reader.fieldnames

    processed = []
    missing_text = 0
    for r in rows:
        newr = dict(r)
        for f in text_field_names:
            if f in newr:
                orig = newr[f]
                new = normalize_text(orig) if orig is not None else ''
                if new == '':
                    missing_text += 1
                newr[f] = new
        processed.append(newr)

    # write out
    with open(outpath, 'w', encoding='utf-8', newline='') as outf:
        writer = csv.DictWriter(outf, fieldnames=headers)
        writer.writeheader()
        for r in processed:
            writer.writerow(r)

    return {
        'input_rows': len(rows),
        'output_rows': len(processed),
        'missing_text_count': missing_text,
        'headers': headers
    }

def count_duplicates(path, key_fields):
    seen = set()
    dup = 0
    with open(path, encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            key = tuple(row[k] for k in key_fields if k in row)
            if key in seen:
                dup += 1
            else:
                seen.add(key)
    return dup

def main():
    report = {}

    # Process BANKING77 train/test
    train_in = RAW / 'banking77_train.csv'
    test_in = RAW / 'banking77_test.csv'
    train_out = PROC / 'banking77_train.csv'
    test_out = PROC / 'banking77_test.csv'

    r_train = process_csv(train_in, train_out, ['text'])
    r_test = process_csv(test_in, test_out, ['text'])

    report['banking_train'] = r_train
    report['banking_test'] = r_test

    # Count intents
    intents = set()
    with open(train_out, encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            intents.add(row.get('category',''))
    with open(test_out, encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            intents.add(row.get('category',''))
    report['banking_unique_intents'] = len([i for i in intents if i])

    # duplicate checks within splits
    report['banking_train_duplicates'] = count_duplicates(train_out, ['text','category'])
    report['banking_test_duplicates'] = count_duplicates(test_out, ['text','category'])

    # Remove cross-split duplicates from processed test to prevent leakage
    train_texts = set()
    with open(train_out, encoding='utf-8') as f:
        r = csv.DictReader(f)
        for row in r:
            train_texts.add(row.get('text',''))

    # read test processed, filter out rows whose text appears in train_texts
    kept = []
    removed = 0
    with open(test_out, encoding='utf-8') as f:
        r = csv.DictReader(f)
        headers = r.fieldnames
        for row in r:
            if row.get('text','') in train_texts:
                removed += 1
            else:
                kept.append(row)

    # overwrite test_out with kept rows
    with open(test_out, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for row in kept:
            writer.writerow(row)

    report['cross_split_duplicates_removed_from_test'] = removed
    report['banking_test_duplicates_after_removal'] = count_duplicates(test_out, ['text','category'])
    report['cross_split_duplicates'] = removed
    # update r_test output_rows to reflect removal
    r_test['output_rows'] = len(kept)

    # Process karanverma19
    karan_in = RAW / 'karanverma19_multilingual_customer_support_intent_dataset.csv'
    karan_out = PROC / 'karanverma19_multilingual_customer_support_intent_dataset.csv'
    r_karan = process_csv(karan_in, karan_out, ['query'])
    report['karan'] = r_karan
    report['karan_duplicates'] = count_duplicates(karan_out, ['query','intent','language'])

    # Malayalam statement
    report['malayalam_policy_statement'] = "Malayalam is retained as a documented language/resource scope and limitation, but no synthetic or translated Malayalam training data is introduced in Step 3G."

    # write preprocessing report (MD)
    report_md = ROOT / 'analysis' / 'STEP3G_PREPROCESSING_REPORT.md'
    with open(report_md, 'w', encoding='utf-8') as fh:
        fh.write('# Step 3G Preprocessing Report\n\n')
        fh.write('## Banking77\n')
        fh.write(f"- train input rows: {r_train['input_rows']}\n")
        fh.write(f"- test input rows: {r_test['input_rows']}\n")
        fh.write(f"- train output rows: {r_train['output_rows']}\n")
        fh.write(f"- test output rows: {r_test['output_rows']}\n")
        fh.write(f"- unique intents (combined): {report['banking_unique_intents']}\n")
        fh.write(f"- train duplicates: {report['banking_train_duplicates']}\n")
        fh.write(f"- test duplicates: {report['banking_test_duplicates']}\n")
        fh.write(f"- cross-split duplicates removed from processed test: {report.get('cross_split_duplicates_removed_from_test',0)}\n")
        fh.write(f"- cross-split duplicates (original in raw): {report['cross_split_duplicates']}\n")
        fh.write('\n## karanverma19\n')
        fh.write(f"- input rows: {r_karan['input_rows']}\n")
        fh.write(f"- output rows: {r_karan['output_rows']}\n")
        fh.write(f"- duplicates: {report['karan_duplicates']}\n")
        fh.write('\n## Missing text counts\n')
        fh.write(f"- banking_train missing text: {r_train['missing_text_count']}\n")
        fh.write(f"- banking_test missing text: {r_test['missing_text_count']}\n")
        fh.write(f"- karan missing text: {r_karan['missing_text_count']}\n")
        fh.write('\n## Malayalam policy\n')
        fh.write(report['malayalam_policy_statement'] + '\n')
        fh.write('\n## Examples of normalization (short)\n')
        # include a few examples: read first 3 rows from previews
        with open(PROC / 'banking77_train.csv', encoding='utf-8') as f:
            r = csv.DictReader(f)
            i = 0
            for row in r:
                fh.write(f"- {row.get('text','')[:200]}\n")
                i += 1
                if i >= 3:
                    break

    # write JSON report
    with open(ROOT / 'analysis' / 'step3g_preprocessing_report.json', 'w', encoding='utf-8') as jf:
        json.dump(report, jf, indent=2, ensure_ascii=False)

    print('Preprocessing complete. Report written to', report_md)

if __name__ == '__main__':
    main()
