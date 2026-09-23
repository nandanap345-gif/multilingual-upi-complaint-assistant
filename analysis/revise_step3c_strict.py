#!/usr/bin/env python3
import json, os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
STEP3C = os.path.join(ROOT, 'analysis', 'step3c_results.json')
REPORT_MD = os.path.join(ROOT, 'analysis', 'STEP3C_INTENT_REPORT.md')

with open(STEP3C, 'r', encoding='utf-8') as f:
    data = json.load(f)
inventory = {it['intent']: it for it in data['inventory']}

# Strict DIRECT set (only clearly transferable to UPI without changing intent meaning)
DIRECT = {
    'declined_transfer', 'failed_transfer', 'pending_transfer',
    'transfer_not_received_by_recipient', 'transfer_fee_charged',
    'cancel_transfer', 'transaction_charged_twice', 'transfer_into_account',
    'transfer_timing', 'Refund_not_showing_up', 'request_refund',
    'declined_transfer'  # duplicate allowed
}

# Borderline set: authentication, bank-transfer proxies, or ambiguous top-up cases
BORDERLINE = {
    'automatic_top_up', 'balance_not_updated_after_cheque_or_cash_deposit',
    'change_pin', 'direct_debit_payment_not_recognised', 'exchange_charge',
    'exchange_rate', 'exchange_via_app', 'passcode_forgotten', 'pending_top_up',
    'pin_blocked', 'receiving_money', 'reverted_card_payment?', 'top_up_failed',
    'top_up_reverted', 'topping_up_by_card', 'unable_to_verify_identity',
    'verify_my_identity', 'verify_source_of_funds', 'why_verify_identity',
    'wrong_exchange_rate_for_cash_withdrawal', 'top_up_by_bank_transfer_charge'
}

assign = {}
for intent, item in inventory.items():
    if intent in DIRECT:
        assign[intent] = 'DIRECT'
    elif intent in BORDERLINE:
        assign[intent] = 'BORDERLINE'
    else:
        assign[intent] = 'IRRELEVANT'

counts = {'DIRECT':0,'BORDERLINE':0,'IRRELEVANT':0}
examples_sum = {'DIRECT':{'train':0,'test':0,'combined':0},'BORDERLINE':{'train':0,'test':0,'combined':0},'IRRELEVANT':{'train':0,'test':0,'combined':0}}
for intent,cat in assign.items():
    counts[cat]+=1
    it = inventory[intent]
    examples_sum[cat]['train'] += it['train_examples']
    examples_sum[cat]['test'] += it['test_examples']
    examples_sum[cat]['combined'] += it['combined_examples']

# Load previous report assignments to detect changes
prev = {}
if os.path.exists(REPORT_MD):
    with open(REPORT_MD, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('- **'):
                parts = line.split('**')
                if len(parts) > 2:
                    name = parts[1]
                    rest = parts[2]
                    if '— DIRECT' in rest:
                        prev[name] = 'DIRECT'
                    elif '— BORDERLINE' in rest:
                        prev[name] = 'BORDERLINE'
                    elif '— IRRELEVANT' in rest:
                        prev[name] = 'IRRELEVANT'

changed = []
for k,v in assign.items():
    pv = prev.get(k)
    if pv and pv != v:
        changed.append((k,pv,v))

# Print concise machine-readable summary to stdout
print('TOTAL_INTENTS', len(assign))
print('DIRECT_COUNT', counts['DIRECT'])
print('BORDERLINE_COUNT', counts['BORDERLINE'])
print('IRRELEVANT_COUNT', counts['IRRELEVANT'])
print('\nEXAMPLES_SUM')
print(json.dumps(examples_sum, indent=2))

print('\nCHANGED_CLASSIFICATIONS_COUNT', len(changed))
for a,b,c in changed:
    print(a, b, '->', c)

print('\nDIRECT_LIST')
for it in sorted([k for k,v in assign.items() if v=='DIRECT']):
    item = inventory[it]
    ex = item.get('representative_examples', [])[:2]
    print(f"- {it} {item['train_examples']} {item['test_examples']} {item['combined_examples']}")
    for e in ex:
        print('   -', e)

print('\nBORDERLINE_LIST')
for it in sorted([k for k,v in assign.items() if v=='BORDERLINE']):
    item = inventory[it]
    ex = item.get('representative_examples', [])[:2]
    print(f"- {it} {item['train_examples']} {item['test_examples']} {item['combined_examples']}")
    for e in ex:
        print('   -', e)

print('\nIRRELEVANT_LIST')
for it in sorted([k for k,v in assign.items() if v=='IRRELEVANT']):
    item = inventory[it]
    print(f"- {it} {item['train_examples']} {item['test_examples']} {item['combined_examples']}")

print('\nDONE')
