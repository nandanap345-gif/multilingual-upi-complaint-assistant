import csv, json, os, sys

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
train = os.path.join(repo_root, 'data', 'raw_data', 'banking77_train.csv')
test = os.path.join(repo_root, 'data', 'raw_data', 'banking77_test.csv')
dataset_infos = os.path.join(repo_root, 'data', 'raw_data', 'banking77_dataset_infos.json')

def analyze(path):
    res = {'path': path}
    with open(path, 'r', encoding='utf-8', newline='') as f:
        reader = csv.reader(f)
        rows = list(reader)
    if not rows:
        res.update({'header': None, 'num_rows': 0})
        return res
    header = rows[0]
    data = rows[1:]
    res['header'] = header
    res['num_rows'] = len(data)
    # columns per row distribution
    dist = {}
    labels = []
    problematic = []
    for idx, row in enumerate(data, start=2):
        dist[len(row)] = dist.get(len(row), 0) + 1
        if len(row) >= 2:
            labels.append(row[-1].strip())
        else:
            problematic.append({'line': idx, 'row': row})
            labels.append('')
    res['col_counts'] = dist
    res['unique_labels'] = sorted(set(labels))
    res['unique_label_count'] = len(set([l for l in labels if l!='']))
    res['sample_problematic'] = problematic[:20]
    # show last 10 rows
    res['last_10_rows'] = data[-10:]
    return res

train_res = analyze(train)
test_res = analyze(test)

official_labels = None
if os.path.exists(dataset_infos):
    try:
        with open(dataset_infos, 'r', encoding='utf-8') as f:
            di = json.load(f)
            names = di['default']['features']['label']['names']
            official_labels = names
    except Exception as e:
        official_labels = None

out = {
    'train': train_res,
    'test': test_res,
    'official_label_count': len(official_labels) if official_labels else None,
    'official_labels_sample': (official_labels[:20] if official_labels else None)
}

# compare labels
if official_labels:
    train_labels_set = set(train_res['unique_labels'])
    test_labels_set = set(test_res['unique_labels'])
    combined = (train_labels_set | test_labels_set)
    official_set = set(official_labels)
    out['labels_only_in_download'] = sorted(list(combined - official_set))
    out['labels_missing_from_download'] = sorted(list(official_set - combined))

print(json.dumps(out, indent=2, ensure_ascii=False))
