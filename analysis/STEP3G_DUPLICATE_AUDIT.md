# STEP 3G — Cross-Split Duplicate Audit

## Dataset Counts

- Raw train: 10003
- Raw test: 3080
- Raw combined: 13083
- Processed train: 10003
- Processed test: 3073

## Duplicate Findings

- Exact cross-split duplicate matches: 7
- Reported duplicates removed: 7
- All duplicate labels identical: True
- Remaining processed train/test overlap: 0
- Leakage check passed: True

## Duplicate Records

### Duplicate 1

- Raw train index: 1722
- Raw test index: 554
- Text: `How do I unblock my PIN?`
- Train category: `pin_blocked`
- Test category: `pin_blocked`
- Labels identical: `True`

### Duplicate 2

- Raw train index: 3103
- Raw test index: 976
- Text: `

What businesses accept this card?`
- Train category: `card_acceptance`
- Test category: `card_acceptance`
- Labels identical: `True`

### Duplicate 3

- Raw train index: 3116
- Raw test index: 977
- Text: `Where can I use my card?`
- Train category: `card_acceptance`
- Test category: `card_acceptance`
- Labels identical: `True`

### Duplicate 4

- Raw train index: 4476
- Raw test index: 1432
- Text: `There are a few transaction that I don't recognize, I think someone managed to get my card details and use it.`
- Train category: `compromised_card`
- Test category: `compromised_card`
- Labels identical: `True`

### Duplicate 5

- Raw train index: 4576
- Raw test index: 1474
- Text: `At which ATMs can I use this card?`
- Train category: `atm_support`
- Test category: `atm_support`
- Labels identical: `True`

### Duplicate 6

- Raw train index: 6984
- Raw test index: 2149
- Text: `Which cash machines will allow me to change my PIN?`
- Train category: `change_pin`
- Test category: `change_pin`
- Labels identical: `True`

### Duplicate 7

- Raw train index: 9921
- Raw test index: 3070
- Text: `I don't live in the UK.  Can I still get a card?`
- Train category: `country_support`
- Test category: `country_support`
- Labels identical: `True`

## Overall Result

**PASS — Step 3G duplicate audit completed successfully.**
