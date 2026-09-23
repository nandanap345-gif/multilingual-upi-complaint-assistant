import csv, json, os, shutil, datetime
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
raw = os.path.join(root, 'data', 'raw_data')
train = os.path.join(raw, 'banking77_train.csv')
test = os.path.join(raw, 'banking77_test.csv')
readme = os.path.join(raw, 'banking77_README.md')
dataset_infos = os.path.join(raw, 'banking77_dataset_infos.json')
prov_path = os.path.join(raw, 'BANKING77_PROVENANCE.json')
# backup existing provenance
if os.path.exists(prov_path):
    ts = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    bak = prov_path.replace('.json', f'.BACKUP.{ts}.json')
    shutil.copy2(prov_path, bak)
    print('BACKUP_CREATED:', bak)
# compute stats using csv reader
def analyze_csv(p):
    with open(p, 'r', encoding='utf-8', newline='') as f:
        reader = csv.reader(f)
        rows = list(reader)
    header = rows[0] if rows else []
    data = rows[1:]
    num_rows = len(data)
    labels = [row[-1].strip() for row in data if len(row)>=2]
    unique_labels = sorted(set(labels))
    size_bytes = os.path.getsize(p)
    return dict(path=os.path.abspath(p), filename=os.path.basename(p), header=header, num_rows=num_rows, size_bytes=size_bytes, unique_label_count=len(unique_labels), unique_labels_sample=unique_labels[:100])
train_info = analyze_csv(train)
test_info = analyze_csv(test)
# license and languages from dataset_infos or README
license = None
languages = []
if os.path.exists(dataset_infos):
    try:
        with open(dataset_infos,'r',encoding='utf-8') as f:
            di = json.load(f)
            lic = di.get('default',{}).get('license')
            if lic: license = lic
            lang = di.get('default',{}).get('language')
            if lang and isinstance(lang, list): languages = lang
    except Exception as e:
        pass
if not license and os.path.exists(readme):
    txt = open(readme,'r',encoding='utf-8').read()
    if 'Creative Commons' in txt or 'CC-BY' in txt:
        license = 'CC-BY-4.0'
    if 'Languages' in txt and 'English' in txt:
        languages = ['English']
# build provenance
prov = {
    'dataset': 'BANKING77',
    'accepted_source': 'https://raw.githubusercontent.com/PolyAI-LDN/task-specific-datasets/master/banking_data',
    'source_files': {
        'train': 'https://raw.githubusercontent.com/PolyAI-LDN/task-specific-datasets/master/banking_data/train.csv',
        'test': 'https://raw.githubusercontent.com/PolyAI-LDN/task-specific-datasets/master/banking_data/test.csv',
        'dataset_page': 'https://huggingface.co/datasets/PolyAI/banking77'
    },
    'license': license or 'UNKNOWN',
    'languages': languages,
    'verified_on': datetime.datetime.utcnow().isoformat() + 'Z',
    'files': {
        'train': train_info,
        'test': test_info
    }
}
# write new provenance
with open(prov_path,'w',encoding='utf-8') as f:
    json.dump(prov,f,indent=2)
print('WROTE:', prov_path)
print('SUMMARY: train_rows=', train_info['num_rows'], 'test_rows=', test_info['num_rows'], 'unique_intents=', train_info['unique_label_count'], ' (train)')
