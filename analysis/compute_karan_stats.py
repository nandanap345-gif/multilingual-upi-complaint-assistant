#!/usr/bin/env python3
import csv, os, statistics, collections

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
P = os.path.join(ROOT, 'data', 'raw_data', 'karanverma19_multilingual_customer_support_intent_dataset.csv')
texts = []
with open(P, 'r', encoding='utf-8', newline='') as f:
    r = csv.reader(f)
    header = next(r, None)
    if header and 'query' in header:
        qidx = header.index('query')
    else:
        qidx = 0
    for row in r:
        if len(row) > qidx:
            texts.append(row[qidx])

chars = [len(t) for t in texts]
words = [len(t.split()) for t in texts]
dups = sum(1 for v in collections.Counter(texts).values() if v > 1)
unique = len(set(texts))

def printf(k,v):
    print(f"{k}: {v}")

printf('rows', len(texts))
printf('unique_queries', unique)
printf('duplicate_queries', dups)
printf('char_min', min(chars) if chars else None)
printf('char_max', max(chars) if chars else None)
printf('char_mean', statistics.mean(chars) if chars else None)
printf('char_median', statistics.median(chars) if chars else None)
printf('char_stdev', statistics.pstdev(chars) if chars else None)
printf('word_min', min(words) if words else None)
printf('word_max', max(words) if words else None)
printf('word_mean', statistics.mean(words) if words else None)
printf('word_median', statistics.median(words) if words else None)
