import csv
from pathlib import Path
ROOT = Path(__file__).parent.parent
raw = ROOT / 'data' / 'raw_data'

def count_csv(path):
    with open(path, encoding='utf-8') as f:
        r = csv.reader(f)
        rows = list(r)
    return len(rows)-1, rows[0] if rows else []

train = raw / 'banking77_train.csv'
test = raw / 'banking77_test.csv'
karan = raw / 'karanverma19_multilingual_customer_support_intent_dataset.csv'

train_count, train_header = count_csv(train)
test_count, test_header = count_csv(test)
karan_count, karan_header = count_csv(karan)

import json
out = {
    'banking_train_rows': train_count,
    'banking_test_rows': test_count,
    'banking_total': train_count + test_count,
    'banking_header': train_header,
    'karan_rows': karan_count,
    'karan_header': karan_header
}
print(json.dumps(out, indent=2))
