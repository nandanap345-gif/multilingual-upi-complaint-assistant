#!/usr/bin/env python3
"""Step 3C: Complaint / Intent Analysis (read-only)
Generates a JSON summary and a markdown report classifying BANKING77 intents
into DIRECT / BORDERLINE / IRRELEVANT for UPI/payment complaints.
"""
import os, csv, json, collections, datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RAW = os.path.join(ROOT, 'data', 'raw_data')
OUT_JSON = os.path.join(ROOT, 'analysis', 'step3c_results.json')
OUT_MD = os.path.join(ROOT, 'analysis', 'STEP3C_INTENT_REPORT.md')

def read_csv(path):
    with open(path, 'r', encoding='utf-8', newline='') as f:
        r = csv.reader(f)
        header = next(r, None)
        rows = [row for row in r]
    return header, rows

train_h, train_rows = read_csv(os.path.join(RAW, 'banking77_train.csv'))
test_h, test_rows = read_csv(os.path.join(RAW, 'banking77_test.csv'))

def counts_and_examples(rows):
    counts = collections.Counter()
    examples = collections.defaultdict(list)
    for row in rows:
        if len(row) < 2:
            continue
        text = row[0]
        intent = row[1]
        counts[intent] += 1
        if len(examples[intent]) < 3:
            examples[intent].append(text)
    return counts, examples

train_counts, train_examples = counts_and_examples(train_rows)
test_counts, test_examples = counts_and_examples(test_rows)

# combined list of intents from dataset_infos if present
infos_path = os.path.join(RAW, 'banking77_dataset_infos.json')
official_intents = None
if os.path.exists(infos_path):
    with open(infos_path, 'r', encoding='utf-8') as f:
        di = json.load(f)
        try:
            official_intents = di['default']['features']['label']['names']
        except Exception:
            official_intents = None

if not official_intents:
    # fallback to union of observed intents
    official_intents = sorted(set(list(train_counts.keys()) + list(test_counts.keys())))

combined_counts = collections.Counter()
for k in official_intents:
    combined_counts[k] = train_counts.get(k, 0) + test_counts.get(k, 0)

# Rule-based classification with manual overrides
direct_keywords = ['transfer', 'top_up', 'top up', 'refund', 'revert', 'receiving_money', 'transaction_charged', 'declined_transfer', 'failed_transfer', 'pending_transfer', 'balance_not_updated', 'verify_top_up', 'top_up_failed', 'top_up_reverted', 'cancel_transfer', 'transfer_not_received', 'transfer_into_account', 'transfer_fee']
borderline_keywords = ['verify', 'identity', 'pin', 'passcode', 'beneficiary', 'direct_debit', 'payment_issue', 'payment_not_recognised', 'request_refund', 'receiving_money', 'cash_withdrawal', 'atm', 'exchange', 'exchange_rate']

def classify_intent(label):
    l = label.lower()
    for kw in direct_keywords:
        if kw in l:
            return 'DIRECT'
    for kw in borderline_keywords:
        if kw in l:
            return 'BORDERLINE'
    return 'IRRELEVANT'

# Manual overrides to correct obvious misclassifications
manual_overrides = {
    'card_payment_fee_charged': 'IRRELEVANT',
    'card_payment_not_recognised': 'IRRELEVANT',
    'card_payment_wrong_exchange_rate': 'IRRELEVANT',
    'card_not_working': 'IRRELEVANT',
    'card_swallowed': 'IRRELEVANT',
    'get_disposable_virtual_card': 'IRRELEVANT',
    'get_physical_card': 'IRRELEVANT',
    'order_physical_card': 'IRRELEVANT',
    'card_arrival': 'IRRELEVANT',
    'card_linking': 'IRRELEVANT',
    'virtual_card_not_working': 'IRRELEVANT',
    'cash_withdrawal_not_recognised': 'IRRELEVANT',
    'cash_withdrawal_charge': 'IRRELEVANT',
    'atm_support': 'IRRELEVANT',
    'contactless_not_working': 'IRRELEVANT',
    'visa_or_mastercard': 'IRRELEVANT',
    'supported_cards_and_currencies': 'IRRELEVANT',
    'balance_not_updated_after_cheque_or_cash_deposit': 'DIRECT',
    'balance_not_updated_after_bank_transfer': 'DIRECT',
    'request_refund': 'DIRECT',
    'Refund_not_showing_up': 'DIRECT'
}

inventory = []
for label in official_intents:
    train_n = train_counts.get(label, 0)
    test_n = test_counts.get(label, 0)
    combined_n = combined_counts.get(label, 0)
    examples = []
    if label in train_examples:
        examples.extend(train_examples[label])
    if label in test_examples:
        examples.extend([e for e in test_examples[label] if e not in examples])
    # choose classification
    if label in manual_overrides:
        cat = manual_overrides[label]
    else:
        cat = classify_intent(label)
    # description: human-readable label
    desc = label.replace('_', ' ')
    inventory.append({
        'intent': label,
        'train_examples': train_n,
        'test_examples': test_n,
        'combined_examples': combined_n,
        'description': desc,
        'relevance': cat,
        'reason': '' ,
        'representative_examples': examples[:3]
    })

# Add simple reasons based on category
for item in inventory:
    intent = item['intent']
    if item['relevance'] == 'DIRECT':
        item['reason'] = 'Represents a payment/transfer/top-up/refund or balance issue that can occur in UPI/digital payments.'
    elif item['relevance'] == 'BORDERLINE':
        item['reason'] = 'May relate to authentication, verification or payment problems that could appear in UPI contexts depending on scope.'
    else:
        item['reason'] = 'Primarily card/ATM/physical-card related or otherwise outside typical UPI complaint scope.'

# Distribution stats
dist = collections.Counter([it['relevance'] for it in inventory])
group_counts = {'train':0,'test':0,'combined':0}
group_examples = {'DIRECT':0,'BORDERLINE':0,'IRRELEVANT':0}
group_examples_split = {'train':collections.Counter(),'test':collections.Counter(),'combined':collections.Counter()}
for it in inventory:
    group_examples[it['relevance']] += it['combined_examples']
    group_examples_split['train'][it['relevance']] += it['train_examples']
    group_examples_split['test'][it['relevance']] += it['test_examples']

results = {
    'generated_on': datetime.datetime.utcnow().isoformat() + 'Z',
    'inventory': inventory,
    'distribution': {
        'intent_group_counts': dict(dist),
        'examples_by_group': dict(group_examples),
        'examples_by_group_split': {k: dict(v) for k,v in group_examples_split.items()}
    }
}

with open(OUT_JSON, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2)

# write markdown report (concise)
with open(OUT_MD, 'w', encoding='utf-8') as f:
    f.write('# Step 3C Intent Analysis Report\n\n')
    f.write('Generated on: ' + results['generated_on'] + '\n\n')
    f.write('## Inventory (77 intents)\n\n')
    for it in inventory:
        f.write(f"- **{it['intent']}** — train:{it['train_examples']} test:{it['test_examples']} total:{it['combined_examples']} — {it['relevance']}\n")
        f.write('  - description: ' + it['description'] + '\n')
        f.write('  - reason: ' + it['reason'] + '\n')
        if it['relevance'] in ('DIRECT','BORDERLINE'):
            for ex in it['representative_examples']:
                f.write('    - example: ' + ex + '\n')
        f.write('\n')
    f.write('## Distribution summary\n\n')
    f.write('Intent counts by category:\n')
    for k,v in dist.items():
        f.write(f'- {k}: {v} intents\n')
    f.write('\nExamples by category (combined):\n')
    for k,v in group_examples.items():
        f.write(f'- {k}: {v} examples\n')
    f.write('\nSplit examples:\n')
    f.write('- train:\n')
    for k,v in group_examples_split['train'].items():
        f.write(f'  - {k}: {v}\n')
    f.write('- test:\n')
    for k,v in group_examples_split['test'].items():
        f.write(f'  - {k}: {v}\n')
    f.write('\n')
    f.write('## Note on methodology\n')
    f.write('Classification used simple keyword rules plus manual overrides; descriptions derived from label names and representative examples from the raw dataset. This is a recommendation step; no raw files were modified.\n')

print('WROTE', OUT_JSON, OUT_MD)
